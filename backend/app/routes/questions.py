"""题库相关 API 路由"""
from flask import Blueprint, request, jsonify
from app.services.question_service import QuestionService
from app.utils.decorators import jwt_required_with_user, admin_required

questions_bp = Blueprint('questions', __name__)


@questions_bp.route('', methods=['GET'])
@jwt_required_with_user
def list_questions(current_user):
    """获取题目列表（支持分页和筛选）
    
    GET /api/questions?page=1&page_size=20&exam_type=civil_service&keyword=数学
    
    Query Parameters:
        - page: 页码（默认1）
        - page_size: 每页数量（默认20）
        - exam_type: 考试类型
        - question_type: 题目类型
        - subject: 科目
        - chapter: 章节
        - difficulty: 难度
        - keyword: 关键词
    
    Response:
        {
            "success": true,
            "data": {
                "questions": [...],
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
        
        # 获取筛选条件
        filters = {}
        if request.args.get('exam_type'):
            filters['exam_type'] = request.args.get('exam_type')
        if request.args.get('question_type'):
            filters['question_type'] = request.args.get('question_type')
        if request.args.get('subject'):
            filters['subject'] = request.args.get('subject')
        if request.args.get('chapter'):
            filters['chapter'] = request.args.get('chapter')
        if request.args.get('difficulty'):
            filters['difficulty'] = int(request.args.get('difficulty'))
        if request.args.get('keyword'):
            filters['keyword'] = request.args.get('keyword')
        
        # 查询题目
        questions, total = QuestionService.list_questions(
            filters=filters if filters else None,
            page=page,
            page_size=page_size
        )
        
        # 计算总页数
        total_pages = (total + page_size - 1) // page_size
        
        return jsonify({
            'success': True,
            'data': {
                'questions': [q.to_dict() for q in questions],
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
                'code': 'QUERY_FAILED',
                'message': '查询题目失败',
                'details': str(e)
            }
        }), 500


@questions_bp.route('/<int:question_id>', methods=['GET'])
@jwt_required_with_user
def get_question(current_user, question_id):
    """获取单个题目详情
    
    GET /api/questions/:id
    
    Response:
        {
            "success": true,
            "data": {
                "question": {...}
            }
        }
    """
    try:
        question = QuestionService.get_question(question_id)
        
        return jsonify({
            'success': True,
            'data': {
                'question': question.to_dict()
            }
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'QUESTION_NOT_FOUND',
                'message': str(e)
            }
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '获取题目失败',
                'details': str(e)
            }
        }), 500


@questions_bp.route('', methods=['POST'])
@admin_required
def create_question(current_user):
    """创建题目（管理员）
    
    POST /api/questions
    
    Request Body:
        {
            "exam_type": "string",
            "question_type": "string",
            "subject": "string",
            "chapter": "string",
            "difficulty": 3,
            "content": "string",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "string",
            "explanation": "string",
            "tags": ["tag1", "tag2"]
        }
    
    Response:
        {
            "success": true,
            "data": {
                "question": {...},
                "message": "创建成功"
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
        
        # 创建题目
        question = QuestionService.create_question(data, created_by=current_user.id)
        
        return jsonify({
            'success': True,
            'data': {
                'question': question.to_dict(),
                'message': '创建成功'
            }
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'CREATE_FAILED',
                'message': str(e)
            }
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '创建题目失败',
                'details': str(e)
            }
        }), 500


