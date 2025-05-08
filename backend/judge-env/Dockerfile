FROM ubuntu:20.04

# 安装必要的工具包、C++编译器和调试工具
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    build-essential \
    g++ \
    gcc \
    gdb \
    cmake \
    time \
    python3 \
    python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /judge

# 创建非root用户以安全运行提交的代码
RUN useradd -m -s /bin/bash judge
RUN chown -R judge:judge /judge

# 切换到judge用户
USER judge

# 设置容器入口点
CMD ["bash"]
