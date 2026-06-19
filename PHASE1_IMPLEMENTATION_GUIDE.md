# 第一阶段实施指南

## 📋 概述

本文档提供第一阶段功能开发的详细实施指南，包括开发顺序、技术方案、数据库设计和 API 设计。

## 🎯 开发目标

完成以下三个核心功能模块：
1. 学习计划管理系统
2. 笔记与标注系统  
3. 成就与激励系统

**预计时间**: 4-6 周  
**团队规模**: 2-3 名开发人员

---

## 📅 开发计划

### Week 1-2: 学习计划管理系统

**任务清单**:
- [ ] 数据库模型设计和迁移
- [ ] 后端 API 开发（CRUD）
- [ ] 学习目标追踪逻辑
- [ ] 提醒系统基础架构
- [ ] 前端页面开发
- [ ] 单元测试和集成测试

### Week 3-4: 笔记与标注系统

**任务清单**:
- [ ] 数据库模型设计和迁移
- [ ] 后端 API 开发
- [ ] Markdown 编辑器集成
- [ ] 笔记搜索功能
- [ ] 导出功能实现
- [ ] 前端组件开发
- [ ] 测试

### Week 5-6: 成就与激励系统

**任务清单**:
- [ ] 数据库模型设计和迁移
- [ ] 积分和等级计算逻辑
- [ ] 成就触发系统
- [ ] 每日任务生成器
- [ ] 后端 API 开发
- [ ] 前端展示组件
- [ ] 测试和优化

---


## 🗄️ 数据库设计

### 1. 学习计划相关表

#### study_plans (学习计划表)
```sql
CREATE TABLE study_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    exam_type VARCHAR(50) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'active',  -- active, completed, paused
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

#### study_goals (学习目标表)
```sql
CREATE TABLE study_goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id INTEGER NOT NULL,
    goal_type VARCHAR(50) NOT NULL,  -- daily_practice, weekly_practice, daily_duration
    target_value INTEGER NOT NULL,
    current_value INTEGER DEFAULT 0,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plan_id) REFERENCES study_plans(id)
);
```

#### study_reminders (学习提醒表)
```sql
CREATE TABLE study_reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    plan_id INTEGER,
    reminder_time TIME NOT NULL,
    frequency VARCHAR(20) DEFAULT 'daily',  -- daily, weekly, custom
    is_enabled BOOLEAN DEFAULT TRUE,
    last_sent_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (plan_id) REFERENCES study_plans(id)
);
```

### 2. 笔记相关表

#### question_notes (题目笔记表)
```sql
CREATE TABLE question_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (question_id) REFERENCES questions(id)
);
```

#### question_bookmarks (题目收藏表)
```sql
CREATE TABLE question_bookmarks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    tags JSON,  -- ["重点", "易错"]
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, question_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (question_id) REFERENCES questions(id)
);
```

### 3. 成就系统相关表

#### achievements (成就定义表)
```sql
CREATE TABLE achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    icon VARCHAR(255),
    category VARCHAR(50),  -- learning, streak, milestone
    criteria JSON NOT NULL,  -- {"type": "practice_count", "value": 100}
    points_reward INTEGER DEFAULT 0,
    tier INTEGER DEFAULT 1,  -- 1, 2, 3 (bronze, silver, gold)
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### user_achievements (用户成就表)
```sql
CREATE TABLE user_achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    achievement_id INTEGER NOT NULL,
    unlocked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    progress INTEGER DEFAULT 0,
    UNIQUE(user_id, achievement_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (achievement_id) REFERENCES achievements(id)
);
```

#### user_points (用户积分表)
```sql
CREATE TABLE user_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    total_points INTEGER DEFAULT 0,
    current_level INTEGER DEFAULT 1,
    streak_days INTEGER DEFAULT 0,
    last_activity_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

#### point_transactions (积分交易记录表)
```sql
CREATE TABLE point_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    points INTEGER NOT NULL,
    reason VARCHAR(100) NOT NULL,
    reference_type VARCHAR(50),  -- practice, exam, achievement, daily_task
    reference_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

