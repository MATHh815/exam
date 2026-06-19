"""自定义异常类"""


class APIException(Exception):
    """API 异常基类"""
    
    def __init__(self, message, code=None, status_code=400, details=None):
        """初始化异常
        
        Args:
            message: 错误消息
            code: 错误代码
            status_code: HTTP 状态码
            details: 详细错误信息
        """
        super().__init__(message)
        self.message = message
        self.code = code or self.__class__.__name__.upper()
        self.status_code = status_code
        self.details = details


class ValidationError(APIException):
    """验证错误"""
    
    def __init__(self, message, details=None):
        super().__init__(
            message=message,
            code='VALIDATION_ERROR',
            status_code=400,
            details=details
        )


class AuthenticationError(APIException):
    """认证错误"""
    
    def __init__(self, message='认证失败', details=None):
        super().__init__(
            message=message,
            code='AUTHENTICATION_ERROR',
            status_code=401,
            details=details
        )


class AuthorizationError(APIException):
    """授权错误"""
    
    def __init__(self, message='权限不足', details=None):
        super().__init__(
            message=message,
            code='AUTHORIZATION_ERROR',
            status_code=403,
            details=details
        )


class ResourceNotFoundError(APIException):
    """资源不存在错误"""
    
    def __init__(self, resource_type, resource_id=None):
        message = f'{resource_type}不存在'
        if resource_id:
            message = f'{resource_type} (ID: {resource_id}) 不存在'
        super().__init__(
            message=message,
            code='RESOURCE_NOT_FOUND',
            status_code=404
        )


class ResourceConflictError(APIException):
    """资源冲突错误"""
    
    def __init__(self, message, details=None):
        super().__init__(
            message=message,
            code='RESOURCE_CONFLICT',
            status_code=409,
            details=details
        )


class BusinessLogicError(APIException):
    """业务逻辑错误"""
    
    def __init__(self, message, details=None):
        super().__init__(
            message=message,
            code='BUSINESS_LOGIC_ERROR',
            status_code=400,
            details=details
        )


class DatabaseError(APIException):
    """数据库错误"""
    
    def __init__(self, message='数据库操作失败', details=None):
        super().__init__(
            message=message,
            code='DATABASE_ERROR',
            status_code=500,
            details=details
        )
