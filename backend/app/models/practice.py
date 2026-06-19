"""练习相关模型"""
from datetime import datetime
from app import db


class PracticeRecord(db.Model):
    """练习记录模型
    
    存储用户的练习答题记录
    """
    __tablename__ = 'practice_records'
    
    # 主键
    id = db.Column(db.Integer, primary_key=True)
    
    # 外键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False, index=True)
    
    # 答题信息
    user_answer = db.Column(db.String(500))  # 用户答案
    is_correct = db.Column(db.Boolean, nullable=False, index=True)  # 是否正确
    time_spent = db.Column(db.Integer)  # 答题时长（秒）
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # 关系
    user = db.relationship('User', backref='practice_records')
    question = db.relationship('Question', backref='practice_records')
    
    def __repr__(self):
        return f'<PracticeRecord {self.id}: user={self.user_id} question={self.question_id} correct={self.is_correct}>'
    
    @staticmethod
    def check_answer(question, user_answer):
        """检查答案是否正确
        
        Args:
            question: 题目对象
            user_answer: 用户答案
            
        Returns:
            bool: 是否正确
        """
        if not user_answer:
            return False
        
        # 简单的字符串比较（实际应用中可能需要更复杂的比较逻辑）
        return str(user_answer).strip().upper() == str(question.correct_answer).strip().upper()
    
    @classmethod
    def create_record(cls, user_id, question_id, user_answer, time_spent=None):
        """创建练习记录
        
        Args:
            user_id: 用户ID
            question_id: 题目ID
            user_answer: 用户答案
            time_spent: 答题时长（秒）
            
        Returns:
            PracticeRecord: 练习记录实例
        """
        from app.models.question import Question
        
        question = Question.query.get(question_id)
        if not question:
            raise ValueError(f'题目不存在: {question_id}')
        
        is_correct = cls.check_answer(question, user_answer)
        
        record = cls(
            user_id=user_id,
            question_id=question_id,
            user_answer=user_answer,
            is_correct=is_correct,
            time_spent=time_spent
        )
        
        return record
    
    def to_dict(self, include_question=False):
        """转换为字典
        
        Args:
            include_question: 是否包含题目信息
            
        Returns:
            dict: 记录信息字典
        """
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'question_id': self.question_id,
            'user_answer': self.user_answer,
            'is_correct': self.is_correct,
            'time_spent': self.time_spent,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_question and self.question:
            data['question'] = self.question.to_dict(
                include_answer=True,
                include_explanation=True
            )
        
        return data


class WrongQuestion(db.Model):
    """错题本模型
    
    存储用户的错题集合
    """
    __tablename__ = 'wrong_questions'
    
    # 主键
    id = db.Column(db.Integer, primary_key=True)
    
    # 外键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False, index=True)
    
    # 错题信息
    wrong_count = db.Column(db.Integer, default=1, nullable=False)  # 错误次数
    mastered = db.Column(db.Boolean, default=False, nullable=False, index=True)  # 是否已掌握
    
    # 时间戳
    last_wrong_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # 关系
    user = db.relationship('User', backref='wrong_questions')
    question = db.relationship('Question', backref='wrong_questions')
    
    # 唯一约束：同一用户不能有重复的错题
    __table_args__ = (
        db.UniqueConstraint('user_id', 'question_id', name='uq_user_question'),
    )
    
    def __repr__(self):
        return f'<WrongQuestion {self.id}: user={self.user_id} question={self.question_id} count={self.wrong_count}>'
    
    def increment_wrong_count(self):
        """增加错误次数"""
        self.wrong_count += 1
        self.last_wrong_at = datetime.utcnow()
        self.mastered = False  # 重新答错，标记为未掌握
    
    def mark_as_mastered(self):
        """标记为已掌握"""
        self.mastered = True
    
    def mark_as_not_mastered(self):
        """标记为未掌握"""
        self.mastered = False
    
    @classmethod
    def add_or_update(cls, user_id, question_id):
        """添加或更新错题
        
        如果错题已存在，增加错误次数；否则创建新记录
        
        Args:
            user_id: 用户ID
            question_id: 题目ID
            
        Returns:
            WrongQuestion: 错题记录
        """
        wrong_question = cls.query.filter_by(
            user_id=user_id,
            question_id=question_id
        ).first()
        
        if wrong_question:
            wrong_question.increment_wrong_count()
        else:
            wrong_question = cls(
                user_id=user_id,
                question_id=question_id
            )
            db.session.add(wrong_question)
        
        return wrong_question
    
    @classmethod
    def get_user_wrong_questions(cls, user_id, mastered=None):
        """获取用户的错题列表
        
        Args:
            user_id: 用户ID
            mastered: 是否已掌握（None表示全部）
            
        Returns:
            list: 错题列表
        """
        query = cls.query.filter_by(user_id=user_id)
        
        if mastered is not None:
            query = query.filter_by(mastered=mastered)
        
        return query.order_by(cls.last_wrong_at.desc()).all()
    
    def to_dict(self, include_question=False):
        """转换为字典
        
        Args:
            include_question: 是否包含题目信息
            
        Returns:
            dict: 错题信息字典
        """
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'question_id': self.question_id,
            'wrong_count': self.wrong_count,
            'mastered': self.mastered,
            'last_wrong_at': self.last_wrong_at.isoformat() if self.last_wrong_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_question and self.question:
            data['question'] = self.question.to_dict(
                include_answer=True,
                include_explanation=True
            )
        
        return data
