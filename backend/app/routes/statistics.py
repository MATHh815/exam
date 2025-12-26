"""统计相关 API 路由"""
from datetime import datetime, date
from flask import Blueprint, request, jsonify
from app.services.statistics_service import StatisticsService
from app.utils.decorators import jwt_required_with_user

statistics_bp = Blueprint('statistics', __name__)


@statistics_bp.route('/overview', methods=['GET'])
@jwt_required_with_user
def get_overview(current_user):
    """获取学习概览统计
    
    GET /api/statistics/overview?start_date=2024-01-01&end_date=2024-12-31
    
    Query Parameters:
        - start_date: 开始日期（可选，格式：YYYY-MM-DD）
        - end_date: 结束日期（可选，格式：YYYY-MM-DD）
    
    Response:
        {
            "success": true,
            "data": {
                "total_practice": 100,
                "total_correct": 80,
                "total_duration": 120,
                "total_exams": 5,
                "accuracy": 80.0,
                "study_days": 10,
                "wrong_count": 20
            }
        }
    """
    try:
        # 获取日期参数
        start_date = None
        end_date = None
        
        if request.args.get('start_date'):
            try:
                start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'INVALID_DATE_FORMAT',
                        'message': '开始日期格式错误，应为 YYYY-MM-DD'
                    }
                }), 400
        
        if request.args.get('end_date'):
            try:
                end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'INVALID_DATE_FORMAT',
                        'message': '结束日期格式错误，应为 YYYY-MM-DD'
                    }
                }), 400
        
        # 验证日期范围
        if start_date and end_date and start_date > end_date:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_DATE_RANGE',
                    'message': '开始日期不能晚于结束日期'
                }
            }), 400
        
        # 获取统计数据
        overview = StatisticsService.get_overview(
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify({
            'success': True,
            'data': overview
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_OVERVIEW_FAILED',
                'message': '获取学习概览失败',
                'details': str(e)
            }
        }), 500


@statistics_bp.route('/knowledge', methods=['GET'])
@jwt_required_with_user
def get_knowledge_analysis(current_user):
    """获取知识点分析
    
    GET /api/statistics/knowledge?start_date=2024-01-01&end_date=2024-12-31
    
    Query Parameters:
        - start_date: 开始日期（可选，格式：YYYY-MM-DD）
        - end_date: 结束日期（可选，格式：YYYY-MM-DD）
    
    Response:
        {
            "success": true,
            "data": {
                "knowledge_points": [
                    {
                        "subject": "行测",
                        "chapter": "数量关系",
                        "total_count": 50,
                        "correct_count": 30,
                        "accuracy": 60.0,
                        "is_weak": false
                    },
                    ...
                ],
                "count": 10
            }
        }
    """
    try:
        # 获取日期参数
        start_date = None
        end_date = None
        
        if request.args.get('start_date'):
            try:
                start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'INVALID_DATE_FORMAT',
                        'message': '开始日期格式错误，应为 YYYY-MM-DD'
                    }
                }), 400
        
        if request.args.get('end_date'):
            try:
                end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'INVALID_DATE_FORMAT',
                        'message': '结束日期格式错误，应为 YYYY-MM-DD'
                    }
                }), 400
        
        # 验证日期范围
        if start_date and end_date and start_date > end_date:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_DATE_RANGE',
                    'message': '开始日期不能晚于结束日期'
                }
            }), 400
        
        # 获取知识点分析
        knowledge_points = StatisticsService.get_knowledge_analysis(
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify({
            'success': True,
            'data': {
                'knowledge_points': knowledge_points,
                'count': len(knowledge_points)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_KNOWLEDGE_FAILED',
                'message': '获取知识点分析失败',
                'details': str(e)
            }
        }), 500


@statistics_bp.route('/trend', methods=['GET'])
@jwt_required_with_user
def get_trend(current_user):
    """获取学习趋势
    
    GET /api/statistics/trend?days=7
    
    Query Parameters:
        - days: 天数（默认7天，最多365天）
    
    Response:
        {
            "success": true,
            "data": {
                "trend": [
                    {
                        "date": "2024-01-01",
                        "practice_count": 10,
                        "correct_count": 8,
                        "accuracy": 80.0,
                        "study_duration": 30,
                        "exam_count": 1
                    },
                    ...
                ],
                "days": 7
            }
        }
    """
    try:
        # 获取天数参数
        days = request.args.get('days', 7, type=int)
        
        # 验证天数范围
        if days <= 0:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_DAYS',
                    'message': '天数必须大于0'
                }
            }), 400
        
        # 限制最大天数
        if days > 365:
            days = 365
        
        # 获取学习趋势
        trend = StatisticsService.get_trend(
            user_id=current_user.id,
            days=days
        )
        
        return jsonify({
            'success': True,
            'data': {
                'trend': trend,
                'days': days
            }
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_PARAMETER',
                'message': str(e)
            }
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_TREND_FAILED',
                'message': '获取学习趋势失败',
                'details': str(e)
            }
        }), 500


@statistics_bp.route('/exams', methods=['GET'])
@jwt_required_with_user
def get_exam_statistics(current_user):
    """获取考试统计
    
    GET /api/statistics/exams?start_date=2024-01-01&end_date=2024-12-31
    
    Query Parameters:
        - start_date: 开始日期（可选，格式：YYYY-MM-DD）
        - end_date: 结束日期（可选，格式：YYYY-MM-DD）
    
    Response:
        {
            "success": true,
            "data": {
                "total_exams": 5,
                "average_score": 85.5,
                "average_accuracy": 85.5,
                "highest_score": 95.0,
                "lowest_score": 75.0,
                "recent_exams": [...]
            }
        }
    """
    try:
        # 获取日期参数
        start_date = None
        end_date = None
        
        if request.args.get('start_date'):
            try:
                start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'INVALID_DATE_FORMAT',
                        'message': '开始日期格式错误，应为 YYYY-MM-DD'
                    }
                }), 400
        
        if request.args.get('end_date'):
            try:
                end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d').date()
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'INVALID_DATE_FORMAT',
                        'message': '结束日期格式错误，应为 YYYY-MM-DD'
                    }
                }), 400
        
        # 验证日期范围
        if start_date and end_date and start_date > end_date:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_DATE_RANGE',
                    'message': '开始日期不能晚于结束日期'
                }
            }), 400
        
        # 获取考试统计
        exam_stats = StatisticsService.get_exam_statistics(
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify({
            'success': True,
            'data': exam_stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_EXAM_STATS_FAILED',
                'message': '获取考试统计失败',
                'details': str(e)
            }
        }), 500
