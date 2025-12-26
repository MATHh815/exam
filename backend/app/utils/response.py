"""统一 API 响应格式"""
from datetime import datetime
from flask import jsonify


def success_response(data=None, message=None, status_code=200):
    """成功响应
    
    Args:
        data: 响应数据
        message: 成功消息
        status_code: HTTP 状态码
    
    Returns:
        Flask Response 对象
    """
    response = {
        'success': True,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    
    if data is not None:
        response['data'] = data
    
    if message:
        response['message'] = message
    
    return jsonify(response), status_code


def error_response(message, code=None, status_code=400, details=None):
    """错误响应
    
    Args:
        message: 错误消息
        code: 错误代码
        status_code: HTTP 状态码
        details: 详细错误信息
    
    Returns:
        Flask Response 对象
    """
    response = {
        'success': False,
        'error': {
            'code': code or 'ERROR',
            'message': message
        },
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    
    if details:
        response['error']['details'] = details
    
    return jsonify(response), status_code


def paginated_response(items, total, page, page_size, message=None):
    """分页响应
    
    Args:
        items: 数据列表
        total: 总数量
        page: 当前页码
        page_size: 每页大小
        message: 消息
    
    Returns:
        Flask Response 对象
    """
    data = {
        'items': items,
        'pagination': {
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size if page_size > 0 else 0
        }
    }
    
    return success_response(data=data, message=message)
