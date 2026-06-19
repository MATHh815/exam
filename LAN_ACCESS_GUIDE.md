# 局域网访问配置指南

## 配置步骤

### 1. 获取服务器的局域网 IP 地址

在运行项目的电脑上打开命令行，运行：

```cmd
ipconfig
```

找到 **IPv4 地址**，例如：`192.168.1.100`

### 2. 修改后端 CORS 配置

编辑 `exam/backend/.env` 文件，将 `YOUR_IP` 替换为你的实际 IP：

```env
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000,http://192.168.1.100:5173
```

**注意**：如果有多台电脑需要访问，添加所有 IP 地址，用逗号分隔。

### 2.5. 修改前端 API 配置（重要！）

编辑 `exam/frontend/.env.development.local` 文件，将 `YOUR_IP` 替换为你的实际 IP：

```env
VITE_API_BASE_URL=http://192.168.1.100:5000/api
```

**这一步很关键**：前端需要知道后端的实际 IP 地址才能在局域网内访问。

### 3. 启动项目

使用 `start_all.bat` 启动项目：

```cmd
cd exam
start_all.bat
```

或者分别启动：

**后端**（在 exam/backend 目录）：
```cmd
cd exam/backend
python run.py
```

**前端**（在 exam/frontend 目录）：
```cmd
cd exam/frontend
npm run dev
```

### 4. 局域网内其他设备访问

在同一局域网内的其他设备上，打开浏览器访问：

```
http://192.168.1.100:5173
```

（将 `192.168.1.100` 替换为你的实际 IP 地址）

## 常见问题

### Q1: 无法访问？

**检查防火墙设置**：

1. 打开 Windows 防火墙设置
2. 允许端口 5000（后端）和 5173（前端）通过防火墙
3. 或者临时关闭防火墙测试

**快速添加防火墙规则**（以管理员身份运行 CMD）：

```cmd
netsh advfirewall firewall add rule name="Exam Backend" dir=in action=allow protocol=TCP localport=5000
netsh advfirewall firewall add rule name="Exam Frontend" dir=in action=allow protocol=TCP localport=5173
```

### Q2: API 请求失败？

**检查两个配置**：

1. 后端的 `.env` 文件中 `CORS_ORIGINS` 包含了访问设备的 IP 地址
2. **前端的 `.env.development.local` 文件中 `VITE_API_BASE_URL` 指向了正确的后端 IP**

打开浏览器开发者工具（F12），查看 Network 标签，看看请求是发送到哪个地址的。

### Q2.5: 如何验证前端配置是否生效？

在前端项目启动后，打开浏览器控制台（F12），输入：
```javascript
console.log(import.meta.env.VITE_API_BASE_URL)
```
应该显示你配置的后端 IP 地址，例如：`http://192.168.1.100:5000/api`

### Q3: 如何查看当前监听的端口？

```cmd
netstat -ano | findstr "5000"
netstat -ano | findstr "5173"
```

### Q4: 手机访问？

确保手机和电脑在同一 WiFi 网络下，然后在手机浏览器访问：
```
http://你的电脑IP:5173
```

### 配置文件说明

### 已修改的文件：

1. **exam/backend/.env** - 添加了 CORS 允许的源地址
2. **exam/backend/run.py** - 修改为监听 `0.0.0.0`（所有网络接口）
3. **exam/frontend/vite.config.js** - 添加 `host: '0.0.0.0'` 允许局域网访问
4. **exam/frontend/.env.development.local** - 配置前端直接访问后端 IP（重要！）

### 配置优先级说明

前端环境变量加载顺序（后面的会覆盖前面的）：
- `.env` - 所有环境通用
- `.env.development` - 开发环境
- `.env.development.local` - 开发环境本地覆盖（不会提交到 git）

所以 `.env.development.local` 中的配置会覆盖其他配置。

## 安全提示

- 仅在可信任的局域网环境中使用此配置
- 生产环境部署时需要更严格的安全配置
- 不要将开发环境直接暴露到公网

## 恢复本地访问

如果只想在本机访问，可以：

1. 删除或重命名 `exam/frontend/.env.development.local` 文件

2. 或者修改 `exam/frontend/.env.development.local`：
   ```env
   VITE_API_BASE_URL=/api
   ```

3. 修改 `exam/backend/run.py`（可选）：
   ```python
   app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)
   ```

4. 修改 `exam/frontend/vite.config.js`（可选）：
   ```javascript
   server: {
     port: 5173,
     // 移除 host: '0.0.0.0'
   }
   ```

5. 修改 `exam/backend/.env`（可选）：
   ```env
   CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
   ```

**最简单的方法**：只需删除 `.env.development.local` 文件即可恢复本地访问。
