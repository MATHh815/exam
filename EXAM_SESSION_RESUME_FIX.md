# 考试会话恢复功能修复

## 问题描述

用户点击"开始考试"后，系统提示"已有进行中的考试，请先完成或提交"，但用户不知道如何继续之前的考试，也找不到考试界面。

## 问题分析

### 原有问题

1. **无法继续考试**：当用户有进行中的考试会话时，系统阻止创建新会话，但没有提供继续考试的选项
2. **会话丢失**：用户刷新页面或关闭浏览器后，无法恢复进行中的考试
3. **用户体验差**：错误提示不友好，没有明确的操作指引

### 业务场景

- 用户在考试过程中意外关闭浏览器
- 用户刷新页面
- 用户点击"开始考试"但已有进行中的会话
- 网络中断后重新连接

## 解决方案

### 1. 后端 API 增强

#### 新增 API：获取当前进行中的会话

**路由**: `GET /api/exams/{paperId}/current-session`

**功能**: 查询用户在指定试卷的进行中会话

**响应**:
```json
{
  "success": true,
  "data": {
    "id": 123,
    "user_id": 1,
    "paper_id": 2,
    "start_time": "2025-12-15T10:00:00Z",
    "end_time": "2025-12-15T12:00:00Z",
    "status": "in_progress",
    "answers": {
      "1": "A",
      "2": "B"
    }
  }
}
```

**实现位置**: `exam/backend/app/routes/exams.py`

### 2. 前端功能增强

#### 2.1 ExamList.vue - 智能错误处理

当检测到"已有进行中的考试"错误时：

1. 显示友好的提示对话框
2. 提供"继续考试"选项
3. 点击后直接跳转到考试页面

**修改内容**:
```javascript
// 检查是否是"已有进行中的考试"错误
if (errorMessage.includes('已有进行中的考试')) {
  // 提示用户有进行中的考试
  await ElMessageBox.confirm(
    '检测到您有一个进行中的考试。您可以继续之前的考试，或者放弃后重新开始。',
    '提示',
    {
      confirmButtonText: '继续考试',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )
  
  // 跳转到考试页面
  router.push({
    name: 'exam',
    params: { paperId: paper.id }
  })
}
```

#### 2.2 Exam.vue - 会话恢复逻辑

**初始化流程**:

1. 检查是否有进行中的会话
2. 如果有，恢复会话状态
3. 如果没有，正常开始新考试

**实现**:
```javascript
async function initExam() {
  // 1. 检查进行中的会话
  const sessionResponse = await getCurrentSession(paperId)
  
  if (sessionResponse.success && sessionResponse.data) {
    // 2. 恢复会话
    await examStore.resumeExam(existingSession, paperData)
    ElMessage.success('已恢复进行中的考试')
    return
  }
  
  // 3. 开始新考试
  await examStore.beginExam(paperId, paperData)
}
```

#### 2.3 Exam Store - 新增 resumeExam 方法

**功能**: 恢复进行中的考试会话

**实现**:
```javascript
async function resumeExam(session, paperData) {
  currentSession.value = session
  currentPaper.value = paperData
  answers.value = session.answers || {}
  examStatus.value = 'in_progress'
  startTime.value = new Date(session.start_time)
  endTime.value = new Date(session.end_time)
  
  // 计算剩余时间
  const now = new Date()
  timeRemaining.value = Math.max(0, Math.floor((endTime.value - now) / 1000))
  
  return { success: true, session: currentSession.value }
}
```

### 3. API 调用增强

#### 新增前端 API 方法

**文件**: `exam/frontend/src/api/exams.js`

```javascript
/**
 * 获取当前进行中的考试会话
 * @param {number} paperId - 试卷ID
 * @returns {Promise}
 */
export function getCurrentSession(paperId) {
  return request({
    url: `/exams/${paperId}/current-session`,
    method: 'get'
  })
}
```

## 用户流程

### 场景1：正常开始考试

1. 用户点击"开始考试"
2. 系统检查无进行中会话
3. 创建新会话
4. 进入考试页面

### 场景2：继续进行中的考试

1. 用户点击"开始考试"
2. 系统检测到进行中会话
3. 显示提示："检测到您有一个进行中的考试"
4. 用户点击"继续考试"
5. 系统恢复会话状态
6. 进入考试页面，显示之前的答案和剩余时间

### 场景3：刷新页面恢复

1. 用户在考试中刷新页面
2. 系统自动检测进行中会话
3. 恢复会话状态
4. 显示提示："已恢复进行中的考试"
5. 继续考试

## 技术细节

### 会话状态管理

**存储位置**: Pinia Store (exam.js)

**状态包含**:
- `currentSession`: 当前会话信息
- `currentPaper`: 试卷信息
- `answers`: 已答题目
- `startTime`: 开始时间
- `endTime`: 结束时间
- `timeRemaining`: 剩余时间

### 时间计算

```javascript
// 计算剩余时间
const now = new Date()
const endTime = new Date(session.end_time)
timeRemaining.value = Math.max(0, Math.floor((endTime - now) / 1000))
```

### 答案恢复

```javascript
// 从会话中恢复答案
answers.value = session.answers || {}
```

## 修改文件清单

### 后端

1. `exam/backend/app/routes/exams.py`
   - 新增 `get_current_session` 路由

### 前端

1. `exam/frontend/src/api/exams.js`
   - 新增 `getCurrentSession` API 方法

2. `exam/frontend/src/views/ExamList.vue`
   - 修改 `handleStartExam` 函数
   - 添加智能错误处理

3. `exam/frontend/src/views/Exam.vue`
   - 修改 `initExam` 函数
   - 添加会话检测和恢复逻辑

4. `exam/frontend/src/stores/exam.js`
   - 新增 `resumeExam` 方法
   - 修改 `beginExam` 方法支持已创建的会话

## 测试场景

### 测试1：正常流程
1. ✅ 首次开始考试
2. ✅ 答题并保存
3. ✅ 提交试卷

### 测试2：会话恢复
1. ✅ 开始考试
2. ✅ 答几道题
3. ✅ 刷新页面
4. ✅ 验证答案和时间恢复

### 测试3：重复开始
1. ✅ 开始考试
2. ✅ 返回试卷列表
3. ✅ 再次点击"开始考试"
4. ✅ 显示提示并提供继续选项

### 测试4：超时处理
1. ✅ 开始考试
2. ✅ 等待超时
3. ✅ 自动提交
4. ✅ 无法恢复已结束的会话

## 注意事项

1. **时间同步**：确保服务器时间和客户端时间同步
2. **会话清理**：已完成或超时的会话不应被恢复
3. **并发控制**：同一用户同一试卷只能有一个进行中会话
4. **数据一致性**：恢复时验证会话状态的有效性

## 后续优化建议

1. **自动保存**：定期自动保存答案到服务器
2. **离线支持**：支持离线答题，网络恢复后同步
3. **会话管理**：提供查看和管理所有进行中会话的界面
4. **提醒功能**：考试即将超时时提醒用户

## 修复时间

2025-12-15

## 版本

v1.0 - 初始实现
