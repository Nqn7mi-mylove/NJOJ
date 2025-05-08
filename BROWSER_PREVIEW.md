# 如何打开 Online Judge 系统的浏览器预览

本文档将指导您如何启动和访问 Online Judge 系统的前端和后端服务，以及如何通过浏览器预览功能测试系统。

## 启动服务

### 步骤 1: 启动 MongoDB 数据库

首先，确保 MongoDB 数据库在 Docker 容器中运行：

```bash
# 检查 MongoDB 容器是否运行
docker ps | grep mongodb

# 如果没有运行，则启动 MongoDB 容器
docker run -d --name mongodb -p 27017:27017 mongo:4.4
```

### 步骤 2: 启动后端服务

启动 FastAPI 后端服务器：

```bash
# 进入后端目录
cd /root/online-judge/backend

# 激活 Python 虚拟环境
source venv/bin/activate

# 启动后端服务
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

成功启动后，您将看到类似以下的输出：

```
INFO:     Will watch for changes in these directories: ['/root/online-judge/backend']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [...]
Connected to MongoDB at localhost:27017
INFO:     Application startup complete.
```

### 步骤 3: 启动前端服务

启动 Vue.js 前端服务器：

```bash
# 进入前端目录
cd /root/online-judge/frontend

# 启动前端服务
npx serve -s dist -l 8080
```

启动成功后，您将看到类似以下的输出，记下服务运行的端口号（可能是 8080 或其他端口）：

```
 ERROR  Cannot copy server address to clipboard...

   ┌───────────────────────────────────────┐
   │                                       │
   │   Serving!                            │
   │                                       │
   │   - Local:    http://localhost:8080   │
   │   - Network:  http://10.7.0.12:8080   │
   │                                       │
   └───────────────────────────────────────┘
```

## 打开浏览器预览

### 方法一：使用命令行工具创建浏览器预览（推荐）

在命令行工具中，您可以使用内置的 `browser_preview` 工具来创建一个浏览器预览：

```
browser_preview --name "Online Judge Frontend" --url http://localhost:8080
```

其中 `8080` 应替换为您的前端服务实际运行的端口号。

### 方法二：直接访问预览 URL

一旦创建了浏览器预览，系统会为您提供一个预览 URL，类似：

```
http://127.0.0.1:41313
```

您可以直接在浏览器中访问这个 URL 来查看和测试您的 Online Judge 系统。

## 常见问题

### 端口占用问题

如果启动服务时出现端口占用错误（例如 "Address already in use"），可以使用以下命令查找和终止占用端口的进程：

```bash
# 查找占用指定端口的进程
lsof -i :8000    # 对于后端端口
lsof -i :8080    # 对于前端端口

# 终止占用端口的进程（替换 PID 为实际进程 ID）
kill -9 PID
```

### 登录问题

如果遇到登录问题，请确保：

1. 后端服务正常运行并连接到 MongoDB
2. 前端服务正常运行
3. 使用正确的账号密码（如 admin/admin123）

如果是新系统，需要先注册账号。如果需要管理员权限，可以在注册后使用以下命令提升用户角色：

```bash
echo 'use oj_system
db.users.updateOne({username: "您的用户名"}, {$set: {role: "admin"}})
exit' | docker exec -i mongodb mongo
```

## 系统访问

成功启动所有服务后，您可以通过以下方式访问 Online Judge 系统：

1. 普通用户：可以浏览题目、提交代码、查看提交历史
2. 管理员用户：可以创建和管理题目、添加测试用例、配置特殊判题程序

祝您使用愉快！