#### daily_tasks (每日任务表)
```sql
CREATE TABLE daily_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    task_date DATE NOT NULL,
    task_type VARCHAR(50) NOT NULL,
    task_description TEXT NOT NULL,
    target_value INTEGER NOT NULL,
    current_value INTEGER DEFAULT 0,
    points_reward INTEGER DEFAULT 0,
    is_completed BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, task_date, task_type),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---


## 🔌 API 设计

### 学习计划 API

#### 创建学习计划
```
POST /api/study-plans
Authorization: Bearer <token>

Request:
{
  "name": "2024国考冲刺计划",
  "description": "最后30天冲刺",
  "exam_type": "civil_service",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "daily_goals": {
    "practice_count": 50,
    "study_duration": 120
  }
}

Response: 201 Created
{
  "success": true,
  "data": {
    "plan": { ... }
  }
}
```

#### 获取学习计划列表
```
GET /api/study-plans?status=active
Authorization: Bearer <token>

Response: 200 OK
{
  "success": true,
  "data": {
    "plans": [ ... ]
  }
}
```

#### 更新学习计划进度
```
PUT /api/study-plans/:id/progress
Authorization: Bearer <token>

Request:
{
  "goal_type": "daily_practice",
  "increment": 1
}

Response: 200 OK
```

### 笔记 API

#### 创建笔记
```
POST /api/notes
Authorization: Bearer <token>

Request:
{
  "question_id": 123,
  "content": "## 解题思路\n\n这道题考察..."
}

Response: 201 Created
```

#### 搜索笔记
```
GET /api/notes/search?keyword=数量关系&subject=行测
Authorization: Bearer <token>

Response: 200 OK
{
  "success": true,
  "data": {
    "notes": [ ... ],
    "total": 15
  }
}
```

#### 导出笔记
```
POST /api/notes/export
Authorization: Bearer <token>

Request:
{
  "format": "pdf",
  "subject": "行测",
  "date_range": {
    "start": "2024-01-01",
    "end": "2024-01-31"
  }
}

Response: 200 OK
{
  "success": true,
  "data": {
    "download_url": "https://...",
    "expires_at": "2024-01-02T00:00:00Z"
  }
}
```

### 收藏 API

#### 收藏题目
```
POST /api/bookmarks
Authorization: Bearer <token>

Request:
{
  "question_id": 123,
  "tags": ["重点", "易错"]
}

Response: 201 Created
```

#### 获取收藏列表
```
GET /api/bookmarks?tags=重点&subject=行测
Authorization: Bearer <token>

Response: 200 OK
```

### 成就 API

#### 获取用户成就
```
GET /api/achievements
Authorization: Bearer <token>

Response: 200 OK
{
  "success": true,
  "data": {
    "earned": [ ... ],
    "in_progress": [ ... ],
    "locked": [ ... ]
  }
}
```

#### 获取积分信息
```
GET /api/points
Authorization: Bearer <token>

Response: 200 OK
{
  "success": true,
  "data": {
    "total_points": 1250,
    "current_level": 3,
    "points_to_next_level": 350,
    "streak_days": 7
  }
}
```

#### 获取每日任务
```
GET /api/daily-tasks
Authorization: Bearer <token>

Response: 200 OK
{
  "success": true,
  "data": {
    "tasks": [
      {
        "id": 1,
        "description": "完成10道练习题",
        "progress": 5,
        "target": 10,
        "points_reward": 50,
        "is_completed": false
      }
    ]
  }
}
```

---


## 💻 技术实现要点

### 1. 学习提醒系统

**方案选择**: 使用 APScheduler 实现定时任务

```python
# backend/app/services/reminder_service.py
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, time

class ReminderService:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
    
    def schedule_reminder(self, user_id, reminder_time):
        """安排学习提醒"""
        job_id = f"reminder_{user_id}"
        self.scheduler.add_job(
            func=self.send_reminder,
            trigger='cron',
            hour=reminder_time.hour,
            minute=reminder_time.minute,
            id=job_id,
            replace_existing=True,
            args=[user_id]
        )
    
    def send_reminder(self, user_id):
        """发送提醒通知"""
        # 实现通知逻辑
        pass
```

### 2. 积分计算系统

**等级计算公式**: `level = floor(sqrt(total_points / 100))`

```python
# backend/app/services/points_service.py
import math

