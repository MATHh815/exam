# 考试 API 路径修复

## 问题描述

在点击"开始考试"按钮时出现错误，提示"加载试卷列表失败"和"请检查网络设置"。

## 问题分析

### 根本原因

**URL 重复拼接问题：**

前端的 `request.js` 中配置的 `baseURL` 已经包含了 `/api` 前缀：

```javascript
// exam/frontend/src/utils/request.js
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',  // 已包含 /api
  // ...
})
```

环境变量配置：
```bash
# .env.development
VITE_API_BASE_URL=http://127.0.0.1:5000/api

# .env.production
VITE_API_BASE_URL=/api
```

但是 API 调用中又加了 `/api` 前缀，导致最终 URL 变成：
- 期望: `http://127.0.0.1:5000/api/exams`
- 实际: `http://127.0.0.1:5000/api/api/exams` ❌

### 后端路由配置

后端在 `app/__init__.py` 中注册蓝图：

```python
app.register_blueprint(exams_bp, url_prefix='/api/exams')
```

实际的后端路由是：`/api/exams/*`

## 修复方案

由于 `baseURL` 已经包含 `/api`，所以 API 调用中应该**移除** `/api` 前缀。

### 修改文件

`exam/frontend/src/api/exams.js`

### 修复的 API 调用

所有 API 调用都移除了 `/api` 前缀：

1. **getExamPapers** - 获取试卷列表
   ```javascript
   // 修复前
   url: '/api/exams'
   
   // 修复后
   url: '/exams'
   ```

2. **getExamPaper** - 获取试卷详情
   ```javascript
   // 修复前
   url: `/api/exams/${paperId}`
   
   // 修复后
   url: `/exams/${paperId}`
   ```

3. **createExamPaper** - 创建试卷
   ```javascript
   // 修复前
   url: '/api/exams'
   
   // 修复后
   url: '/exams'
   ```

4. **updateExamPaper** - 更新试卷
   ```javascript
   // 修复前
   url: `/api/exams/${paperId}`
   
   // 修复后
   url: `/exams/${paperId}`
   ```

5. **deleteExamPaper** - 删除试卷
   ```javascript
   // 修复前
   url: `/api/exams/${paperId}`
   
   // 修复后
   url: `/exams/${paperId}`
   ```

6. **addQuestionToPaper** - 添加题目到试卷
   ```javascript
   // 修复前
   url: `/api/exams/${paperId}/questions`
   
   // 修复后
   url: `/exams/${paperId}/questions`
   ```

7. **publishExamPaper** - 发布试卷
   ```javascript
   // 修复前
   url: `/api/exams/${paperId}/publish`
   
   // 修复后
   url: `/exams/${paperId}/publish`
   ```

8. **startExam** - 开始考试
   ```javascript
   // 修复前
   url: `/api/exams/${paperId}/start`
   
   // 修复后
   url: `/exams/${paperId}/start`
   ```

9. **submitAnswer** - 提交答案
   ```javascript
   // 修复前
   url: `/api/exams/sessions/${sessionId}/answer`
   
   // 修复后
   url: `/exams/sessions/${sessionId}/answer`
   ```

10. **submitExam** - 提交试卷
    ```javascript
    // 修复前
    url: `/api/exams/sessions/${sessionId}/submit`
    
    // 修复后
    url: `/exams/sessions/${sessionId}/submit`
    ```

11. **getExamResult** - 获取考试结果
    ```javascript
    // 修复前
    url: `/api/exams/results/${resultId}`
    
    // 修复后
    url: `/exams/results/${resultId}`
    ```

12. **getExamHistory** - 获取考试历史
    ```javascript
    // 修复前
    url: '/api/exams/results'
    
    // 修复后
    url: '/exams/results'
    ```

## 测试验证

修复后，以下功能应该正常工作：

1. ✅ 试卷列表加载
2. ✅ 点击"开始考试"按钮
3. ✅ 创建新试卷（管理员）
4. ✅ 查看考试历史

## 相关文件

- `exam/frontend/src/api/exams.js` - 考试 API 接口定义
- `exam/backend/app/routes/exams.py` - 后端考试路由
- `exam/backend/app/__init__.py` - 蓝图注册配置

## 注意事项

所有 API 调用都应该遵循统一的路径规范：

- 认证相关：`/api/auth/*`
- 题目相关：`/api/questions/*`
- 练习相关：`/api/practice/*`
- 考试相关：`/api/exams/*`
- 统计相关：`/api/statistics/*`
- 数据相关：`/api/data/*`

## 修复时间

2025-12-15


## URL 拼接规则

### 正确的配置方式

**方式1：baseURL 包含 /api（当前使用）**
```javascript
// request.js
baseURL: '/api'  // 或 'http://127.0.0.1:5000/api'

// API 调用
url: '/exams'  // 最终: /api/exams ✓
```

**方式2：baseURL 不包含 /api**
```javascript
// request.js
baseURL: '/'  // 或 'http://127.0.0.1:5000'

// API 调用
url: '/api/exams'  // 最终: /api/exams ✓
```

### 错误的配置（已修复）

```javascript
// request.js
baseURL: '/api'

// API 调用
url: '/api/exams'  // 最终: /api/api/exams ❌
```

## 测试验证

修复后，以下功能应该正常工作：

1. ✅ 试卷列表加载
2. ✅ 点击"开始考试"按钮
3. ✅ 考试会话创建
4. ✅ 答案提交
5. ✅ 试卷提交
6. ✅ 查看考试结果
7. ✅ 查看考试历史
8. ✅ 创建新试卷（管理员）
9. ✅ 管理试卷（管理员）

## 相关文件

- `exam/frontend/src/api/exams.js` - 考试 API 接口定义（已修复）
- `exam/frontend/src/utils/request.js` - Axios 请求配置
- `exam/frontend/.env.development` - 开发环境配置
- `exam/frontend/.env.production` - 生产环境配置
- `exam/backend/app/routes/exams.py` - 后端考试路由
- `exam/backend/app/__init__.py` - 蓝图注册配置

## 注意事项

1. **统一规范**：所有 API 模块都应该遵循相同的 URL 规范
2. **环境变量**：确保 `VITE_API_BASE_URL` 配置正确
3. **后端服务**：确保后端服务在 `http://127.0.0.1:5000` 运行
4. **CORS 配置**：确保后端允许前端域名的跨域请求

## 修复时间

2025-12-15

## 修复版本

v2 - 修复了 URL 重复拼接问题
