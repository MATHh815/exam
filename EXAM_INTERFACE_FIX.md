# 考试界面显示问题修复

## 问题描述
用户点击"开始考试"后，显示"考试已开始"消息，但没有显示刷题界面。

## 根本原因
当 `ExamList.vue` 调用 `startExam` API 创建会话后，会跳转到 `/exam/:paperId?sessionId=xxx`。
`Exam.vue` 的 `initExam()` 函数接收到 `sessionId` 参数后，调用 `examStore.beginExam(paperId, paperData, sessionId)`。

但是 `beginExam` 函数在处理已存在的 `sessionId` 时，只创建了一个简单的对象：
```javascript
session = { id: sessionId }
```

这个对象缺少关键字段：
- `start_time` - 导致时间计算错误
- `end_time` - 导致倒计时无法工作
- `answers` - 导致答案状态为空

## 解决方案

### 修改 1: 修复 `exam/frontend/src/stores/exam.js` 中的 `beginExam` 函数

当接收到 `sessionId` 参数时，构建完整的会话对象：

```javascript
if (sessionId) {
  // 使用已创建的会话 - 需要构建完整的会话对象
  const now = new Date()
  const endTime = new Date(now.getTime() + paperData.duration * 60 * 1000)
  
  session = {
    id: sessionId,
    user_id: null, // 会在后端验证
    paper_id: paperId,
    start_time: now.toISOString(),
    end_time: endTime.toISOString(),
    status: 'in_progress',
    answers: {}
  }
}
```

### 修改 2: 简化 `exam/frontend/src/views/Exam.vue` 中的 `initExam` 函数

- 先获取试卷详情
- 如果有 `sessionId`，直接开始考试
- 如果没有 `sessionId`，尝试检查进行中的会话
- 如果都没有，确认后创建新会话

## 测试步骤

1. 清理所有进行中的会话：
```bash
cd exam/backend
python quick_clear_sessions.py
```

2. 在浏览器中访问考试列表页面
3. 点击"开始考试"按钮
4. 确认开始考试
5. 应该能看到：
   - 考试标题和类型标签
   - 倒计时器
   - 题目卡片
   - 上一题/下一题按钮
   - 右侧答题进度
   - 自动保存状态

## 相关文件
- `exam/frontend/src/stores/exam.js` - 考试状态管理
- `exam/frontend/src/views/Exam.vue` - 考试界面
- `exam/frontend/src/views/ExamList.vue` - 考试列表
- `exam/backend/app/routes/exams.py` - 考试API路由

## 注意事项
- 确保后端服务正在运行
- 确保前端开发服务器正在运行
- 确保数据库中有已发布的试卷和题目
