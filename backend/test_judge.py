import docker
import tempfile
import os
import sys

# 测试Docker评测环境
print("测试Docker评测环境...")

# 初始化Docker客户端
try:
    import os
    os.environ["DOCKER_HOST"] = "unix:///var/run/docker.sock"
    client = docker.from_env()
    print("成功连接到Docker服务")
except Exception as e:
    print(f"连接Docker失败: {e}")
    sys.exit(1)

# 检查judge-env镜像是否存在
try:
    client.images.get("judge-env")
    print("judge-env镜像已找到")
except docker.errors.ImageNotFound:
    print("judge-env镜像未找到")
    sys.exit(1)

# 创建一个临时目录和测试代码
with tempfile.TemporaryDirectory() as temp_dir:
    print(f"创建临时目录: {temp_dir}")
    
    # 写入一个简单的C++程序
    test_code = """
    #include <iostream>
    using namespace std;
    
    int main() {
        int a, b;
        cin >> a >> b;
        cout << "测试成功: " << a + b << endl;
        return 0;
    }
    """
    
    with open(os.path.join(temp_dir, "solution.cpp"), "w") as f:
        f.write(test_code)
    
    # 写入测试输入
    with open(os.path.join(temp_dir, "input.txt"), "w") as f:
        f.write("10 20")
    
    # 编译代码
    print("编译代码...")
    try:
        container = client.containers.run(
            "judge-env",
            command=f"bash -c 'cd /judge && g++ -std=c++17 -O2 -Wall solution.cpp -o solution'",
            volumes={temp_dir: {"bind": "/judge", "mode": "rw"}},
            detach=True,
            network_disabled=True
        )
        
        # 等待容器完成
        result = container.wait()
        logs = container.logs().decode("utf-8")
        container.remove()
        
        if result["StatusCode"] != 0:
            print(f"编译失败: {logs}")
            sys.exit(1)
        else:
            print("编译成功")
    except Exception as e:
        print(f"编译过程出错: {e}")
        sys.exit(1)
    
    # 运行代码
    print("运行代码...")
    try:
        container = client.containers.run(
            "judge-env",
            command=f"bash -c 'cd /judge && ./solution < input.txt > output.txt'",
            volumes={temp_dir: {"bind": "/judge", "mode": "rw"}},
            detach=True,
            network_disabled=True
        )
        
        # 等待容器完成
        result = container.wait()
        logs = container.logs().decode("utf-8")
        container.remove()
        
        if result["StatusCode"] != 0:
            print(f"运行失败: {logs}")
            sys.exit(1)
        else:
            print("运行成功")
            
            # 读取输出
            with open(os.path.join(temp_dir, "output.txt"), "r") as f:
                output = f.read().strip()
                print(f"程序输出: {output}")
    except Exception as e:
        print(f"运行过程出错: {e}")
        sys.exit(1)

print("测试完成！Docker评测环境工作正常。")
print("现在您可以使用Online Judge系统提交代码并运行测试用例。")
