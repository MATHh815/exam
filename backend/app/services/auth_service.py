"""认证服务模块"""
from datetime import datetime
from flask_jwt_extended import create_access_token, create_refresh_token
from app import db
from app.models.user import User


class AuthService:
    """认证服务类
    
    提供用户注册、登录、密码重置等认证相关功能
    """
    
    @staticmethod
    def register(username, password, email, nickname=None):
        """用户注册
        
        Args:
            username: 用户名
            password: 密码（明文）
            email: 邮箱
            nickname: 昵称（可选）
        
        Returns:
            User: 创建的用户对象
        
        Raises:
            ValueError: 用户名或邮箱已存在
        """
        # 检查用户名是否已存在
        if User.query.filter_by(username=username).first():
            raise ValueError('用户名已存在')
        
        # 检查邮箱是否已存在
        if User.query.filter_by(email=email).first():
            raise ValueError('邮箱已被注册')
        
        # 创建用户
        user = User(
            username=username,
            email=email,
            nickname=nickname or username
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return user
    
    @staticmethod
    def login(username, password):
        """用户登录
        
        Args:
            username: 用户名
            password: 密码（明文）
        
        Returns:
            tuple: (用户对象, 访问令牌, 刷新令牌)
        
        Raises:
            ValueError: 用户名或密码错误
        """
        # 查找用户
        user = User.query.filter_by(username=username).first()
        
        # 验证用户存在且密码正确
        if not user or not user.check_password(password):
            raise ValueError('用户名或密码错误')
        
        # 检查用户是否被禁用
        if not user.is_active:
            raise ValueError('账户已被禁用')
        
        # 生成令牌
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return user, access_token, refresh_token
    
    @staticmethod
    def update_profile(user_id, **kwargs):
        """更新用户信息
        
        Args:
            user_id: 用户ID
            **kwargs: 要更新的字段（nickname, email, avatar）
        
        Returns:
            User: 更新后的用户对象
        
        Raises:
            ValueError: 用户不存在或邮箱已被使用
        """
        user = User.query.get(user_id)
        if not user:
            raise ValueError('用户不存在')
        
        # 如果更新邮箱，检查是否已被其他用户使用
        if 'email' in kwargs and kwargs['email'] != user.email:
            existing_user = User.query.filter_by(email=kwargs['email']).first()
            if existing_user:
                raise ValueError('邮箱已被使用')
        
        # 更新允许的字段
        allowed_fields = ['nickname', 'email', 'avatar']
        for field in allowed_fields:
            if field in kwargs:
                setattr(user, field, kwargs[field])
        
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return user
    
    @staticmethod
    def change_password(user_id, old_password, new_password):
        """修改密码
        
        Args:
            user_id: 用户ID
            old_password: 旧密码
            new_password: 新密码
        
        Returns:
            bool: 是否成功
        
        Raises:
            ValueError: 用户不存在或旧密码错误
        """
        user = User.query.get(user_id)
        if not user:
            raise ValueError('用户不存在')
        
        # 验证旧密码
        if not user.check_password(old_password):
            raise ValueError('旧密码错误')
        
        # 设置新密码
        user.set_password(new_password)
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return True
    
    @staticmethod
    def reset_password(email, new_password):
        """重置密码（通过邮箱）
        
        Args:
            email: 邮箱
            new_password: 新密码
        
        Returns:
            bool: 是否成功
        
        Raises:
            ValueError: 邮箱不存在
        """
        user = User.query.filter_by(email=email).first()
        if not user:
            raise ValueError('邮箱不存在')
        
        user.set_password(new_password)
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return True
    
    @staticmethod
    def deactivate_user(user_id):
        """停用用户账户
        
        Args:
            user_id: 用户ID
        
        Returns:
            bool: 是否成功
        
        Raises:
            ValueError: 用户不存在
        """
        user = User.query.get(user_id)
        if not user:
            raise ValueError('用户不存在')
        
        user.is_active = False
        user.updated_at = datetime.utcnow()
        db.session.commit()
        
        return True
    
    @staticmethod
    def get_user_by_id(user_id):
        """根据ID获取用户
        
        Args:
            user_id: 用户ID
        
        Returns:
            User: 用户对象
        
        Raises:
            ValueError: 用户不存在
        """
        user = User.query.get(user_id)
        if not user:
            raise ValueError('用户不存在')
        return user
