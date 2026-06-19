# 考试开始问题调试指南

## 问题现象
点击"开始考试"后，出现错误："Request failed with status code 500"，无法进入答题界面。

## 调试步骤

### 步骤 1：检查浏览器控制台

1. 打开浏览器开发者工具（F12）
2. 切换到 **Console** 标签
3. 点击"开始考试"
4. 查看完整的错误信息

**需要查找的信息：**
- 错误的完整堆栈跟踪
- API 请求的 URL
- 请求的参数

### 步骤 2：检查网络请求

1. 在开发者工具中切换到 **Network** 标签
2. 点击"开始考试"
3. 找到失败的请求（通常是红色的）
4. 点击该请求，查看以下信息：

**Headers 标签：**
```
Request URL: http://localhost:5000/api/exams/{paperId}/start
Request Method: POST
Status Code: 500 Internal Server Error
```

**Response 标签：**
查看后端返回的错误信息，应该类似：
```json
{
  "success": false,
  "error": {
    "code": "START_EXAM_ERROR",
    "message": "具体的错误信息"
  }
}
```

**Request Headers：**
检查是否有 Authorization 头：
```
Authorization: Bearer <token>
```

### 步骤 3：检查后端日志

查看后端控制台输出，寻找以下信息：

```
127.0.0.1 - - [日期时间] "POST /api/exams/1/start HTTP/1.1" 500 -
```

如果看到 500 错误，应该会有详细的错误堆栈。

### 步骤 4：常见问题排查

#### 问题 1：认证失败

**症状：**
- 后端日志显示 401 或 403 错误
- 或者没有看到 POST /api/exams/{id}/start 请求

**解决方案：**
1. 检查用户是否已登录
2. 检查 localStorage 中是否有 token：
   ```javascript
   // 在浏览器控制台执行
   console.log(localStorage.getItem('token'))
   ```
3. 如果没有 token，重新登录

#### 问题 2：试卷 ID 错误

**症状：**
- 后端返回 "试卷不存在"

**解决方案：**
1. 检查 URL 中的试卷 ID 是否正确
2. 在浏览器控制台执行：
   ```javascript
   // 检查当前路由参数
   console.log(window.location.pathname)
   ```

#### 问题 3：已有进行中的考试

**症状：**
- 后端返回 "已有进行中的考试，请先完成或提交"

**解决方案：**
运行清理脚本：
```bash
cd exam/backend
python quick_clear_sessions.py
```

#### 问题 4：CORS 错误

**症状：**
- 浏览器控制台显示 CORS 相关错误
- 请求被阻止

**解决方案：**
1. 确认后端已启动
2. 确认前端配置的 API 地址正确
3. 检查 `exam/frontend/src/utils/request.js` 中的 baseURL

### 步骤 5：手动测试 API

使用 curl 或 Postman 测试 API：

```bash
# 1. 先登录获取 token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"student","password":"password123"}'

# 2. 使用返回的 token 开始考试
curl -X POST http://localhost:5000/api/exams/1/start \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <你的token>"
```

**预期响应：**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "user_id": 2,
    "paper_id": 1,
    "start_time": "2025-12-18T08:00:00",
    "end_time": "2025-12-18T10:00:00",
    "status": "in_progress",
    "answers": {}
  },
  "message": "考试开始"
}
```

### 步骤 6：检查前端代码

检查 `exam/frontend/src/views/ExamList.vue` 中的 `handleStartExam` 函数：

```javascript
async function handleStartExam(paper) {
  try {
    // 确认对话框
    await ElMessageBox.confirm(...)

    startingExam.value = paper.id

    // 调用开始考试 API
    const response = await startExam(paper.id)  // 这里调用 API

    if (response.success && response.data) {
      ElMessage.success('考试已开始，祝你取得好成绩！')
      
      // 跳转到考试页面
      router.push({
        name: 'exam',
        params: { paperId: paper.id },
        query: { sessionId: response.data.id }  // 传递 sessionId
      })
    }
  } catch (error) {
    // 错误处理
    console.error('开始考试失败:', error)
    // 查看完整的错误对象
    console.log('错误详情:', error.response)
  }
}
```

### 步骤 7：添加更多调试日志

在 `exam/frontend/src/api/exams.js` 中的 `startExam` 函数添加日志：

```javascript
export function startExam(paperId) {
  console.log('调用 startExam API, paperId:', paperId)
  
  return request({
    url: `/exams/${paperId}/start`,
    method: 'post'
  }).then(response => {
    console.log('startExam 响应:', response)
    return response
  }).catch(error => {
    console.error('startExam 错误:', error)
    console.error('错误响应:', error.response)
    throw error
  })
}
```

## 快速修复方案

如果以上步骤都无法解决问题，尝试以下快速修复：

### 方案 1：清理所有会话

```bash
cd exam/backend
python quick_clear_sessions.py
```

### 方案 2：重新登录

1. 退出登录
2. 清除浏览器缓存和 localStorage
3. 重新登录

### 方案 3：重启服务

```bash
# 停止后端服务（Ctrl+C）
# 重新启动
cd exam/backend
python run.py

# 停止前端服务（Ctrl+C）
# 重新启动
cd exam/frontend
npm run dev
```

### 方案 4：检查数据库

```bash
cd exam/backend
python check_paper_questions.py --check
```

确保试卷有题目。

## 需要提供的信息

如果问题仍然存在，请提供以下信息：

1. **浏览器控制台的完整错误信息**（截图或文本）
2. **Network 标签中失败请求的详细信息**：
   - Request URL
   - Request Headers
   - Response（错误信息）
3. **后端控制台的日志**（特别是 500 错误的堆栈跟踪）
4. **当前的 URL**（浏览器地址栏）
5. **用户信息**（用户名，是否已登录）

## 相关文件

- `exam/frontend/src/views/ExamList.vue` - 试卷列表和开始考试
- `exam/frontend/src/api/exams.js` - API 调用
- `exam/backend/app/routes/exams.py` - 后端路由
- `exam/backend/app/services/exam_service.py` - 考试服务
