import os
import tempfile
import shutil
import asyncio
import subprocess
from bson.objectid import ObjectId
import logging
import re

from app.db.mongodb import db
from app.models.submission import JudgeStatus
from app.core.config import settings
from app.judge.llm_evaluator import LLMEvaluator
from app.judge.llm_evaluator import llm_evaluator as global_llm_evaluator

# 检查Docker是否可用
try:
    result = subprocess.run(["docker", "version"], capture_output=True, text=True)
    if result.returncode == 0:
        docker_available = True
        print("Successfully connected to Docker daemon")
    else:
        docker_available = False
        print(f"Warning: Docker connection error: {result.stderr}")
        print("Judge service will be disabled. Make sure Docker is running and accessible.")
except Exception as e:
    docker_available = False
    print(f"Warning: Docker connection error: {e}")
    print("Judge service will be disabled. Make sure Docker is running and accessible.")

async def judge_submission(submission_id: str, problem_id: str, user_id: str):
    """
    Judge a code submission.
    
    Args:
        submission_id: Submission ID
        problem_id: Problem ID
        user_id: User ID
    """
    submissions_collection = db.db.submissions
    problems_collection = db.db.problems
    
    # Update submission status to judging
    await submissions_collection.update_one(
        {"_id": ObjectId(submission_id)},
        {"$set": {"status": JudgeStatus.JUDGING}}
    )
    
    # Get submission and problem data
    submission = await submissions_collection.find_one({"_id": ObjectId(submission_id)})
    problem = await problems_collection.find_one({"_id": ObjectId(problem_id)})
    
    # Extract code from submission
    code = submission["code"]
    
    # Check if Docker is available
    if not docker_available:
        await _update_submission_status(
            submission_id, 
            JudgeStatus.SYSTEM_ERROR, 
            "Docker is not available. Judge service is disabled."
        )
        
        # Even if docker is unavailable, we can still provide LLM evaluation
        try:
            # 创建一个基本的测试结果对象，表明Docker不可用，未运行测试
            dummy_test_results = [{
                "id": "docker_unavailable",
                "status": "SYSTEM_ERROR",
                "actual_output": "Docker不可用，无法运行测试",
                "expected_output": "N/A",
                "test_case": {"name": "系统错误", "tag": "Docker不可用"}
            }]
            
            llm_results = await llm_evaluator.evaluate_code(
                code=code,
                problem_description=problem["description"],
                test_results=dummy_test_results
            )
            
            # Update submission with LLM evaluation results
            await submissions_collection.update_one(
                {"_id": ObjectId(submission_id)},
                {"$set": {"llm_evaluation": llm_results}}
            )
        except Exception as e:
            print(f"LLM evaluation failed: {str(e)}")
            # 创建前端可以显示的错误结果格式
            error_result = {
                "error": f"LLM评估遇到错误: {str(e)}",
                "summary": "代码评估过程中遇到技术问题",
                "code_standard": {"pros": [], "cons": ["评估失败"]},
                "code_logic": {"pros": [], "cons": []},
                "code_efficiency": {"pros": [], "cons": []},
                "improvement_suggestions": ["由于技术原因无法提供详细建议"],
                "overall_score": "N/A"
            }
            
            # 更新提交记录，使用错误信息但保持前端期望的格式
            await submissions_collection.update_one(
                {"_id": ObjectId(submission_id)},
                {"$set": {"llm_evaluation": error_result}}
            )
            
        return
    
    try:
        # Create temporary directory for judging
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save code to file
            with open(os.path.join(temp_dir, "solution.cpp"), "w") as f:
                f.write(code)
            
            # Get problem test cases and metadata
            test_cases = problem.get("test_cases", [])
            time_limit = problem.get("time_limit", 1000)  # ms
            memory_limit = problem.get("memory_limit", 256)  # MB
            
            # Check if there's a special judge
            has_special_judge = problem.get("has_special_judge", False)
            special_judge_code = problem.get("special_judge_code", "")
            
            # Compile code
            compile_result = await _compile_code(temp_dir)
            
            if not compile_result["success"]:
                # Update submission status to compilation error
                await _update_submission_status(
                    submission_id, 
                    JudgeStatus.COMPILATION_ERROR, 
                    compile_result["error"]
                )
                return
            
            # Run test cases
            test_case_results = []
            passed_test_cases = 0
            final_status = JudgeStatus.ACCEPTED
            
            for i, test_case in enumerate(test_cases):
                # 确保每个测试用例都有一个ID
                if "id" not in test_case:
                    test_case["id"] = f"tc{i+1}"
                
                result = await _run_test_case(
                    temp_dir, 
                    test_case,
                    time_limit, 
                    memory_limit,
                    has_special_judge, 
                    special_judge_code
                )
                
                test_case_results.append(result)
                
                if result["status"] != JudgeStatus.ACCEPTED:
                    final_status = result["status"]
                    break
                
                passed_test_cases += 1
            
            # After processing test cases, perform LLM evaluation
            try:
                # 添加非常明显的打印语句，确认这段代码确实被执行
                print("\n!!!!!!! 准备调用LLM评估器 !!!!!!!!!")
                print(f"\n!!!!!!! 提交ID: {submission_id} !!!!!!!!!")
                print(f"\n!!!!!!! 测试用例结果数量: {len(test_case_results)} !!!!!!!!!\n")
                
                # Get problem description
                problem_description = problem["description"]
                
                # 直接传递测试用例结果列表，而不是包装到字典中
                print("\n!!!!!!! 正在调用llm_evaluator.evaluate_code !!!!!!!!!")
                
                # 重要修改：每次调用前创建新的评估器实例
                # 这确保我们使用的是最新的代码，而不是服务启动时创建的单例
                print("\n!!!!!!! 创建新的LLM评估器实例 !!!!!!!!!")
                fresh_evaluator = LLMEvaluator()
                
                llm_results = await fresh_evaluator.evaluate_code(
                    code=code,
                    problem_description=problem_description,
                    test_results=test_case_results
                )
                
                print("\n!!!!!!! LLM评估完成 !!!!!!!!!")
                print(f"\n!!!!!!! 返回结果类型: {type(llm_results)} !!!!!!!!!")
                print(f"\n!!!!!!! 返回结果的键: {list(llm_results.keys()) if isinstance(llm_results, dict) else 'Not a dict'} !!!!!!!!!\n")
                
                # Update submission with LLM evaluation results
                await submissions_collection.update_one(
                    {"_id": ObjectId(submission_id)},
                    {"$set": {"llm_evaluation": llm_results}}
                )
            except Exception as e:
                print(f"LLM evaluation failed: {str(e)}")
                # 创建前端可以显示的错误结果格式
                error_result = {
                    "error": f"LLM评估遇到错误: {str(e)}",
                    "summary": "代码评估过程中遇到技术问题",
                    "code_standard": {"pros": [], "cons": ["评估失败"]},
                    "code_logic": {"pros": [], "cons": []},
                    "code_efficiency": {"pros": [], "cons": []},
                    "improvement_suggestions": ["由于技术原因无法提供详细建议"],
                    "overall_score": "N/A"
                }
                
                # 更新提交记录，使用错误信息但保持前端期望的格式
                await submissions_collection.update_one(
                    {"_id": ObjectId(submission_id)},
                    {"$set": {"llm_evaluation": error_result}}
                )
            
            # Update submission with results
            await submissions_collection.update_one(
                {"_id": ObjectId(submission_id)},
                {"$set": {
                    "status": final_status,
                    "test_case_results": test_case_results,
                    "time_used": max([case["time_used"] for case in test_case_results]) if test_case_results else 0,
                    "memory_used": max([case["memory_used"] for case in test_case_results]) if test_case_results else 0
                }}
            )
            
            if final_status == JudgeStatus.ACCEPTED:
                # Update user's solved problems if not already solved
                await db.db.users.update_one(
                    {
                        "_id": ObjectId(user_id),
                        "solved_problems": {"$ne": problem_id}
                    },
                    {"$addToSet": {"solved_problems": problem_id}}
                )
                
                # Update problem's accepted count (only count once per user)
                user_accepted = await submissions_collection.find_one({
                    "problem_id": problem_id,
                    "user_id": user_id,
                    "status": JudgeStatus.ACCEPTED,
                    "_id": {"$ne": ObjectId(submission_id)}
                })
                
                if not user_accepted:
                    await problems_collection.update_one(
                        {"_id": ObjectId(problem_id)},
                        {"$inc": {"accepted_count": 1}}
                    )
            
    except Exception as e:
        # Update submission status to system error
        await _update_submission_status(submission_id, JudgeStatus.SYSTEM_ERROR, str(e))

