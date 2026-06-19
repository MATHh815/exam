# 快速开始指南

本指南将帮助你快速搭建和运行考公考研考编系统。

## 前置要求

- Python 3.9+
- Node.js 16+
- npm 或 yarn

## 第一步：克隆项目

```bash
# 如果你还没有克隆项目
git clone <repository-url>
cd exam
```

## 第二步：后端设置

### 1. 创建虚拟环境

```bash
cd backend
python -m venv venv
```

### 2. 激活虚拟环境

Windows:
```bash
venv\Scripts\activate
```

macOS/Linux:
```bash
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
# 复制示例配置文件
copy .env.example .env  # Windows
cp .env.example .env    # macOS/Linux

# 编辑 .env 文件，至少修改以下配置：
# SECRET_KEY=your-secret-key
# JWT_SECRET_KEY=your-jwt-secret-key
```

### 5. 初始化数据库

```bash
# 方式一：使用 Flask-Migrate
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# 方式二：使用自定义命令
python run.py init_db
```

### 6. 运行后端服务

```bash
# 开发模式
flask run

# 或者
python run.py
```

后端服务将在 http://localhost:5000 运行

## 第三步：前端设置

### 1. 安装依赖

```bash
cd ../frontend
npm install
```

### 2. 运行开发服务器

```bash
npm run dev
```

前端应用将在 http://localhost:5173 运行

## 第四步：验证安装

1. 打开浏览器访问 http://localhost:5173
2. 你应该能看到应用的主页面
3. 后端 API 可以通过 http://localhost:5000/api 访问

## 常见问题

### 后端启动失败

**问题：** `ModuleNotFoundError: No module named 'flask'`

**解决：** 确保你已经激活了虚拟环境并安装了依赖
```bash
source venv/bin/activate  # 或 venv\Scripts\activate (Windows)
pip install -r requirements.txt
```

**问题：** `ImportError: cannot import name 'EVENT_TYPE_CLOSED' from 'watchdog.events'`

**解决：** 这是 watchdog 版本冲突问题，有两种解决方案：

方案一：使用 --no-reload 标志运行
```bash
python run.py --no-reload
```

方案二：升级 watchdog 包
```bash
pip install --upgrade watchdog
```

### 数据库错误

**问题：** `OperationalError: no such table`

**解决：** 运行数据库迁移
```bash
flask db upgrade
```

### 前端启动失败

**问题：** `Error: Cannot find module`

**解决：** 重新安装依赖
```bash
rm -rf node_modules package-lock.json
npm install
```

### CORS 错误

**问题：** 前端无法访问后端 API

**解决：** 检查后端 .env 文件中的 CORS_ORIGINS 配置
```
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

## 下一步

- 查看 [README.md](README.md) 了解项目详情
- 查看 [.kiro/specs/exam-system/](../.kiro/specs/exam-system/) 了解开发规范
- 开始实现功能模块

## 开发工作流

1. 查看任务列表：`.kiro/specs/exam-system/tasks.md`
2. 选择一个任务开始开发
3. 编写代码和测试
4. 运行测试确保通过
5. 提交代码

## 测试

运行后端测试：
```bash
cd backend
pytest
```

运行前端测试：
```bash
cd frontend
npm run test
```

## 需要帮助？

如果遇到问题，请：
1. 查看错误日志
2. 检查配置文件
3. 查看项目文档
4. 提交 Issue


## 快速启动脚本

为了更方便地启动项目，我们提供了快速启动脚本：

### Windows 用户

```bash
cd exam/backend
start.bat
```

### macOS/Linux 用户

```bash
cd exam/backend
chmod +x start.sh
./start.sh
```

这些脚本会自动：
1. 激活虚拟环境
2. 检查并初始化数据库（如果需要）
3. 启动开发服务器（已禁用 reloader 避免 watchdog 问题）

## 手动启动（如果脚本不工作）

如果快速启动脚本不工作，可以手动执行以下步骤：

```bash
# 1. 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 2. 初始化数据库（首次运行）
python init_db.py

# 3. 启动服务器
python run.py
```
