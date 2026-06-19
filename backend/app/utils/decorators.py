"""装饰器工具模块"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models.user import User


def jwt_required_with_user(fn):
    """JWT 认证装饰器（自动获取用户对象）
    
    验证 JWT 令牌并将当前用户对象注入到函数参数中
    
    Usage:
        @jwt_required_with_user
        def my_route(current_user):
            return jsonify({'user': current_user.username})
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id_str = get_jwt_identity()
        
        # 将字符串ID转换为整数
        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_USER_ID',
                    'message': '无效的用户ID'
                }
            }), 400
        
        current_user = User.query.get(user_id)
        
        if not current_user:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'USER_NOT_FOUND',
                    'message': '用户不存在'
                }
            }), 404
        
        if not current_user.is_active:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'USER_INACTIVE',
                    'message': '账户已被禁用'
                }
            }), 403
        
        return fn(current_user=current_user, *args, **kwargs)
    
    return wrapper


def admin_required(fn):
    """管理员权限装饰器
    
    验证当前用户是否为管理员
    
    Usage:
        @admin_required
        def admin_route(current_user):
            return jsonify({'message': 'Admin only'})
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id_str = get_jwt_identity()
        
        # 将字符串ID转换为整数
        try:
            user_id = int(user_id_str)
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_USER_ID',
                    'message': '无效的用户ID'
                }
            }), 400
        
        current_user = User.query.get(user_id)
        
        if not current_user:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'USER_NOT_FOUND',
                    'message': '用户不存在'
                }
            }), 404
        
        if not current_user.is_active:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'USER_INACTIVE',
                    'message': '账户已被禁用'
                }
            }), 403
        
        if current_user.role != 'admin':
            return jsonify({
                'success': False,
                'error': {
                    'code': 'ADMIN_REQUIRED',
                    'message': '需要管理员权限'
                }
            }), 403
        
        return fn(current_user=current_user, *args, **kwargs)
    
    return wrapper
