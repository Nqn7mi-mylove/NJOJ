"""Core evaluator module for LLM-based code evaluation."""

import json
import uuid
import traceback
from typing import Dict, List, Any, Optional

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

from .config import llm_config
from .prompts import ERROR_ANALYSIS_PROMPT, IMPROVEMENT_PROMPT
from .models import EvaluationResult, ErrorAnalysis, ImprovementSuggestion
from .utils import (
    parse_llm_response,
    direct_json_parse,
    format_test_results,
    create_error_response,
    create_fallback_response
)


class LLMEvaluator:
    """Class for evaluating code using a Large Language Model."""
    
    def __init__(self, model_name: str = None):
        """Initialize the LLM evaluator.
        
        Args:
            model_name: Optional name of the LLM model to use, defaults to config value
        """
        # Use provided model name or default from config
        self.model_name = model_name or llm_config.model_name
        
        # Set up environment variables
        llm_config.setup_environment()
        
        # Initialize LangChain chat model
        self.chat_model = ChatOpenAI(
            api_key=llm_config.api_key,
            model=self.model_name,
            temperature=llm_config.temperature,
            model_kwargs=llm_config.get_model_kwargs()
        )
        
        # Define prompt templates
        self.error_analysis_template = PromptTemplate.from_template(ERROR_ANALYSIS_PROMPT)
        self.improvement_template = PromptTemplate.from_template(IMPROVEMENT_PROMPT)
    
    async def evaluate_code(
            self, 
            code: str, 
            problem_description: str,
            test_results: Optional[List[Dict[str, Any]]] = None
        ) -> Dict[str, Any]:
        """Evaluate code using the LLM with a two-step process.
        
        Args:
            code: The code to evaluate
            problem_description: The problem description
            test_results: Optional test results to include in the evaluation
            
        Returns:
            dict: The evaluation results
        """
        try:
            # 调试标记：每次请求显示唯一ID，帮助跟踪调用是否真的发生
            request_id = str(uuid.uuid4())[:8]
            print(f"===== 开始LLM评估 [ID:{request_id}] =====")
            
            # 检查API密钥是否配置
            if not llm_config.api_key:
                print("警告: 未配置API密钥，无法进行LLM评估")
                return create_error_response("未配置OpenAI API密钥")
                
            # 格式化测试结果
            formatted_test_results = format_test_results(test_results) if test_results else "无测试结果"
            
            # 如果没有测试结果，直接返回一个错误响应
            if not test_results or len(test_results) == 0:
                print("无测试结果，无法进行评估")
                return create_error_response("AI评估服务暂时不可用")
                
            # 使用双步评估
            try:
                print("开始第一步：错误分析")
                # 第一步：错误分析 - 使用安全的封装方法
                error_analysis = await self._safe_error_analysis(code, problem_description, formatted_test_results)
                if error_analysis is None:
                    print("错误分析失败，评估终止")
                    return create_error_response("AI评估服务暂时不可用")
                
                print("开始第二步：改进建议")
                # 第二步：改进建议 - 使用安全的封装方法
                improvement_data = await self._safe_improvement_analysis(
                    code, problem_description, formatted_test_results, error_analysis
                )
                
                if improvement_data is None:
                    print("改进建议分析失败，使用错误分析结果构建基本响应")
                    # 使用错误分析结果构建一个基本响应
                    return {
                        "error_types": error_analysis.get("error_types", []),
                        "explanation": error_analysis.get("explanation", ""),
                        "error_details": error_analysis.get("error_details", []),
                        "code_standard": {"pros": [], "cons": ["评估部分失败"]},
                        "code_logic": {"pros": [], "cons": []},
                        "code_efficiency": {"pros": [], "cons": []},
                        "improvement_suggestions": ["由于部分评估失败，无法提供详细建议"],
                        "overall_score": "0",
                        "summary": "部分评估完成"
                    }
                
                # 确保字段正确
                self._ensure_evaluation_fields(improvement_data)
                
                # 合并结果
                result = {
                    # 错误分析部分
                    "error_types": error_analysis.get("error_types", []),
                    "explanation": error_analysis.get("explanation", ""),
                    "error_details": error_analysis.get("error_details", []),
                    
                    # 改进建议部分
                    "code_standard": improvement_data.get("code_standard", {"pros": [], "cons": []}),
                    "code_logic": improvement_data.get("code_logic", {"pros": [], "cons": []}),
                    "code_efficiency": improvement_data.get("code_efficiency", {"pros": [], "cons": []}),
                    "improvement_suggestions": improvement_data.get("improvement_suggestions", []),
                    "overall_score": improvement_data.get("overall_score", "0"),
                    "summary": improvement_data.get("summary", "")
                }
                
                return result
            except Exception as e:
                print("\n====== 双步评估异常详细堆栈 ======")
                traceback.print_exc()
                print(f"双步评估过程中出现错误: {type(e).__name__}: {str(e)}")
                print("====================================\n")
                
                # 返回错误响应
                return create_error_response("AI评估服务暂时不可用")
        except Exception as e:
            print("\n====== LLM评估总体异常 ======")
            traceback.print_exc()
            print(f"LLM评估过程中出现错误: {type(e).__name__}: {str(e)}")
            print("====================================\n")
            
            # 提供一个默认响应
            return create_error_response("AI评估服务暂时不可用")
            
    async def _safe_error_analysis(self, code: str, problem_description: str, test_results: str) -> Optional[Dict[str, Any]]:
        """安全地执行错误分析，处理所有可能的异常
        
        Args:
            code: 待评估代码
            problem_description: 问题描述
            test_results: 格式化的测试结果
            
        Returns:
            Optional[Dict[str, Any]]: 成功时返回分析结果，失败时返回None
        """
        try:
            # 格式化提示模板
            formatted_prompt = self.error_analysis_template.format(
                problem_description=problem_description,
                code=code,
                test_results=test_results
            )
            
            # 调用API
            analysis_result = await self._call_llm_api(formatted_prompt)
            
            # 打印原始响应，帮助调试
            print("\n====== LLM原始响应(错误分析) ======")
            print(f"\n{analysis_result}\n")
            print("======================================\n")
            
            # 打印响应的字节表示，帮助调试不可见字符
            print("\n====== 原始响应的字节表示 ======")
            print(repr(analysis_result))
            print("======================================\n")
            
            # 解析结果
            error_analysis = direct_json_parse(analysis_result)
            print("错误分析解析成功")
            return error_analysis
        except Exception as e:
            print(f"错误分析失败: {type(e).__name__}: {str(e)}")
            return None
    
    async def _safe_improvement_analysis(
            self, 
            code: str, 
            problem_description: str, 
            test_results: str, 
            error_analysis: Dict[str, Any]
        ) -> Optional[Dict[str, Any]]:
        """安全地执行改进建议分析，处理所有可能的异常
        
        Args:
            code: 待评估代码
            problem_description: 问题描述
            test_results: 格式化的测试结果
            error_analysis: 错误分析结果
            
        Returns:
            Optional[Dict[str, Any]]: 成功时返回改进建议，失败时返回None
        """
        try:
            # 格式化提示模板
            formatted_prompt = self.improvement_template.format(
                problem_description=problem_description,
                code=code,
                test_results=test_results,
                analysis=json.dumps(error_analysis, ensure_ascii=False)
            )
            
            # 调用API
            improvement_result = await self._call_llm_api(formatted_prompt)
            
            # 解析结果
            improvement_data = direct_json_parse(improvement_result)
            print("改进建议解析成功")
            return improvement_data
        except Exception as e:
            print(f"改进建议分析失败: {type(e).__name__}: {str(e)}")
            return None
            

    async def _call_llm_api(self, prompt: str) -> str:
        """Call the LLM API with a prompt using LangChain.
        
        Args:
            prompt: The prompt to send to the API
            
        Returns:
            str: The response text
        """
        try:
            # 打印配置信息以进行调试
            print("\n====== LLM配置信息 ======")
            print(f"模型名称: {self.model_name}")
            print(f"API基础URL: {llm_config.api_base}")
            print(f"API密钥: {llm_config.api_key[:5]}...{llm_config.api_key[-4:] if len(llm_config.api_key) > 9 else ''}")
            print(f"温度: {llm_config.temperature}")
            print(f"响应格式JSON: {llm_config.response_format_json}")
            print(f"模型参数: {llm_config.get_model_kwargs()}")
            print("==============================\n")
            
            # 使用LangChain调用LLM
            print("\n====== 发送给LLM的提示 ======")
            print(prompt[:500] + "..." if len(prompt) > 500 else prompt)  # 防止过长
            print("==============================\n")
            
            print("开始调用LLM API...")
            response = await self.chat_model.apredict(prompt)
            print("LLM API调用完成!")
            
            # 打印原始响应，无论是否发生异常
            print("\n====== LLM原始响应 ======")
            print(response)
            print("==============================\n")
            
            # 打印字节表示，便于调试不可见字符
            print("\n====== 原始响应的字节表示 ======")
            print(repr(response))
            print("==============================\n")
            
            return response
        except Exception as e:
            print(f"\n====== LLM API调用异常 ======")
            print(f"异常类型: {type(e).__name__}")
            print(f"异常消息: {str(e)}")
            traceback.print_exc()
            print("==============================\n")
            
            # 返回一个显示错误的特殊响应，而不是直接抛出异常
            # 这样我们可以看到错误细节，而不是一个通用的KeyError
            error_response = {
                "error": f"API调用失败: {type(e).__name__}: {str(e)}",
                "error_types": ["API错误"],
                "explanation": str(e)
            }
            return json.dumps(error_response)
    
    def _ensure_evaluation_fields(self, data: Dict[str, Any]) -> None:
        """确保评估结果包含所有必要字段
        
        Args:
            data: 评估结果数据
        """
        # 确保基本字段存在
        if "code_standard" not in data:
            data["code_standard"] = {"pros": [], "cons": []}
        elif isinstance(data["code_standard"], list):
            data["code_standard"] = {"pros": [], "cons": data["code_standard"]}
            
        if "code_logic" not in data:
            data["code_logic"] = {"pros": [], "cons": []}
            
        if "code_efficiency" not in data:
            data["code_efficiency"] = {"pros": [], "cons": []}
            
        if "improvement_suggestions" not in data:
            if "suggestions" in data:
                data["improvement_suggestions"] = data["suggestions"]
            else:
                data["improvement_suggestions"] = []
                
        if "summary" not in data:
            data["summary"] = ""
            
        if "overall_score" not in data:
            data["overall_score"] = "0"
            
        # 确保字段格式正确
        for field in ["code_standard", "code_logic", "code_efficiency"]:
            if field in data and isinstance(data[field], dict):
                if "pros" not in data[field]:
                    data[field]["pros"] = []
                if "cons" not in data[field]:
                    data[field]["cons"] = []


# Create a singleton instance
llm_evaluator = LLMEvaluator()
