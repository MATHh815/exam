"""学习日程模型"""
from datetime import datetime, time, timedelta
from app import db


class StudySchedule(db.Model):
    """学习日程模型
    
    存储用户的学习日程安排
    """
    __tablename__ = 'study_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # 日程信息
    title = db.Column(db.String(200), nullable=False)  # 日程标题
    activity_type = db.Column(db.String(50), nullable=False)  # 活动类型
    subject = db.Column(db.String(50))  # 科目
    
    # 时间信息
    schedule_date = db.Column(db.Date, nullable=False, index=True)  # 日程日期
    start_time = db.Column(db.Time, nullable=False)  # 开始时间
    end_time = db.Column(db.Time, nullable=False)  # 结束时间
    
    # 重复设置
    repeat_type = db.Column(db.String(20), default='once')  # once, daily, weekly, custom
    repeat_days = db.Column(db.String(50))  # 重复的星期几（1,2,3,4,5 表示周一到周五）
    repeat_until = db.Column(db.Date)  # 重复截止日期
    
    # 状态
    status = db.Column(db.String(20), default='pending')  # pending, completed, cancelled
    is_completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    
    # 备注
    description = db.Column(db.Text)  # 详细描述
    location = db.Column(db.String(200))  # 地点（如：图书馆、自习室）
    
    # 提醒
    reminder_minutes = db.Column(db.Integer, default=15)  # 提前多少分钟提醒
    is_reminder_enabled = db.Column(db.Boolean, default=True)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref='study_schedules')
    
    def __repr__(self):
        return f'<StudySchedule {self.title} on {self.schedule_date}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'activity_type': self.activity_type,
            'subject': self.subject,
            'schedule_date': self.schedule_date.isoformat() if self.schedule_date else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'repeat_type': self.repeat_type,
            'repeat_days': self.repeat_days,
            'repeat_until': self.repeat_until.isoformat() if self.repeat_until else None,
            'status': self.status,
            'is_completed': self.is_completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'description': self.description,
            'location': self.location,
            'reminder_minutes': self.reminder_minutes,
            'is_reminder_enabled': self.is_reminder_enabled,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'duration_minutes': self.get_duration_minutes()
        }
    
    def get_duration_minutes(self):
        """计算时长（分钟）"""
        if not self.start_time or not self.end_time:
            return 0
        
        start_datetime = datetime.combine(datetime.today(), self.start_time)
        end_datetime = datetime.combine(datetime.today(), self.end_time)
        
        # 处理跨天的情况
        if end_datetime < start_datetime:
            end_datetime = datetime.combine(datetime.today() + timedelta(days=1), self.end_time)
        
        duration = end_datetime - start_datetime
        return int(duration.total_seconds() / 60)


# 活动类型常量
ACTIVITY_TYPES = {
    'memorize': '背单词/记忆',
    'lecture': '听课/看视频',
    'practice': '做题/练习',
    'review': '复习笔记',
    'mock_exam': '模拟考试',
    'reading': '阅读教材',
    'writing': '写作练习',
    'rest': '休息'
}

# 科目常量（考研）
SUBJECTS = {
    # 公共课
    'politics': '政治',
    'english': '英语',
    'math': '数学',
    
    # 专业课 - 计算机
    'data_structure': '数据结构',
    'computer_organization': '计算机组成原理',
    'operating_system': '操作系统',
    'computer_network': '计算机网络',
    
    # 专业课 - 经济学
    'economics': '经济学',
    'management': '管理学',
    
    # 专业课 - 法学
    'law': '法学',
    
    # 专业课 - 其他
    'major_course_1': '专业课一',
    'major_course_2': '专业课二'
}
