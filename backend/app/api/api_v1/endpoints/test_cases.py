from typing import Any, List
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from bson.objectid import ObjectId
import os
import tempfile
import shutil

from app.db.mongodb import db
from app.api.deps import get_current_admin_user
from app.models.problem import TestCase

router = APIRouter()

@router.post("/upload", response_model=List[TestCase])
async def upload_test_cases(
    files: List[UploadFile] = File(...),
    current_user = Depends(get_current_admin_user)
) -> Any:
    """
    Upload test case files (.in and .out) and return parsed test cases.
    Files should be named with matching prefixes, e.g. test1.in, test1.out.
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files uploaded"
        )
    
    # 创建临时目录存储上传的文件
    temp_dir = tempfile.mkdtemp()
    try:
        # 保存上传的文件到临时目录
        for file in files:
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)
        
        # 解析文件并生成测试用例
        test_cases = parse_test_case_files(temp_dir)
        
        return test_cases
    finally:
        # 清理临时目录
        shutil.rmtree(temp_dir)

def parse_test_case_files(directory: str) -> List[TestCase]:
    """
    解析目录中的.in和.out文件，生成测试用例列表
    文件名应当有对应的前缀，如test1.in和test1.out
    """
    # 获取目录中的所有文件
    files = os.listdir(directory)
    
    # 分离.in和.out文件
    in_files = [f for f in files if f.endswith('.in')]
    out_files = [f for f in files if f.endswith('.out')]
    
    # 按文件名排序
    in_files.sort()
    out_files.sort()
    
    test_cases = []
    
    # 创建文件名映射，去除.in和.out后缀
    in_map = {os.path.splitext(f)[0]: f for f in in_files}
    out_map = {os.path.splitext(f)[0]: f for f in out_files}
    
    # 查找匹配的文件对
    for base_name in in_map:
        if base_name in out_map:
            # 读取文件内容
            with open(os.path.join(directory, in_map[base_name]), 'r') as f:
                input_content = f.read()
            
            with open(os.path.join(directory, out_map[base_name]), 'r') as f:
                output_content = f.read()
            
            # 创建测试用例
            test_case = TestCase(
                input=input_content,
                output=output_content,
                is_sample=False  # 默认为非样例测试用例
            )
            test_cases.append(test_case)
    
    return test_cases