class PointsService:
    @staticmethod
    def calculate_level(total_points):
        """计算用户等级"""
        return math.floor(math.sqrt(total_points / 100))
    
    @staticmethod
    def points_to_next_level(current_points):
        """计算到下一级所需积分"""
        current_level = PointsService.calculate_level(current_points)
        next_level_points = (current_level + 1) ** 2 * 100
        return next_level_points - current_points
    
    def award_points(self, user_id, points, reason, reference_type=None, reference_id=None):
        """奖励积分"""
        # 1. 创建积分交易记录
        # 2. 更新用户总积分
        # 3. 检查是否升级
        # 4. 触发升级成就
        pass
```

### 3. 成就触发系统

**事件驱动架构**:

```python
# backend/app/services/achievement_service.py

class AchievementService:
    def check_achievements(self, user_id, event_type, event_data):
        """检查并触发成就"""
        achievements = Achievement.query.filter_by(
            category=event_type,
            is_active=True
        ).all()
        
        for achievement in achievements:
            if self._check_criteria(user_id, achievement.criteria, event_data):
                self._unlock_achievement(user_id, achievement.id)
    
    def _check_criteria(self, user_id, criteria, event_data):
        """检查成就条件"""
        # 根据 criteria 类型判断是否满足条件
        pass
    
    def _unlock_achievement(self, user_id, achievement_id):
        """解锁成就"""
        # 1. 创建用户成就记录
        # 2. 奖励积分
        # 3. 发送通知
        pass
```

### 4. 每日任务生成器

**定时任务**: 每天凌晨 0:00 生成任务

```python
# backend/app/services/daily_task_service.py

class DailyTaskService:
    TASK_TEMPLATES = [
        {
            "type": "practice_count",
            "description": "完成{value}道练习题",
            "target": 10,
            "points": 50
        },
        {
            "type": "study_duration",
            "description": "学习{value}分钟",
            "target": 30,
            "points": 30
        },
        {
            "type": "exam_count",
            "description": "完成{value}次模拟考试",
            "target": 1,
            "points": 100
        }
    ]
    
    def generate_daily_tasks(self, user_id):
        """为用户生成每日任务"""
        today = date.today()
        
        for template in self.TASK_TEMPLATES:
            task = DailyTask(
                user_id=user_id,
                task_date=today,
                task_type=template["type"],
                task_description=template["description"].format(value=template["target"]),
                target_value=template["target"],
                points_reward=template["points"]
            )
            db.session.add(task)
        
        db.session.commit()
```

### 5. 笔记导出功能

**使用 ReportLab 生成 PDF**:

```python
# backend/app/services/export_service.py
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

class ExportService:
    def export_notes_to_pdf(self, user_id, filters):
        """导出笔记为 PDF"""
        notes = self._get_filtered_notes(user_id, filters)
        
        # 创建 PDF
        filename = f"notes_{user_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
        filepath = os.path.join(EXPORT_DIR, filename)
        
        c = canvas.Canvas(filepath, pagesize=A4)
        
        # 添加内容
        for note in notes:
            self._add_note_to_pdf(c, note)
        
        c.save()
        
        return filepath
```

---


## 🎨 前端组件设计

### 1. 学习计划组件

#### StudyPlanCard.vue
```vue
<template>
  <el-card class="study-plan-card">
    <div class="plan-header">
      <h3>{{ plan.name }}</h3>
      <el-tag :type="statusType">{{ statusText }}</el-tag>
    </div>
    
    <div class="plan-progress">
      <el-progress 
        :percentage="progressPercentage" 
        :status="progressStatus"
      />
      <span class="progress-text">
        {{ plan.current_value }} / {{ plan.target_value }}
      </span>
    </div>
    
    <div class="plan-goals">
      <div v-for="goal in plan.goals" :key="goal.id" class="goal-item">
        <span>{{ goal.description }}</span>
        <el-progress 
          :percentage="calculateGoalProgress(goal)" 
          :width="50"
          type="circle"
        />
      </div>
    </div>
  </el-card>
