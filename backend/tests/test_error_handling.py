"""测试错误处理和验证系统"""
import pytest
from flask import Flask
from app import create_app, db
from app.utils.exceptions import (
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    ResourceNotFoundError,
    ResourceConflictError,
    BusinessLogicError,
    DatabaseError
)
from app.utils.response import success_response, error_response, paginated_response
from app.utils.validators import (
    validate_email,
    validate_password,
    validate_username,
    validate_pagination_params,
    validate_required_fields
)


class TestCustomExceptions:
    """测试自定义异常"""
    
    def test_validation_error(self):
        """测试验证错误"""
        error = ValidationError('验证失败', details={'field': 'username'})
        assert error.message == '验证失败'
        assert error.code == 'VALIDATION_ERROR'
        assert error.status_code == 400
        assert error.details == {'field': 'username'}
    
    def test_authentication_error(self):
        """测试认证错误"""
        error = AuthenticationError('认证失败')
        assert error.message == '认证失败'
        assert error.code == 'AUTHENTICATION_ERROR'
        assert error.status_code == 401
    
    def test_authorization_error(self):
        """测试授权错误"""
        error = AuthorizationError('权限不足')
        assert error.message == '权限不足'
        assert error.code == 'AUTHORIZATION_ERROR'
        assert error.status_code == 403
    
    def test_resource_not_found_error(self):
        """测试资源不存在错误"""
        error = ResourceNotFoundError('用户', 123)
        assert '用户' in error.message
        assert '123' in error.message
        assert error.code == 'RESOURCE_NOT_FOUND'
        assert error.status_code == 404
    
    def test_resource_conflict_error(self):
        """测试资源冲突错误"""
        error = ResourceConflictError('用户名已存在')
        assert error.message == '用户名已存在'
        assert error.code == 'RESOURCE_CONFLICT'
        assert error.status_code == 409
    
    def test_business_logic_error(self):
        """测试业务逻辑错误"""
        error = BusinessLogicError('余额不足')
        assert error.message == '余额不足'
        assert error.code == 'BUSINESS_LOGIC_ERROR'
        assert error.status_code == 400
    
    def test_database_error(self):
        """测试数据库错误"""
        error = DatabaseError('数据库连接失败')
        assert error.message == '数据库连接失败'
        assert error.code == 'DATABASE_ERROR'
        assert error.status_code == 500


class TestResponseHelpers:
    """测试响应辅助函数"""
    
    def test_success_response(self, app):
        """测试成功响应"""
        with app.app_context():
            response, status_code = success_response(
                data={'user': {'id': 1}},
                message='操作成功'
            )
            data = response.get_json()
            
            assert status_code == 200
            assert data['success'] is True
            assert data['data'] == {'user': {'id': 1}}
            assert data['message'] == '操作成功'
            assert 'timestamp' in data
    
    def test_success_response_with_custom_status(self, app):
        """测试自定义状态码的成功响应"""
        with app.app_context():
            response, status_code = success_response(
                data={'id': 1},
                status_code=201
            )
            assert status_code == 201
    
    def test_error_response(self, app):
        """测试错误响应"""
        with app.app_context():
            response, status_code = error_response(
                message='验证失败',
                code='VALIDATION_ERROR',
                status_code=400,
                details={'field': 'username'}
            )
            data = response.get_json()
            
            assert status_code == 400
            assert data['success'] is False
            assert data['error']['code'] == 'VALIDATION_ERROR'
            assert data['error']['message'] == '验证失败'
            assert data['error']['details'] == {'field': 'username'}
            assert 'timestamp' in data
    
    def test_paginated_response(self, app):
        """测试分页响应"""
        with app.app_context():
            items = [{'id': i} for i in range(1, 21)]
            response, status_code = paginated_response(
                items=items,
                total=100,
                page=1,
                page_size=20
            )
            data = response.get_json()
            
            assert status_code == 200
            assert data['success'] is True
            assert len(data['data']['items']) == 20
            assert data['data']['pagination']['total'] == 100
        assert data['data']['pagination']['page'] == 1
        assert data['data']['pagination']['page_size'] == 20
        assert data['data']['pagination']['total_pages'] == 5


