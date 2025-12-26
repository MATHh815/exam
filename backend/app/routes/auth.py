"""认证相关 API 路由"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from app.services.auth_service import AuthService
from app.utils.decorators import jwt_required_with_user

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
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
            }
        }
    """
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_DATA',
                    'message': '缺少请求数据'
                }
            }), 400
        
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        nickname = data.get('nickname')
        
        if not username or not password or not email:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_FIELDS',
                    'message': '缺少必填字段',
                    'details': {
                        'required': ['username', 'password', 'email']
                    }
                }
            }), 400
        
        # 注册用户
        user = AuthService.register(
            username=username,
            password=password,
            email=email,
            nickname=nickname
        )
        
        return jsonify({
            'success': True,
            'data': {
                'user': user.to_dict(),
                'message': '注册成功'
            }
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'REGISTRATION_FAILED',
                'message': str(e)
            }
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '注册失败',
                'details': str(e)
            }
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
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
            }
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_DATA',
                    'message': '缺少请求数据'
                }
            }), 400
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_FIELDS',
                    'message': '缺少用户名或密码'
                }
            }), 400
        
        # 登录
        user, access_token, refresh_token = AuthService.login(username, password)
        
        return jsonify({
            'success': True,
            'data': {
                'user': user.to_dict(),
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'LOGIN_FAILED',
                'message': str(e)
            }
        }), 401
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '登录失败',
                'details': str(e)
            }
        }), 500


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """用户登出
    
    POST /api/auth/logout
    
    Headers:
        Authorization: Bearer <access_token>
    
    Response:
        {
            "success": true,
            "data": {
                "message": "登出成功"
            }
        }
    
    Note: 实际的令牌失效需要配合令牌黑名单机制
    """
    # TODO: 将令牌加入黑名单
    return jsonify({
        'success': True,
        'data': {
            'message': '登出成功'
        }
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
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
            }
        }
    """
    try:
        user_id = get_jwt_identity()
        access_token = create_access_token(identity=user_id)
        
        return jsonify({
            'success': True,
            'data': {
                'access_token': access_token
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'REFRESH_FAILED',
                'message': '刷新令牌失败',
                'details': str(e)
            }
        }), 500


@auth_bp.route('/profile', methods=['GET'])
@jwt_required_with_user
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
            }
        }
    """
    return jsonify({
        'success': True,
        'data': {
            'user': current_user.to_dict()
        }
    }), 200


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required_with_user
def update_profile(current_user):
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
                "user": {...},
                "message": "更新成功"
            }
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_DATA',
                    'message': '缺少请求数据'
                }
            }), 400
        
        # 更新用户信息
        updated_user = AuthService.update_profile(
            user_id=current_user.id,
            **data
        )
        
        return jsonify({
            'success': True,
            'data': {
                'user': updated_user.to_dict(),
                'message': '更新成功'
            }
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'UPDATE_FAILED',
                'message': str(e)
            }
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '更新失败',
                'details': str(e)
            }
        }), 500


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required_with_user
def change_password(current_user):
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
            "data": {
                "message": "密码修改成功"
            }
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_DATA',
                    'message': '缺少请求数据'
                }
            }), 400
        
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        if not old_password or not new_password:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_FIELDS',
                    'message': '缺少旧密码或新密码'
                }
            }), 400
        
        # 修改密码
        AuthService.change_password(
            user_id=current_user.id,
            old_password=old_password,
            new_password=new_password
        )
        
        return jsonify({
            'success': True,
            'data': {
                'message': '密码修改成功'
            }
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'CHANGE_PASSWORD_FAILED',
                'message': str(e)
            }
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '密码修改失败',
                'details': str(e)
            }
        }), 500


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
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
            "data": {
                "message": "密码重置成功"
            }
        }
    
    Note: 实际应用中应该先发送验证码到邮箱，验证后再重置密码
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_DATA',
                    'message': '缺少请求数据'
                }
            }), 400
        
        email = data.get('email')
        new_password = data.get('new_password')
        
        if not email or not new_password:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_FIELDS',
                    'message': '缺少邮箱或新密码'
                }
            }), 400
        
        # 重置密码
        AuthService.reset_password(email, new_password)
        
        return jsonify({
            'success': True,
            'data': {
                'message': '密码重置成功'
            }
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'RESET_PASSWORD_FAILED',
                'message': str(e)
            }
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '密码重置失败',
                'details': str(e)
            }
        }), 500