</template>
```

#### StudyPlanForm.vue
```vue
<template>
  <el-form :model="form" :rules="rules" ref="formRef">
    <el-form-item label="计划名称" prop="name">
      <el-input v-model="form.name" />
    </el-form-item>
    
    <el-form-item label="考试类型" prop="exam_type">
      <el-select v-model="form.exam_type">
        <el-option label="公务员考试" value="civil_service" />
        <el-option label="研究生考试" value="postgraduate" />
        <el-option label="事业编考试" value="public_institution" />
      </el-select>
    </el-form-item>
    
    <el-form-item label="时间范围" prop="dateRange">
      <el-date-picker
        v-model="form.dateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
      />
    </el-form-item>
    
    <el-form-item label="每日目标">
      <el-input-number v-model="form.daily_practice_count" :min="1" />
      <span>道题</span>
    </el-form-item>
  </el-form>
</template>
```

### 2. 笔记组件

#### NoteEditor.vue
```vue
<template>
  <div class="note-editor">
    <el-input
      v-model="content"
      type="textarea"
      :rows="10"
      placeholder="支持 Markdown 格式..."
    />
    
    <div class="editor-toolbar">
      <el-button @click="preview = !preview">
        {{ preview ? '编辑' : '预览' }}
      </el-button>
      <el-button type="primary" @click="saveNote">保存</el-button>
    </div>
    
    <div v-if="preview" class="markdown-preview" v-html="renderedContent" />
  </div>
</template>

<script setup>
import { marked } from 'marked'
import { computed } from 'vue'

const renderedContent = computed(() => {
  return marked(content.value)
})
</script>
```

### 3. 成就组件

#### AchievementWall.vue
```vue
<template>
  <div class="achievement-wall">
    <div class="wall-header">
      <h2>成就墙</h2>
      <div class="stats">
        <span>已解锁: {{ earnedCount }}</span>
        <span>总计: {{ totalCount }}</span>
      </div>
    </div>
    
    <div class="achievement-grid">
      <div 
        v-for="achievement in achievements" 
        :key="achievement.id"
        class="achievement-item"
        :class="{ locked: !achievement.unlocked }"
      >
        <img :src="achievement.icon" :alt="achievement.name" />
        <div class="achievement-info">
          <h4>{{ achievement.name }}</h4>
          <p>{{ achievement.description }}</p>
          <el-progress 
            v-if="!achievement.unlocked"
            :percentage="achievement.progress"
          />
        </div>
      </div>
    </div>
  </div>
</template>
```

#### PointsDisplay.vue
```vue
<template>
  <div class="points-display">
    <div class="level-badge">
      <span class="level-number">{{ level }}</span>
      <span class="level-text">级</span>
    </div>
    
    <div class="points-info">
      <div class="total-points">
        <span class="label">总积分</span>
        <span class="value">{{ totalPoints }}</span>
      </div>
      
      <el-progress 
        :percentage="levelProgress"
        :format="() => `${pointsToNextLevel} 分升级`"
      />
    </div>
    
    <div class="streak-info">
      <i class="el-icon-trophy" />
      <span>连续学习 {{ streakDays }} 天</span>
    </div>
  </div>
</template>
```

---


## 🧪 测试策略

### 1. 单元测试

#### 测试积分计算
```python
# backend/tests/test_points_service.py
import pytest
from app.services.points_service import PointsService

def test_calculate_level():
    """测试等级计算"""
    assert PointsService.calculate_level(0) == 0
    assert PointsService.calculate_level(100) == 1
    assert PointsService.calculate_level(400) == 2
    assert PointsService.calculate_level(900) == 3

def test_points_to_next_level():
    """测试升级所需积分"""
    assert PointsService.points_to_next_level(0) == 100
    assert PointsService.points_to_next_level(100) == 300
    assert PointsService.points_to_next_level(400) == 500
```

#### 测试成就触发
```python
# backend/tests/test_achievement_service.py
def test_unlock_achievement(client, auth_headers):
    """测试成就解锁"""
    # 创建测试成就
    achievement = Achievement(
        name="初学者",
        criteria={"type": "practice_count", "value": 10}
    )
    db.session.add(achievement)
    db.session.commit()
    
    # 模拟完成10道题
    service = AchievementService()
    service.check_achievements(
        user_id=1,
        event_type="practice",
        event_data={"total_count": 10}
    )
    
    # 验证成就已解锁
    user_achievement = UserAchievement.query.filter_by(
        user_id=1,
        achievement_id=achievement.id
    ).first()
    
    assert user_achievement is not None
    assert user_achievement.unlocked_at is not None
