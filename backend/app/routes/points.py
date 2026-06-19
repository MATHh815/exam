"""积分相关路由"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.points_service import PointsService


points_bp = Blueprint('points', __name__, url_prefix='/api/points')


@points_bp.route('', methods=['GET'])
@jwt_required()
def get_user_points():
    """获取用户积分信息
    
    Returns:
        JSON: 用户积分详细信息
    """
    try:
        user_id = get_jwt_identity()
        
        # 获取积分信息
        points_info = PointsService.get_user_points(user_id)
        
        return jsonify({
            'success': True,
            'data': points_info
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@points_bp.route('/history', methods=['GET'])
@jwt_required()
def get_point_history():
    """获取积分历史记录
    
    Query Parameters:
        limit (int): 返回记录数量，默认50
        offset (int): 偏移量，默认0
    
    Returns:
        JSON: 积分历史记录列表
    """
    try:
        user_id = get_jwt_identity()
        
        # 获取查询参数
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # 验证参数
        if limit < 1 or limit > 100:
            return jsonify({
                'success': False,
                'error': 'Limit must be between 1 and 100'
            }), 400
        
        if offset < 0:
            return jsonify({
                'success': False,
                'error': 'Offset must be non-negative'
            }), 400
        
        # 获取积分历史
        history = PointsService.get_point_history(
            user_id=user_id,
            limit=limit,
            offset=offset
        )
        
        return jsonify({
            'success': True,
            'data': history
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@points_bp.route('/leaderboard', methods=['GET'])
@jwt_required()
def get_leaderboard():
    """获取积分排行榜
    
    Query Parameters:
        limit (int): 返回记录数量，默认10
    
    Returns:
        JSON: 积分排行榜
    """
    try:
        from app.models.achievement import UserPoints
        
        # 获取查询参数
        limit = request.args.get('limit', 10, type=int)
        
        # 验证参数
        if limit < 1 or limit > 100:
            return jsonify({
                'success': False,
                'error': 'Limit must be between 1 and 100'
            }), 400
        
        # 查询排行榜
        top_users = UserPoints.query\
            .order_by(UserPoints.total_points.desc())\
            .limit(limit)\
            .all()
        
        leaderboard = []
        for rank, user_points in enumerate(top_users, start=1):
            leaderboard.append({
                'rank': rank,
                'user_id': user_points.user_id,
                'total_points': user_points.total_points,
                'current_level': user_points.current_level,
                'streak_days': user_points.streak_days
            })
        
        return jsonify({
            'success': True,
            'data': {
                'leaderboard': leaderboard,
                'total': len(leaderboard)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
