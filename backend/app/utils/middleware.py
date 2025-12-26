"""中间件函数"""
import time
from functools import wraps
from flask import request, g, current_app
from app.utils.exceptions import ValidationError


def log_request_time(f):
    """记录请求处理时间的装饰器
    
    Usage:
        @log_request_time
        def my_route():
            pass
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        elapsed_time = time.time() - start_time
        
        current_app.logger.info(
            f'请求处理完成: {request.method} {request.path} - '
            f'耗时: {elapsed_time:.3f}s'
        )
        
        return result
    return wrapper


def validate_content_type(content_type='application/json'):
    """验证请求 Content-Type 的装饰器
    
    Args:
        content_type: 期望的 Content-Type
    
    Usage:
        @validate_content_type('application/json')
        def my_route():
            pass
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if request.method in ['POST', 'PUT', 'PATCH']:
                if not request.is_json:
                    raise ValidationError(
                        f'Content-Type 必须是 {content_type}',
                        details={'received': request.content_type}
                    )
            return f(*args, **kwargs)
        return wrapper
    return decorator


def rate_limit_by_ip(max_requests=100, window_seconds=60):
    """基于 IP 的简单速率限制装饰器
    
    Args:
        max_requests: 时间窗口内最大请求数
        window_seconds: 时间窗口（秒）
    
    Note: 这是一个简单实现，生产环境建议使用 Redis
    
    Usage:
        @rate_limit_by_ip(max_requests=10, window_seconds=60)
        def my_route():
            pass
    """
    def decorator(f):
        # 存储请求记录 {ip: [(timestamp, count)]}
        request_records = {}
        
        @wraps(f)
        def wrapper(*args, **kwargs):
            client_ip = request.remote_addr
            current_time = time.time()
            
            # 清理过期记录
            if client_ip in request_records:
                request_records[client_ip] = [
                    (ts, count) for ts, count in request_records[client_ip]
                    if current_time - ts < window_seconds
                ]
            else:
                request_records[client_ip] = []
            
            # 计算当前窗口内的请求数
            total_requests = sum(count for _, count in request_records[client_ip])
            
            if total_requests >= max_requests:
                raise ValidationError(
                    '请求过于频繁，请稍后再试',
                    details={
                        'max_requests': max_requests,
                        'window_seconds': window_seconds
                    }
                )
            
            # 记录本次请求
            request_records[client_ip].append((current_time, 1))
            
            return f(*args, **kwargs)
        
        return wrapper
    return decorator
