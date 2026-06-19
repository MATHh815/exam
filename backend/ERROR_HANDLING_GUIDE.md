# 错误处理和验证系统使用指南

本文档介绍考试系统后端的错误处理和输入验证机制。

## 目录

1. [统一响应格式](#统一响应格式)
2. [自定义异常](#自定义异常)
3. [输入验证](#输入验证)
4. [全局错误处理](#全局错误处理)
5. [日志系统](#日志系统)
6. [最佳实践](#最佳实践)

## 统一响应格式

### 成功响应

```python
from app.utils.response import success_response

# 基本成功响应
return success_response(data={'user': user_dict}, message='操作成功')

# 响应格式
{
    "success": true,
    "data": {...},
    "message": "操作成功",
    "timestamp": "2024-01-01T00:00:00Z"
}
```

### 错误响应

```python
from app.utils.response import error_response

# 基本错误响应
return error_response(
    message='验证失败',
    code='VALIDATION_ERROR',
    status_code=400,
    details={'field': 'username', 'error': '用户名已存在'}
)

# 响应格式
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "验证失败",
        "details": {...}
    },
    "timestamp": "2024-01-01T00:00:00Z"
}
```

### 分页响应

```python
from app.utils.response import paginated_response

# 分页响应
return paginated_response(
    items=[...],
    total=100,
    page=1,
    page_size=20,
    message='查询成功'
)

# 响应格式
{
    "success": true,
    "data": {
        "items": [...],
        "pagination": {
            "total": 100,
            "page": 1,
            "page_size": 20,
            "total_pages": 5
        }
    },
    "message": "查询成功",
    "timestamp": "2024-01-01T00:00:00Z"
}
```

## 自定义异常

系统提供了多种自定义异常类，用于不同的错误场景。

### 可用异常类

```python
from app.utils.exceptions import (
    ValidationError,           # 验证错误 (400)
    AuthenticationError,       # 认证错误 (401)
    AuthorizationError,        # 授权错误 (403)
    ResourceNotFoundError,     # 资源不存在 (404)
    ResourceConflictError,     # 资源冲突 (409)
    BusinessLogicError,        # 业务逻辑错误 (400)
    DatabaseError              # 数据库错误 (500)
)
```

### 使用示例

```python
from app.utils.exceptions import ValidationError, ResourceNotFoundError

# 验证错误
if not username:
    raise ValidationError('用户名不能为空')

# 资源不存在
user = User.query.get(user_id)
if not user:
    raise ResourceNotFoundError('用户', user_id)

# 带详细信息的错误
raise ValidationError(
    '数据验证失败',
    details={'username': '用户名已存在', 'email': '邮箱格式不正确'}
)
```

### 异常会自动被全局错误处理器捕获并转换为统一格式的响应

## 输入验证

### 使用 Marshmallow Schema

#### 1. 定义 Schema

```python
# app/schemas/user_schema.py
from marshmallow import Schema, fields, validates, ValidationError, validate

class UserRegistrationSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=20))
    password = fields.Str(required=True, validate=validate.Length(min=8))
    email = fields.Email(required=True)
    nickname = fields.Str(validate=validate.Length(max=50))
    
    @validates('username')
    def validate_username_format(self, value):
        if not value.isalnum():
            raise ValidationError('用户名只能包含字母和数字')
```

#### 2. 在路由中使用 Schema

```python
from app.utils.validators import validate_with_schema
from app.schemas import UserRegistrationSchema

@app.route('/register', methods=['POST'])
@validate_with_schema(UserRegistrationSchema)
def register(validated_data):
    # validated_data 已经过验证和清洗
    user = AuthService.register(**validated_data)
    return success_response(data={'user': user.to_dict()})
```

### 验证工具函数

```python
from app.utils.validators import (
    validate_email,
    validate_password,
    validate_username,
    validate_pagination_params,
    validate_required_fields
)

# 验证邮箱
if not validate_email(email):
    raise ValidationError('邮箱格式不正确')

# 验证密码强度
is_valid, error_msg = validate_password(password)
if not is_valid:
    raise ValidationError(error_msg)

# 验证分页参数
page, page_size = validate_pagination_params()

# 验证必填字段
validate_required_fields(data, ['username', 'password', 'email'])
```

## 全局错误处理

系统自动处理以下错误：

### HTTP 错误

- **400 Bad Request**: 请求参数错误
- **401 Unauthorized**: 未授权访问
- **403 Forbidden**: 禁止访问
- **404 Not Found**: 资源不存在
- **405 Method Not Allowed**: 请求方法不允许
- **409 Conflict**: 资源冲突
- **500 Internal Server Error**: 服务器内部错误

### 自定义异常

所有继承自 `APIException` 的异常都会被自动处理并返回统一格式的响应。

### 数据库错误

SQLAlchemy 错误会被自动捕获，数据库会话会自动回滚。

### 未预期的异常

所有未捕获的异常都会被记录到日志，并返回 500 错误响应。

## 日志系统

### 日志级别

- **DEBUG**: 详细的调试信息
- **INFO**: 一般信息
- **WARNING**: 警告信息
- **ERROR**: 错误信息
- **CRITICAL**: 严重错误

### 日志文件

- `logs/app.log`: 所有日志
- `logs/app_error.log`: 仅错误日志

### 日志配置

在 `config.py` 中配置：

```python
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = 'logs/app.log'
```

### 在代码中使用日志

```python
from flask import current_app

# 记录信息
current_app.logger.info('用户登录成功')

# 记录警告
current_app.logger.warning('密码错误次数过多')

# 记录错误
current_app.logger.error('数据库连接失败', exc_info=True)
```

### 自动日志记录

系统自动记录：

- 应用启动信息
- 每个请求的方法和路径
- 每个响应的状态码
- 所有错误和异常

## 中间件

### 请求时间记录

```python
from app.utils.middleware import log_request_time

@app.route('/users')
@log_request_time
def get_users():
    # 自动记录请求处理时间
    return success_response(data={'users': users})
```

### Content-Type 验证

```python
from app.utils.middleware import validate_content_type

@app.route('/users', methods=['POST'])
@validate_content_type('application/json')
def create_user():
    # 自动验证 Content-Type
    data = request.get_json()
    return success_response(data={'user': user})
```

### 速率限制

```python
from app.utils.middleware import rate_limit_by_ip

@app.route('/login', methods=['POST'])
@rate_limit_by_ip(max_requests=5, window_seconds=60)
def login():
    # 限制每个 IP 每分钟最多 5 次请求
    return success_response(data={'token': token})
```

## 最佳实践

### 1. 使用自定义异常而不是直接返回错误响应

❌ 不推荐：
```python
@app.route('/users/<int:user_id>')
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return error_response('用户不存在', status_code=404)
    return success_response(data={'user': user.to_dict()})
```

✅ 推荐：
```python
@app.route('/users/<int:user_id>')
def get_user(user_id):
    user = User.query.get(user_id)
    if not user:
        raise ResourceNotFoundError('用户', user_id)
    return success_response(data={'user': user.to_dict()})
```

### 2. 使用 Schema 验证而不是手动验证

❌ 不推荐：
```python
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data.get('username'):
        raise ValidationError('缺少用户名')
    if len(data['username']) < 3:
        raise ValidationError('用户名太短')
    # ... 更多验证
```

✅ 推荐：
```python
@app.route('/register', methods=['POST'])
@validate_with_schema(UserRegistrationSchema)
def register(validated_data):
    # 数据已验证
    user = AuthService.register(**validated_data)
    return success_response(data={'user': user.to_dict()})
```

### 3. 在服务层抛出异常，在路由层处理响应

```python
# services/auth_service.py
class AuthService:
    @staticmethod
    def login(username, password):
        user = User.query.filter_by(username=username).first()
        if not user:
            raise AuthenticationError('用户名或密码错误')
        if not user.check_password(password):
            raise AuthenticationError('用户名或密码错误')
        return user, access_token, refresh_token

# routes/auth.py
@app.route('/login', methods=['POST'])
@validate_with_schema(UserLoginSchema)
def login(validated_data):
    user, access_token, refresh_token = AuthService.login(
        validated_data['username'],
        validated_data['password']
    )
    return success_response(data={
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    })
```

### 4. 记录有意义的日志

```python
# 记录关键操作
current_app.logger.info(f'用户 {user.username} 登录成功')

# 记录错误时包含上下文
current_app.logger.error(
    f'用户 {user_id} 更新失败: {str(e)}',
    exc_info=True
)

# 不要记录敏感信息
# ❌ current_app.logger.info(f'密码: {password}')
# ✅ current_app.logger.info('密码验证成功')
```

### 5. 使用统一的响应格式

所有 API 都应该使用 `success_response` 和 `error_response`，确保响应格式一致。

## 完整示例

```python
from flask import Blueprint
from app.utils.response import success_response
from app.utils.validators import validate_with_schema
from app.utils.middleware import log_request_time, validate_content_type
from app.utils.exceptions import ResourceNotFoundError
from app.schemas import UserRegistrationSchema
from app.services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@validate_content_type('application/json')
@validate_with_schema(UserRegistrationSchema)
@log_request_time
def register(validated_data):
    """用户注册"""
    user = AuthService.register(**validated_data)
    return success_response(
        data={'user': user.to_dict()},
        message='注册成功',
        status_code=201
    )
```

## 测试

### 测试错误处理

```python
def test_validation_error(client):
    response = client.post('/api/auth/register', json={
        'username': 'ab',  # 太短
        'password': 'password123',
        'email': 'test@example.com'
    })
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'VALIDATION_ERROR' in data['error']['code']

def test_resource_not_found(client):
    response = client.get('/api/users/99999')
    assert response.status_code == 404
    data = response.get_json()
    assert data['success'] is False
    assert 'NOT_FOUND' in data['error']['code']
```

## 总结

通过使用统一的错误处理和验证系统：

1. **一致性**: 所有 API 返回统一格式的响应
2. **可维护性**: 集中管理错误处理逻辑
3. **可读性**: 代码更简洁，意图更清晰
4. **可测试性**: 更容易编写和维护测试
5. **可调试性**: 详细的日志记录帮助快速定位问题

参考 `app/routes/auth_improved.py` 查看完整的使用示例。
