"""成就相关路由"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.achievement_service import AchievementService


achievements_bp = Blueprint('achievements', __name__, url_prefix='/api/achievements')


@achievements_bp.route('', methods=['GET'])
@jwt_required()
def get_achievements():
    """获取所有成就定义
    
    Query Parameters:
        category (str): 成就类别筛选 (learning, streak, milestone)
    
    Returns:
        JSON: 成就列表
    """
    try:
        category = request.args.get('category')
        
        # 验证类别
        if category and category not in ['learning', 'streak', 'milestone']:
            return jsonify({
                'success': False,
                'error': 'Invalid category. Must be one of: learning, streak, milestone'
            }), 400
        
        achievements = AchievementService.get_all_achievements(category=category)
        
        return jsonify({
            'success': True,
            'data': {
                'achievements': achievements,
                'total': len(achievements)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@achievements_bp.route('/<int:achievement_id>', methods=['GET'])
@jwt_required()
def get_achievement(achievement_id):
    """获取成就详情
    
    Args:
        achievement_id: 成就ID
    
    Returns:
        JSON: 成就详细信息
    """
    try:
        achievement = AchievementService.get_achievement(achievement_id)
        
        if not achievement:
            return jsonify({
                'success': False,
                'error': 'Achievement not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': achievement
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@achievements_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user_achievements():
    """获取用户成就
    
    返回三个类别：
    - earned: 已解锁的成就
    - in_progress: 进行中的成就
    - locked: 未开始的成就
    
    Returns:
        JSON: 用户成就信息
    """
    try:
        user_id = get_jwt_identity()
        
        achievements = AchievementService.get_user_achievements(user_id)
        
        return jsonify({
            'success': True,
            'data': achievements
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@achievements_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_achievement_stats():
    """获取用户成就统计
    
    Returns:
        JSON: 成就统计信息
    """
    try:
        user_id = get_jwt_identity()
        
        stats = AchievementService.get_achievement_stats(user_id)
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@achievements_bp.route('/check', methods=['POST'])
@jwt_required()
def check_achievements():
    """手动检查成就（用于测试）
    
    Request Body:
        event_type (str): 事件类型
        event_data (dict): 事件数据
    
    Returns:
        JSON: 新解锁的成就列表
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        event_type = data.get('event_type', 'manual_check')
        event_data = data.get('event_data', {})
        
        newly_unlocked = AchievementService.check_achievements(
            user_id=user_id,
            event_type=event_type,
            event_data=event_data
        )
        
        return jsonify({
            'success': True,
            'data': {
                'newly_unlocked': newly_unlocked,
                'count': len(newly_unlocked)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
