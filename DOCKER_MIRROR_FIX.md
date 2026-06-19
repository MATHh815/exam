# Docker 镜像源配置指南

## 问题

Docker无法拉取镜像，错误：
```
failed to resolve source metadata for docker.io/library/python:3.9-slim
lookup docker.mirrors.ustc.edu.cn: no such host
```

## 解决方案

### 方法1: 使用Docker Desktop配置（推荐）

1. **打开Docker Desktop**

2. **进入设置**
   - 点击右上角的齿轮图标 ⚙️
   - 或者右键托盘图标 → Settings

3. **配置镜像源**
   - 左侧菜单选择 `Docker Engine`
   - 在JSON配置中添加镜像源：

```json
{
  "builder": {
    "gc": {
      "defaultKeepStorage": "20GB",
      "enabled": true
    }
  },
  "experimental": false,
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://dockerproxy.com",
    "https://docker.mirrors.sjtug.sjtu.edu.cn",
    "https://docker.nju.edu.cn"
  ]
}
```

4. **应用并重启**
   - 点击 `Apply & Restart`
   - 等待Docker重启完成

### 方法2: 直接使用国内镜像

修改 Dockerfile，使用国内镜像：

#### backend/Dockerfile
```dockerfile
# 使用阿里云镜像
FROM registry.cn-hangzhou.aliyuncs.com/library/python:3.9-slim

# 或使用网易镜像
# FROM hub-mirror.c.163.com/library/python:3.9-slim

# 其余内容不变...
```

#### frontend/Dockerfile
```dockerfile
# 使用阿里云镜像
FROM registry.cn-hangzhou.aliyuncs.com/library/node:18-alpine

# 或使用网易镜像
# FROM hub-mirror.c.163.com/library/node:18-alpine

# 其余内容不变...
```

### 方法3: 使用代理（如果有VPN）

在 docker-compose.yml 中添加代理配置：

```yaml
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
      args:
        HTTP_PROXY: http://your-proxy:port
        HTTPS_PROXY: http://your-proxy:port
    # ... 其他配置
```

## 推荐的镜像源（2024年可用）

1. **DaoCloud**: https://docker.m.daocloud.io
2. **上海交大**: https://docker.mirrors.sjtug.sjtu.edu.cn
3. **南京大学**: https://docker.nju.edu.cn
4. **DockerProxy**: https://dockerproxy.com

## 验证配置

配置完成后，测试是否可以拉取镜像：

```bash
# 测试拉取Python镜像
docker pull python:3.9-slim

# 测试拉取Node镜像
docker pull node:18-alpine
```

如果成功，会看到：
```
3.9-slim: Pulling from library/python
...
Status: Downloaded newer image for python:3.9-slim
```

## 重新构建

配置好镜像源后，重新构建：

```bash
cd exam

# 清理旧的构建缓存
docker-compose down -v
docker system prune -a

# 重新构建
docker-compose up --build
```

## 如果还是不行

尝试完全不使用镜像源，直接从Docker Hub拉取（需要网络畅通）：

1. 删除 Docker Engine 配置中的 `registry-mirrors`
2. 重启 Docker Desktop
3. 重新构建

或者使用我准备的备用方案（见下一节）。
