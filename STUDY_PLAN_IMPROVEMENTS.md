# 学习计划功能改进

## 改进概述

本次改进解决了学习计划功能的三个主要问题：

1. **状态逻辑问题** - 计划创建后立即显示为"已完成"
2. **目标类型有限** - 只有2-3种基础目标类型
3. **缺少进度追踪** - 没有根据实际学习活动自动更新进度

## 改进内容

### 1. 自动状态管理

**问题**：计划创建后状态就是"completed"，不符合实际情况

**解决方案**：实现智能状态判断逻辑

```python
# 状态自动判断规则：
- 如果当前日期 > 结束日期 或 所有目标完成 → status = 'completed'
- 如果开始日期 <= 当前日期 <= 结束日期 → status = 'active'
- 用户手动暂停 → status = 'paused'（不会自动改变）
```

**实现位置**：
- `exam/backend/app/services/study_plan_service.py` - `_update_plan_status()` 方法
- 在 `get_user_plans()` 中自动调用，每次获取计划列表时更新状态

### 2. 丰富的目标类型

**问题**：只有 `daily_practice`、`weekly_practice`、`daily_duration` 三种类型

**解决方案**：扩展到 14 种目标类型，支持多维度学习目标

#### 新增目标类型

**练习数量类**（5种）：
- `daily_practice` - 每日练习题数
- `weekly_practice` - 每周练习题数
- `monthly_practice` - 每月练习题数 ⭐新增
- `subject_daily_practice` - 科目每日练习题数 ⭐新增
- `subject_weekly_practice` - 科目每周练习题数 ⭐新增

**学习时长类**（3种）：
- `daily_duration` - 每日学习时长（分钟）
- `weekly_duration` - 每周学习时长（分钟）⭐新增
- `subject_daily_duration` - 科目每日学习时长 ⭐新增

**正确率类**（2种）：
- `accuracy_rate` - 总体正确率（百分比）⭐新增
- `subject_accuracy_rate` - 科目正确率 ⭐新增

**考试类**（2种）：
- `exam_count` - 考试次数
- `exam_score` - 考试目标分数 ⭐新增

**章节类**（2种）：
- `chapter_completion` - 章节完成数 ⭐新增
- `subject_chapter_completion` - 科目章节完成数 ⭐新增

#### 科目支持

带 `subject_` 前缀的目标类型需要指定科目：
- 行测 (xingce)
- 申论 (shenlun)
- 数学 (math)
- 英语 (english)
- 政治 (politics)
- 专业课 (major)

### 3. 数据库改进

**新增字段**：

```sql
-- study_goals 表
ALTER TABLE study_goals ADD COLUMN subject VARCHAR(50);        -- 科目
ALTER TABLE study_goals ADD COLUMN completed_at DATETIME;      -- 完成时间
```

**迁移脚本**：
```bash
cd exam/backend
python migrate_study_plan_improvements.py
```

### 4. 前端表单改进

**改进点**：
- 目标类型按类别分组显示（练习数量、学习时长、正确率、考试、章节）
- 科目特定目标自动显示科目选择器
- 根据目标类型动态调整输入范围和标签
- 智能默认值设置

**示例**：
- 正确率目标：范围 1-100%，默认 80%
- 学习时长：范围 5-1440 分钟，默认 60 分钟
- 练习题数：范围 1-1000 题，默认 10 题

## 使用示例

### 创建多样化学习计划

```javascript
// 前端调用示例
const planData = {
  name: "2024国考冲刺计划",
  exam_type: "civil_service",
  start_date: "2024-01-01",
  end_date: "2024-01-31",
  description: "最后30天冲刺",
  goals: [
    {
      goal_type: "subject_daily_practice",  // 科目每日练习
      subject: "xingce",                     // 行测
      target_value: 50,
      period_start: "2024-01-01",
      period_end: "2024-01-31"
    },
    {
      goal_type: "subject_accuracy_rate",   // 科目正确率
      subject: "xingce",
      target_value: 85,                      // 85%
      period_start: "2024-01-01",
      period_end: "2024-01-31"
    },
    {
      goal_type: "daily_duration",          // 每日学习时长
      target_value: 120,                     // 120分钟
      period_start: "2024-01-01",
      period_end: "2024-01-31"
    },
    {
      goal_type: "exam_count",              // 模拟考试次数
      target_value: 5,
      period_start: "2024-01-01",
      period_end: "2024-01-31"
    }
  ]
}
```

### 自动进度追踪

系统会在以下情况自动更新进度：

```python
# 1. 完成练习时
StudyPlanService.auto_update_progress_on_practice(user_id)

# 2. 完成考试时
StudyPlanService.auto_update_progress_on_exam(user_id)

# 3. 累计学习时长时
StudyPlanService.auto_update_progress_on_study_duration(user_id, duration_minutes)
```

## 测试步骤

### 1. 运行数据库迁移

```bash
cd exam/backend
python migrate_study_plan_improvements.py
```

### 2. 启动后端

```bash
cd exam/backend
python run.py
```

### 3. 启动前端

```bash
cd exam/frontend
npm run dev
```

### 4. 测试场景

#### 场景1：创建包含多种目标的计划

1. 登录系统
2. 进入"学习计划"页面
3. 点击"创建计划"
4. 填写基本信息
5. 添加多个不同类型的目标：
   - 每日练习题数
   - 科目每日练习（选择科目）
   - 每日学习时长
   - 正确率目标
