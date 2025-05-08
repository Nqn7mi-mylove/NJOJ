#!/bin/bash

echo "测试Docker评测环境..."

# 检查Docker是否可用
if ! docker info > /dev/null 2>&1; then
    echo "错误：无法连接到Docker服务"
    exit 1
fi

echo "成功连接到Docker服务"

# 检查judge-env镜像是否存在
if ! docker image inspect judge-env > /dev/null 2>&1; then
    echo "错误：judge-env镜像未找到"
    exit 1
fi

echo "judge-env镜像已找到"

# 创建临时目录
TEMP_DIR=$(mktemp -d)
echo "创建临时目录: $TEMP_DIR"

# 清理函数
cleanup() {
    echo "清理临时文件..."
    rm -rf "$TEMP_DIR"
    echo "清理完成"
}

# 捕获脚本退出信号，确保清理
trap cleanup EXIT

# 创建测试代码
cat > "$TEMP_DIR/solution.cpp" << EOF
#include <iostream>
using namespace std;

int main() {
    int a, b;
    cin >> a >> b;
    cout << "测试成功: " << a + b << endl;
    return 0;
}
EOF

# 创建测试输入
echo "10 20" > "$TEMP_DIR/input.txt"

# 编译代码
echo "编译代码..."
docker run --rm -v "$TEMP_DIR:/judge" --user root judge-env bash -c "cd /judge && g++ -std=c++17 -O2 -Wall solution.cpp -o solution"

if [ $? -ne 0 ]; then
    echo "编译失败"
    exit 1
fi

echo "编译成功"

# 运行代码
echo "运行代码..."
docker run --rm -v "$TEMP_DIR:/judge" --user root judge-env bash -c "cd /judge && ./solution < input.txt > output.txt"

if [ $? -ne 0 ]; then
    echo "运行失败"
    exit 1
fi

echo "运行成功"

# 显示输出
echo "程序输出:"
cat "$TEMP_DIR/output.txt"

echo "测试完成！Docker评测环境工作正常。"
echo "现在您可以使用Online Judge系统提交代码并运行测试用例。"
