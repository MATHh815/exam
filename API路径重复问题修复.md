# API 路径重复问题修复

## 问题描述

后端日志显示 404 错误，API 路径重复了 `/api/` 前缀：

```
GET /api/api/points HTTP/1.1" 404
GET /api/api/achievements/user HTTP/1.1" 404
GET /api/api/achievements/stats HTTP/1.1" 404
```

正确的路径应该是：
```
GET /api/points HTTP/1.1" 200
GET /api/achievements/user HTTP/1.1" 200
GET /api/achievements/stats HTTP/1.1" 200
```

---

## 根本原因

**双重 `/api/` 前缀问题**：

1. **request.js 的 baseURL**: `/api`
2. **API 模块的 URL**: `/api/points`
3. **最终请求**: `/api` + `/api/points` = `/api/api/points` ❌

---

## 解决方案

API 模块中的 URL 不应该包含 `/api/` 前缀，因为 `baseURL` 已经设置了。

### 修复规则

```javascript
// ❌ 错误 - URL 包含 /api/
export function getUserPoints() {
  return request({
    url: '/api/points',  // 错误！
    method: 'get'
  })
}

// ✅ 正确 - URL 不包含 /api/
export function getUserPoints() {
  return request({
    url: '/points',  // 正确！
    method: 'get'
  })
}
```

---

## 修复的文件

### 1. points.js

**修改前**:
```javascript
url: '/api/points'
url: '/api/points/history'
url: '/api/points/leaderboard'
```

**修改后**:
```javascript
url: '/points'
url: '/points/history'
url: '/points/leaderboard'
```

### 2. achievements.js

**修改前**:
```javascript
url: '/api/achievements'
url: `/api/achievements/${id}`
url: '/api/achievements/user'
url: '/api/achievements/stats'
url: '/api/achievements/check'
```

**修改后**:
```javascript
url: '/achievements'
url: `/achievements/${id}`
url: '/achievements/user'
url: '/achievements/stats'
url: '/achievements/check'
```

### 3. dailyTasks.js

**修改前**:
```javascript
url: '/api/daily-tasks'
url: `/api/daily-tasks/${id}/complete`
url: '/api/daily-tasks/stats'
url: '/api/daily-tasks/templates'
```

**修改后**:
```javascript
url: '/daily-tasks'
url: `/daily-tasks/${id}/complete`
url: '/daily-tasks/stats'
url: '/daily-tasks/templates'
```

---

## 工作原理

### Axios 请求流程

```
API 调用: getUserPoints()
  ↓
request({ url: '/points' })
  ↓
baseURL + url = '/api' + '/points'
  ↓
最终请求: GET /api/points
  ↓
Vite 代理: /api → http://localhost:5000
  ↓
后端接收: GET /api/points
```

### Vite 代理配置

`vite.config.js`:
```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:5000',
      changeOrigin: true
    }
  }
}
```

这意味着：
- 前端请求: `http://localhost:5173/api/points`
- 代理转发: `http://localhost:5000/api/points`

---

## 验证修复

### 1. 刷新浏览器
按 `F5` 刷新页面

### 2. 检查网络请求

打开浏览器开发者工具（F12）→ Network 标签

**应该看到**:
- ✅ `GET /api/points` - 200
- ✅ `GET /api/achievements/user` - 200
- ✅ `GET /api/achievements/stats` - 200
- ✅ `GET /api/daily-tasks` - 200

**不应该看到**:
- ❌ `GET /api/api/points` - 404
- ❌ `GET /api/api/achievements/user` - 404

### 3. 检查后端日志

后端日志应该显示：
```
GET /api/points HTTP/1.1" 200
GET /api/achievements/user HTTP/1.1" 200
GET /api/achievements/stats HTTP/1.1" 200
```

---

## 其他 API 模块检查

确保其他 API 模块也遵循相同规则：

### ✅ 正确的 API 模块

这些模块已经正确（不包含 `/api/` 前缀）：

- `auth.js` - `/auth/login`, `/auth/register`
- `questions.js` - `/questions`, `/questions/random`
- `practice.js` - `/practice/start`, `/practice/submit`
- `exams.js` - `/exams`, `/exams/papers`
- `statistics.js` - `/statistics/overview`
- `studyPlans.js` - `/study-plans`
- `notes.js` - `/notes`
- `bookmarks.js` - `/bookmarks`
- `reminders.js` - `/reminders`

### ❌ 需要检查的模块

如果发现其他模块有类似问题，按照相同方式修复。

---

## 最佳实践

### API 模块 URL 规范

```javascript
// ✅ 推荐：相对路径，不包含 /api/
export function getResource() {
  return request({
    url: '/resource',
    method: 'get'
  })
}

// ❌ 不推荐：包含 /api/ 前缀
export function getResource() {
  return request({
    url: '/api/resource',  // 会导致路径重复
    method: 'get'
  })
}

// ❌ 不推荐：绝对路径
export function getResource() {
  return request({
    url: 'http://localhost:5000/api/resource',  // 硬编码，不灵活
    method: 'get'
  })
}
```

### request.js 配置

```javascript
const request = axios.create({
  baseURL: '/api',  // 统一的 API 前缀
  timeout: 15000
})
```

### Vite 代理配置

```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:5000',
      changeOrigin: true
      // 不需要 rewrite，保持 /api 前缀
    }
  }
}
```

---

## 常见错误

### 错误 1: 路径重复

**症状**: 404 错误，路径包含 `/api/api/`

**原因**: API 模块 URL 包含了 `/api/` 前缀

**解决**: 移除 API 模块 URL 中的 `/api/` 前缀

### 错误 2: 路径缺失

**症状**: 404 错误，路径不包含 `/api/`

**原因**: baseURL 未设置或设置错误

**解决**: 检查 `request.js` 中的 `baseURL` 配置

### 错误 3: CORS 错误

**症状**: CORS policy 错误

**原因**: Vite 代理未正确配置

**解决**: 检查 `vite.config.js` 中的 proxy 配置

---

## 调试技巧

### 1. 查看完整请求 URL

在 `request.js` 的请求拦截器中添加日志：

```javascript
request.interceptors.request.use(config => {
  console.log('完整请求 URL:', config.baseURL + config.url)
  return config
})
```

### 2. 查看后端日志

后端日志会显示实际接收到的请求路径：
```
GET /api/points HTTP/1.1" 200
```

### 3. 使用浏览器开发者工具

Network 标签会显示：
- Request URL: 完整的请求地址
- Status: 响应状态码
- Response: 响应内容

---

## 相关文档

- `exam/frontend/src/utils/request.js` - Axios 配置
- `exam/frontend/vite.config.js` - Vite 代理配置
- `exam/backend/app/__init__.py` - 后端路由注册

---

**修复时间**: 2024-12-26  
**问题**: API 路径重复 `/api/api/`  
**解决方案**: 移除 API 模块 URL 中的 `/api/` 前缀  
**状态**: 已修复 ✓
