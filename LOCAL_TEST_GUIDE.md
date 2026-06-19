# 本地测试指南（不使用Docker）

## 快速测试步骤

### 1. 启动后端

```bash
cd exam/backend

# 激活虚拟环境
venv\Scripts\activate

# 确保数据库已初始化
python init_db.py

# 启动后端
python run.py
```

后端会在 http://localhost:5000 运行

### 2. 启动前端（新开一个终端）

```bash
cd exam/frontend

# 安装依赖（如果还没安装）
npm install

# 启动前端
npm run dev
```

前端会在 http://localhost:5173 运行

### 3. 测试登录

1. 打开浏览器访问 http://localhost:5173
2. 按 F12 打开开发者工具
3. 切换到 Console 标签
4. 登录（admin / admin123）
5. 观察控制台输出

### 预期结果

✅ **修复成功**:
```
登录成功，token和用户信息已保存
路由守卫检查token: 存在
store中已有用户信息: admin
路由守卫检查通过，放行
请求携带token: /api/...
```

❌ **修复前的问题**:
```
未授权 (401)
未授权 (401)
未授权 (401)
```

## 一键启动脚本

我已经为你创建了启动脚本，更方便：

### Windows

```bash
# 启动后端
cd exam/backend
start_backend.bat

# 启动前端（新终端）
cd exam/frontend
npm run dev
```

## 故障排除

### 后端启动失败

**问题**: 端口5000被占用

**解决**:
```bash
# 查找占用端口的进程
netstat -ano | findstr :5000

# 结束进程
taskkill /PID <进程ID> /F
```

### 前端启动失败

**问题**: 端口5173被占用

**解决**:
```bash
# 查找占用端口的进程
netstat -ano | findstr :5173

# 结束进程
taskkill /PID <进程ID> /F
```

### 数据库错误

**问题**: `OperationalError: no such table`

**解决**:
```bash
cd exam/backend
python init_db.py
```

## 提交代码

测试通过后，提交代码：

```bash
cd exam
git add .
git commit -m "fix: 修复登录后未授权重定向问题"
git push
```

## 下一步

回到你自己的电脑后：
1. `git pull` 拉取最新代码
2. 按照本指南测试
3. 确认问题已解决
