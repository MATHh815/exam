"""学习计划相关 API 路由"""
from flask import Blueprint, request, jsonify
from app.services.study_plan_service import StudyPlanService
from app.utils.decorators import jwt_required_with_user
from datetime import datetime

study_plans_bp = Blueprint('study_plans', __name__)


@study_plans_bp.route('', methods=['POST'])
@jwt_required_with_user
def create_plan(current_user):
    """创建学习计划
    
    POST /api/study-plans
    
    Request Body:
        {
            "name": "2024国考冲刺",
            "description": "最后30天冲刺计划",
            "exam_type": "civil_service",
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
            "goals": [
                {
                    "goal_type": "daily_practice",
                    "target_value": 50
                },
                {
                    "goal_type": "weekly_practice",
                    "target_value": 400
                }
            ]
        }
    
    Response:
        {
            "success": true,
            "data": {
                "plan": {...},
                "message": "学习计划创建成功"
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
        
        # 验证必填字段
        required_fields = ['name', 'exam_type', 'start_date', 'end_date']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_REQUIRED_FIELDS',
                    'message': '缺少必填字段',
                    'details': {'missing_fields': missing_fields}
                }
            }), 400
        
        # 创建学习计划
        plan = StudyPlanService.create_plan(
            user_id=current_user.id,
            plan_data=data
        )
        
        return jsonify({
            'success': True,
            'data': {
                'plan': plan.to_dict(),
                'message': '学习计划创建成功'
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
                'code': 'CREATE_PLAN_FAILED',
                'message': '创建学习计划失败',
                'details': str(e)
            }
        }), 500


@study_plans_bp.route('', methods=['GET'])
@jwt_required_with_user
def get_plans(current_user):
    """获取学习计划列表
    
    GET /api/study-plans?status=active
    
    Query Parameters:
        - status: 计划状态 (active, completed, paused)
    
    Response:
        {
            "success": true,
            "data": {
                "plans": [...],
                "count": 5
            }
        }
    """
    try:
        # 获取筛选参数
        status = request.args.get('status')
        
        # 验证状态值
        if status and status not in ['active', 'completed', 'paused']:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_STATUS',
                    'message': '无效的状态值',
                    'details': '状态必须是 active, completed 或 paused'
                }
            }), 400
        
        # 获取学习计划列表
        plans = StudyPlanService.get_user_plans(
            user_id=current_user.id,
            status=status
        )
        
        return jsonify({
            'success': True,
            'data': {
                'plans': [plan.to_dict() for plan in plans],
                'count': len(plans)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_PLANS_FAILED',
                'message': '获取学习计划列表失败',
                'details': str(e)
            }
        }), 500


@study_plans_bp.route('/<int:plan_id>', methods=['GET'])
@jwt_required_with_user
def get_plan(current_user, plan_id):
    """获取学习计划详情
    
    GET /api/study-plans/:id
    
    Response:
        {
            "success": true,
            "data": {
                "plan": {...}
            }
        }
    """
    try:
        # 获取学习计划
        plan = StudyPlanService.get_plan_by_id(plan_id, current_user.id)
        
        if not plan:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'PLAN_NOT_FOUND',
                    'message': '学习计划不存在'
                }
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'plan': plan.to_dict()
            }
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'ACCESS_DENIED',
                'message': str(e)
            }
        }), 403
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_PLAN_FAILED',
                'message': '获取学习计划失败',
                'details': str(e)
            }
        }), 500


@study_plans_bp.route('/<int:plan_id>', methods=['PUT'])
@jwt_required_with_user
def update_plan(current_user, plan_id):
    """更新学习计划
    
    PUT /api/study-plans/:id
    
    Request Body:
        {
            "name": "更新后的计划名称",
            "description": "更新后的描述",
            "status": "paused"
        }
    
    Response:
        {
            "success": true,
            "data": {
                "plan": {...},
                "message": "学习计划更新成功"
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
        
        # 更新学习计划
        plan = StudyPlanService.update_plan(
            plan_id=plan_id,
            user_id=current_user.id,
            plan_data=data
        )
        
        return jsonify({
            'success': True,
            'data': {
                'plan': plan.to_dict(),
                'message': '学习计划更新成功'
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
                'code': 'UPDATE_PLAN_FAILED',
                'message': '更新学习计划失败',
                'details': str(e)
            }
        }), 500


@study_plans_bp.route('/<int:plan_id>', methods=['DELETE'])
@jwt_required_with_user
def delete_plan(current_user, plan_id):
    """删除学习计划（软删除）
    
    DELETE /api/study-plans/:id
    
    Response:
        {
            "success": true,
            "data": {
                "message": "学习计划删除成功"
            }
        }
    """
    try:
        # 删除学习计划
        StudyPlanService.delete_plan(plan_id, current_user.id)
        
        return jsonify({
            'success': True,
            'data': {
                'message': '学习计划删除成功'
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
                'code': 'DELETE_PLAN_FAILED',
                'message': '删除学习计划失败',
                'details': str(e)
            }
        }), 500


@study_plans_bp.route('/<int:plan_id>/progress', methods=['PUT'])
@jwt_required_with_user
def update_progress(current_user, plan_id):
    """更新学习进度
    
    PUT /api/study-plans/:id/progress
    
    Request Body:
        {
            "goal_type": "daily_practice",
            "increment": 1
        }
    
    Response:
        {
            "success": true,
            "data": {
                "message": "进度更新成功",
                "updated_goals": [...]
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
        
        goal_type = data.get('goal_type')
        increment = data.get('increment', 1)
        
        if not goal_type:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_GOAL_TYPE',
                    'message': '缺少目标类型'
                }
            }), 400
        
        # 更新进度
        updated_goals = StudyPlanService.update_progress(
            plan_id=plan_id,
            user_id=current_user.id,
            goal_type=goal_type,
            increment=increment
        )
        
        return jsonify({
            'success': True,
            'data': {
                'message': '进度更新成功',
                'updated_goals': [goal.to_dict() for goal in updated_goals]
            }
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'UPDATE_PROGRESS_FAILED',
                'message': str(e)
            }
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'UPDATE_PROGRESS_ERROR',
                'message': '更新进度失败',
                'details': str(e)
            }
        }), 500


@study_plans_bp.route('/<int:plan_id>/report', methods=['GET'])
@jwt_required_with_user
def get_report(current_user, plan_id):
    """获取学习报告
    
    GET /api/study-plans/:id/report
    
    Response:
        {
            "success": true,
            "data": {
                "report": {
                    "plan": {...},
                    "goals": [...],
                    "practice_stats": {...},
                    "exam_stats": {...},
                    "overall_progress": 75.5
                }
            }
        }
    """
    try:
        # 生成学习报告
        report = StudyPlanService.generate_report(plan_id, current_user.id)
        
        return jsonify({
            'success': True,
            'data': {
                'report': report
            }
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'REPORT_GENERATION_FAILED',
                'message': str(e)
            }
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_REPORT_ERROR',
                'message': '获取学习报告失败',
                'details': str(e)
            }
        }), 500