async def _update_submission_status(submission_id: str, status: JudgeStatus, error_message: str = None):
    """
    Update submission status.
    
    Args:
        submission_id: Submission ID
        status: Status to update
        error_message: Error message if any
    """
    update_data = {"status": status}
    if error_message:
        update_data["error_message"] = error_message
    
    await db.db.submissions.update_one(
        {"_id": ObjectId(submission_id)},
        {"$set": update_data}
    )

async def _compile_code(temp_dir: str) -> dict:
    """
    Compile C++ code.
    
    Args:
        temp_dir: Temporary directory path
    
    Returns:
        dict: Compilation result
    """
    try:
        # 使用subprocess调用Docker命令编译代码
        cmd = [
            "docker", "run", "--rm", 
            "-v", f"{temp_dir}:/judge", 
            "--user", "root",
            "judge-env", 
            "bash", "-c", 
            "cd /judge && g++ -std=c++17 -O2 -Wall solution.cpp -o solution"
        ]
        
        # 运行编译命令
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # 检查编译结果
        if result.returncode != 0:
            return {"success": False, "error": result.stderr}
        
        # 检查二进制文件是否存在
        if os.path.exists(os.path.join(temp_dir, "solution")):
            return {"success": True}
        else:
            return {"success": False, "error": "Compilation succeeded but binary not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def _run_test_case(temp_dir: str, test_case: dict, time_limit: int, memory_limit: int, 
                         has_special_judge: bool, special_judge_code: str = None) -> dict:
    """
    Run a test case.
    
    Args:
        temp_dir: Temporary directory path
        test_case: Test case data
        time_limit: Time limit in ms
        memory_limit: Memory limit in MB
        has_special_judge: Whether to use special judge
        special_judge_code: Special judge code if any
    
    Returns:
        dict: Test case result
    """
    try:
        # Write input to file
        input_file = os.path.join(temp_dir, "input.txt")
        with open(input_file, "w") as f:
            f.write(test_case["input"])
        
        # Write expected output to file
        expected_output_file = os.path.join(temp_dir, "expected_output.txt")
        with open(expected_output_file, "w") as f:
            f.write(test_case["output"])
        
        # Prepare special judge if needed
        if has_special_judge and special_judge_code:
            special_judge_file = os.path.join(temp_dir, "special_judge.cpp")
            with open(special_judge_file, "w") as f:
                f.write(special_judge_code)
            
            # Compile special judge
            sj_cmd = [
                "docker", "run", "--rm", 
                "-v", f"{temp_dir}:/judge", 
                "--user", "root",
                "judge-env", 
                "bash", "-c", 
                "cd /judge && g++ -std=c++17 -O2 -Wall special_judge.cpp -o special_judge"
            ]
            subprocess.run(sj_cmd, capture_output=True, text=True, check=True)
        
        # Run solution with time and memory constraints
        run_cmd = [
            "docker", "run", "--rm", 
            "-v", f"{temp_dir}:/judge", 
            "--user", "root",
            "-m", f"{memory_limit}m",
            "--memory-swap", f"{memory_limit}m",
            "--name", f"judge-container-{test_case['id']}",
            "judge-env", 
            "bash", "-c", 
            f"cd /judge && /usr/bin/time -v timeout {time_limit/1000} ./solution < input.txt > output.txt 2> time_stats.txt"
        ]
        
        # 运行测试用例
        run_result = subprocess.run(run_cmd, capture_output=True, text=True)
        
        # 解析运行结果
        output_file = os.path.join(temp_dir, "output.txt")
        time_stats_file = os.path.join(temp_dir, "time_stats.txt")
        
        # 检查是否存在输出文件
        if not os.path.exists(output_file):
            return {
                "test_case_id": test_case["id"],
                "status": JudgeStatus.SYSTEM_ERROR,
                "time_used": 0,
                "memory_used": memory_used,
                "error_message": "No output file produced",
                "output": ""
            }
        
        # 读取程序输出
        with open(output_file, "r") as f:
            actual_output = f.read()
        
        # 计算时间和内存使用
        time_used = 0
        memory_used = 0
        if os.path.exists(time_stats_file):
            with open(time_stats_file, "r") as f:
                time_content = f.read()
                
                # 获取执行时间（秒）
                time_match = re.search(r"User time \(seconds\): (\d+\.\d+)", time_content)
                if time_match:
                    time_used = int(float(time_match.group(1)) * 1000)  # 转换为毫秒
                    
                # 获取最大驻留集大小（内存使用）
                memory_match = re.search(r"Maximum resident set size \(kbytes\): (\d+)", time_content)
                if memory_match:
                    memory_used = int(memory_match.group(1))  # 已经是KB单位
        
        # 检查时间限制
        if time_used > time_limit:
            return {
                "test_case_id": test_case["id"],
                "status": JudgeStatus.TIME_LIMIT_EXCEEDED,
                "time_used": time_used,
                "memory_used": memory_used,
                "error_message": f"Time limit exceeded: {time_used}ms > {time_limit}ms",
                "output": actual_output[:100] + "..." if len(actual_output) > 100 else actual_output
            }
        
        # 检查运行时错误
        if run_result.returncode != 0:
            return {
                "test_case_id": test_case["id"],
                "status": JudgeStatus.RUNTIME_ERROR,
                "time_used": time_used,
                "memory_used": memory_used,
                "error_message": run_result.stderr,
                "output": actual_output[:100] + "..." if len(actual_output) > 100 else actual_output
            }
        
        # 如果使用特殊评测
        if has_special_judge and os.path.exists(os.path.join(temp_dir, "special_judge")):
            # 运行特殊评测
            sj_run_cmd = [
                "docker", "run", "--rm", 
                "-v", f"{temp_dir}:/judge", 
                "--user", "root",
                "judge-env", 
                "bash", "-c", 
                "cd /judge && ./special_judge"
            ]
            sj_result = subprocess.run(sj_run_cmd, capture_output=True, text=True)
            
            # 检查特殊评测结果
            if sj_result.returncode == 0:
                return {
                    "test_case_id": test_case["id"],
                    "status": JudgeStatus.ACCEPTED,
                    "time_used": time_used,
                    "memory_used": memory_used,
                    "error_message": None,
                    "output": actual_output[:100] + "..." if len(actual_output) > 100 else actual_output
                }
            else:
                return {
                    "test_case_id": test_case["id"],
                    "status": JudgeStatus.WRONG_ANSWER,
                    "time_used": time_used,
                    "memory_used": memory_used,
                    "error_message": sj_result.stdout or sj_result.stderr,
                    "output": actual_output[:100] + "..." if len(actual_output) > 100 else actual_output
                }
        else:
            # 普通评测，简单比较输出
            expected_output = test_case["output"].strip()
            actual_output = actual_output.strip()
            
            if expected_output == actual_output:
                return {
                    "test_case_id": test_case["id"],
                    "status": JudgeStatus.ACCEPTED,
                    "time_used": time_used,
                    "memory_used": memory_used,
                    "error_message": None,
                    "output": actual_output[:100] + "..." if len(actual_output) > 100 else actual_output
                }
            else:
                return {
                    "test_case_id": test_case["id"],
                    "status": JudgeStatus.WRONG_ANSWER,
                    "time_used": time_used,
                    "memory_used": memory_used,
                    "error_message": "Output doesn't match expected output",
                    "output": actual_output[:100] + "..." if len(actual_output) > 100 else actual_output
                }
    except Exception as e:
        return {
            "test_case_id": test_case["id"],
            "status": JudgeStatus.SYSTEM_ERROR,
            "time_used": time_used,
            "memory_used": memory_used,
            "error_message": str(e),
            "output": ""
        }
