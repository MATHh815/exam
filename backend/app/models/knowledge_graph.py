"""
知识点关系图谱模型
"""
from datetime import datetime
from app import db

class KnowledgeRelation(db.Model):
    """知识点关系"""
    __tablename__ = 'knowledge_relations'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # 关系节点
    source_id = db.Column(db.Integer, db.ForeignKey('knowledge_points.id'), nullable=False)
    target_id = db.Column(db.Integer, db.ForeignKey('knowledge_points.id'), nullable=False)
    
    # 关系类型
    relation_type = db.Column(db.String(20), default='prerequisite')  # prerequisite/related/similar
    strength = db.Column(db.Float, default=1.0)  # 关系强度 0-1
    
    # 描述
    description = db.Column(db.Text)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    source = db.relationship('KnowledgePoint', foreign_keys=[source_id], backref='outgoing_relations')
    target = db.relationship('KnowledgePoint', foreign_keys=[target_id], backref='incoming_relations')
    
    def to_dict(self):
        return {
            'id': self.id,
            'source_id': self.source_id,
            'target_id': self.target_id,
            'relation_type': self.relation_type,
            'strength': self.strength,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class UserKnowledgeMastery(db.Model):
    """用户知识点掌握度"""
    __tablename__ = 'user_knowledge_mastery'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    knowledge_point_id = db.Column(db.Integer, db.ForeignKey('knowledge_points.id'), nullable=False)
    
    # 掌握度数据
    mastery_score = db.Column(db.Float, default=0.0)  # 0-100
    practice_count = db.Column(db.Integer, default=0)  # 练习次数
    correct_count = db.Column(db.Integer, default=0)  # 正确次数
    
    # 最近表现（最近10次）
    recent_practices = db.Column(db.Text)  # JSON 格式存储最近练习记录
    
    # 时间戳
    last_practice_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', backref=db.backref('knowledge_mastery', lazy='dynamic'))
    knowledge_point = db.relationship('KnowledgePoint', backref=db.backref('user_mastery', lazy='dynamic'))
    
    # 唯一约束
    __table_args__ = (
        db.UniqueConstraint('user_id', 'knowledge_point_id', name='unique_user_knowledge'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'knowledge_point_id': self.knowledge_point_id,
            'mastery_score': round(self.mastery_score, 2),
            'practice_count': self.practice_count,
            'correct_count': self.correct_count,
            'correct_rate': round(self.correct_count / self.practice_count * 100, 2) if self.practice_count > 0 else 0,
            'last_practice_date': self.last_practice_date.isoformat() if self.last_practice_date else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
