# 考试界面无题目问题修复

## 问题描述
用户点击"开始考试"后，跳转到考试界面，但是没有显示做题界面。

## 问题原因分析

经过代码审查，发现以下问题：

1. **前端 Exam.vue 的 initExam() 逻辑问题**：
   - 当从 ExamList 跳转过来时，URL 包含 `sessionId` 参数
   - 代码调用 `getExamPaper(paperId, true)` 获取试卷详情
   - 但是当有 `sessionId` 时，直接调用 `examStore.beginExam(paperId, paperData, sessionId)`
   - 这个流程中，`paperData` 应该包含 `questions` 数组

2. **可能的数据问题**：
   - 后端返回的试卷数据中，`questions` 字段可能为空
   - 或者前端没有正确处理返回的题目数据

3. **Store 状态问题**：
   - `examStore.currentPaper` 可能没有正确设置
   - `questions` computed 属性依赖 `currentPaper?.questions`

## 修复方案

### 方案 1：修复前端 Exam.vue 的初始化逻辑

在 `Exam.vue` 中，确保获取试卷时包含题目，并正确处理：

```javascript
// exam/frontend/src/views/Exam.vue
async function initExam() {
  const paperId = route.params.paperId
  const sessionId = route.query.sessionId
  
  if (!paperId) {
    ElMessage.error('缺少试卷ID')
    router.push('/dashboard')
    return
  }
  
  try {
    loading.value = true
    
    // 如果已经有进行中的考试会话，直接使用
    if (examStore.isExamInProgress && examStore.currentPaper?.id === parseInt(paperId)) {
      // 检查是否有题目
      if (!examStore.currentPaper.questions || examStore.currentPaper.questions.length === 0) {
        throw new Error('试卷没有题目')
      }
      return
    }
    
    // 获取试卷详情（包含题目）- 这里必须包含题目
    const response = await getExamPaper(paperId, true)
    
    if (!response.success) {
      throw new Error(response.error?.message || '获取试卷失败')
    }
    
    const paperData = response.data
    
    // 验证试卷是否有题目
    if (!paperData.questions || paperData.questions.length === 0) {
      throw new Error('该试卷暂无题目，无法开始考试')
    }
    
    console.log('试卷数据:', paperData)
    console.log('题目数量:', paperData.questions?.length)
    
    // ... 后续逻辑
  } catch (error) {
    // ... 错误处理
  }
}
```

### 方案 2：检查后端返回数据

确保后端正确返回题目数据。在 `exam/backend/app/routes/exams.py` 中：

```python
@exams_bp.route('/<int:paper_id>', methods=['GET'])
@jwt_required_with_user
def get_paper(current_user, paper_id):
    """获取试卷详情"""
    try:
        include_questions = request.args.get('include_questions', 'false').lower() == 'true'
        
        paper = ExamPaperService.get_paper(paper_id, include_questions=include_questions)
        
        if not paper:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'PAPER_NOT_FOUND',
                    'message': '试卷不存在'
                }
            }), 404
        
        # 获取试卷基本信息
        paper_dict = paper.to_dict(include_questions=False)
        
        # 如果需要题目列表，获取详细题目信息
        if include_questions:
            questions = ExamPaperService.get_paper_questions(paper_id)
            paper_dict['questions'] = questions
            print(f"返回试卷 {paper_id} 的题目数量: {len(questions)}")  # 调试日志
        
        return jsonify({
            'success': True,
            'data': paper_dict
        }), 200
        
    except Exception as e:
        print(f"获取试卷失败: {str(e)}")  # 调试日志
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_PAPER_ERROR',
                'message': str(e)
            }
        }), 500
```

### 方案 3：添加调试日志

在关键位置添加 console.log 来追踪数据流：

```javascript
// exam/frontend/src/views/Exam.vue
async function initExam() {
  // ...
  const response = await getExamPaper(paperId, true)
  console.log('API 响应:', response)
  console.log('试卷数据:', response.data)
  console.log('题目列表:', response.data?.questions)
  
  if (!response.data?.questions || response.data.questions.length === 0) {
    console.error('试卷没有题目！')
    ElMessage.error('该试卷暂无题目，无法开始考试')
    router.push('/exams')
    return
  }
  // ...
}
```

## 快速诊断步骤

1. **打开浏览器开发者工具**（F12）
2. **切换到 Console 标签**
3. **点击"开始考试"**
4. **查看控制台输出**：
   - 检查 API 请求：`/api/exams/{paperId}?include_questions=true`
   - 查看响应数据中是否有 `questions` 字段
   - 查看 `questions` 数组的长度

5. **切换到 Network 标签**
6. **找到 `/api/exams/{paperId}` 请求**
7. **查看 Response**：
   ```json
   {
     "success": true,
     "data": {
       "id": 1,
       "name": "试卷名称",
       "questions": [...]  // 这里应该有题目数组
     }
   }
   ```

## 临时解决方案

如果问题紧急，可以先检查数据库：

```sql
-- 检查试卷是否有题目
SELECT 
    ep.id,
    ep.name,
    COUNT(epq.id) as question_count
FROM exam_papers ep
LEFT JOIN exam_paper_questions epq ON ep.id = epq.paper_id
WHERE ep.id = {试卷ID}
GROUP BY ep.id;

-- 如果 question_count 为 0，说明试卷没有题目
-- 需要先添加题目到试卷
```

## 预防措施

1. **在试卷发布前验证**：确保试卷至少有一道题目
2. **前端添加验证**：在开始考试前检查题目数量
3. **后端添加验证**：在 `start_exam` API 中验证试卷是否有题目

## 相关文件

- `exam/frontend/src/views/Exam.vue` - 考试界面组件
- `exam/frontend/src/stores/exam.js` - 考试状态管理
- `exam/backend/app/routes/exams.py` - 考试路由
- `exam/backend/app/services/exam_paper_service.py` - 试卷服务
