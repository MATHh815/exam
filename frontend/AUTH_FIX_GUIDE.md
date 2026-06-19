# 认证问题修复指南

## 问题描述
登录成功后显示"未授权"错误，然后重定向回登录页面。

## 根本原因
1. **时序问题**: 登录成功后立即跳转，但token还没完全保存到localStorage
2. **并发请求**: 页面组件在加载时立即发起API请求，此时token可能还未就绪
3. **路由守卫**: 路由守卫在获取用户信息时可能触发额外的API请求

## 已实施的修复

### 1. Login.vue - 添加延迟确保token保存
```javascript
// 登录成功后等待100ms确保token已保存
await new Promise(resolve => setTimeout(resolve, 100))
```

### 2. user.js Store - 同步保存所有数据
```javascript
// 批量同步写入localStorage，确保原子性
accessToken.value = access_token
refreshToken.value = refresh_token
user.value = userData

localStorage.setItem('access_token', access_token)
localStorage.setItem('refresh_token', refresh_token)
localStorage.setItem('user', JSON.stringify(userData))
```

### 3. request.js - 增强日志和错误处理
```javascript
// 添加详细的调试日志
console.log('请求携带token:', config.url)
console.error('错误详情:', { url, status, message })
```

### 4. router/index.js - 优化路由守卫
```javascript
// 不等待fetchUserInfo，让页面先加载
// 在后台异步获取用户信息
userStore.fetchUserInfo().catch(error => {
  console.error('后台获取用户信息失败:', error)
})
```

## 测试步骤

### 1. 清除浏览器缓存
```
1. 打开浏览器开发者工具 (F12)
2. 进入 Application/应用 标签
3. 清除 Local Storage
4. 清除 Session Storage
5. 刷新页面
```

### 2. 测试登录流程
```
1. 打开浏览器控制台 (F12 -> Console)
2. 访问登录页面
3. 输入用户名和密码
4. 点击登录
5. 观察控制台输出
```

### 3. 预期的控制台输出
```
登录成功，token和用户信息已保存
路由守卫检查token: 存在
store中已有用户信息: [用户名]
路由守卫检查通过，放行
请求携带token: /api/...
```

### 4. 如果仍然出现问题
检查以下内容：

#### A. 检查localStorage
```javascript
// 在控制台执行
console.log('Token:', localStorage.getItem('access_token'))
console.log('User:', localStorage.getItem('user'))
```

#### B. 检查后端CORS配置
```python
# exam/backend/config.py
# 确保开发环境允许所有来源
class DevelopmentConfig(Config):
    CORS_ORIGINS = ['*']
```

#### C. 检查API基础URL
```javascript
// exam/frontend/.env 或 .env.development
VITE_API_BASE_URL=http://localhost:5000/api
```

#### D. 检查后端是否运行
```bash
# 访问健康检查端点
curl http://localhost:5000/health
```

## 额外的调试技巧

### 1. 启用详细日志
在 `exam/frontend/src/main.js` 中添加：
```javascript
// 开发环境启用详细日志
if (import.meta.env.DEV) {
  console.log('开发模式：详细日志已启用')
}
```

### 2. 监控localStorage变化
```javascript
// 在控制台执行
window.addEventListener('storage', (e) => {
  console.log('Storage changed:', e.key, e.newValue)
})
```

### 3. 检查网络请求
```
1. 打开开发者工具 Network 标签
2. 登录
3. 查看所有请求的状态码
4. 检查请求头中是否包含 Authorization
```

## 常见错误和解决方案

### 错误1: "未授权" (401)
**原因**: Token未正确保存或传递
**解决**: 
- 检查localStorage中是否有access_token
- 检查请求头中是否包含Authorization
- 查看控制台日志确认token保存成功

### 错误2: CORS错误
**原因**: 后端CORS配置不正确
**解决**:
```python
# config.py
class DevelopmentConfig(Config):
    CORS_ORIGINS = ['*']
```

### 错误3: 无限重定向
**原因**: 路由守卫逻辑错误
**解决**: 已在router/index.js中修复，确保在登录页不触发重定向

### 错误4: Token过期
**原因**: JWT token有效期太短
**解决**:
```python
# config.py
JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=3600)  # 1小时
```

## 验证修复成功的标志

✅ 登录后不再显示"未授权"错误
✅ 成功跳转到Dashboard页面
✅ 页面数据正常加载
✅ 刷新页面后仍保持登录状态
✅ 控制台没有401错误

## 如果问题仍然存在

请提供以下信息：
1. 浏览器控制台的完整日志
2. Network标签中失败请求的详细信息
3. localStorage中的内容
4. 后端日志（exam/backend/logs/app.log）

## 联系支持

如果以上步骤都无法解决问题，请：
1. 截图控制台错误
2. 导出Network请求日志
3. 提供复现步骤