class TestValidators:
    """测试验证器"""
    
    def test_validate_email_valid(self):
        """测试有效邮箱"""
        assert validate_email('test@example.com') is True
        assert validate_email('user.name@domain.co.uk') is True
    
    def test_validate_email_invalid(self):
        """测试无效邮箱"""
        assert validate_email('invalid') is False
        assert validate_email('test@') is False
        assert validate_email('@example.com') is False
    
    def test_validate_password_valid(self):
        """测试有效密码"""
        is_valid, error = validate_password('password123')
        assert is_valid is True
        assert error is None
    
    def test_validate_password_too_short(self):
        """测试密码太短"""
        is_valid, error = validate_password('pass1')
        assert is_valid is False
        assert '8 位' in error
    
    def test_validate_password_no_letter(self):
        """测试密码缺少字母"""
        is_valid, error = validate_password('12345678')
        assert is_valid is False
        assert '字母' in error
    
    def test_validate_password_no_digit(self):
        """测试密码缺少数字"""
        is_valid, error = validate_password('password')
        assert is_valid is False
        assert '数字' in error
    
    def test_validate_username_valid(self):
        """测试有效用户名"""
        is_valid, error = validate_username('user123')
        assert is_valid is True
        assert error is None
    
    def test_validate_username_too_short(self):
        """测试用户名太短"""
        is_valid, error = validate_username('ab')
        assert is_valid is False
        assert '3 位' in error
    
    def test_validate_username_too_long(self):
        """测试用户名太长"""
        is_valid, error = validate_username('a' * 21)
        assert is_valid is False
        assert '20 位' in error
    
    def test_validate_username_invalid_chars(self):
        """测试用户名包含非法字符"""
        is_valid, error = validate_username('user@123')
        assert is_valid is False
        assert '字母、数字和下划线' in error
    
    def test_validate_required_fields_success(self):
        """测试必填字段验证成功"""
        data = {'username': 'test', 'password': 'pass123', 'email': 'test@example.com'}
        # 不应该抛出异常
        validate_required_fields(data, ['username', 'password', 'email'])
    
    def test_validate_required_fields_missing(self):
        """测试缺少必填字段"""
        data = {'username': 'test'}
        with pytest.raises(ValidationError) as exc_info:
            validate_required_fields(data, ['username', 'password', 'email'])
        
        assert '缺少必填字段' in str(exc_info.value)
        assert 'password' in exc_info.value.details['missing_fields']
        assert 'email' in exc_info.value.details['missing_fields']


class TestGlobalErrorHandlers:
    """测试全局错误处理器"""
    
    @pytest.fixture
    def app(self):
        """创建测试应用"""
        app = create_app('testing')
        
        # 添加测试路由
        @app.route('/test/validation-error')
        def test_validation_error():
            raise ValidationError('测试验证错误', details={'field': 'test'})
        
        @app.route('/test/authentication-error')
        def test_authentication_error():
            raise AuthenticationError('测试认证错误')
        
        @app.route('/test/resource-not-found')
        def test_resource_not_found():
            raise ResourceNotFoundError('测试资源', 123)
        
        @app.route('/test/unexpected-error')
        def test_unexpected_error():
            raise Exception('未预期的错误')
        
        return app
    
    @pytest.fixture
    def client(self, app):
        """创建测试客户端"""
        return app.test_client()
    
    def test_validation_error_handler(self, client):
        """测试验证错误处理"""
        response = client.get('/test/validation-error')
        data = response.get_json()
        
        assert response.status_code == 400
        assert data['success'] is False
        assert data['error']['code'] == 'VALIDATION_ERROR'
        assert data['error']['message'] == '测试验证错误'
        assert data['error']['details'] == {'field': 'test'}
    
    def test_authentication_error_handler(self, client):
        """测试认证错误处理"""
        response = client.get('/test/authentication-error')
        data = response.get_json()
        
        assert response.status_code == 401
        assert data['success'] is False
        assert data['error']['code'] == 'AUTHENTICATION_ERROR'
    
    def test_resource_not_found_handler(self, client):
        """测试资源不存在错误处理"""
        response = client.get('/test/resource-not-found')
        data = response.get_json()
        
        assert response.status_code == 404
        assert data['success'] is False
        assert data['error']['code'] == 'RESOURCE_NOT_FOUND'
    
    def test_unexpected_error_handler(self, client):
        """测试未预期错误处理"""
        response = client.get('/test/unexpected-error')
        data = response.get_json()
        
        assert response.status_code == 500
        assert data['success'] is False
        assert data['error']['code'] == 'UNEXPECTED_ERROR'
    
    def test_404_handler(self, client):
        """测试 404 错误处理"""
        response = client.get('/nonexistent-route')
        data = response.get_json()
        
        assert response.status_code == 404
        assert data['success'] is False
        assert data['error']['code'] == 'NOT_FOUND'


class TestSchemaValidation:
    """测试 Schema 验证"""
    
    @pytest.fixture
    def app(self):
        """创建测试应用"""
        from app.schemas import UserRegistrationSchema
        from app.utils.validators import validate_with_schema
        from app.utils.response import success_response
        
        app = create_app('testing')
        
        @app.route('/test/register', methods=['POST'])
        @validate_with_schema(UserRegistrationSchema)
        def test_register(validated_data):
            return success_response(data=validated_data)
        
        return app
    
    @pytest.fixture
    def client(self, app):
        """创建测试客户端"""
        return app.test_client()
    
    def test_valid_registration_data(self, client):
        """测试有效的注册数据"""
        response = client.post('/test/register', json={
            'username': 'testuser',
            'password': 'password123',
            'email': 'test@example.com',
            'nickname': 'Test User'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['username'] == 'testuser'
    
    def test_missing_required_field(self, client):
        """测试缺少必填字段"""
        response = client.post('/test/register', json={
            'username': 'testuser',
            'email': 'test@example.com'
            # 缺少 password
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'VALIDATION_ERROR' in data['error']['code']
    
    def test_invalid_email_format(self, client):
        """测试无效的邮箱格式"""
        response = client.post('/test/register', json={
            'username': 'testuser',
            'password': 'password123',
            'email': 'invalid-email'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_username_too_short(self, client):
        """测试用户名太短"""
        response = client.post('/test/register', json={
            'username': 'ab',
            'password': 'password123',
            'email': 'test@example.com'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
    
    def test_password_too_short(self, client):
        """测试密码太短"""
        response = client.post('/test/register', json={
            'username': 'testuser',
            'password': 'pass1',
            'email': 'test@example.com'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
