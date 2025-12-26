# 模拟考试列表功能

## 功能概述
为考试系统添加了"模拟考试"列表页面,用户可以浏览所有已发布的试卷,查看试卷详情,并开始考试。

## 新增文件

### 1. ExamList.vue
路径: `exam/frontend/src/views/ExamList.vue`

这是模拟考试列表的主页面,包含以下功能:

#### 功能特性
- ✅ 试卷列表展示(卡片式布局)
- ✅ 考试类型筛选
- ✅ 试卷详情查看
- ✅ 开始考试功能
- ✅ 分页支持
- ✅ 响应式设计

#### 显示信息
每个试卷卡片显示:
- 试卷名称
- 考试类型标签
- 试卷描述
- 考试时长
- 题目数量
- 总分和及格分
- 已考次数(如果有)
- 最高分(如果有)

#### 操作功能
- **开始考试**: 点击后弹出确认对话框,确认后调用 API 创建考试会话并跳转到考试页面
- **查看详情**: 在对话框中显示试卷的完整信息

## 修改文件

### 1. router/index.js
添加了新路由:
```javascript
{
  path: '/exams',
  name: 'examList',
  component: () => import('../views/ExamList.vue'),
  meta: { requiresAuth: true, title: '模拟考试' }
}
```

### 2. Dashboard.vue
修改了 `goToExams()` 方法:
```javascript
// 修改前
function goToExams() {
  ElMessage.info('考试列表功能开发中')
}

// 修改后
function goToExams() {
  router.push('/exams')
}
```

## 使用流程

### 用户操作流程
1. 用户在 Dashboard 点击"模拟考试"卡片
2. 跳转到考试列表页面 (`/exams`)
3. 浏览可用的试卷列表
4. 可以通过考试类型进行筛选
5. 点击"查看详情"查看试卷完整信息
6. 点击"开始考试"按钮
7. 确认后创建考试会话
8. 跳转到考试页面开始答题

### API 调用流程
1. **加载试卷列表**
   ```
   GET /api/exams?is_published=true&page=1&page_size=12
   ```

2. **开始考试**
   ```
   POST /api/exams/{paper_id}/start
   ```
   返回考试会话信息,包含 session_id

3. **跳转到考试页面**
   ```
   /exam/{paper_id}?sessionId={session_id}
   ```

## 数据结构

### 试卷对象 (Paper)
```javascript
{
  id: 1,
  name: "2024年公务员行测模拟试卷",
  exam_type: "civil_service",
  description: "包含言语理解、数量关系、判断推理等模块",
  duration: 120,
  total_score: 100,
  pass_score: 60,
  question_count: 50,
  is_published: true,
  created_at: "2024-01-01T00:00:00",
  attempt_count: 5,  // 用户已考次数
  best_score: 85     // 用户最高分
}
```

### 考试会话对象 (Session)
```javascript
{
  id: 1,
  user_id: 1,
  paper_id: 1,
  start_time: "2024-01-01T10:00:00",
  end_time: null,
  status: "in_progress"
}
```

## 样式特点

### 布局
- 响应式网格布局
- 桌面端: 3-4列
- 平板端: 2列
- 手机端: 1列

### 卡片设计
- 悬停效果: 上移 + 阴影加深
- 清晰的信息层次
- 图标 + 文字的信息展示
- 主次操作按钮区分

### 颜色方案
- 公务员考试: 蓝色 (primary)
- 研究生考试: 绿色 (success)
- 事业编考试: 橙色 (warning)

## 后端 API 支持

### 已实现的 API
✅ `GET /api/exams` - 获取试卷列表
✅ `GET /api/exams/:id` - 获取试卷详情
✅ `POST /api/exams/:id/start` - 开始考试
✅ `POST /api/exams/sessions/:id/answer` - 提交答案
✅ `POST /api/exams/sessions/:id/submit` - 提交试卷
✅ `GET /api/exams/results/:id` - 获取考试结果
✅ `GET /api/exams/results` - 获取考试历史

### API 权限
- 普通用户: 可以查看已发布的试卷,开始考试,查看自己的考试结果
- 管理员: 额外可以创建、编辑、删除、发布试卷

## 测试步骤

### 前置条件
1. 后端服务运行中
2. 数据库中有已发布的试卷数据
3. 用户已登录

### 测试流程
1. **访问考试列表**
   - 在 Dashboard 点击"模拟考试"
   - 应该跳转到 `/exams` 页面
   - 应该显示所有已发布的试卷

2. **筛选功能**
   - 选择考试类型
   - 点击"搜索"
   - 应该只显示对应类型的试卷
   - 点击"重置"应该清除筛选

3. **查看详情**
   - 点击任意试卷的"查看详情"按钮
   - 应该弹出对话框显示试卷完整信息

4. **开始考试**
   - 点击"开始考试"按钮
   - 应该弹出确认对话框
   - 点击"开始"
   - 应该创建考试会话
   - 应该跳转到考试页面

5. **分页功能**
   - 如果试卷超过12个
   - 应该显示分页组件
   - 切换页码应该加载对应页的数据

## 相关文件

### 前端
- `exam/frontend/src/views/ExamList.vue` - 考试列表页面(新增)
- `exam/frontend/src/views/Dashboard.vue` - 仪表盘(修改)
- `exam/frontend/src/router/index.js` - 路由配置(修改)
- `exam/frontend/src/api/exams.js` - 考试 API(已存在)
- `exam/frontend/src/views/Exam.vue` - 考试页面(已存在)
- `exam/frontend/src/views/ExamResult.vue` - 考试结果页面(已存在)

### 后端
- `exam/backend/app/routes/exams.py` - 考试路由(已存在)
- `exam/backend/app/services/exam_service.py` - 考试服务(已存在)
- `exam/backend/app/services/exam_paper_service.py` - 试卷服务(已存在)
- `exam/backend/app/models/exam.py` - 考试模型(已存在)

## 后续优化建议

### 功能增强
1. 添加试卷搜索功能(按名称搜索)
2. 添加难度筛选
3. 显示试卷的平均分和通过率
4. 添加试卷收藏功能
5. 显示考试排行榜

### 性能优化
1. 实现虚拟滚动(如果试卷数量很大)
2. 添加骨架屏加载效果
3. 图片懒加载

### 用户体验
1. 添加试卷预览功能(不计分)
2. 显示考试倒计时提醒
3. 添加考试历史记录快速入口
4. 支持继续未完成的考试

## 注意事项

1. **考试会话管理**: 确保用户不能同时进行多个考试
2. **时间控制**: 考试页面需要实现倒计时和自动提交
3. **数据持久化**: 考试过程中的答案需要实时保存
4. **防作弊**: 考虑添加防切屏、防复制等措施
5. **错误处理**: 网络中断时的数据恢复机制

## 完成状态

- ✅ 考试列表页面
- ✅ 试卷筛选功能
- ✅ 试卷详情查看
- ✅ 开始考试功能
- ✅ 路由配置
- ✅ Dashboard 跳转
- ✅ 响应式设计
- ✅ 后端 API 集成

功能已完整实现,可以正常使用!
