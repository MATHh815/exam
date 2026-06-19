"""
番茄钟模型
"""
from datetime import datetime
from app import db

class PomodoroSession(db.Model):
    """番茄钟会话"""
    __tablename__ = 'pomodoro_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 会话信息
    duration = db.Column(db.Integer, default=25)  # 时长（分钟）
    session_type = db.Column(db.String(20), default='focus')  # focus/short_break/long_break
    
    # 状态
    status = db.Column(db.String(20), default='completed')  # completed/interrupted
    
    # 关联信息
    subject = db.Column(db.String(100))  # 学习科目
    notes = db.Column(db.Text)  # 备注
    
    # 积分奖励
    points_earned = db.Column(db.Integer, default=0)
    
    # 时间戳
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref=db.backref('pomodoro_sessions', lazy='dynamic'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'duration': self.duration,
            'session_type': self.session_type,
            'status': self.status,
            'subject': self.subject,
            'notes': self.notes,
            'points_earned': self.points_earned,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class PomodoroStats(db.Model):
    """番茄钟统计"""
    __tablename__ = 'pomodoro_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    
    # 统计数据
    total_sessions = db.Column(db.Integer, default=0)  # 总会话数
    total_focus_time = db.Column(db.Integer, default=0)  # 总专注时长（分钟）
    total_points = db.Column(db.Integer, default=0)  # 总积分
    
    # 连续记录
    current_streak = db.Column(db.Integer, default=0)  # 当前连续天数
    longest_streak = db.Column(db.Integer, default=0)  # 最长连续天数
    last_session_date = db.Column(db.Date)  # 最后一次会话日期
    
    # 今日统计
    today_sessions = db.Column(db.Integer, default=0)  # 今日会话数
    today_focus_time = db.Column(db.Integer, default=0)  # 今日专注时长
    
    # 时间戳
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref=db.backref('pomodoro_stats', uselist=False))
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'total_sessions': self.total_sessions,
            'total_focus_time': self.total_focus_time,
            'total_points': self.total_points,
            'current_streak': self.current_streak,
            'longest_streak': self.longest_streak,
            'last_session_date': self.last_session_date.isoformat() if self.last_session_date else None,
            'today_sessions': self.today_sessions,
            'today_focus_time': self.today_focus_time,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
