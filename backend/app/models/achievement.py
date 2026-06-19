"""成就和积分模型"""
from datetime import datetime
from app import db


class Achievement(db.Model):
    """成就定义模型
    
    存储系统中所有可获得的成就
    """
    __tablename__ = 'achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(255))
    category = db.Column(db.String(50), index=True)  # learning, streak, milestone
    criteria = db.Column(db.JSON, nullable=False)  # {"type": "practice_count", "value": 100}
    points_reward = db.Column(db.Integer, default=0)
    tier = db.Column(db.Integer, default=1, index=True)  # 1, 2, 3 (bronze, silver, gold)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Achievement {self.name}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'category': self.category,
            'criteria': self.criteria,
            'points_reward': self.points_reward,
            'tier': self.tier,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class UserAchievement(db.Model):
    """用户成就模型
    
    存储用户获得的成就
    """
    __tablename__ = 'user_achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id'), nullable=False, index=True)
    unlocked_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    progress = db.Column(db.Integer, default=0)
    
    user = db.relationship('User', backref='user_achievements')
    achievement = db.relationship('Achievement', backref='user_achievements')
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'achievement_id', name='uq_user_achievement'),
    )
    
    def __repr__(self):
        return f'<UserAchievement user={self.user_id} achievement={self.achievement_id}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'achievement_id': self.achievement_id,
            'unlocked_at': self.unlocked_at.isoformat() if self.unlocked_at else None,
            'progress': self.progress
        }


class UserPoints(db.Model):
    """用户积分模型
    
    存储用户的积分和等级信息
    """
    __tablename__ = 'user_points'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True, index=True)
    total_points = db.Column(db.Integer, default=0)
    current_level = db.Column(db.Integer, default=1, index=True)
    streak_days = db.Column(db.Integer, default=0)
    last_activity_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('points', uselist=False))
    
    def __repr__(self):
        return f'<UserPoints user={self.user_id} points={self.total_points}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'total_points': self.total_points,
            'current_level': self.current_level,
            'streak_days': self.streak_days,
            'last_activity_date': self.last_activity_date.isoformat() if self.last_activity_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class PointTransaction(db.Model):
    """积分交易记录模型
    
    存储用户积分的变动历史
    """
    __tablename__ = 'point_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    points = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(100), nullable=False)
    reference_type = db.Column(db.String(50))  # practice, exam, achievement, daily_task
    reference_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    user = db.relationship('User', backref='point_transactions')
    
    def __repr__(self):
        return f'<PointTransaction user={self.user_id} points={self.points}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'points': self.points,
            'reason': self.reason,
            'reference_type': self.reference_type,
            'reference_id': self.reference_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class DailyTask(db.Model):
    """每日任务模型
    
    存储用户的每日任务
    """
    __tablename__ = 'daily_tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    task_date = db.Column(db.Date, nullable=False, index=True)
    task_type = db.Column(db.String(50), nullable=False)
    task_description = db.Column(db.Text, nullable=False)
    target_value = db.Column(db.Integer, nullable=False)
    current_value = db.Column(db.Integer, default=0)
    points_reward = db.Column(db.Integer, default=0)
    is_completed = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='daily_tasks')
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'task_date', 'task_type', name='uq_user_task_date'),
    )
    
    def __repr__(self):
        return f'<DailyTask user={self.user_id} type={self.task_type}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'task_date': self.task_date.isoformat() if self.task_date else None,
            'task_type': self.task_type,
            'task_description': self.task_description,
            'target_value': self.target_value,
            'current_value': self.current_value,
            'points_reward': self.points_reward,
            'is_completed': self.is_completed,
            'progress_percentage': round((self.current_value / self.target_value * 100) if self.target_value > 0 else 0, 2),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
