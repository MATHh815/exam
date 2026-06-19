"""每日任务相关路由"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.daily_task_service import DailyTaskService


daily_tasks_bp = Blueprint('daily_tasks', __name__, url_prefix='/api/daily-tasks')


@daily_tasks_bp.route('', methods=['GET'])
@jwt_required()
def get_daily_tasks():
    """获取今日任务
    
    Returns:
        JSON: 今日任务列表
    """
    try:
        user_id = get_jwt_identity()
        
        tasks = DailyTaskService.get_today_tasks(user_id)
        
        return jsonify({
            'success': True,
            'data': {
                'tasks': tasks,
                'total': len(tasks)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@daily_tasks_bp.route('/<int:task_id>/complete', methods=['PUT'])
@jwt_required()
def complete_task(task_id):
    """完成任务
    
    Args:
        task_id: 任务ID
    
    Returns:
        JSON: 完成后的任务信息
    """
    try:
        user_id = get_jwt_identity()
        
        # 验证任务属于当前用户
        from app.models.achievement import DailyTask
        task = DailyTask.query.get(task_id)
        
        if not task:
            return jsonify({
                'success': False,
                'error': 'Task not found'
            }), 404
        
        if task.user_id != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403
        
        if task.is_completed:
            return jsonify({
                'success': False,
                'error': 'Task already completed'
            }), 400
        
        # 完成任务
        completed_task = DailyTaskService.complete_task(task_id)
        
        return jsonify({
            'success': True,
            'data': completed_task
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@daily_tasks_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_task_stats():
    """获取任务统计
    
    Returns:
        JSON: 任务统计信息
    """
    try:
        user_id = get_jwt_identity()
        
        stats = DailyTaskService.get_task_stats(user_id)
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@daily_tasks_bp.route('/templates', methods=['GET'])
@jwt_required()
def get_task_templates():
    """获取任务模板
    
    Returns:
        JSON: 任务模板列表
    """
    try:
        templates = DailyTaskService.get_task_templates()
        
        return jsonify({
            'success': True,
            'data': {
                'templates': templates,
                'total': len(templates)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
