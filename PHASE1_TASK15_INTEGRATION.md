# Task 15 实施指南 - 系统集成

## 任务概述

**任务**: Task 15 - 系统集成  
**目标**: 将积分系统、成就系统、每日任务系统集成到现有功能中  
**状态**: 📋 实施指南

## 集成点概览

### 1. 练习系统集成

**触发时机**: 练习提交成功后

**需要集成的功能**:
- ✅ 积分奖励（练习得分 + 连续奖励）
- ✅ 成就检查（练习次数、答对题目数）
- ✅ 每日任务更新（完成练习、答对题目）
- ✅ 学习计划进度更新

**集成位置**: `exam/backend/app/routes/practice.py` 或 `exam/backend/app/services/practice_service.py`

**示例代码**:
```python
# 在练习提交成功后
from app.services.points_service import PointsService
from app.services.achievement_service import AchievementService
from app.services.daily_task_service import DailyTaskService

# 1. 奖励积分
points_result = PointsService.award_practice_points(
    user_id=user_id,
    practice_id=practice_id,
    score=score
)

# 2. 检查成就
newly_unlocked = AchievementService.check_achievements(
    user_id=user_id,
    event_type='practice_completed',
    event_data={'practice_id': practice_id, 'score': score}
)

# 3. 更新每日任务
DailyTaskService.update_task_progress(
    user_id=user_id,
    task_type='daily_practice',
    increment=1
)

# 4. 更新答对题目数（如果有正确题目数）
if correct_count > 0:
    DailyTaskService.update_task_progress(
        user_id=user_id,
        task_type='daily_questions',
        increment=correct_count
    )

# 5. 检查是否升级触发成就
if points_result.get('level_up'):
    AchievementService.check_achievements(
        user_id=user_id,
        event_type='level_up',
        event_data={'new_level': points_result['new_level']}
    )
```

### 2. 考试系统集成

**触发时机**: 考试提交成功后

**需要集成的功能**:
- ✅ 积分奖励（考试得分 × 2 + 连续奖励）
- ✅ 成就检查（考试次数、满分、高分）
- ✅ 学习计划进度更新

**集成位置**: `exam/backend/app/routes/exams.py` 或 `exam/backend/app/services/exam_service.py`

**示例代码**:
```python
# 在考试提交成功后
from app.services.points_service import PointsService
from app.services.achievement_service import AchievementService

# 1. 奖励积分
points_result = PointsService.award_exam_points(
    user_id=user_id,
    exam_id=exam_id,
    score=score
)

# 2. 检查成就
newly_unlocked = AchievementService.check_achievements(
    user_id=user_id,
    event_type='exam_completed',
    event_data={'exam_id': exam_id, 'score': score}
)

# 3. 检查是否升级触发成就
if points_result.get('level_up'):
    AchievementService.check_achievements(
        user_id=user_id,
        event_type='level_up',
        event_data={'new_level': points_result['new_level']}
    )
```

### 3. 笔记系统集成

**触发时机**: 笔记创建成功后

**需要集成的功能**:
- ✅ 每日任务更新（创建笔记）
- ✅ 成就检查（笔记数量）

**集成位置**: `exam/backend/app/routes/notes.py` 或 `exam/backend/app/services/note_service.py`

**示例代码**:
```python
# 在笔记创建成功后
from app.services.daily_task_service import DailyTaskService
from app.services.achievement_service import AchievementService

# 1. 更新每日任务
DailyTaskService.update_task_progress(
    user_id=user_id,
    task_type='daily_notes',
    increment=1
)

# 2. 检查成就
AchievementService.check_achievements(
    user_id=user_id,
    event_type='note_created',
    event_data={'note_id': note_id}
)
```

### 4. 学习计划系统集成

**触发时机**: 学习计划完成时

**需要集成的功能**:
- ✅ 成就检查（完成学习计划）

**集成位置**: `exam/backend/app/routes/study_plans.py` 或 `exam/backend/app/services/study_plan_service.py`

**示例代码**:
```python
# 在学习计划标记为完成后
from app.services.achievement_service import AchievementService

# 检查成就
AchievementService.check_achievements(
    user_id=user_id,
    event_type='plan_completed',
    event_data={'plan_id': plan_id}
)
```

### 5. 错题复习集成

**触发时机**: 错题复习完成后

**需要集成的功能**:
- ✅ 每日任务更新（复习错题）

**集成位置**: 错题复习相关路由

**示例代码**:
```python
# 在错题复习完成后
from app.services.daily_task_service import DailyTaskService

# 更新每日任务
DailyTaskService.update_task_progress(
    user_id=user_id,
    task_type='daily_review',
    increment=1
)
```

## 实施步骤

### Step 1: 检查现有路由

需要检查以下文件是否存在练习/考试提交的路由：
- `exam/backend/app/routes/practice.py`
- `exam/backend/app/routes/exams.py`

### Step 2: 添加集成代码

