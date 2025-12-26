"""练习相关 API 路由"""
from flask import Blueprint, request, jsonify
from app.services.practice_service import PracticeService
from app.utils.decorators import jwt_required_with_user

practice_bp = Blueprint('practice', __name__)


@practice_bp.route('/start', methods=['POST'])
@jwt_required_with_user
def start_practice(current_user):
    """开始练习
    
    POST /api/practice/start
    
    Request Body:
        {
            "count": 10,
            "exam_type": "civil_service",
            "question_type": "single_choice",
            "subject": "行测",
            "chapter": "数量关系",
            "difficulty": 3,
            "from_wrong_book": false
        }
    
    Response:
        {
            "success": true,
            "data": {
                "questions": [...],
                "count": 10
            }
        }
    """
    try:
        data = request.get_json() or {}
        
        # 获取参数
        count = data.get('count', 10)
        
        # 限制数量
        if count > 50:
            count = 50
        
        # 构建筛选条件
        filters = {}
        if data.get('exam_type'):
            filters['exam_type'] = data['exam_type']
        if data.get('question_type'):
            filters['question_type'] = data['question_type']
        if data.get('subject'):
            filters['subject'] = data['subject']
        if data.get('chapter'):
            filters['chapter'] = data['chapter']
        if data.get('difficulty'):
            filters['difficulty'] = data['difficulty']
        if data.get('from_wrong_book'):
            filters['from_wrong_book'] = True
        
        # 开始练习
        questions = PracticeService.start_practice(
            user_id=current_user.id,
            filters=filters if filters else None,
            count=count
        )
        
        return jsonify({
            'success': True,
            'data': {
                'questions': [q.to_dict() for q in questions],
                'count': len(questions)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'START_PRACTICE_FAILED',
                'message': '开始练习失败',
                'details': str(e)
            }
        }), 500


@practice_bp.route('/submit', methods=['POST'])
@jwt_required_with_user
def submit_answer(current_user):
    """提交答案
    
    POST /api/practice/submit
    
    Request Body:
        {
            "question_id": 1,
            "user_answer": "A",
            "time_spent": 30
        }
    
    Response:
        {
            "success": true,
            "data": {
                "is_correct": true,
                "correct_answer": "A",
                "explanation": "解析内容",
                "question": {...}
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
        
        question_id = data.get('question_id')
        user_answer = data.get('user_answer')
        time_spent = data.get('time_spent', 0)
        
        if not question_id:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_QUESTION_ID',
                    'message': '缺少题目ID'
                }
            }), 400
        
        # 提交答案
        result = PracticeService.submit_answer(
            user_id=current_user.id,
            question_id=question_id,
            user_answer=user_answer,
            time_spent=time_spent
        )
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SUBMIT_FAILED',
                'message': str(e)
            }
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '提交答案失败',
                'details': str(e)
            }
        }), 500


@practice_bp.route('/history', methods=['GET'])
@jwt_required_with_user
def get_history(current_user):
    """获取练习历史
    
    GET /api/practice/history?page=1&page_size=20&is_correct=true
    
    Query Parameters:
        - page: 页码
        - page_size: 每页数量
        - is_correct: 是否正确（true/false）
        - start_date: 开始日期
        - end_date: 结束日期
    
    Response:
        {
            "success": true,
            "data": {
                "records": [...],
                "total": 100,
                "page": 1,
                "page_size": 20,
                "total_pages": 5
            }
        }
    """
    try:
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        
        # 限制页大小
        if page_size > 100:
            page_size = 100
        
        # 构建筛选条件
        filters = {}
        if request.args.get('is_correct'):
            is_correct_str = request.args.get('is_correct').lower()
            filters['is_correct'] = is_correct_str == 'true'
        
        if request.args.get('start_date'):
            filters['start_date'] = request.args.get('start_date')
        
        if request.args.get('end_date'):
            filters['end_date'] = request.args.get('end_date')
        
        # 获取练习历史
        records, total = PracticeService.get_practice_history(
            user_id=current_user.id,
            page=page,
            page_size=page_size,
            filters=filters if filters else None
        )
        
        # 计算总页数
        total_pages = (total + page_size - 1) // page_size
        
        return jsonify({
            'success': True,
            'data': {
                'records': [r.to_dict(include_question=True) for r in records],
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': total_pages
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_HISTORY_FAILED',
                'message': '获取练习历史失败',
                'details': str(e)
            }
        }), 500


@practice_bp.route('/wrong-book', methods=['GET'])
@jwt_required_with_user
def get_wrong_book(current_user):
    """获取错题本
    
    GET /api/practice/wrong-book?mastered=false&exam_type=civil_service
    
    Query Parameters:
        - mastered: 是否已掌握（true/false）
        - exam_type: 考试类型
        - subject: 科目
    
    Response:
        {
            "success": true,
            "data": {
                "wrong_questions": [
                    {
                        "wrong_question": {...},
                        "question": {...}
                    },
                    ...
                ],
                "count": 10
            }
        }
    """
    try:
        # 构建筛选条件
        filters = {}
        
        if request.args.get('mastered'):
            mastered_str = request.args.get('mastered').lower()
            filters['mastered'] = mastered_str == 'true'
        
        if request.args.get('exam_type'):
            filters['exam_type'] = request.args.get('exam_type')
        
        if request.args.get('subject'):
            filters['subject'] = request.args.get('subject')
        
        # 获取错题本
        wrong_questions = PracticeService.get_wrong_book(
            user_id=current_user.id,
            filters=filters if filters else None
        )
        
        return jsonify({
            'success': True,
            'data': {
                'wrong_questions': wrong_questions,
                'count': len(wrong_questions)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_WRONG_BOOK_FAILED',
                'message': '获取错题本失败',
                'details': str(e)
            }
        }), 500


@practice_bp.route('/wrong-book/<int:wrong_question_id>', methods=['DELETE'])
@jwt_required_with_user
def remove_from_wrong_book(current_user, wrong_question_id):
    """从错题本移除
    
    DELETE /api/practice/wrong-book/:id
    
    Response:
        {
            "success": true,
            "data": {
                "message": "移除成功"
            }
        }
    """
    try:
        PracticeService.remove_from_wrong_book(
            user_id=current_user.id,
            wrong_question_id=wrong_question_id
        )
        
        return jsonify({
            'success': True,
            'data': {
                'message': '移除成功'
            }
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'REMOVE_FAILED',
                'message': str(e)
            }
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '移除失败',
                'details': str(e)
            }
        }), 500


@practice_bp.route('/summary', methods=['GET'])
@jwt_required_with_user
def get_summary(current_user):
    """获取练习概览统计
    
    GET /api/practice/summary?days=7
    
    Query Parameters:
        - days: 统计天数（默认7天）
    
    Response:
        {
            "success": true,
            "data": {
                "total_practice": 100,
                "correct_count": 80,
                "accuracy": 80.0,
                "total_time": 120,
                "wrong_book_count": 20,
                "daily_stats": [...]
            }
        }
    """
    try:
        days = request.args.get('days', 7, type=int)
        
        # 限制天数范围
        if days < 1:
            days = 1
        if days > 365:
            days = 365
        
        # 获取统计信息
        summary = PracticeService.get_practice_summary(
            user_id=current_user.id,
            days=days
        )
        
        return jsonify({
            'success': True,
            'data': summary
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_SUMMARY_FAILED',
                'message': '获取统计信息失败',
                'details': str(e)
            }
        }), 500
