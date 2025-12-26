"""用户模型"""
from datetime import datetime
import bcrypt
from app import db


class User(db.Model):
    """用户模型
    
    存储用户的基本信息和认证信息
    """
    __tablename__ = 'users'
    
    # 主键
    id = db.Column(db.Integer, primary_key=True)
    
    # 认证信息
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    
    # 个人信息
    nickname = db.Column(db.String(80))
    avatar = db.Column(db.String(255))
    
    # 角色和状态
    role = db.Column(db.String(20), default='user', nullable=False)  # user, admin
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系（将在其他模型创建后启用）
    # practice_records = db.relationship('PracticeRecord', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    # wrong_questions = db.relationship('WrongQuestion', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    # exam_sessions = db.relationship('ExamSession', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    # exam_results = db.relationship('ExamResult', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    # study_statistics = db.relationship('StudyStatistics', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """设置密码（哈希）
        
        Args:
            password: 明文密码
        """
        # 使用 bcrypt 生成密码哈希
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    def check_password(self, password):
        """验证密码
        
        Args:
            password: 明文密码
            
        Returns:
            bool: 密码是否正确
        """
        password_bytes = password.encode('utf-8')
        hash_bytes = self.password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)
    
    def to_dict(self, include_email=False):
        """转换为字典
        
        Args:
            include_email: 是否包含邮箱（敏感信息）
            
        Returns:
            dict: 用户信息字典
        """
        data = {
            'id': self.id,
            'username': self.username,
            'nickname': self.nickname,
            'avatar': self.avatar,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_email:
            data['email'] = self.email
        
        return data
    
    @staticmethod
    def validate_password(password):
        """验证密码强度
        
        Args:
            password: 密码
            
        Returns:
            tuple: (是否有效, 错误信息)
        """
        if len(password) < 8:
            return False, '密码长度至少为8位'
        
        if not any(c.isalpha() for c in password):
            return False, '密码必须包含字母'
        
        if not any(c.isdigit() for c in password):
            return False, '密码必须包含数字'
        
        return True, None
    
    @staticmethod
    def validate_username(username):
        """验证用户名
        
        Args:
            username: 用户名
            
        Returns:
            tuple: (是否有效, 错误信息)
        """
        if len(username) < 3:
            return False, '用户名长度至少为3位'
        
        if len(username) > 80:
            return False, '用户名长度不能超过80位'
        
        if not username.isalnum() and '_' not in username:
            return False, '用户名只能包含字母、数字和下划线'
        
        return True, None
