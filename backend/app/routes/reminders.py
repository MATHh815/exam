"""学习提醒路由模块"""
from flask import Blueprint, request, jsonify
from app.services.reminder_service import ReminderService
from app.utils.decorators import jwt_required_with_user


reminders_bp = Blueprint('reminders', __name__)


@reminders_bp.route('/api/reminders', methods=['POST'])
@jwt_required_with_user
def create_reminder(current_user):
    """创建学习提醒
    
    请求体:
        {
            "plan_id": 1,
            "reminder_time": "08:00",
            "frequency": "daily",
            "is_enabled": true,
            "message": "该学习了！"
        }
    
    响应:
        {
            "success": true,
            "data": {
                "id": 1,
                "plan_id": 1,
                "reminder_time": "08:00:00",
                "frequency": "daily",
                "is_enabled": true,
                "message": "该学习了！",
                "created_at": "2024-01-01T00:00:00"
            }
        }
    """
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data or 'plan_id' not in data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_FIELD',
                    'message': '缺少必填字段：plan_id'
                }
            }), 400
        
        if 'reminder_time' not in data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_FIELD',
                    'message': '缺少必填字段：reminder_time'
                }
            }), 400
        
        # 创建提醒
        reminder = ReminderService.create_reminder(
            user_id=current_user.id,
            plan_id=data['plan_id'],
            reminder_data=data
        )
        
        return jsonify({
            'success': True,
            'data': reminder.to_dict()
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e)
            }
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': '创建提醒失败',
                'details': str(e)
            }
        }), 500


@reminders_bp.route('/api/reminders', methods=['GET'])
@jwt_required_with_user
def get_reminders(current_user):
    """获取用户的提醒列表
    
    查询参数:
        - plan_id: 学习计划ID（可选）
    
    响应:
        {
            "success": true,
            "data": [
                {
                    "id": 1,
                    "plan_id": 1,
                    "reminder_time": "08:00:00",
                    "frequency": "daily",
                    "is_enabled": true,
                    "message": "该学习了！",
                    "last_sent_at": "2024-01-01T08:00:00",
                    "created_at": "2024-01-01T00:00:00"
                }
            ]
        }
    """
    try:
        plan_id = request.args.get('plan_id', type=int)
        
        reminders = ReminderService.get_user_reminders(
            user_id=current_user.id,
            plan_id=plan_id
        )
        
        return jsonify({
            'success': True,
            'data': [r.to_dict() for r in reminders]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': '获取提醒列表失败',
                'details': str(e)
            }
        }), 500


@reminders_bp.route('/api/reminders/<int:reminder_id>', methods=['GET'])
@jwt_required_with_user
def get_reminder(current_user, reminder_id):
    """获取单个提醒详情
    
    响应:
        {
            "success": true,
            "data": {
                "id": 1,
                "plan_id": 1,
                "reminder_time": "08:00:00",
                "frequency": "daily",
                "is_enabled": true,
                "message": "该学习了！",
                "last_sent_at": "2024-01-01T08:00:00",
                "created_at": "2024-01-01T00:00:00"
            }
        }
    """
    try:
        from app.models.study_plan import StudyReminder
        
        reminder = StudyReminder.query.filter_by(
            id=reminder_id,
            user_id=current_user.id
        ).first()
        
        if not reminder:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'NOT_FOUND',
                    'message': '提醒不存在'
                }
            }), 404
        
        return jsonify({
            'success': True,
            'data': reminder.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': '获取提醒详情失败',
                'details': str(e)
            }
        }), 500


@reminders_bp.route('/api/reminders/<int:reminder_id>', methods=['PUT'])
@jwt_required_with_user
def update_reminder(current_user, reminder_id):
    """更新学习提醒
    
    请求体:
        {
            "reminder_time": "09:00",
            "frequency": "weekly",
            "is_enabled": false,
            "message": "新的提醒消息"
        }
    
    响应:
        {
            "success": true,
            "data": {
                "id": 1,
                "plan_id": 1,
                "reminder_time": "09:00:00",
                "frequency": "weekly",
                "is_enabled": false,
                "message": "新的提醒消息",
                "updated_at": "2024-01-01T00:00:00"
            }
        }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_DATA',
                    'message': '请求体不能为空'
                }
            }), 400
        
        # 更新提醒
        reminder = ReminderService.update_reminder(
            reminder_id=reminder_id,
            user_id=current_user.id,
            update_data=data
        )
        
        return jsonify({
            'success': True,
            'data': reminder.to_dict()
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e)
            }
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': '更新提醒失败',
                'details': str(e)
            }
        }), 500


@reminders_bp.route('/api/reminders/<int:reminder_id>', methods=['DELETE'])
@jwt_required_with_user
def delete_reminder(current_user, reminder_id):
    """删除学习提醒
    
    响应:
        {
            "success": true,
            "message": "提醒已删除"
        }
    """
    try:
        ReminderService.delete_reminder(
            reminder_id=reminder_id,
            user_id=current_user.id
        )
        
        return jsonify({
            'success': True,
            'message': '提醒已删除'
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': str(e)
            }
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': '删除提醒失败',
                'details': str(e)
            }
        }), 500
