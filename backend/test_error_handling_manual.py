"""手动测试错误处理和验证系统"""
from app import create_app, db
from app.utils.exceptions import ValidationError, ResourceNotFoundError
from app.utils.response import success_response, error_response, paginated_response
from app.utils.validators import validate_email, validate_password, validate_username


def test_exceptions():
    """测试自定义异常"""
    print("=" * 50)
    print("测试自定义异常")
    print("=" * 50)
    
    # 测试 ValidationError
    try:
        raise ValidationError('测试验证错误', details={'field': 'username'})
    except ValidationError as e:
        print(f"[OK] ValidationError: {e.message}, code: {e.code}, status: {e.status_code}")
        print(f"  Details: {e.details}")
    
    # 测试 ResourceNotFoundError
    try:
        raise ResourceNotFoundError('用户', 123)
    except ResourceNotFoundError as e:
        print(f"[OK] ResourceNotFoundError: {e.message}, code: {e.code}, status: {e.status_code}")
    
    print()


def test_validators():
    """测试验证器"""
    print("=" * 50)
    print("测试验证器")
    print("=" * 50)
    
    # 测试邮箱验证
    print("邮箱验证:")
    print(f"  test@example.com: {validate_email('test@example.com')}")
    print(f"  invalid-email: {validate_email('invalid-email')}")
    
    # 测试密码验证
    print("\n密码验证:")
    is_valid, error = validate_password('password123')
    print(f"  password123: valid={is_valid}, error={error}")
    
    is_valid, error = validate_password('pass1')
    print(f"  pass1: valid={is_valid}, error={error}")
    
    is_valid, error = validate_password('12345678')
    print(f"  12345678: valid={is_valid}, error={error}")
    
    # 测试用户名验证
    print("\n用户名验证:")
    is_valid, error = validate_username('user123')
    print(f"  user123: valid={is_valid}, error={error}")
    
    is_valid, error = validate_username('ab')
    print(f"  ab: valid={is_valid}, error={error}")
    
    is_valid, error = validate_username('user@123')
    print(f"  user@123: valid={is_valid}, error={error}")
    
    print()


def test_responses():
    """测试响应格式"""
    print("=" * 50)
    print("测试响应格式")
    print("=" * 50)
    
    app = create_app('testing')
    
    with app.app_context():
        # 测试成功响应
        response, status_code = success_response(
            data={'user': {'id': 1, 'username': 'test'}},
            message='操作成功'
        )
        data = response.get_json()
        print("成功响应:")
        print(f"  Status: {status_code}")
        print(f"  Success: {data['success']}")
        print(f"  Data: {data['data']}")
        print(f"  Message: {data['message']}")
        print(f"  Timestamp: {data['timestamp']}")
        
        # 测试错误响应
        response, status_code = error_response(
            message='验证失败',
            code='VALIDATION_ERROR',
            status_code=400,
            details={'field': 'username', 'error': '用户名已存在'}
        )
        data = response.get_json()
        print("\n错误响应:")
        print(f"  Status: {status_code}")
        print(f"  Success: {data['success']}")
        print(f"  Error Code: {data['error']['code']}")
        print(f"  Error Message: {data['error']['message']}")
        print(f"  Error Details: {data['error']['details']}")
        
        # 测试分页响应
        items = [{'id': i, 'name': f'Item {i}'} for i in range(1, 21)]
        response, status_code = paginated_response(
            items=items,
            total=100,
            page=1,
            page_size=20
        )
        data = response.get_json()
        print("\n分页响应:")
        print(f"  Status: {status_code}")
        print(f"  Items count: {len(data['data']['items'])}")
        print(f"  Total: {data['data']['pagination']['total']}")
        print(f"  Page: {data['data']['pagination']['page']}")
        print(f"  Page size: {data['data']['pagination']['page_size']}")
        print(f"  Total pages: {data['data']['pagination']['total_pages']}")
    
    print()


