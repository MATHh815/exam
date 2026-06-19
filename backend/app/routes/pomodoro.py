"""
番茄钟路由
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.pomodoro_service import PomodoroService

pomodoro_bp = Blueprint('pomodoro', __name__, url_prefix='/api/pomodoro')

@pomodoro_bp.route('/complete', methods=['POST'])
@jwt_required()
def complete_session():
    """完成番茄钟会话"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        duration = data.get('duration', 25)
        session_type = data.get('session_type', 'focus')
        subject = data.get('subject')
        notes = data.get('notes')
        
        result = PomodoroService.complete_session(
            user_id=current_user_id,
            duration=duration,
            session_type=session_type,
            subject=subject,
            notes=notes
        )
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'完成会话失败: {str(e)}'
        }), 500

@pomodoro_bp.route('/interrupt', methods=['POST'])
@jwt_required()
def interrupt_session():
    """中断番茄钟会话"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        duration = data.get('duration', 0)
        session_type = data.get('session_type', 'focus')
        subject = data.get('subject')
        
        result = PomodoroService.interrupt_session(
            user_id=current_user_id,
            duration=duration,
            session_type=session_type,
            subject=subject
        )
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'中断会话失败: {str(e)}'
        }), 500

@pomodoro_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """获取番茄钟统计"""
    try:
        current_user_id = get_jwt_identity()
        stats = PomodoroService.get_user_stats(current_user_id)
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取统计失败: {str(e)}'
        }), 500

@pomodoro_bp.route('/sessions/recent', methods=['GET'])
@jwt_required()
def get_recent_sessions():
    """获取最近的会话"""
    try:
        current_user_id = get_jwt_identity()
        days = request.args.get('days', 7, type=int)
        sessions = PomodoroService.get_recent_sessions(current_user_id, days)
        
        return jsonify({
            'success': True,
            'data': sessions
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取会话失败: {str(e)}'
        }), 500

@pomodoro_bp.route('/trend', methods=['GET'])
@jwt_required()
def get_daily_trend():
    """获取每日趋势"""
    try:
        current_user_id = get_jwt_identity()
        days = request.args.get('days', 30, type=int)
        trend = PomodoroService.get_daily_trend(current_user_id, days)
        
        return jsonify({
            'success': True,
            'data': trend
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取趋势失败: {str(e)}'
        }), 500
