# 清理考试会话指南

## 问题描述

当出现"已有进行中的考试"错误时，可以使用以下方法清理会话。

## 快速清理（推荐）

### 方法1：使用快速清理脚本

```bash
cd exam/backend
python quick_clear_sessions.py
```

这个脚本会：
1. 查找所有进行中的考试会话
2. 显示会话信息
3. 自动删除所有进行中的会话

### 方法2：使用交互式清理脚本

```bash
cd exam/backend
python clear_sessions.py
```

可选参数：
```bash
# 只清理特定用户的会话
python clear_sessions.py --user-id 1
```

这个脚本会：
1. 查找进行中的考试会话
2. 显示会话详情
3. 询问确认后删除

## 手动清理（数据库）

### 使用 SQLite

```bash
cd exam/backend
sqlite3 instance/exam.db

# 查看进行中的会话
SELECT * FROM exam_sessions WHERE status = 'in_progress';

# 删除所有进行中的会话
DELETE FROM exam_sessions WHERE status = 'in_progress';

# 退出
.quit
```

### 使用 Python Shell

```bash
cd exam/backend
python

>>> from app import create_app, db
>>> from app.models.exam import ExamSession
>>> app = create_app()
>>> with app.app_context():
...     sessions = ExamSession.query.filter_by(status='in_progress').all()
...     for s in sessions:
...         db.session.delete(s)
...     db.session.commit()
...     print(f"已删除 {len(sessions)} 个会话")
```

## 预防措施

### 1. 正常提交考试

确保用户完成考试后点击"提交试卷"按钮，这样会话状态会变为 `completed`。

### 2. 超时自动提交

系统会在考试时间到期时自动提交试卷。

### 3. 定期清理

可以设置定时任务清理超时但未提交的会话：

```python
# 清理超时的会话
from datetime import datetime
from app.models.exam import ExamSession

with app.app_context():
    now = datetime.utcnow()
    timeout_sessions = ExamSession.query.filter(
        ExamSession.status == 'in_progress',
        ExamSession.end_time < now
    ).all()
    
    for session in timeout_sessions:
        session.status = 'timeout'
    
    db.session.commit()
```

## 故障排查

### 问题1：500 错误

**症状**: 点击"开始考试"时出现 "Request failed with status code 500"

**原因**: 
- 后端 API 出错
- 数据库连接问题
- 模型序列化问题

**解决**:
1. 检查后端日志
2. 清理进行中的会话
3. 重启后端服务

### 问题2：无法删除会话

**症状**: 删除会话时出错

**原因**: 
- 外键约束
- 数据库锁定

**解决**:
```bash
# 先删除相关的考试结果
DELETE FROM exam_results WHERE session_id IN (
    SELECT id FROM exam_sessions WHERE status = 'in_progress'
);

# 再删除会话
DELETE FROM exam_sessions WHERE status = 'in_progress';
```

## 开发建议

### 1. 添加会话管理界面

为管理员提供一个界面来查看和管理所有考试会话。

### 2. 自动清理机制

实现后台任务定期清理超时的会话：

```python
# 使用 APScheduler
from apscheduler.schedulers.background import BackgroundScheduler

def cleanup_timeout_sessions():
    with app.app_context():
        now = datetime.utcnow()
        ExamSession.query.filter(
            ExamSession.status == 'in_progress',
            ExamSession.end_time < now
        ).update({'status': 'timeout'})
        db.session.commit()

scheduler = BackgroundScheduler()
scheduler.add_job(cleanup_timeout_sessions, 'interval', hours=1)
scheduler.start()
```

### 3. 会话恢复优化

- 在前端存储会话ID到 localStorage
- 页面加载时自动检测并恢复
- 提供"放弃考试"选项

## 相关文件

- `exam/backend/quick_clear_sessions.py` - 快速清理脚本
- `exam/backend/clear_sessions.py` - 交互式清理脚本
- `exam/backend/app/models/exam.py` - ExamSession 模型
- `exam/backend/app/routes/exams.py` - 考试路由
- `exam/backend/app/services/exam_service.py` - 考试服务

## 注意事项

⚠️ **警告**: 清理会话会导致用户丢失未提交的答案！

建议：
1. 在生产环境谨慎使用
2. 清理前备份数据库
3. 通知用户会话将被清理
4. 考虑实现"放弃考试"功能而不是直接删除

## 更新日志

- 2025-12-15: 创建清理脚本和文档