```

### 2. 集成测试

#### 测试学习计划流程
```python
def test_study_plan_workflow(client, auth_headers):
    """测试完整的学习计划流程"""
    # 1. 创建学习计划
    response = client.post('/api/study-plans', 
        headers=auth_headers,
        json={
            "name": "测试计划",
            "exam_type": "civil_service",
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
            "daily_goals": {"practice_count": 10}
        }
    )
    assert response.status_code == 201
    plan_id = response.json['data']['plan']['id']
    
    # 2. 更新进度
    response = client.put(f'/api/study-plans/{plan_id}/progress',
        headers=auth_headers,
        json={"goal_type": "daily_practice", "increment": 5}
    )
    assert response.status_code == 200
    
    # 3. 查看进度
    response = client.get(f'/api/study-plans/{plan_id}',
        headers=auth_headers
    )
    assert response.json['data']['plan']['current_value'] == 5
```

### 3. 性能测试

```python
# backend/tests/test_performance.py
import time

def test_api_response_time(client, auth_headers):
    """测试 API 响应时间"""
    start = time.time()
    response = client.get('/api/study-plans', headers=auth_headers)
    duration = time.time() - start
    
    assert response.status_code == 200
    assert duration < 0.2  # 应在 200ms 内响应
```

---


## 📦 依赖包

### 后端新增依赖

```txt
# requirements.txt 新增内容
APScheduler==3.10.4          # 定时任务
reportlab==4.0.7             # PDF 生成
markdown==3.5.1              # Markdown 解析
python-dateutil==2.8.2       # 日期处理
```

### 前端新增依赖

```json
// package.json 新增内容
{
  "dependencies": {
    "marked": "^11.0.0",           // Markdown 渲染
    "dompurify": "^3.0.6",         // XSS 防护
    "vue-cal": "^4.9.0"            // 日历组件
  }
}
```

---

## 🚀 部署清单

### 数据库迁移

```bash
# 1. 创建迁移文件
flask db migrate -m "Add phase 1 tables"

# 2. 执行迁移
flask db upgrade

# 3. 初始化成就数据
python scripts/init_achievements.py
```

### 环境变量配置

```bash
# .env 新增配置
REMINDER_ENABLED=true
EXPORT_DIR=/path/to/exports
MAX_EXPORT_SIZE=10485760  # 10MB
```

### 定时任务启动

```python
# backend/run.py 修改
from app.services.reminder_service import ReminderService
from app.services.daily_task_service import DailyTaskService

# 启动提醒服务
reminder_service = ReminderService()

# 启动每日任务生成器
task_service = DailyTaskService()
task_service.start_scheduler()
```

---

## ✅ 验收标准

### 功能验收

- [ ] 用户可以创建、编辑、删除学习计划
- [ ] 学习进度自动更新并正确显示
- [ ] 学习提醒按时发送
- [ ] 用户可以添加、编辑、删除笔记
- [ ] 笔记支持 Markdown 格式
- [ ] 笔记搜索功能正常
- [ ] 笔记可以导出为 PDF
- [ ] 用户可以收藏和取消收藏题目
- [ ] 成就系统正确触发和解锁
- [ ] 积分正确计算和累加
- [ ] 等级正确升级
- [ ] 每日任务每天生成并可完成

### 性能验收

- [ ] 所有 API 响应时间 < 500ms
- [ ] 笔记搜索响应时间 < 500ms
- [ ] PDF 导出在 2 秒内完成（100 条笔记以内）
- [ ] 数据库查询使用索引优化

### 安全验收

- [ ] 所有 API 需要身份验证
- [ ] 用户只能访问自己的数据
- [ ] 输入验证完整
- [ ] XSS 防护到位
- [ ] SQL 注入防护（使用 ORM）

---

## 📞 技术支持

如有问题，请联系：
- 后端负责人：[姓名]
- 前端负责人：[姓名]
- 项目经理：[姓名]

---

**文档版本**: 1.0  
**最后更新**: 2024-12-26  
**下一次评审**: 开发开始后第 2 周
