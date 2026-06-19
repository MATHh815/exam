# 🐳 Docker 快速测试指南

## 一键启动测试

```bash
cd exam
docker-test.bat
```

就这么简单！脚本会自动完成所有设置。

## 测试步骤

### 1️⃣ 启动服务（已完成）

脚本已经帮你：
- ✅ 构建Docker镜像
- ✅ 启动前后端服务
- ✅ 初始化数据库

### 2️⃣ 打开浏览器

访问: http://localhost:5173

### 3️⃣ 打开开发者工具

按 `F12` 打开控制台

### 4️⃣ 登录测试

使用默认账户：
- 用户名: `admin`
- 密码: `admin123`

### 5️⃣ 观察控制台

✅ **修复成功的标志**:
```
登录成功，token和用户信息已保存
路由守卫检查token: 存在
store中已有用户信息: admin
路由守卫检查通过，放行
```

❌ **修复前的问题**:
```
未授权 (401)
未授权 (401)
未授权 (401)
```

## 查看日志

```bash
# 实时查看所有日志
docker-compose logs -f

# 只看后端日志
docker-compose logs -f backend

# 只看前端日志
docker-compose logs -f frontend
```

## 停止服务

```bash
docker-compose down
```

## 重新测试

```bash
# 清理并重新开始
docker-compose down -v
docker-test.bat
```

## 需要帮助？

查看详细文档: `DOCKER_TEST_GUIDE.md`
