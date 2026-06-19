# 第一阶段快速开始指南

## 🎯 立即开始

本文档帮助你快速开始第一阶段的开发工作。

---

## 📋 开发前准备

### 1. 阅读文档

请按顺序阅读以下文档：

1. ✅ [功能路线图](FEATURE_ROADMAP.md) - 了解整体规划
2. ✅ [需求文档](.kiro/specs/exam-enhancements-phase1/requirements.md) - 详细需求
3. ✅ [实施指南](PHASE1_IMPLEMENTATION_GUIDE.md) - 技术方案
4. ✅ 本文档 - 快速开始

### 2. 环境准备

确保你的开发环境已经搭建好：

```bash
# 检查 Python 版本
python --version  # 应该是 3.9+

# 检查 Node.js 版本
node --version    # 应该是 16+

# 激活虚拟环境
cd exam/backend
source venv/bin/activate  # Windows: venv\Scripts\activate

# 确认依赖已安装
pip list | grep Flask
npm list --depth=0
```

### 3. 创建开发分支

```bash
# 从 main 分支创建开发分支
git checkout main
git pull origin main
git checkout -b feature/phase1-enhancements

# 或者为每个模块创建独立分支
git checkout -b feature/study-plan-system
git checkout -b feature/note-system
git checkout -b feature/achievement-system
```

---

## 🚀 开始开发

### 方式一：使用 Kiro Spec 工作流（推荐）

Kiro 可以帮助你按照 spec 逐步实现功能。

1. **查看 spec 文档**
```bash
# 需求文档位置
.kiro/specs/exam-enhancements-phase1/requirements.md
```

2. **让 Kiro 创建设计文档**

在 Kiro 中输入：
```
请基于 .kiro/specs/exam-enhancements-phase1/requirements.md 创建设计文档
```

3. **让 Kiro 创建任务列表**

设计文档完成后：
```
请基于设计文档创建任务列表
```

4. **开始执行任务**

任务列表创建后：
```
请执行第一个任务
```

### 方式二：手动开发

如果你想手动开发，按照以下顺序进行：

#### Week 1: 学习计划系统 - 数据库

1. **创建数据模型**

```bash
# 创建模型文件
touch exam/backend/app/models/study_plan.py
```

在文件中添加：
```python
# exam/backend/app/models/study_plan.py
from datetime import datetime
from app import db

class StudyPlan(db.Model):
    __tablename__ = 'study_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    exam_type = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='active')
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref='study_plans')
    goals = db.relationship('StudyGoal', backref='plan', cascade='all, delete-orphan')
```

2. **创建数据库迁移**

```bash
cd exam/backend
flask db migrate -m "Add study plan tables"
flask db upgrade
```

3. **测试模型**

```bash
python
>>> from app import db
>>> from app.models.study_plan import StudyPlan
>>> # 测试创建
```

#### Week 1: 学习计划系统 - API

1. **创建服务层**

```bash
touch exam/backend/app/services/study_plan_service.py
```

2. **创建路由**

```bash
touch exam/backend/app/routes/study_plans.py
```

3. **注册路由**

在 `exam/backend/app/__init__.py` 中注册新路由。

4. **测试 API**

```bash
# 启动服务器
python run.py

# 在另一个终端测试
curl -X POST http://localhost:5000/api/study-plans \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"测试计划","exam_type":"civil_service",...}'
```

---

## 📝 开发检查清单

### 每个功能模块完成后检查：

- [ ] 数据模型已创建并迁移
- [ ] 服务层逻辑已实现
- [ ] API 路由已创建
- [ ] 单元测试已编写并通过
- [ ] API 文档已更新
- [ ] 前端组件已实现
- [ ] 集成测试已通过
- [ ] 代码已提交到 Git

### 代码质量检查：

```bash
# 后端代码检查
cd exam/backend
black app/                    # 格式化
flake8 app/                   # 代码检查
pytest tests/                 # 运行测试

# 前端代码检查
cd exam/frontend
npm run lint                  # 代码检查
npm run test                  # 运行测试
```

---

## 🐛 常见问题

### 问题 1: 数据库迁移失败

```bash
# 解决方案：删除迁移并重新创建
rm -rf migrations/
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### 问题 2: 导入错误

确保在 `app/__init__.py` 中导入了新模型：

```python
from app.models.study_plan import StudyPlan, StudyGoal
```

### 问题 3: API 404 错误

检查路由是否正确注册：

```python
# app/__init__.py
from app.routes import study_plans
app.register_blueprint(study_plans.bp)
```

---

## 📚 参考资源

- [Flask 文档](https://flask.palletsprojects.com/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [Vue 3 文档](https://vuejs.org/)
- [Element Plus 文档](https://element-plus.org/)

---

## 💡 开发建议

1. **小步快跑**: 每完成一个小功能就提交代码
2. **测试驱动**: 先写测试，再写实现
3. **文档同步**: 及时更新 API 文档
4. **代码审查**: 定期进行代码审查
5. **性能监控**: 关注 API 响应时间

---

## 🎉 准备好了吗？

现在你可以开始开发了！建议从最简单的功能开始：

**推荐开发顺序**:
1. 学习计划基础 CRUD
2. 学习目标追踪
3. 笔记基础功能
4. 积分系统
5. 成就系统
6. 高级功能（提醒、导出等）

**开始第一个任务**:
```
创建 StudyPlan 数据模型
```

祝开发顺利！🚀
