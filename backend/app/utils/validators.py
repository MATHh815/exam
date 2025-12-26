"""输入验证工具"""
import re
from functools import wraps
from flask import request
from marshmallow import ValidationError as MarshmallowValidationError
from app.utils.exceptions import ValidationError


def validate_email(email):
    """验证邮箱格式
    
    Args:
        email: 邮箱地址
    
    Returns:
        bool: 是否有效
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """验证密码强度
    
    Args:
        password: 密码
    
    Returns:
        tuple: (是否有效, 错误消息)
    """
    if len(password) < 8:
        return False, '密码长度至少为 8 位'
    
    if not re.search(r'[a-zA-Z]', password):
        return False, '密码必须包含字母'
    
    if not re.search(r'\d', password):
        return False, '密码必须包含数字'
    
    return True, None


def validate_username(username):
    """验证用户名格式
    
    Args:
        username: 用户名
    
    Returns:
        tuple: (是否有效, 错误消息)
    """
    if len(username) < 3:
        return False, '用户名长度至少为 3 位'
    
    if len(username) > 20:
        return False, '用户名长度不能超过 20 位'
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, '用户名只能包含字母、数字和下划线'
    
    return True, None


def validate_with_schema(schema_class):
    """使用 Marshmallow Schema 验证请求数据的装饰器
    
    Args:
        schema_class: Marshmallow Schema 类
    
    Returns:
        装饰器函数
    
    Usage:
        @validate_with_schema(UserSchema)
        def create_user(validated_data):
            # validated_data 是验证后的数据
            pass
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # 获取请求数据
            data = request.get_json()
            
            if data is None:
                raise ValidationError('缺少请求数据')
            
            # 验证数据
            schema = schema_class()
            try:
                validated_data = schema.load(data)
            except MarshmallowValidationError as e:
                raise ValidationError('数据验证失败', details=e.messages)
            
            # 将验证后的数据传递给视图函数
            return f(validated_data=validated_data, *args, **kwargs)
        
        return wrapper
    return decorator


def validate_pagination_params():
    """验证分页参数
    
    Returns:
        tuple: (page, page_size)
    
    Raises:
        ValidationError: 参数无效时
    """
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        
        if page < 1:
            raise ValidationError('页码必须大于 0')
        
        if page_size < 1:
            raise ValidationError('每页大小必须大于 0')
        
        if page_size > 100:
            raise ValidationError('每页大小不能超过 100')
        
        return page, page_size
        
    except ValueError:
        raise ValidationError('分页参数必须是整数')


def validate_required_fields(data, required_fields):
    """验证必填字段
    
    Args:
        data: 数据字典
        required_fields: 必填字段列表
    
    Raises:
        ValidationError: 缺少必填字段时
    """
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    
    if missing_fields:
        raise ValidationError(
            '缺少必填字段',
            details={'missing_fields': missing_fields}
        )
