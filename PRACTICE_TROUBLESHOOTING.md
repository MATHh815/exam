# 练习功能故障排查指南

## 问题现象
点击"开始练习"后出现错误：
- "网站连接失败，请检查网络连接"
- "开始练习失败"

## 诊断步骤

### 1. 确认后端服务运行状态

**检查后端是否运行：**
```bash
cd exam/backend
python run.py
```

后端应该显示：
```
* Running on http://127.0.0.1:5000
```

### 2. 测试后端API

**方法1：使用浏览器**
在浏览器中打开：`http://localhost:5000/health`

应该看到：
```json
{
  "success": true,
  "message": "考试系统运行正常",
  "version": "1.0.0"
}
```

**方法2：使用测试脚本**
```bash
cd exam/backend
python test_practice_api.py
```

### 3. 使用连接测试工具

在浏览器中打开：`exam/frontend/test-connection.html`

按顺序点击测试按钮：
1. 测试健康检查
2. 测试登录
3. 测试开始练习

如果某个测试失败，记录错误信息。

### 4. 检查前端配置

**检查 `.env.development` 文件：**
```bash
cd exam/frontend
cat .env.development
```

应该包含：
```
VITE_API_BASE_URL=http://127.0.0.1:5000/api
```

**如果修改了配置文件，需要重启前端：**
```bash
# 停止前端服务（Ctrl+C）
# 重新启动
npm run dev
```

### 5. 检查浏览器开发者工具

1. 打开浏览器开发者工具（F12）
2. 切换到 Network（网络）标签
3. 点击"开始练习"
4. 查看是否有请求发出

**可能的情况：**

#### 情况A：没有任何请求
- 前端代码有错误
- 检查Console标签是否有JavaScript错误

#### 情况B：请求失败（红色）
- 点击失败的请求查看详情
- 常见错误：
  - `ERR_CONNECTION_REFUSED`: 后端未运行
  - `CORS error`: CORS配置问题
  - `404 Not Found`: API路径错误
  - `401 Unauthorized`: Token过期或无效

### 6. 常见问题和解决方案

#### 问题1：CORS错误
**错误信息：**
```
Access to XMLHttpRequest at 'http://localhost:5000/api/practice/start' 
from origin 'http://localhost:5173' has been blocked by CORS policy
```

**解决方案：**
1. 检查 `exam/backend/.env` 中的CORS配置：
```
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:3000
```

2. 重启后端服务

#### 问题2：localhost vs 127.0.0.1
有时 `localhost` 和 `127.0.0.1` 会有不同的行为。

**解决方案：**
尝试修改 `exam/frontend/.env.development`：
```
# 从
VITE_API_BASE_URL=http://localhost:5000/api

# 改为
VITE_API_BASE_URL=http://127.0.0.1:5000/api
```

然后重启前端。

#### 问题3：Token过期
**错误信息：**
```json
{
  "error": {
    "code": "TOKEN_EXPIRED",
    "message": "令牌已过期"
  }
}
```

**解决方案：**
1. 退出登录
2. 重新登录
3. 再次尝试开始练习

#### 问题4：数据库中没有题目
**错误信息：**
```
没有找到符合条件的题目
```

**解决方案：**
```bash
cd exam/backend
python -c "from app import create_app, db; from app.models.question import Question; app = create_app(); app.app_context().push(); print(f'题目总数: {Question.query.filter_by(is_deleted=False).count()}')"
```

如果题目数为0，需要导入题目数据。

#### 问题5：端口被占用
**错误信息：**
```
Address already in use
```

**解决方案：**
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <进程ID> /F

# 或者修改端口
# 在 exam/backend/run.py 中修改：
app.run(host='127.0.0.1', port=5001, debug=True, use_reloader=False)

# 同时修改前端配置：
VITE_API_BASE_URL=http://127.0.0.1:5001/api
```

### 7. 完整的重启流程

如果以上都不行，尝试完全重启：

```bash
# 1. 停止所有服务（Ctrl+C）

# 2. 重启后端
cd exam/backend
python run.py

# 3. 在新终端重启前端
cd exam/frontend
npm run dev

# 4. 清除浏览器缓存
# - 按 Ctrl+Shift+Delete
# - 或者使用无痕模式（Ctrl+Shift+N）

# 5. 重新登录并测试
```

### 8. 获取详细日志

**后端日志：**
```bash
cd exam/backend
cat logs/app.log
```

**前端控制台：**
- 打开开发者工具（F12）
- 查看Console标签
- 截图所有错误信息

## 快速诊断命令

```bash
# 一键诊断脚本
cd exam/backend
python test_practice_api.py
```

这个脚本会测试：
1. 后端健康检查
2. 登录功能
3. 开始练习功能
4. 数据库题目数量

## 需要帮助？

如果以上步骤都无法解决问题，请提供以下信息：

1. 后端运行的完整输出
2. 浏览器开发者工具的Network标签截图
3. 浏览器开发者工具的Console标签截图
4. `test_practice_api.py` 的完整输出
5. 操作系统和浏览器版本
