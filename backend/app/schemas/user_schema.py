"""用户相关的数据验证模式"""
from marshmallow import Schema, fields, validates, ValidationError, validate
from app.utils.validators import validate_email, validate_password, validate_username


class UserRegistrationSchema(Schema):
    """用户注册验证模式"""
    
    username = fields.Str(required=True, validate=validate.Length(min=3, max=20))
    password = fields.Str(required=True, validate=validate.Length(min=8))
    email = fields.Email(required=True)
    nickname = fields.Str(validate=validate.Length(max=50))
    
    @validates('username')
    def validate_username_format(self, value):
        """验证用户名格式"""
        is_valid, error_msg = validate_username(value)
        if not is_valid:
            raise ValidationError(error_msg)
    
    @validates('password')
    def validate_password_strength(self, value):
        """验证密码强度"""
        is_valid, error_msg = validate_password(value)
        if not is_valid:
            raise ValidationError(error_msg)


class UserLoginSchema(Schema):
    """用户登录验证模式"""
    
    username = fields.Str(required=True)
    password = fields.Str(required=True)


class UserUpdateSchema(Schema):
    """用户信息更新验证模式"""
    
    nickname = fields.Str(validate=validate.Length(max=50))
    email = fields.Email()
    avatar = fields.Str(validate=validate.Length(max=500))


class PasswordChangeSchema(Schema):
    """密码修改验证模式"""
    
    old_password = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=8))
    
    @validates('new_password')
    def validate_new_password_strength(self, value):
        """验证新密码强度"""
        is_valid, error_msg = validate_password(value)
        if not is_valid:
            raise ValidationError(error_msg)


class PasswordResetSchema(Schema):
    """密码重置验证模式"""
    
    email = fields.Email(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=8))
    
    @validates('new_password')
    def validate_new_password_strength(self, value):
        """验证新密码强度"""
        is_valid, error_msg = validate_password(value)
        if not is_valid:
            raise ValidationError(error_msg)
