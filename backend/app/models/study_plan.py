"""学习计划模型"""
from datetime import datetime
from app import db


class StudyPlan(db.Model):
    """学习计划模型
    
    存储用户创建的学习计划信息
    """
    __tablename__ = 'study_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    exam_type = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='active', index=True)  # active, completed, paused
    is_deleted = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref='study_plans')
    goals = db.relationship('StudyGoal', backref='plan', cascade='all, delete-orphan')
    reminders = db.relationship('StudyReminder', backref='plan')
    
    def __repr__(self):
        return f'<StudyPlan {self.name}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'exam_type': self.exam_type,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'is_deleted': self.is_deleted,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'goals': [goal.to_dict() for goal in self.goals] if self.goals else []
        }


class StudyGoal(db.Model):
    """学习目标模型
    
    存储学习计划中的具体目标
    """
    __tablename__ = 'study_goals'
    
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('study_plans.id'), nullable=False, index=True)
    goal_type = db.Column(db.String(50), nullable=False)  # daily_practice, weekly_practice, daily_duration, etc.
    subject = db.Column(db.String(50))  # 科目（用于科目特定目标）
    target_value = db.Column(db.Integer, nullable=False)
    current_value = db.Column(db.Integer, default=0)
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    is_completed = db.Column(db.Boolean, default=False, index=True)
    completed_at = db.Column(db.DateTime)  # 完成时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<StudyGoal {self.goal_type}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'plan_id': self.plan_id,
            'goal_type': self.goal_type,
            'subject': self.subject,
            'target_value': self.target_value,
            'current_value': self.current_value,
            'period_start': self.period_start.isoformat() if self.period_start else None,
            'period_end': self.period_end.isoformat() if self.period_end else None,
            'is_completed': self.is_completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'progress_percentage': round((self.current_value / self.target_value * 100) if self.target_value > 0 else 0, 2),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class StudyReminder(db.Model):
    """学习提醒模型
    
    存储用户设置的学习提醒
    """
    __tablename__ = 'study_reminders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('study_plans.id'), index=True)
    reminder_time = db.Column(db.Time, nullable=False)
    frequency = db.Column(db.String(20), default='daily')  # daily, weekly, custom
    is_enabled = db.Column(db.Boolean, default=True, index=True)
    last_sent_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='reminders')
    
    def __repr__(self):
        return f'<StudyReminder {self.reminder_time}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan_id': self.plan_id,
            'reminder_time': self.reminder_time.isoformat() if self.reminder_time else None,
            'frequency': self.frequency,
            'is_enabled': self.is_enabled,
            'last_sent_at': self.last_sent_at.isoformat() if self.last_sent_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