6. 提交创建

**预期结果**：
- 计划创建成功
- 状态显示为"进行中"（active）
- 所有目标正确显示，包括科目信息

#### 场景2：验证状态自动更新

1. 创建一个开始日期为今天、结束日期为明天的计划
2. 查看计划列表，状态应为"进行中"
3. 等待结束日期过后（或手动修改数据库中的 end_date）
4. 刷新计划列表

**预期结果**：
- 计划状态自动变为"已完成"（completed）

#### 场景3：测试科目特定目标

1. 创建包含"科目每日练习"目标的计划
2. 选择科目为"行测"
3. 设置目标值为 50 题
4. 提交创建

**预期结果**：
- 目标正确保存，包含科目信息
- 在计划详情中显示科目名称

## API 变更

### 创建计划 API

**请求示例**：
```json
POST /api/study-plans
{
  "name": "考研数学冲刺",
  "exam_type": "postgraduate",
  "start_date": "2024-01-01",
  "end_date": "2024-03-01",
  "goals": [
    {
      "goal_type": "subject_daily_practice",
      "subject": "math",
      "target_value": 30,
      "period_start": "2024-01-01",
      "period_end": "2024-03-01"
    },
    {
      "goal_type": "subject_accuracy_rate",
      "subject": "math",
      "target_value": 90,
      "period_start": "2024-01-01",
      "period_end": "2024-03-01"
    }
  ]
}
```

**响应示例**：
```json
{
  "success": true,
  "data": {
    "plan": {
      "id": 1,
      "name": "考研数学冲刺",
      "status": "active",
      "goals": [
        {
          "id": 1,
          "goal_type": "subject_daily_practice",
          "subject": "math",
          "target_value": 30,
          "current_value": 0,
          "progress_percentage": 0,
          "is_completed": false
        }
      ]
    }
  }
}
```

## 后续优化建议

### 1. 自动进度同步

在以下位置集成自动进度更新：

```python
# exam/backend/app/routes/practice.py
@practice_bp.route('/submit', methods=['POST'])
def submit_practice():
    # ... 提交练习逻辑 ...
    
    # 自动更新学习计划进度
    StudyPlanService.auto_update_progress_on_practice(current_user.id)
    
    return jsonify(...)

# exam/backend/app/routes/exams.py
@exams_bp.route('/submit', methods=['POST'])
def submit_exam():
    # ... 提交考试逻辑 ...
    
    # 自动更新学习计划进度
    StudyPlanService.auto_update_progress_on_exam(current_user.id)
    
    return jsonify(...)
```

### 2. 正确率目标追踪

实现基于实际练习记录的正确率计算：

```python
@staticmethod
def sync_accuracy_goals(user_id: int, subject: str = None):
    """同步正确率目标进度"""
    today = date.today()
    
    # 查询活跃的正确率目标
    goals = StudyGoal.query.join(StudyPlan).filter(
        StudyPlan.user_id == user_id,
        StudyPlan.status == 'active',
        StudyGoal.goal_type.in_(['accuracy_rate', 'subject_accuracy_rate']),
        StudyGoal.period_start <= today,
        StudyGoal.period_end >= today
    ).all()
    
    for goal in goals:
        # 计算实际正确率
        records = PracticeRecord.query.filter(
            PracticeRecord.user_id == user_id,
            PracticeRecord.created_at >= goal.period_start,
            PracticeRecord.created_at <= goal.period_end
        )
        
        if goal.subject:
            # 按科目过滤
            records = records.join(Question).filter(
                Question.subject == goal.subject
            )
        
        records = records.all()
        
        if records:
            correct_count = sum(1 for r in records if r.is_correct)
            accuracy = int((correct_count / len(records)) * 100)
            goal.current_value = accuracy
            
            if accuracy >= goal.target_value:
                goal.is_completed = True
                goal.completed_at = datetime.utcnow()
    
    db.session.commit()
```

### 3. 章节完成度追踪

需要先实现章节管理功能，然后追踪章节完成情况。

### 4. 学习报告增强

在学习报告中展示各类目标的完成情况和趋势分析。

## 文件清单

### 后端文件
- `exam/backend/app/models/study_plan.py` - 模型定义（已更新）
- `exam/backend/app/services/study_plan_service.py` - 业务逻辑（已更新）
- `exam/backend/app/routes/study_plans.py` - API路由（无需修改）
- `exam/backend/migrate_study_plan_improvements.py` - 数据库迁移脚本（新增）

### 前端文件
- `exam/frontend/src/components/StudyPlanForm.vue` - 创建表单（已更新）
- `exam/frontend/src/views/StudyPlans.vue` - 列表页面（无需修改）
- `exam/frontend/src/components/StudyPlanCard.vue` - 卡片组件（建议更新以显示科目）

## 总结

本次改进大幅提升了学习计划功能的实用性：

✅ **状态管理智能化** - 根据日期和完成情况自动更新状态
✅ **目标类型丰富** - 从 3 种扩展到 14 种，支持科目特定目标
✅ **数据结构完善** - 添加科目和完成时间字段
✅ **用户体验优化** - 表单智能化，自动调整输入范围和标签

下一步可以实现自动进度同步，让学习计划真正成为用户学习的智能助手。
