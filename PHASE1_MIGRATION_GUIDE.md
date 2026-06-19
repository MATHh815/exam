# 第一阶段数据库迁移指南

## 概述

本指南说明如何执行第一阶段功能增强的数据库迁移。迁移将创建 10 个新表来支持学习计划、笔记和成就系统。

## 新增的数据表

### 学习计划模块
- **study_plans** - 学习计划主表
- **study_goals** - 学习目标表
- **study_reminders** - 学习提醒表

### 笔记模块
- **question_notes** - 题目笔记表
- **question_bookmarks** - 题目收藏表

### 成就模块
- **achievements** - 成就定义表
- **user_achievements** - 用户成就表
- **user_points** - 用户积分表
- **point_transactions** - 积分交易记录表
- **daily_tasks** - 每日任务表

## 迁移步骤

### 方法 1: 使用批处理脚本（推荐）

1. 进入后端目录：
```bash
cd exam/backend
```

2. 运行迁移脚本：
```bash
migrate_phase1.bat
```

3. 按照提示操作，脚本会自动：
   - 激活虚拟环境
   - 生成迁移脚本
   - 应用迁移到数据库

### 方法 2: 手动执行

1. 激活虚拟环境：
```bash
cd exam/backend
venv\Scripts\activate
```

2. 生成迁移脚本：
```bash
flask db migrate -m "Add Phase 1 enhancement models"
```

3. 检查生成的迁移文件：
   - 打开 `migrations/versions/` 目录
   - 查看最新的迁移文件
   - 确认包含所有 10 个新表的创建语句

4. 应用迁移：
```bash
flask db upgrade
```

## 验证迁移

运行验证脚本确保所有表都已正确创建：

```bash
python verify_phase1_migration.py
```

验证脚本会检查：
- ✓ 所有 10 个表是否存在
- ✓ 关键索引是否创建
- ✓ 唯一约束是否设置

## 预期输出

成功的迁移应该显示：

```
========================================
验证第一阶段数据库迁移
========================================

检查表是否存在:
------------------------------------------------------------
✓ study_plans              (学习计划)
✓ study_goals              (学习目标)
✓ study_reminders          (学习提醒)
✓ question_notes           (题目笔记)
✓ question_bookmarks       (题目收藏)
✓ achievements             (成就定义)
✓ user_achievements        (用户成就)
✓ user_points              (用户积分)
✓ point_transactions       (积分交易记录)
✓ daily_tasks              (每日任务)

========================================
✓ 所有表都已成功创建！
========================================
```

## 数据库结构说明

### 关键索引

1. **study_plans**
   - `user_id` - 用户查询索引
   - `is_deleted` - 软删除过滤索引

2. **question_notes**
   - `(user_id, question_id)` - 复合索引，优化查询性能

3. **user_points**
   - `user_id` - 唯一索引

4. **point_transactions**
   - `created_at` - 时间排序索引

### 唯一约束

1. **question_bookmarks**
   - `(user_id, question_id)` - 防止重复收藏

2. **user_achievements**
   - `(user_id, achievement_id)` - 防止重复获得成就

3. **daily_tasks**
   - `(user_id, task_date, task_type)` - 每天每种任务只能有一个

## 回滚迁移

如果需要回滚迁移：

```bash
flask db downgrade
```

**警告**: 回滚会删除所有新表及其数据！

## 故障排除

### 问题 1: 虚拟环境未激活

**错误信息**: `'flask' 不是内部或外部命令`

**解决方案**:
```bash
cd exam/backend
venv\Scripts\activate
```

### 问题 2: 迁移冲突

**错误信息**: `Target database is not up to date`

**解决方案**:
```bash
flask db stamp head
flask db migrate -m "Add Phase 1 enhancement models"
flask db upgrade
```

### 问题 3: 表已存在

**错误信息**: `Table 'study_plans' already exists`

**解决方案**:
1. 检查数据库中是否已有这些表
2. 如果是测试环境，可以删除数据库重新创建
3. 如果是生产环境，需要手动调整迁移脚本

## 下一步

迁移完成后，可以继续：

1. ✓ 任务 2.1-2.3 已完成（模型创建）
2. ✓ 任务 2.4 已完成（数据库迁移）
3. → 继续任务 3：实现学习计划管理系统

## 相关文件

- `backend/app/models/study_plan.py` - 学习计划模型
- `backend/app/models/note.py` - 笔记和收藏模型
- `backend/app/models/achievement.py` - 成就和积分模型
- `backend/migrate_phase1.bat` - 迁移批处理脚本
- `backend/verify_phase1_migration.py` - 验证脚本

## 技术细节

### 软删除实现

部分表使用软删除机制（`is_deleted` 字段）：
- `study_plans`
- `question_notes`

查询时需要过滤 `is_deleted=False` 的记录。

### JSON 字段

以下表使用 JSON 字段存储结构化数据：
- `achievements.criteria` - 成就触发条件
- `question_bookmarks.tags` - 收藏标签

### 时间戳

所有表都包含时间戳字段：
- `created_at` - 创建时间（自动设置）
- `updated_at` - 更新时间（自动更新，部分表）

## 参考资料

- [Flask-Migrate 文档](https://flask-migrate.readthedocs.io/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [设计文档](../.kiro/specs/exam-enhancements-phase1/design.md)
- [需求文档](../.kiro/specs/exam-enhancements-phase1/requirements.md)
