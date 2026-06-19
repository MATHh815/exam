# API 连接问题解决指南

## 问题描述

前端显示"基于了未知的路径格式"错误，这通常表示：
1. **后端服务器未运行** ← 最常见原因
2. 用户积分记录未初始化
3. API 路由未正确注册
4. 网络连接问题

---

## 🚀 快速修复

### 最简单的方法：一键启动

在 `exam` 目录下运行：
```bash
start_all.bat
```

这会自动完成所有步骤！

---

## 快速诊断

### 步骤 1: 检查后端服务器

在浏览器中访问：
```
http://localhost:5000/health
```

**预期结果**:
```json
{
  "success": true,
  "message": "考试系统运行正常",
  "version": "1.0.0"
}
```

**如果无法访问**:
- 后端服务器未运行
- 需要启动后端服务器

### 步骤 2: 启动后端服务器

```bash
cd exam/backend
python run.py
```

**预期输出**:
```
* Running on http://127.0.0.1:5000
* Running on http://localhost:5000
```

### 步骤 3: 检查 API 端点

访问：
```
http://localhost:5000/api
```

**预期结果**:
```json
{
  "success": true,
  "message": "API 服务运行正常",
  "endpoints": {
    "auth": "/api/auth",
    "questions": "/api/questions",
    ...
  }
}
```

### 步骤 4: 检查游戏化 API

访问以下端点（需要登录）：
- http://localhost:5000/api/points
- http://localhost:5000/api/achievements
- http://localhost:5000/api/daily-tasks

---

## 常见问题

### Q1: 后端服务器无法启动

**可能原因**:
1. 端口 5000 被占用
2. Python 依赖未安装
3. 数据库未初始化

**解决方案**:

#### 检查端口占用
```bash
# Windows
netstat -ano | findstr :5000

# 如果端口被占用，杀死进程
taskkill /PID <进程ID> /F
```

#### 安装依赖
```bash
cd exam/backend
pip install -r requirements.txt
```

#### 初始化数据库
```bash
cd exam/backend
python migrate_phase1.py
python init_achievements.py
```

### Q2: API 返回 404

**可能原因**:
1. 路由未注册
2. URL 路径错误

**解决方案**:

检查 `exam/backend/app/__init__.py` 中的蓝图注册：
```python
app.register_blueprint(points_bp)
app.register_blueprint(achievements_bp)
app.register_blueprint(daily_tasks_bp)
```

### Q3: API 返回 401 (未授权)

**这是正常的！**

游戏化 API 需要登录才能访问。

**解决方案**:
1. 先登录系统
2. 然后访问游戏化功能

### Q4: CORS 错误

**错误信息**:
```
Access to XMLHttpRequest at 'http://localhost:5000/api/...' 
from origin 'http://localhost:5173' has been blocked by CORS policy
```

**解决方案**:

检查 `exam/backend/.env` 文件：
```
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

或者使用通配符（仅开发环境）：
```
CORS_ORIGINS=*
```

---

## 完整启动流程

### 1. 启动后端服务器

```bash
# 进入后端目录
cd exam/backend

# 启动服务器
python run.py
```

**等待看到**:
```
* Running on http://127.0.0.1:5000
```

### 2. 启动前端开发服务器

```bash
# 新开一个终端
cd exam/frontend

# 安装依赖（如果还没安装）
npm install

# 启动开发服务器
npm run dev
```

**等待看到**:
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
```

### 3. 访问系统

在浏览器中打开：
```
http://localhost:5173
```

### 4. 登录系统

使用你的账号登录

### 5. 访问游戏化功能

- 点击左侧菜单"游戏化"
- 或访问 `/achievements`
- 或访问 `/daily-tasks`

---

## 使用诊断工具

运行诊断脚本：
```bash
cd exam/frontend
diagnose_api.bat
```

这会自动检查：
- 后端服务器状态
- API 端点可用性
- 游戏化 API 注册情况

---

## 验证清单

启动系统后，请验证：

- [ ] 后端服务器运行在 http://localhost:5000
- [ ] 前端服务器运行在 http://localhost:5173
- [ ] 可以访问 http://localhost:5000/health
- [ ] 可以访问 http://localhost:5000/api
- [ ] 可以登录系统
- [ ] 可以访问个人中心
- [ ] 可以看到"游戏化"菜单
- [ ] 点击"游戏化"不报错

---

## 调试技巧

### 1. 查看浏览器控制台

按 `F12` 打开开发者工具，查看：
- Console 标签：JavaScript 错误
- Network 标签：API 请求状态

### 2. 查看后端日志

后端日志文件位置：
```
exam/backend/logs/app.log
exam/backend/logs/app_error.log
```

### 3. 测试 API

使用 curl 或 Postman 测试 API：
```bash
# 测试健康检查
curl http://localhost:5000/health

# 测试 API 信息
curl http://localhost:5000/api

# 测试积分 API（需要 token）
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:5000/api/points
```

---

## 获取帮助

如果问题仍未解决：

1. 查看 `TROUBLESHOOTING.md`
2. 查看 `QUICK_FIX.md`
3. 检查后端日志文件
4. 检查浏览器控制台错误

---

**创建时间**: 2024-12-26  
**维护者**: Kiro AI Assistant

