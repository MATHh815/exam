"""题目模型"""
from datetime import datetime
from app import db


class Question(db.Model):
    """题目模型
    
    存储各类考试题目的信息
    """
    __tablename__ = 'questions'
    
    # 主键
    id = db.Column(db.Integer, primary_key=True)
    
    # 题目分类
    exam_type = db.Column(db.String(50), nullable=False, index=True)  # civil_service, postgraduate, public_institution
    question_type = db.Column(db.String(50), nullable=False, index=True)  # single_choice, multiple_choice, true_false, fill_blank, essay
    subject = db.Column(db.String(100), index=True)  # 科目：行测、申论、数学、英语等
    chapter = db.Column(db.String(100), index=True)  # 章节
    difficulty = db.Column(db.Integer, default=3, index=True)  # 难度：1-5
    
    # 题目内容
    content = db.Column(db.Text, nullable=False)  # 题目内容
    options = db.Column(db.JSON)  # 选项（JSON 格式）
    correct_answer = db.Column(db.String(500), nullable=False)  # 正确答案
    explanation = db.Column(db.Text)  # 解析
    tags = db.Column(db.JSON)  # 标签（JSON 数组）
    
    # 创建信息
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 软删除标记
    is_deleted = db.Column(db.Boolean, default=False, nullable=False, index=True)
    
    # 关系
    creator = db.relationship('User', backref='created_questions', foreign_keys=[created_by])
    
    def __repr__(self):
        return f'<Question {self.id}: {self.content[:30]}...>'
    
    def soft_delete(self):
        """软删除题目
        
        将题目标记为已删除，但不从数据库中物理删除
        """
        self.is_deleted = True
        self.updated_at = datetime.utcnow()
    
    def restore(self):
        """恢复已删除的题目"""
        self.is_deleted = False
        self.updated_at = datetime.utcnow()
    
    def to_dict(self, include_answer=False, include_explanation=False):
        """转换为字典
        
        Args:
            include_answer: 是否包含正确答案
            include_explanation: 是否包含解析
            
        Returns:
            dict: 题目信息字典
        """
        data = {
            'id': self.id,
            'exam_type': self.exam_type,
            'question_type': self.question_type,
            'subject': self.subject,
            'chapter': self.chapter,
            'difficulty': self.difficulty,
            'content': self.content,
            'options': self.options,
            'tags': self.tags,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_answer:
            data['correct_answer'] = self.correct_answer
        
        if include_explanation:
            data['explanation'] = self.explanation
        
        return data
    
    @staticmethod
    def validate_exam_type(exam_type):
        """验证考试类型
        
        Args:
            exam_type: 考试类型
            
        Returns:
            tuple: (是否有效, 错误信息)
        """
        valid_types = ['civil_service', 'postgraduate', 'public_institution']
        if exam_type not in valid_types:
            return False, f'考试类型必须是以下之一: {", ".join(valid_types)}'
        return True, None
    
    @staticmethod
    def validate_question_type(question_type):
        """验证题目类型
        
        Args:
            question_type: 题目类型
            
        Returns:
            tuple: (是否有效, 错误信息)
        """
        valid_types = ['single_choice', 'multiple_choice', 'true_false', 'fill_blank', 'essay']
        if question_type not in valid_types:
            return False, f'题目类型必须是以下之一: {", ".join(valid_types)}'
        return True, None
    
    @staticmethod
    def validate_difficulty(difficulty):
        """验证难度级别
        
        Args:
            difficulty: 难度级别
            
        Returns:
            tuple: (是否有效, 错误信息)
        """
        if not isinstance(difficulty, int):
            return False, '难度必须是整数'
        
        if difficulty < 1 or difficulty > 5:
            return False, '难度必须在1-5之间'
        
        return True, None
    
    @staticmethod
    def validate_options(question_type, options):
        """验证选项格式
        
        Args:
            question_type: 题目类型
            options: 选项数据
            
        Returns:
            tuple: (是否有效, 错误信息)
        """
        # 选择题和判断题需要选项
        if question_type in ['single_choice', 'multiple_choice', 'true_false']:
            if not options:
                return False, f'{question_type} 类型题目必须提供选项'
            
            if not isinstance(options, (list, dict)):
                return False, '选项必须是列表或字典格式'
            
            if isinstance(options, list) and len(options) < 2:
                return False, '选项至少需要2个'
        
        # 填空题和简答题不需要选项
        elif question_type in ['fill_blank', 'essay']:
            if options:
                return False, f'{question_type} 类型题目不应该有选项'
        
        return True, None
    
    @classmethod
    def create_from_dict(cls, data, created_by=None):
        """从字典创建题目
        
        Args:
            data: 题目数据字典
            created_by: 创建者ID
            
        Returns:
            Question: 题目实例
            
        Raises:
            ValueError: 数据验证失败
        """
        # 验证必填字段
        required_fields = ['exam_type', 'question_type', 'content', 'correct_answer']
        for field in required_fields:
            if field not in data:
                raise ValueError(f'缺少必填字段: {field}')
        
        # 验证考试类型
        valid, error = cls.validate_exam_type(data['exam_type'])
        if not valid:
            raise ValueError(error)
        
        # 验证题目类型
        valid, error = cls.validate_question_type(data['question_type'])
        if not valid:
            raise ValueError(error)
        
        # 验证难度
        if 'difficulty' in data:
            valid, error = cls.validate_difficulty(data['difficulty'])
            if not valid:
                raise ValueError(error)
        
        # 验证选项
        valid, error = cls.validate_options(data['question_type'], data.get('options'))
        if not valid:
            raise ValueError(error)
        
        # 创建题目实例
        question = cls(
            exam_type=data['exam_type'],
            question_type=data['question_type'],
            subject=data.get('subject'),
            chapter=data.get('chapter'),
            difficulty=data.get('difficulty', 3),
            content=data['content'],
            options=data.get('options'),
            correct_answer=data['correct_answer'],
            explanation=data.get('explanation'),
            tags=data.get('tags', []),
            created_by=created_by
        )
        
        return question
    
    def update_from_dict(self, data):
        """从字典更新题目（保持ID不变）
        
        Args:
            data: 更新数据字典
            
        Raises:
            ValueError: 数据验证失败
        """
        # 验证考试类型
        if 'exam_type' in data:
            valid, error = self.validate_exam_type(data['exam_type'])
            if not valid:
                raise ValueError(error)
            self.exam_type = data['exam_type']
        
        # 验证题目类型
        if 'question_type' in data:
            valid, error = self.validate_question_type(data['question_type'])
            if not valid:
                raise ValueError(error)
            self.question_type = data['question_type']
        
        # 验证难度
        if 'difficulty' in data:
            valid, error = self.validate_difficulty(data['difficulty'])
            if not valid:
                raise ValueError(error)
            self.difficulty = data['difficulty']
        
        # 验证选项
        if 'options' in data:
            question_type = data.get('question_type', self.question_type)
            valid, error = self.validate_options(question_type, data['options'])
            if not valid:
                raise ValueError(error)
            self.options = data['options']
        
        # 更新其他字段
        if 'subject' in data:
            self.subject = data['subject']
        if 'chapter' in data:
            self.chapter = data['chapter']
        if 'content' in data:
            self.content = data['content']
        if 'correct_answer' in data:
            self.correct_answer = data['correct_answer']
        if 'explanation' in data:
            self.explanation = data['explanation']
        if 'tags' in data:
            self.tags = data['tags']
        
        self.updated_at = datetime.utcnow()
