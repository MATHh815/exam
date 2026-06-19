"""笔记和收藏模型"""
from datetime import datetime
from app import db


class QuestionNote(db.Model):
    """题目笔记模型
    
    存储用户对题目的笔记
    """
    __tablename__ = 'question_notes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    tags = db.Column(db.JSON)  # ["重点", "易错"]
    linked_questions = db.Column(db.JSON)  # [123, 456] - 笔记中链接的题目ID列表
    is_deleted = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='notes')
    question = db.relationship('Question', backref='notes')
    
    # 索引
    __table_args__ = (
        db.Index('idx_user_question', 'user_id', 'question_id'),
    )
    
    def __repr__(self):
        return f'<QuestionNote {self.id}>'
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'question_id': self.question_id,
            'content': self.content,
            'tags': self.tags or [],
            'linked_questions': self.linked_questions or [],
            'is_deleted': self.is_deleted,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class QuestionBookmark(db.Model):
    """题目收藏模型
    
    存储用户收藏的题目
    """
    __tablename__ = 'question_bookmarks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False, index=True)
    tags = db.Column(db.JSON)  # ["重点", "易错"]
    notes = db.Column(db.Text)  # 备注信息
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='bookmarks')
    question = db.relationship('Question', backref='bookmarks')
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'question_id', name='uq_user_question_bookmark'),
    )
    
    def __repr__(self):
        return f'<QuestionBookmark {self.id}>'
    
    def to_dict(self):
        """转换为字典"""
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'question_id': self.question_id,
            'tags': self.tags or [],
            'notes': self.notes or '',
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        # 如果有关联的题目，添加题目信息
        if self.question:
            result['question'] = {
                'id': self.question.id,
                'content': self.question.content,
                'exam_type': self.question.exam_type,
                'subject': self.question.subject,
                'chapter': self.question.chapter,
                'difficulty': self.question.difficulty,
                'question_type': self.question.question_type,
                'options': self.question.options,
                'answer': self.question.answer,
                'explanation': self.question.explanation
            }
        
        return result

