"""学习日程相关 API 路由"""
from flask import Blueprint, request, jsonify
from datetime import datetime, date
from app.services.study_schedule_service import StudyScheduleService
from app.models.study_schedule import ACTIVITY_TYPES, SUBJECTS
from app.utils.decorators import jwt_required_with_user

study_schedules_bp = Blueprint('study_schedules', __name__)


@study_schedules_bp.route('', methods=['POST'])
@jwt_required_with_user
def create_schedule(current_user):
    """创建学习日程
    
    POST /api/study-schedules
    
    Request Body:
        {
            "title": "背英语单词",
            "activity_type": "memorize",
            "subject": "english",
            "schedule_date": "2025-12-30",
            "start_time": "09:00",
            "end_time": "10:00",
            "repeat_type": "once",
            "description": "背诵考研核心词汇",
            "location": "图书馆",
            "reminder_minutes": 15
        }
    
    Response:
        {
            "success": true,
            "data": {
                "schedule": {...},
                "message": "日程创建成功"
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
                    'message': '缺少请求数据'
                }
            }), 400
        
        # 创建日程
        schedule = StudyScheduleService.create_schedule(
            user_id=current_user.id,
            schedule_data=data
        )
        
        return jsonify({
            'success': True,
            'data': {
                'schedule': schedule.to_dict(),
                'message': '日程创建成功'
            }
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
                'code': 'CREATE_SCHEDULE_FAILED',
                'message': '创建日程失败',
                'details': str(e)
            }
        }), 500


@study_schedules_bp.route('/today', methods=['GET'])
@jwt_required_with_user
def get_today_schedules(current_user):
    """获取今天的日程
    
    GET /api/study-schedules/today
    
    Response:
        {
            "success": true,
            "data": {
                "schedules": [...],
                "count": 5,
                "date": "2025-12-30"
            }
        }
    """
    try:
        schedules = StudyScheduleService.get_today_schedules(current_user.id)
        
        return jsonify({
            'success': True,
            'data': {
                'schedules': [schedule.to_dict() for schedule in schedules],
                'count': len(schedules),
                'date': date.today().isoformat()
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_SCHEDULES_FAILED',
                'message': '获取今日日程失败',
                'details': str(e)
            }
        }), 500


@study_schedules_bp.route('', methods=['GET'])
@jwt_required_with_user
def get_schedules(current_user):
    """获取日期范围内的日程
    
    GET /api/study-schedules?start_date=2025-12-30&end_date=2026-01-05
    
    Query Parameters:
        - start_date: 开始日期 (YYYY-MM-DD)
        - end_date: 结束日期 (YYYY-MM-DD)
    
    Response:
        {
            "success": true,
            "data": {
                "schedules": [...],
                "count": 15
            }
        }
    """
    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        if not start_date_str or not end_date_str:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_PARAMETERS',
                    'message': '缺少开始日期或结束日期'
                }
            }), 400
        
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_DATE_FORMAT',
                    'message': '日期格式错误，应为 YYYY-MM-DD'
                }
            }), 400
        
        schedules = StudyScheduleService.get_schedules_by_date_range(
            current_user.id,
            start_date,
            end_date
        )
        
        return jsonify({
            'success': True,
            'data': {
                'schedules': [schedule.to_dict() for schedule in schedules],
                'count': len(schedules)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_SCHEDULES_FAILED',
                'message': '获取日程失败',
                'details': str(e)
            }
        }), 500


@study_schedules_bp.route('/<int:schedule_id>', methods=['PUT'])
@jwt_required_with_user
def update_schedule(current_user, schedule_id):
    """更新日程
    
    PUT /api/study-schedules/:id
    
    Request Body:
        {
            "title": "更新后的标题",
            "description": "更新后的描述",
            "status": "completed"
        }
    
    Response:
        {
            "success": true,
            "data": {
                "schedule": {...},
                "message": "日程更新成功"
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
                    'message': '缺少请求数据'
                }
            }), 400
        
        schedule = StudyScheduleService.update_schedule(
            schedule_id=schedule_id,
            user_id=current_user.id,
            schedule_data=data
        )
        
        return jsonify({
            'success': True,
            'data': {
                'schedule': schedule.to_dict(),
                'message': '日程更新成功'
            }
        }), 200
        
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
                'code': 'UPDATE_SCHEDULE_FAILED',
                'message': '更新日程失败',
                'details': str(e)
            }
        }), 500


@study_schedules_bp.route('/<int:schedule_id>/complete', methods=['PUT'])
@jwt_required_with_user
def complete_schedule(current_user, schedule_id):
    """完成日程
    
    PUT /api/study-schedules/:id/complete
    
    Response:
        {
            "success": true,
            "data": {
                "schedule": {...},
                "message": "日程已完成"
            }
        }
    """
    try:
        schedule = StudyScheduleService.complete_schedule(
            schedule_id=schedule_id,
            user_id=current_user.id
        )
        
        return jsonify({
            'success': True,
            'data': {
                'schedule': schedule.to_dict(),
                'message': '日程已完成'
            }
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'COMPLETE_FAILED',
                'message': str(e)
            }
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'COMPLETE_SCHEDULE_FAILED',
                'message': '完成日程失败',
                'details': str(e)
            }
        }), 500


@study_schedules_bp.route('/<int:schedule_id>', methods=['DELETE'])
@jwt_required_with_user
def delete_schedule(current_user, schedule_id):
    """删除日程
    
    DELETE /api/study-schedules/:id
    
    Response:
        {
            "success": true,
            "data": {
                "message": "日程删除成功"
            }
        }
    """
    try:
        StudyScheduleService.delete_schedule(schedule_id, current_user.id)
        
        return jsonify({
            'success': True,
            'data': {
                'message': '日程删除成功'
            }
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'DELETE_FAILED',
                'message': str(e)
            }
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'DELETE_SCHEDULE_FAILED',
                'message': '删除日程失败',
                'details': str(e)
            }
        }), 500


@study_schedules_bp.route('/statistics', methods=['GET'])
@jwt_required_with_user
def get_statistics(current_user):
    """获取日程统计
    
    GET /api/study-schedules/statistics?start_date=2025-12-01&end_date=2025-12-31
    
    Query Parameters:
        - start_date: 开始日期 (YYYY-MM-DD)
        - end_date: 结束日期 (YYYY-MM-DD)
    
    Response:
        {
            "success": true,
            "data": {
                "statistics": {
                    "total_count": 50,
                    "completed_count": 35,
                    "pending_count": 15,
                    "completion_rate": 70.0,
                    "activity_stats": {...},
                    "subject_stats": {...}
                }
            }
        }
    """
    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        if not start_date_str or not end_date_str:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_PARAMETERS',
                    'message': '缺少开始日期或结束日期'
                }
            }), 400
        
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_DATE_FORMAT',
                    'message': '日期格式错误，应为 YYYY-MM-DD'
                }
            }), 400
        
        statistics = StudyScheduleService.get_statistics(
            current_user.id,
            start_date,
            end_date
        )
        
        return jsonify({
            'success': True,
            'data': {
                'statistics': statistics
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_STATISTICS_FAILED',
                'message': '获取统计数据失败',
                'details': str(e)
            }
        }), 500


@study_schedules_bp.route('/options', methods=['GET'])
def get_options():
    """获取活动类型和科目选项
    
    GET /api/study-schedules/options
    
    Response:
        {
            "success": true,
            "data": {
                "activity_types": {...},
                "subjects": {...}
            }
        }
    """
    return jsonify({
        'success': True,
        'data': {
            'activity_types': ACTIVITY_TYPES,
            'subjects': SUBJECTS
        }
    }), 200
