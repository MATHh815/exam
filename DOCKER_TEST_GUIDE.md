# Docker 测试指南

## 前置要求

1. **安装 Docker Desktop**
   - Windows: https://www.docker.com/products/docker-desktop
   - 确保 Docker Desktop 正在运行

2. **确认 Docker 可用**
   ```bash
   docker --version
   docker-compose --version
   ```

## 快速启动

### 方法1: 使用脚本（推荐）

```bash
cd exam
docker-test.bat
```

脚本会自动：
- 清理旧容器
- 构建镜像
- 启动服务
- 初始化数据库
- 检查服务状态

### 方法2: 手动启动

```bash
cd exam

# 构建并启动
docker-compose up -d --build

# 等待服务启动
timeout /t 30

# 初始化数据库
docker-compose exec backend python init_db.py

# 查看日志
docker-compose logs -f
```

## 访问应用

启动成功后：

- **前端**: http://localhost:5173
- **后端**: http://localhost:5000
- **API**: http://localhost:5000/api
- **健康检查**: http://localhost:5000/health

## 测试认证修复

### 1. 打开浏览器开发者工具

```
按 F12 打开开发者工具
切换到 Console 标签
```

### 2. 清除缓存

```
Application -> Storage -> Clear site data
```

### 3. 访问登录页

```
http://localhost:5173/login
```

### 4. 登录测试

使用默认账户：
- 用户名: `admin`
- 密码: `admin123`

### 5. 观察控制台日志

登录成功后，你应该看到：

```
✅ 登录成功，token和用户信息已保存
✅ 路由守卫检查token: 存在
✅ store中已有用户信息: admin
✅ 路由守卫检查通过，放行
✅ 请求携带token: /api/...
```

### 6. 验证修复效果

- ✅ 登录后不再显示"未授权"错误
- ✅ 成功跳转到Dashboard页面
- ✅ 页面数据正常加载
- ✅ 控制台没有401错误

## 常用命令

### 查看服务状态
```bash
docker-compose ps
```

### 查看日志
```bash
# 所有服务
docker-compose logs -f

# 只看后端
docker-compose logs -f backend

# 只看前端
docker-compose logs -f frontend
```

### 重启服务
```bash
# 重启所有服务
docker-compose restart

# 只重启后端
docker-compose restart backend

# 只重启前端
docker-compose restart frontend
```

### 进入容器
```bash
# 进入后端容器
docker-compose exec backend bash

# 进入前端容器
docker-compose exec frontend sh
```

### 停止服务
```bash
# 停止但保留数据
docker-compose stop

# 停止并删除容器（保留镜像）
docker-compose down

# 停止并删除所有（包括数据卷）
docker-compose down -v
```

### 重新构建
```bash
# 重新构建所有镜像
docker-compose build

# 重新构建并启动
docker-compose up -d --build

# 只重新构建后端
docker-compose build backend

# 只重新构建前端
docker-compose build frontend
```

## 故障排除

### 问题1: Docker Desktop 未运行

**错误**: `error during connect: This error may indicate that the docker daemon is not running`

**解决**: 
1. 启动 Docker Desktop
2. 等待 Docker 完全启动（托盘图标不再转动）
3. 重新运行命令

### 问题2: 端口被占用

**错误**: `Bind for 0.0.0.0:5000 failed: port is already allocated`

**解决**:
```bash
# 查看占用端口的进程
netstat -ano | findstr :5000
netstat -ano | findstr :5173

# 停止占用端口的进程
taskkill /PID <进程ID> /F

# 或修改 docker-compose.yml 中的端口映射
```

### 问题3: 构建失败

**错误**: `ERROR [backend 4/7] RUN pip install...`

**解决**:
```bash
# 清理 Docker 缓存
docker system prune -a

# 重新构建
docker-compose build --no-cache
```

### 问题4: 前端无法访问后端

**错误**: 前端显示网络错误

**解决**:
1. 检查后端是否运行: `curl http://localhost:5000/health`
2. 检查 CORS 配置: `exam/backend/config.py`
3. 查看后端日志: `docker-compose logs backend`

### 问题5: 数据库未初始化

**错误**: `OperationalError: no such table`

**解决**:
```bash
# 手动初始化数据库
docker-compose exec backend python init_db.py

# 或重新启动并初始化
docker-compose down -v
docker-compose up -d
docker-compose exec backend python init_db.py
```

## 性能优化

### 使用卷挂载加速开发

docker-compose.yml 已配置了卷挂载：
- 后端代码修改会自动重载
- 前端代码修改会触发热更新

### 减少构建时间

```bash
# 使用构建缓存
docker-compose build

# 并行构建
docker-compose build --parallel
```

## 清理资源

### 清理未使用的镜像
```bash
docker image prune -a
```

### 清理所有 Docker 资源
```bash
docker system prune -a --volumes
```

## 生产环境部署

如果要部署到生产环境，需要修改：

1. **环境变量** (docker-compose.yml)
   ```yaml
   environment:
     - FLASK_ENV=production
     - SECRET_KEY=<生产环境密钥>
     - JWT_SECRET_KEY=<生产环境JWT密钥>
   ```

2. **CORS 配置**
   ```yaml
   - CORS_ORIGINS=https://yourdomain.com
   ```

3. **数据库**
   ```yaml
   - DATABASE_URL=postgresql://user:pass@db:5432/exam
   ```

4. **前端构建**
   ```dockerfile
   # 使用多阶段构建
   FROM node:18-alpine as builder
   WORKDIR /app
   COPY package*.json ./
   RUN npm ci
   COPY . .
   RUN npm run build

   FROM nginx:alpine
   COPY --from=builder /app/dist /usr/share/nginx/html
   ```

## 测试检查清单

- [ ] Docker Desktop 已启动
- [ ] 服务成功构建
- [ ] 服务成功启动
- [ ] 数据库已初始化
- [ ] 后端健康检查通过
- [ ] 前端页面可访问
- [ ] 登录功能正常
- [ ] 控制台无401错误
- [ ] Dashboard数据加载正常
- [ ] 刷新页面保持登录状态

## 下一步

测试通过后：
1. 提交代码到Git仓库
2. 在生产环境部署
3. 配置CI/CD自动化部署

## 需要帮助？

如果遇到问题：
1. 查看日志: `docker-compose logs -f`
2. 检查服务状态: `docker-compose ps`
3. 查看本文档的故障排除部分
4. 参考 AUTH_FIX_GUIDE.md