def test_schemas():
    """测试 Schema 验证"""
    print("=" * 50)
    print("测试 Schema 验证")
    print("=" * 50)
    
    from app.schemas import UserRegistrationSchema
    from marshmallow import ValidationError as MarshmallowValidationError
    
    schema = UserRegistrationSchema()
    
    # 测试有效数据
    print("有效数据:")
    try:
        data = {
            'username': 'testuser',
            'password': 'password123',
            'email': 'test@example.com',
            'nickname': 'Test User'
        }
        result = schema.load(data)
        print(f"  ✓ 验证通过: {result}")
    except MarshmallowValidationError as e:
        print(f"  ✗ 验证失败: {e.messages}")
    
    # 测试缺少必填字段
    print("\n缺少必填字段:")
    try:
        data = {
            'username': 'testuser',
            'email': 'test@example.com'
            # 缺少 password
        }
        result = schema.load(data)
        print(f"  ✓ 验证通过: {result}")
    except MarshmallowValidationError as e:
        print(f"  ✗ 验证失败: {e.messages}")
    
    # 测试无效邮箱
    print("\n无效邮箱:")
    try:
        data = {
            'username': 'testuser',
            'password': 'password123',
            'email': 'invalid-email'
        }
        result = schema.load(data)
        print(f"  ✓ 验证通过: {result}")
    except MarshmallowValidationError as e:
        print(f"  ✗ 验证失败: {e.messages}")
    
    # 测试用户名太短
    print("\n用户名太短:")
    try:
        data = {
            'username': 'ab',
            'password': 'password123',
            'email': 'test@example.com'
        }
        result = schema.load(data)
        print(f"  ✓ 验证通过: {result}")
    except MarshmallowValidationError as e:
        print(f"  ✗ 验证失败: {e.messages}")
    
    # 测试密码太弱
    print("\n密码太弱:")
    try:
        data = {
            'username': 'testuser',
            'password': 'pass1',
            'email': 'test@example.com'
        }
        result = schema.load(data)
        print(f"  ✓ 验证通过: {result}")
    except MarshmallowValidationError as e:
        print(f"  ✗ 验证失败: {e.messages}")
    
    print()


def test_global_error_handlers():
    """测试全局错误处理器"""
    print("=" * 50)
    print("测试全局错误处理器")
    print("=" * 50)
    
    app = create_app('testing')
    
    # 添加测试路由
    @app.route('/test/validation-error')
    def test_validation_error():
        raise ValidationError('测试验证错误', details={'field': 'test'})
    
    @app.route('/test/resource-not-found')
    def test_resource_not_found():
        raise ResourceNotFoundError('测试资源', 123)
    
    client = app.test_client()
    
    # 测试 ValidationError 处理
    print("ValidationError 处理:")
    response = client.get('/test/validation-error')
    data = response.get_json()
    print(f"  Status: {response.status_code}")
    print(f"  Success: {data['success']}")
    print(f"  Error Code: {data['error']['code']}")
    print(f"  Error Message: {data['error']['message']}")
    
    # 测试 ResourceNotFoundError 处理
    print("\nResourceNotFoundError 处理:")
    response = client.get('/test/resource-not-found')
    data = response.get_json()
    print(f"  Status: {response.status_code}")
    print(f"  Success: {data['success']}")
    print(f"  Error Code: {data['error']['code']}")
    print(f"  Error Message: {data['error']['message']}")
    
    # 测试 404 处理
    print("\n404 处理:")
    response = client.get('/nonexistent-route')
    data = response.get_json()
    print(f"  Status: {response.status_code}")
    print(f"  Success: {data['success']}")
    print(f"  Error Code: {data['error']['code']}")
    
    print()


if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("错误处理和验证系统测试")
    print("=" * 50 + "\n")
    
    test_exceptions()
    test_validators()
    test_responses()
    test_schemas()
    test_global_error_handlers()
    
    print("=" * 50)
    print("所有测试完成！")
    print("=" * 50)
