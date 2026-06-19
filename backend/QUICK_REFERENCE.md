# 错误处理和验证系统 - 快速参考

## 导入

```python
# 异常
from app.utils.exceptions import (
    ValidationError, AuthenticationError, AuthorizationError,
    ResourceNotFoundError, ResourceConflictError, BusinessLogicError
)

# 响应
from app.utils.response import success_response, error_response, paginated_response

# 验证器
from app.utils.validators import validate_with_schema, validate_email, validate_password

# 中间件
from app.utils.middleware import log_request_time, validate_content_type

# Schemas
from app.schemas import UserRegistrationSchema, UserLoginSchema
```

## 路由模板

```python
@bp.route('/resource', methods=['POST'])
@validate_content_type('application/json')
@validate_with_schema(ResourceSchema)
@log_request_time
def create_resource(validated_data):
    """创建资源"""
    resource = ResourceService.create(**validated_data)
    return success_response(
        data={'resource': resource.to_dict()},
        message='创建成功',
        status_code=201
    )
```

## 抛出异常

```python
# 验证错误
raise ValidationError('数据无效', details={'field': 'error'})

# 认证错误
raise AuthenticationError('认证失败')

# 资源不存在
raise ResourceNotFoundError('用户', user_id)

# 资源冲突
raise ResourceConflictError('用户名已存在')
```

## 响应格式

```python
# 成功
return success_response(data={'key': 'value'}, message='成功')

# 错误（通常不需要，抛出异常即可）
return error_response('错误', code='ERROR_CODE', status_code=400)

# 分页
return paginated_response(items=list, total=100, page=1, page_size=20)
```

## Schema 示例

```python
from marshmallow import Schema, fields, validates, ValidationError, validate

class MySchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True)
    age = fields.Int(validate=validate.Range(min=0, max=150))
    
    @validates('name')
    def validate_name(self, value):
        if value.lower() == 'admin':
            raise ValidationError('名称不能为 admin')
```

## 日志记录

```python
from flask import current_app

current_app.logger.debug('调试信息')
current_app.logger.info('一般信息')
current_app.logger.warning('警告信息')
current_app.logger.error('错误信息', exc_info=True)
```

## 常见模式

### 服务层

```python
class MyService:
    @staticmethod
    def get_by_id(resource_id):
        resource = Resource.query.get(resource_id)
        if not resource:
            raise ResourceNotFoundError('资源', resource_id)
        return resource
    
    @staticmethod
    def create(name, email):
        if Resource.query.filter_by(email=email).first():
            raise ResourceConflictError('邮箱已存在')
        
        resource = Resource(name=name, email=email)
        db.session.add(resource)
        db.session.commit()
        return resource
```

### 路由层

```python
@bp.route('/resources/<int:id>')
@jwt_required_with_user
def get_resource(current_user, id):
    resource = MyService.get_by_id(id)
    return success_response(data={'resource': resource.to_dict()})

@bp.route('/resources', methods=['POST'])
@validate_with_schema(ResourceSchema)
def create_resource(validated_data):
    resource = MyService.create(**validated_data)
    return success_response(
        data={'resource': resource.to_dict()},
        status_code=201
    )
```

## 测试

```python
def test_validation_error(client):
    response = client.post('/api/resource', json={'invalid': 'data'})
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'VALIDATION_ERROR' in data['error']['code']

def test_resource_not_found(client):
    response = client.get('/api/resources/99999')
    assert response.status_code == 404
    data = response.get_json()
    assert data['success'] is False
```

## 配置

```python
# config.py
LOG_LEVEL = 'INFO'
LOG_FILE = 'logs/app.log'
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
```

## 记住

1. ✅ 在服务层抛出异常
2. ✅ 在路由层使用装饰器验证
3. ✅ 使用 success_response 返回成功
4. ✅ 让全局处理器处理异常
5. ✅ 记录有意义的日志
6. ❌ 不要在路由层手动验证
7. ❌ 不要手动构建响应格式
8. ❌ 不要记录敏感信息