在相应的路由或服务中添加上述集成代码。

### Step 3: 测试集成

1. 测试练习提交是否触发积分、成就、任务更新
2. 测试考试提交是否触发积分、成就更新
3. 测试笔记创建是否触发任务更新
4. 测试升级是否触发成就检查

### Step 4: 配置定时任务

配置每日任务重置的定时任务：

```python
# 在 app/__init__.py 或单独的 scheduler.py 中
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.daily_task_service import DailyTaskService

def init_scheduler(app):
    """初始化定时任务"""
    scheduler = BackgroundScheduler()
    
    # 每天0:00重置每日任务
    scheduler.add_job(
        func=DailyTaskService.reset_daily_tasks,
        trigger='cron',
        hour=0,
        minute=0,
        id='reset_daily_tasks'
    )
    
    scheduler.start()
    
    # 确保应用关闭时停止调度器
    import atexit
    atexit.register(lambda: scheduler.shutdown())
    
    return scheduler
```

## 集成检查清单

### 积分系统集成
- [ ] 练习完成时奖励积分
- [ ] 考试完成时奖励积分（得分×2）
- [ ] 连续学习奖励计算正确
- [ ] 升级时触发成就检查

### 成就系统集成
- [ ] 练习完成时检查成就
- [ ] 考试完成时检查成就
- [ ] 升级时检查成就
- [ ] 笔记创建时检查成就
- [ ] 学习计划完成时检查成就

### 每日任务集成
- [ ] 练习完成时更新任务
- [ ] 答对题目时更新任务
- [ ] 笔记创建时更新任务
- [ ] 错题复习时更新任务
- [ ] 学习时长累计更新任务

### 定时任务
- [ ] 配置每日任务重置定时任务
- [ ] 测试定时任务执行

## 注意事项

1. **错误处理**: 集成代码应该有适当的错误处理，避免影响主要功能
2. **性能考虑**: 集成调用应该异步或快速完成，不影响用户体验
3. **事务管理**: 确保数据库事务正确处理
4. **日志记录**: 记录集成调用的结果，便于调试

## 示例：完整的练习提交集成

```python
@practice_bp.route('/submit', methods=['POST'])
@jwt_required()
def submit_practice():
    """提交练习"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # 1. 处理练习提交（原有逻辑）
        practice_id = data.get('practice_id')
        answers = data.get('answers')
        
        # 计算得分和正确题目数
        score, correct_count = calculate_score(answers)
        
        # 保存练习记录
        practice_record = save_practice_record(
            user_id=user_id,
            practice_id=practice_id,
            answers=answers,
            score=score
        )
        
        # 2. 集成：奖励积分
        try:
            points_result = PointsService.award_practice_points(
                user_id=user_id,
                practice_id=practice_id,
                score=score
            )
        except Exception as e:
            app.logger.error(f"Failed to award points: {e}")
            points_result = {}
        
        # 3. 集成：检查成就
        try:
            newly_unlocked = AchievementService.check_achievements(
                user_id=user_id,
                event_type='practice_completed',
                event_data={'practice_id': practice_id, 'score': score}
            )
            
            # 如果升级，再次检查成就
            if points_result.get('level_up'):
                level_achievements = AchievementService.check_achievements(
                    user_id=user_id,
                    event_type='level_up',
                    event_data={'new_level': points_result['new_level']}
                )
                newly_unlocked.extend(level_achievements)
        except Exception as e:
            app.logger.error(f"Failed to check achievements: {e}")
            newly_unlocked = []
        
        # 4. 集成：更新每日任务
        try:
            DailyTaskService.update_task_progress(
                user_id=user_id,
                task_type='daily_practice',
                increment=1
            )
            
            if correct_count > 0:
                DailyTaskService.update_task_progress(
                    user_id=user_id,
                    task_type='daily_questions',
                    increment=correct_count
                )
        except Exception as e:
            app.logger.error(f"Failed to update daily tasks: {e}")
        
        # 5. 返回结果
        return jsonify({
            'success': True,
            'data': {
                'practice_record': practice_record.to_dict(),
                'score': score,
                'correct_count': correct_count,
                'points_awarded': points_result.get('points_awarded', 0),
                'level_up': points_result.get('level_up', False),
                'new_level': points_result.get('new_level'),
                'newly_unlocked_achievements': newly_unlocked
            }
        }), 200
        
    except Exception as e:
        app.logger.error(f"Practice submission error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
```

## 总结

Task 15 的集成工作需要在现有的练习、考试、笔记等功能中添加调用积分、成就、每日任务服务的代码。由于这些是现有系统的修改，建议：

1. 先在测试环境中实施
2. 逐个功能点集成和测试
3. 确保错误处理完善，不影响主要功能
4. 记录详细的日志便于调试

**注意**: 由于需要修改现有的路由文件，建议在实际实施前备份相关文件。

---

**创建时间**: 2024-12-26  
**开发者**: Kiro AI Assistant
