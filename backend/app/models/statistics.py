"""学习统计模型"""
from datetime import datetime, date
from app import db


class StudyStatistics(db.Model):
    """学习统计模型
    
    按日期聚合用户的学习数据
    """
    __tablename__ = 'study_statistics'
    
    # 主键
    id = db.Column(db.Integer, primary_key=True)
    
    # 外键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # 日期
    date = db.Column(db.Date, nullable=False, index=True)
    
    # 统计数据
    practice_count = db.Column(db.Integer, default=0, nullable=False)  # 练习题数
    correct_count = db.Column(db.Integer, default=0, nullable=False)  # 正确题数
    study_duration = db.Column(db.Integer, default=0, nullable=False)  # 学习时长（分钟）
    exam_count = db.Column(db.Integer, default=0, nullable=False)  # 考试次数
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    user = db.relationship('User', backref='study_statistics')
    
    # 唯一约束：每个用户每天只有一条统计记录
    __table_args__ = (
        db.UniqueConstraint('user_id', 'date', name='uq_user_date'),
    )
    
    def __repr__(self):
        return f'<StudyStatistics {self.id}: user={self.user_id} date={self.date} practice={self.practice_count}>'
    
    @classmethod
    def get_or_create(cls, user_id, target_date=None):
        """获取或创建统计记录
        
        Args:
            user_id: 用户ID
            target_date: 目标日期（默认为今天）
            
        Returns:
            StudyStatistics: 统计记录
        """
        if target_date is None:
            target_date = date.today()
        
        stats = cls.query.filter_by(
            user_id=user_id,
            date=target_date
        ).first()
        
        if not stats:
            stats = cls(
                user_id=user_id,
                date=target_date
            )
            db.session.add(stats)
        
        return stats
    
    def add_practice(self, is_correct, time_spent=0):
        """添加练习记录
        
        Args:
            is_correct: 是否正确
            time_spent: 答题时长（秒）
        """
        # 确保字段不是None
        if self.practice_count is None:
            self.practice_count = 0
        if self.correct_count is None:
            self.correct_count = 0
        if self.study_duration is None:
            self.study_duration = 0
        
        self.practice_count += 1
        if is_correct:
            self.correct_count += 1
        if time_spent:
            self.study_duration += int(time_spent / 60)  # 转换为分钟
        self.updated_at = datetime.utcnow()
    
    def add_exam(self):
        """添加考试记录"""
        if self.exam_count is None:
            self.exam_count = 0
        self.exam_count += 1
        self.updated_at = datetime.utcnow()
    
    def calculate_accuracy(self):
        """计算正确率
        
        Returns:
            float: 正确率（百分比）
        """
        if self.practice_count == 0:
            return 0.0
        return round((self.correct_count / self.practice_count) * 100, 2)
    
    @classmethod
    def get_user_statistics(cls, user_id, start_date=None, end_date=None):
        """获取用户的统计数据
        
        Args:
            user_id: 用户ID
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            list: 统计记录列表
        """
        query = cls.query.filter_by(user_id=user_id)
        
        if start_date:
            query = query.filter(cls.date >= start_date)
        
        if end_date:
            query = query.filter(cls.date <= end_date)
        
        return query.order_by(cls.date.desc()).all()
    
    @classmethod
    def get_overview(cls, user_id, start_date=None, end_date=None):
        """获取学习概览
        
        Args:
            user_id: 用户ID
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            dict: 概览数据
        """
        stats_list = cls.get_user_statistics(user_id, start_date, end_date)
        
        total_practice = sum(s.practice_count for s in stats_list)
        total_correct = sum(s.correct_count for s in stats_list)
        total_duration = sum(s.study_duration for s in stats_list)
        total_exams = sum(s.exam_count for s in stats_list)
        
        accuracy = 0.0
        if total_practice > 0:
            accuracy = round((total_correct / total_practice) * 100, 2)
        
        return {
            'total_practice': total_practice,
            'total_correct': total_correct,
            'total_duration': total_duration,
            'total_exams': total_exams,
            'accuracy': accuracy,
            'study_days': len(stats_list)
        }
    
    @classmethod
    def get_trend(cls, user_id, days=7):
        """获取学习趋势
        
        Args:
            user_id: 用户ID
            days: 天数
            
        Returns:
            list: 趋势数据
        """
        from datetime import timedelta
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        stats_list = cls.get_user_statistics(user_id, start_date, end_date)
        
        # 创建日期到统计的映射
        stats_map = {s.date: s for s in stats_list}
        
        # 填充所有日期
        trend = []
        current_date = start_date
        while current_date <= end_date:
            stats = stats_map.get(current_date)
            if stats:
                trend.append({
                    'date': current_date.isoformat(),
                    'practice_count': stats.practice_count,
                    'correct_count': stats.correct_count,
                    'accuracy': stats.calculate_accuracy(),
                    'study_duration': stats.study_duration,
                    'exam_count': stats.exam_count
                })
            else:
                trend.append({
                    'date': current_date.isoformat(),
                    'practice_count': 0,
                    'correct_count': 0,
                    'accuracy': 0.0,
                    'study_duration': 0,
                    'exam_count': 0
                })
            
            current_date += timedelta(days=1)
        
        return trend
    
    def to_dict(self):
        """转换为字典
        
        Returns:
            dict: 统计信息字典
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date.isoformat() if self.date else None,
            'practice_count': self.practice_count,
            'correct_count': self.correct_count,
            'accuracy': self.calculate_accuracy(),
            'study_duration': self.study_duration,
            'exam_count': self.exam_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
