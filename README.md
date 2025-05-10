# 在线评判系统 (Online Judge System)

一个现代化的在线评判系统，基于FastAPI、Vue.js和MongoDB构建，运行在Debian 12上。系统提供代码在线编辑、提交、自动评判等功能，支持代码隔离执行环境，保证评判的安全和公平。

## 功能特点

- 题库管理系统，支持Markdown格式题目描述
- 代码提交和自动评判系统
- 基于Docker的隔离评判环境
- 管理员题目管理和系统配置工具
- 目前支持C++语言（计划添加更多语言支持）
- 用户认证和授权系统
- 提交记录和评判结果展示

## 技术栈

### 后端
- **FastAPI** (Python): 高性能的异步Web框架
- **MongoDB**: 文档型数据库，用于存储题目、用户和提交记录
- **Docker**: 提供代码隔离执行环境
- **JWT**: 用于用户认证和授权
- **uvicorn**: ASGI服务器

### 前端
- **Vue.js**: 前端框架
- **Element Plus**: UI组件库
- **Markdown-it**: Markdown渲染引擎
- **Axios**: HTTP客户端
- **Vuex**: 状态管理

## 系统架构

系统由以下主要组件构成：

- **前端应用** (`/frontend`): Vue.js应用，提供用户界面
- **后端服务** (`/backend`): FastAPI服务，处理API请求
- **数据库**: MongoDB，存储系统数据
- **评判环境** (`/backend/app/judge`): Docker容器，提供代码执行环境

### 系统流程

1. 用户通过前端界面浏览题目
2. 用户提交代码到后端
3. 后端将代码保存到数据库并加入评判队列
4. 评判模块在Docker容器中编译和执行代码
5. 将评判结果保存到数据库
6. 前端查询并显示评判结果

## 安装要求

### 系统要求
- Debian 12或其他Linux发行版
- Docker 20.10+
- Python 3.9+
- Node.js 14+
- MongoDB 4.4+
- Nginx 1.18+（用于生产环境）

## 安装和启动指南

### 1. 克隆仓库

```bash
git clone https://github.com/Nqn7mi-mylove/NJOJ.git
cd NJOJ

### 2. 后端设置

#### 安装依赖

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 配置环境变量
创建`.env`文件，包含以下配置：

```
MONGODB_URL=mongodb://localhost:27017
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOW_SIGNUP=true
```

#### 启动MongoDB数据库

```bash
docker run -d -p 27017:27017 --name mongodb mongo:4.4
```

#### 启动后端服务

```bash
cd /root/online-judge/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

或使用提供的脚本：

```bash
bash /root/start-backend.sh
```

### 3. 前端设置

#### 安装依赖

```bash
cd frontend
npm install
```

#### 开发模式启动

```bash
npm run serve
```

#### 构建生产版本

```bash
npm run build
```

#### 部署前端

使用提供的脚本部署到Nginx：

```bash
bash /root/deploy-frontend.sh
```

## 系统配置

### Nginx配置

对于生产环境，前端应用通过Nginx提供服务，配置文件位于`/etc/nginx/sites-available/njoj.site.conf`。

### Docker配置

系统使用Docker进行代码评判，确保Docker服务已启动并配置正确。

## 关键目录结构

```
online-judge/
├── backend/             # 后端FastAPI应用
│   ├── app/            # 主应用代码
│   │   ├── api/        # API端点
│   │   ├── core/       # 核心功能（认证等）
│   │   ├── db/         # 数据库连接
│   │   ├── judge/      # 评判模块
│   │   ├── models/     # 数据模型
│   │   └── schemas/    # Pydantic模式
│   └── venv/           # Python虚拟环境
│
├── frontend/           # 前端Vue应用
│   ├── public/         # 静态资源
│   ├── src/            # 源代码
│   │   ├── assets/     # 资源文件
│   │   ├── components/ # Vue组件
│   │   ├── store/      # Vuex存储
│   │   ├── views/      # 页面视图
│   │   └── router/     # 路由定义
│   └── node_modules/   # Node.js依赖
```

## API文档

启动后端后，可以通过以下URL访问自动生成的API文档：

- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc

## 功能实现细节

### 用户认证

系统使用JWT（JSON Web Token）进行用户认证。用户登录后，服务器颁发有时间限制的访问令牌，前端将此令牌存储在localStorage中并在每次API请求中通过Authorization头发送。

### 代码评判

代码评判使用Docker进行隔离，过程如下：

1. 用户提交代码后，系统在数据库中创建提交记录，状态为"pending"
2. 评判模块读取提交记录，状态更新为"judging"
3. 在Docker容器中编译代码，如果编译失败，状态更新为"compilation_error"
4. 针对题目的每个测试用例，在容器中运行代码，监控执行时间和内存使用
5. 根据输出结果与预期结果比较，确定结果（通过、答案错误、超时等）
6. 所有测试用例执行完毕后，更新提交记录的最终状态

### 安全考虑

- 代码在Docker容器中执行，资源受限，防止恶意代码破坏系统
- 用户认证确保只有授权用户可以提交代码和访问其提交记录
- 管理员功能受到访问控制保护

## 维护和故障排除

### 日志

- 后端日志：启动uvicorn时可以指定`--log-level`参数
- Docker日志：使用`docker logs mongodb`查看MongoDB日志

### 常见问题

1. **后端无法启动**：检查MongoDB是否正在运行，环境变量是否正确设置
2. **评判失败**：检查Docker服务状态，确保有足够权限执行容器
3. **前端无法连接后端**：检查API地址配置和CORS设置

## 扩展和定制

### 添加新的编程语言支持

要添加新的编程语言支持，需要：

1. 在评判模块中添加相应的编译器和执行环境
2. 在前端编辑器中添加语言支持
3. 更新语言选择下拉菜单

### 自定义题目标签

可以在管理界面中定义和管理题目标签，用于对题目进行分类。

## 一些闲话

本项目为本人毕业设计，由Windsurf辅助开发。
如有问题或建议，请通过Issues提交反馈。