@questions_bp.route('/<int:question_id>', methods=['PUT'])
@admin_required
def update_question(current_user, question_id):
    """更新题目（管理员）
    
    PUT /api/questions/:id
    
    Request Body:
        {
            "content": "string",
            "difficulty": 4,
            ...
        }
    
    Response:
        {
            "success": true,
            "data": {
                "question": {...},
                "message": "更新成功"
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
        
        # 更新题目
        question = QuestionService.update_question(question_id, data)
        
        return jsonify({
            'success': True,
            'data': {
                'question': question.to_dict(),
                'message': '更新成功'
            }
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'UPDATE_FAILED',
                'message': str(e)
            }
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '更新题目失败',
                'details': str(e)
            }
        }), 500


@questions_bp.route('/<int:question_id>', methods=['DELETE'])
@admin_required
def delete_question(current_user, question_id):
    """删除题目（管理员，软删除）
    
    DELETE /api/questions/:id
    
    Response:
        {
            "success": true,
            "data": {
                "message": "删除成功"
            }
        }
    """
    try:
        QuestionService.delete_question(question_id)
        
        return jsonify({
            'success': True,
            'data': {
                'message': '删除成功'
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
                'code': 'INTERNAL_ERROR',
                'message': '删除题目失败',
                'details': str(e)
            }
        }), 500


@questions_bp.route('/import', methods=['POST'])
@admin_required
def import_questions(current_user):
    """批量导入题目（管理员）
    
    POST /api/questions/import
    
    Request Body:
        {
            "questions": [
                {
                    "exam_type": "string",
                    "question_type": "string",
                    "content": "string",
                    "correct_answer": "string",
                    ...
                },
                ...
            ]
        }
    
    Response:
        {
            "success": true,
            "data": {
                "success_count": 10,
                "failed_count": 2,
                "errors": [...],
                "message": "导入完成"
            }
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'questions' not in data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_DATA',
                    'message': '缺少题目数据'
                }
            }), 400
        
        questions_data = data['questions']
        
        if not isinstance(questions_data, list):
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_FORMAT',
                    'message': '题目数据必须是数组格式'
                }
            }), 400
        
        # 批量导入
        result = QuestionService.import_questions(questions_data, created_by=current_user.id)
        
        return jsonify({
            'success': True,
            'data': {
                'success_count': result['success_count'],
                'failed_count': result['failed_count'],
                'errors': result['errors'],
                'message': f"导入完成：成功{result['success_count']}个，失败{result['failed_count']}个"
            }
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'IMPORT_FAILED',
                'message': str(e)
            }
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '批量导入失败',
                'details': str(e)
            }
        }), 500


@questions_bp.route('/random', methods=['GET'])
@jwt_required_with_user
def get_random_questions(current_user):
    """随机获取题目
    
    GET /api/questions/random?count=10&exam_type=civil_service&difficulty=3
    
    Query Parameters:
        - count: 数量（默认10）
        - exam_type: 考试类型
        - question_type: 题目类型
        - subject: 科目
        - chapter: 章节
        - difficulty: 难度
    
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
        # 获取参数
        count = request.args.get('count', 10, type=int)
        exam_type = request.args.get('exam_type')
        
        # 限制数量
        if count > 50:
            count = 50
        
        # 获取筛选条件
        filters = {}
        if request.args.get('question_type'):
            filters['question_type'] = request.args.get('question_type')
        if request.args.get('subject'):
            filters['subject'] = request.args.get('subject')
        if request.args.get('chapter'):
            filters['chapter'] = request.args.get('chapter')
        if request.args.get('difficulty'):
            filters['difficulty'] = int(request.args.get('difficulty'))
        
        # 随机抽题
        questions = QuestionService.random_questions(
            exam_type=exam_type,
            count=count,
            filters=filters if filters else None
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
                'code': 'RANDOM_FAILED',
                'message': '随机抽题失败',
                'details': str(e)
            }
        }), 500


@questions_bp.route('/statistics', methods=['GET'])
@admin_required
def get_statistics(current_user):
    """获取题库统计信息（管理员）
    
    GET /api/questions/statistics?exam_type=civil_service
    
    Query Parameters:
        - exam_type: 考试类型（可选）
    
    Response:
        {
            "success": true,
            "data": {
                "total": 1000,
                "by_exam_type": {...},
                "by_question_type": {...},
                "by_difficulty": {...}
            }
        }
    """
    try:
        # 获取筛选条件
        filters = {}
        if request.args.get('exam_type'):
            filters['exam_type'] = request.args.get('exam_type')
        
        # 获取统计信息
        stats = QuestionService.get_statistics(filters if filters else None)
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'STATISTICS_FAILED',
                'message': '获取统计信息失败',
                'details': str(e)
            }
        }), 500
