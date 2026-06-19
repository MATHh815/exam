"""
错题分析路由
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from app.services.wrong_analysis_service import WrongAnalysisService
from app.utils.decorators import handle_errors

wrong_analysis_bp = Blueprint('wrong_analysis', __name__, url_prefix='/api/statistics/wrong-questions')


@wrong_analysis_bp.route('/overview', methods=['GET'])
@jwt_required()
@handle_errors
def get_wrong_overview():
    """
    获取错题概览
    
    返回错题总数、错题率、改善率等统计数据
    """
    user_id = get_jwt_identity()
    days = request.args.get('days', 30, type=int)
    
    # 参数验证
    if days < 1 or days > 365:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_PARAMETER',
                'message': '天数参数必须在 1-365 之间'
            }
        }), 400
    
    data = WrongAnalysisService.get_overview(user_id, days)
    
    return jsonify({
        'success': True,
        'data': data,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })


@wrong_analysis_bp.route('/distribution', methods=['GET'])
@jwt_required()
@handle_errors
def get_wrong_distribution():
    """
    获取错题分布
    
    按科目、题型或知识点统计错题分布
    """
    user_id = get_jwt_identity()
    dimension = request.args.get('dimension', 'subject')
    days = request.args.get('days', 30, type=int)
    
    # 参数验证
    if dimension not in ['subject', 'type', 'knowledge']:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_PARAMETER',
                'message': '维度参数必须是 subject、type 或 knowledge'
            }
        }), 400
    
    if days < 1 or days > 365:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_PARAMETER',
                'message': '天数参数必须在 1-365 之间'
            }
        }), 400
    
    data = WrongAnalysisService.get_distribution(user_id, dimension, days)
    
    return jsonify({
        'success': True,
        'data': data,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })


@wrong_analysis_bp.route('/frequent', methods=['GET'])
@jwt_required()
@handle_errors
def get_frequent_wrong():
    """
    获取高频错题
    
    返回错误次数最多的题目列表
    """
    user_id = get_jwt_identity()
    limit = request.args.get('limit', 10, type=int)
    
    # 参数验证
    if limit < 1 or limit > 50:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_PARAMETER',
                'message': '数量参数必须在 1-50 之间'
            }
        }), 400
    
    data = WrongAnalysisService.get_frequent_wrong(user_id, limit)
    
    return jsonify({
        'success': True,
        'data': data,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })


@wrong_analysis_bp.route('/trend', methods=['GET'])
@jwt_required()
@handle_errors
def get_wrong_trend():
    """
    获取错题趋势
    
    返回每日错题数和错题率的变化趋势
    """
    user_id = get_jwt_identity()
    days = request.args.get('days', 30, type=int)
    
    # 参数验证
    if days < 7 or days > 365:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_PARAMETER',
                'message': '天数参数必须在 7-365 之间'
            }
        }), 400
    
    data = WrongAnalysisService.get_trend(user_id, days)
    
    return jsonify({
        'success': True,
        'data': data,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })


@wrong_analysis_bp.route('/weak-points', methods=['GET'])
@jwt_required()
@handle_errors
def get_weak_points():
    """
    获取薄弱知识点
    
    返回掌握度最低的知识点列表
    """
    user_id = get_jwt_identity()
    limit = request.args.get('limit', 10, type=int)
    
    # 参数验证
    if limit < 1 or limit > 50:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_PARAMETER',
                'message': '数量参数必须在 1-50 之间'
            }
        }), 400
    
    data = WrongAnalysisService.get_weak_points(user_id, limit)
    
    return jsonify({
        'success': True,
        'data': data,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })


@wrong_analysis_bp.route('/suggestions', methods=['GET'])
@jwt_required()
@handle_errors
def get_learning_suggestions():
    """
    获取学习建议
    
    基于错题分析生成个性化学习建议
    """
    user_id = get_jwt_identity()
    
    data = WrongAnalysisService.get_suggestions(user_id)
    
    return jsonify({
        'success': True,
        'data': data,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })
