# API URL 重复问题修复

## 问题描述

点击"开始练习"按钮后，出现以下错误：
- "网站连接失败，请检查网络连接"
- "开始练习失败"

## 问题原因

前端API请求URL配置错误，导致URL路径重复了 `/api` 前缀：

- **错误的URL**: `/api/api/practice/start` (404 Not Found)
- **正确的URL**: `/api/practice/start` (200 OK)

### 根本原因

在 `exam/frontend/src/utils/request.js` 中，axios实例已经配置了 `baseURL: '/api'`：

```javascript
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  // ...
})
```

但在各个API文件中，URL又包含了 `/api` 前缀：

```javascript
// 错误示例
export function startPractice(data) {
  return request({
    url: '/api/practice/start',  // ❌ 多余的 /api
    method: 'post',
    data
  })
}
```

这导致最终请求的URL变成：`baseURL + url = /api + /api/practice/start = /api/api/practice/start`

## 解决方案

移除所有API文件中URL的 `/api` 前缀：

```javascript
// 正确示例
export function startPractice(data) {
  return request({
    url: '/practice/start',  // ✅ 正确
    method: 'post',
    data
  })
}
```

## 修复的文件

以下文件已修复：

1. `exam/frontend/src/api/practice.js` - 练习相关API
2. `exam/frontend/src/api/statistics.js` - 统计相关API
3. `exam/frontend/src/api/auth.js` - 认证相关API
4. `exam/frontend/src/api/questions.js` - 题目相关API
5. `exam/frontend/src/api/exams.js` - 考试相关API

## 验证

修复后，后端日志显示：

```
127.0.0.1 - - [15/Dec/2025 10:18:13] "POST /api/practice/start HTTP/1.1" 200 -  ✅
```

而不是之前的404错误：

```
127.0.0.1 - - [15/Dec/2025 10:18:38] "OPTIONS /api/api/practice/start HTTP/1.1" 404 -  ❌
```

## 注意事项

以后添加新的API调用时，请确保：

1. URL路径**不要**包含 `/api` 前缀
2. 直接从资源路径开始，例如：`/practice/start`、`/questions`、`/auth/login` 等
3. `baseURL` 已经在 `request.js` 中统一配置为 `/api`

## 测试

修复后，请测试以下功能：

- [x] 开始练习
- [ ] 提交答案
- [ ] 查看练习历史
- [ ] 查看错题本
- [ ] 查看统计数据
- [ ] 题目管理
- [ ] 考试功能

修复日期：2025-12-15
