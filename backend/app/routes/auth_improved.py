"""改进的认证 API 路由示例 - 展示如何使用新的错误处理和验证系统"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token

from app.services.auth_service import AuthService
from app.utils.decorators import jwt_required_with_user
from app.utils.response import success_response, error_response
from app.utils.validators import validate_with_schema
from app.utils.middleware import log_request_time, validate_content_type
from app.schemas import (
    UserRegistrationSchema,
    UserLoginSchema,
    UserUpdateSchema,
    PasswordChangeSchema,
    PasswordResetSchema
)

auth_improved_bp = Blueprint('auth_improved', __name__)


@auth_improved_bp.route('/register', methods=['POST'])
@validate_content_type('application/json')
@validate_with_schema(UserRegistrationSchema)
@log_request_time
def register(validated_data):
    """用户注册
    
    POST /api/auth/register
    
    Request Body:
        {
            "username": "string",
            "password": "string",
            "email": "string",
            "nickname": "string" (optional)
        }
    
    Response:
        {
            "success": true,
            "data": {
                "user": {...},
                "message": "注册成功"
            },
            "timestamp": "2024-01-01T00:00:00Z"
        }
    """
    # 注册用户
    user = AuthService.register(**validated_data)
    
    return success_response(
        data={'user': user.to_dict()},
        message='注册成功',
        status_code=201
    )


@auth_improved_bp.route('/login', methods=['POST'])
@validate_content_type('application/json')
@validate_with_schema(UserLoginSchema)
@log_request_time
def login(validated_data):
    """用户登录
    
    POST /api/auth/login
    
    Request Body:
        {
            "username": "string",
            "password": "string"
        }
    
    Response:
        {
            "success": true,
            "data": {
                "user": {...},
                "access_token": "string",
                "refresh_token": "string"
            },
            "timestamp": "2024-01-01T00:00:00Z"
        }
    """
    # 登录
    user, access_token, refresh_token = AuthService.login(
        validated_data['username'],
        validated_data['password']
    )
    
    return success_response(
        data={
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        }
    )


@auth_improved_bp.route('/logout', methods=['POST'])
@jwt_required()
@log_request_time
def logout():
    """用户登出
    
    POST /api/auth/logout
    
    Headers:
        Authorization: Bearer <access_token>
    
    Response:
        {
            "success": true,
            "message": "登出成功",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    """
    # TODO: 将令牌加入黑名单
    return success_response(message='登出成功')


@auth_improved_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
@log_request_time
def refresh():
    """刷新访问令牌
    
    POST /api/auth/refresh
    
    Headers:
        Authorization: Bearer <refresh_token>
    
    Response:
        {
            "success": true,
            "data": {
                "access_token": "string"
            },
            "timestamp": "2024-01-01T00:00:00Z"
        }
    """
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)
    
    return success_response(data={'access_token': access_token})


@auth_improved_bp.route('/profile', methods=['GET'])
@jwt_required_with_user
@log_request_time
def get_profile(current_user):
    """获取当前用户信息
    
    GET /api/auth/profile
    
    Headers:
        Authorization: Bearer <access_token>
    
    Response:
        {
            "success": true,
            "data": {
                "user": {...}
            },
            "timestamp": "2024-01-01T00:00:00Z"
        }
    """
    return success_response(data={'user': current_user.to_dict()})


@auth_improved_bp.route('/profile', methods=['PUT'])
@jwt_required_with_user
@validate_content_type('application/json')
@validate_with_schema(UserUpdateSchema)
@log_request_time
def update_profile(current_user, validated_data):
    """更新用户信息
    
    PUT /api/auth/profile
    
    Headers:
        Authorization: Bearer <access_token>
    
    Request Body:
        {
            "nickname": "string" (optional),
            "email": "string" (optional),
            "avatar": "string" (optional)
        }
    
    Response:
        {
            "success": true,
            "data": {
                "user": {...}
            },
            "message": "更新成功",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    """
    # 更新用户信息
    updated_user = AuthService.update_profile(
        user_id=current_user.id,
        **validated_data
    )
    
    return success_response(
        data={'user': updated_user.to_dict()},
        message='更新成功'
    )


@auth_improved_bp.route('/change-password', methods=['POST'])
@jwt_required_with_user
@validate_content_type('application/json')
@validate_with_schema(PasswordChangeSchema)
@log_request_time
def change_password(current_user, validated_data):
    """修改密码
    
    POST /api/auth/change-password
    
    Headers:
        Authorization: Bearer <access_token>
    
    Request Body:
        {
            "old_password": "string",
            "new_password": "string"
        }
    
    Response:
        {
            "success": true,
            "message": "密码修改成功",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    """
    # 修改密码
    AuthService.change_password(
        user_id=current_user.id,
        old_password=validated_data['old_password'],
        new_password=validated_data['new_password']
    )
    
    return success_response(message='密码修改成功')


@auth_improved_bp.route('/reset-password', methods=['POST'])
@validate_content_type('application/json')
@validate_with_schema(PasswordResetSchema)
@log_request_time
def reset_password(validated_data):
    """重置密码
    
    POST /api/auth/reset-password
    
    Request Body:
        {
            "email": "string",
            "new_password": "string"
        }
    
    Response:
        {
            "success": true,
            "message": "密码重置成功",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    
    Note: 实际应用中应该先发送验证码到邮箱，验证后再重置密码
    """
    # 重置密码
    AuthService.reset_password(
        validated_data['email'],
        validated_data['new_password']
    )
    
    return success_response(message='密码重置成功')
