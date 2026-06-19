"""考试和试卷 API 路由"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.exam_paper_service import ExamPaperService
from app.services.exam_service import ExamService
from app.utils.decorators import jwt_required_with_user, admin_required

exams_bp = Blueprint('exams', __name__)


@exams_bp.route('', methods=['GET'])
@jwt_required_with_user
def list_papers(current_user):
    """获取试卷列表
    
    Query Parameters:
        exam_type: 考试类型筛选
        is_published: 发布状态筛选
        page: 页码（默认1）
        page_size: 每页数量（默认20）
    """
    try:
        exam_type = request.args.get('exam_type')
        is_published = request.args.get('is_published')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        
        # 转换 is_published 参数
        if is_published is not None:
            is_published = is_published.lower() == 'true'
        
        papers, total = ExamPaperService.list_papers(
            exam_type=exam_type,
            is_published=is_published,
            page=page,
            page_size=page_size
        )
        
        return jsonify({
            'success': True,
            'data': {
                'papers': [paper.to_dict() for paper in papers],
                'total': total,
                'page': page,
                'page_size': page_size
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'LIST_PAPERS_ERROR',
                'message': str(e)
            }
        }), 500


@exams_bp.route('/<int:paper_id>', methods=['GET'])
@jwt_required_with_user
def get_paper(current_user, paper_id):
    """获取试卷详情
    
    Query Parameters:
        include_questions: 是否包含题目列表（默认false）
    """
    try:
        include_questions = request.args.get('include_questions', 'false').lower() == 'true'
        
        print(f"[DEBUG] 获取试卷 {paper_id}, include_questions={include_questions}")
        
        paper = ExamPaperService.get_paper(paper_id, include_questions=include_questions)
        
        if not paper:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'PAPER_NOT_FOUND',
                    'message': '试卷不存在'
                }
            }), 404
        
        # 获取试卷基本信息
        paper_dict = paper.to_dict(include_questions=False)
        
        # 如果需要题目列表，获取详细题目信息
        if include_questions:
            questions = ExamPaperService.get_paper_questions(paper_id)
            paper_dict['questions'] = questions
            print(f"[DEBUG] 试卷 {paper_id} 包含 {len(questions)} 道题目")
        
        return jsonify({
            'success': True,
            'data': paper_dict
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_PAPER_ERROR',
                'message': str(e)
            }
        }), 500


@exams_bp.route('', methods=['POST'])
@admin_required
def create_paper(current_user):
    """创建试卷（管理员）
    
    Request Body:
        name: 试卷名称
        exam_type: 考试类型
        duration: 考试时长（分钟）
        description: 试卷描述（可选）
        total_score: 总分（可选）
        pass_score: 及格分（可选）
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': '请求数据不能为空'
                }
            }), 400
        
        paper = ExamPaperService.create_paper(
            name=data.get('name'),
            exam_type=data.get('exam_type'),
            created_by=current_user.id,
            duration=data.get('duration'),
            description=data.get('description'),
            total_score=data.get('total_score'),
            pass_score=data.get('pass_score')
        )
        
        return jsonify({
            'success': True,
            'data': paper.to_dict(),
            'message': '试卷创建成功'
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
                'code': 'CREATE_PAPER_ERROR',
                'message': str(e)
            }
        }), 500


@exams_bp.route('/<int:paper_id>', methods=['PUT'])
@admin_required
def update_paper(current_user, paper_id):
    """更新试卷（管理员）
    
    如果试卷已发布，将创建新版本
    
    Request Body:
        name: 试卷名称（可选）
        description: 试卷描述（可选）
        duration: 考试时长（可选）
        pass_score: 及格分（可选）
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': '请求数据不能为空'
                }
            }), 400
        
        paper = ExamPaperService.edit_paper(paper_id, **data)
        
        return jsonify({
            'success': True,
            'data': paper.to_dict(),
            'message': '试卷更新成功'
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
                'code': 'UPDATE_PAPER_ERROR',
                'message': str(e)
            }
        }), 500


@exams_bp.route('/<int:paper_id>', methods=['DELETE'])
@admin_required
def delete_paper(current_user, paper_id):
    """删除试卷（管理员）
    
    软删除，标记为不可用
    """
    try:
        ExamPaperService.delete_paper(paper_id)
        
        return jsonify({
            'success': True,
            'message': '试卷删除成功'
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
                'code': 'DELETE_PAPER_ERROR',
                'message': str(e)
            }
        }), 500


@exams_bp.route('/<int:paper_id>/questions', methods=['POST'])
@admin_required
def add_question_to_paper(current_user, paper_id):
    """添加题目到试卷（管理员）
    
    Request Body:
        question_id: 题目ID
        order: 题目顺序
        score: 题目分值
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': '请求数据不能为空'
                }
            }), 400
        
        paper_question = ExamPaperService.add_question_to_paper(
            paper_id=paper_id,
            question_id=data.get('question_id'),
            order=data.get('order'),
            score=data.get('score')
        )
        
        return jsonify({
            'success': True,
            'data': paper_question.to_dict(),
            'message': '题目添加成功'
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e)
            }
        }), 400
    except RuntimeError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'OPERATION_ERROR',
                'message': str(e)
            }
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'ADD_QUESTION_ERROR',
                'message': str(e)
            }
        }), 500


@exams_bp.route('/<int:paper_id>/publish', methods=['POST'])
@admin_required
def publish_paper(current_user, paper_id):
    """发布试卷（管理员）"""
    try:
        paper = ExamPaperService.publish_paper(paper_id)
        
        return jsonify({
            'success': True,
            'data': paper.to_dict(),
            'message': '试卷发布成功'
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e)
            }
        }), 400
    except RuntimeError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'OPERATION_ERROR',
                'message': str(e)
            }
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'PUBLISH_PAPER_ERROR',
                'message': str(e)
            }
        }), 500


@exams_bp.route('/<int:paper_id>/current-session', methods=['GET'])
@jwt_required_with_user
def get_current_session(current_user, paper_id):
    """获取当前用户在指定试卷的进行中会话
    
    如果有进行中的会话，返回会话信息
    """
    try:
        from app.models.exam import ExamSession
        
        # 查找进行中的会话
        session = ExamSession.query.filter_by(
            user_id=current_user.id,
            paper_id=paper_id,
            status='in_progress'
        ).first()
        
        if session:
            return jsonify({
                'success': True,
                'data': session.to_dict()
            }), 200
        else:
            return jsonify({
                'success': True,
                'data': None
            }), 200
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_SESSION_ERROR',
                'message': str(e)
            }
        }), 500


@exams_bp.route('/<int:paper_id>/start', methods=['POST'])
@jwt_required_with_user
def start_exam(current_user, paper_id):
    """开始考试
    
    创建考试会话
    """
    try:
        session = ExamService.start_exam(
            user_id=current_user.id,
            paper_id=paper_id
        )
        
        return jsonify({
            'success': True,
            'data': session.to_dict(),
            'message': '考试开始'
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e)
            }
        }), 400
    except RuntimeError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'OPERATION_ERROR',
                'message': str(e)
            }
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'START_EXAM_ERROR',
                'message': str(e)
            }
        }), 500


@exams_bp.route('/sessions/<int:session_id>/answer', methods=['POST'])
@jwt_required_with_user
def submit_answer(current_user, session_id):
    """提交单题答案
    
    实时保存答案
    
    Request Body:
        question_id: 题目ID
        answer: 用户答案
        question_index: 当前题目索引（可选）
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': '请求数据不能为空'
                }
            }), 400
        
        # 验证会话属于当前用户
        session = ExamService.get_session(session_id)
        if not session or session.user_id != current_user.id:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': '无权访问此考试会话'
                }
            }), 403
        
        ExamService.submit_answer(
            session_id=session_id,
            question_id=data.get('question_id'),
            answer=data.get('answer'),
            question_index=data.get('question_index')
        )
        
        return jsonify({
            'success': True,
            'message': '答案已保存'
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e)
            }
        }), 400
    except RuntimeError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'OPERATION_ERROR',
                'message': str(e)
            }
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SUBMIT_ANSWER_ERROR',
                'message': str(e)
            }
        }), 500


@exams_bp.route('/sessions/<int:session_id>/progress', methods=['POST'])
@jwt_required_with_user
def save_progress(current_user, session_id):
    """保存考试进度
    
    Request Body:
        question_index: 当前题目索引
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_REQUEST',
                    'message': '请求数据不能为空'
                }
            }), 400
        
        # 验证会话属于当前用户
        session = ExamService.get_session(session_id)
        if not session or session.user_id != current_user.id:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': '无权访问此考试会话'
                }
            }), 403
        
        ExamService.save_progress(
            session_id=session_id,
            question_index=data.get('question_index', 0)
        )
        
        return jsonify({
            'success': True,
            'message': '进度已保存'
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
                'code': 'SAVE_PROGRESS_ERROR',
                'message': str(e)
            }
        }), 500


@exams_bp.route('/sessions/<int:session_id>/pause', methods=['POST'])
@jwt_required_with_user
def pause_exam(current_user, session_id):
    """暂停考试"""
    try:
        # 验证会话属于当前用户
        session = ExamService.get_session(session_id)
        if not session or session.user_id != current_user.id:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': '无权访问此考试会话'
                }
            }), 403
        
        session = ExamService.pause_exam(session_id)
        
        return jsonify({
            'success': True,
            'data': session.to_dict(),
            'message': '考试已暂停'
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e)
            }
        }), 400
    except RuntimeError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'OPERATION_ERROR',
                'message': str(e)
            }
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'PAUSE_EXAM_ERROR',
                'message': str(e)
            }
        }), 500


@exams_bp.route('/sessions/<int:session_id>/resume', methods=['POST'])
@jwt_required_with_user
def resume_exam(current_user, session_id):
    """恢复暂停的考试"""
    try:
        # 验证会话属于当前用户
        session = ExamService.get_session(session_id)
        if not session or session.user_id != current_user.id:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': '无权访问此考试会话'
                }
            }), 403
        
        session = ExamService.resume_exam(session_id)
        
        return jsonify({
            'success': True,
            'data': session.to_dict(),
            'message': '考试已恢复'
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e)
            }
        }), 400
    except RuntimeError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'OPERATION_ERROR',
                'message': str(e)
            }
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'RESUME_EXAM_ERROR',
                'message': str(e)
            }
        }), 500


@exams_bp.route('/sessions/<int:session_id>', methods=['GET'])
@jwt_required_with_user
def get_session_detail(current_user, session_id):
    """获取考试会话详情"""
    try:
        session = ExamService.get_session(session_id)
        
        if not session:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'SESSION_NOT_FOUND',
                    'message': '考试会话不存在'
                }
            }), 404
        
        # 验证会话属于当前用户
        if session.user_id != current_user.id:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': '无权访问此考试会话'
                }
            }), 403
        
        # 获取试卷信息
        paper = session.paper
        session_dict = session.to_dict()
        session_dict['paper'] = paper.to_dict() if paper else None
        
        return jsonify({
            'success': True,
            'data': session_dict
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_SESSION_ERROR',
                'message': str(e)
            }
        }), 500


@exams_bp.route('/sessions', methods=['GET'])
@jwt_required_with_user
def list_user_sessions(current_user):
    """获取用户所有考试会话（包括未完成的）
    
    Query Parameters:
        status: 状态筛选（可选）: in_progress, paused, submitted, timeout
        page: 页码（默认1）
        page_size: 每页数量（默认20）
    """
    try:
        status = request.args.get('status')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        
        sessions, total = ExamService.list_user_sessions(
            user_id=current_user.id,
            status=status,
            page=page,
            page_size=page_size
        )
        
        # 为每个会话添加试卷信息
        sessions_data = []
        for session in sessions:
            session_dict = session.to_dict()
            session_dict['paper'] = session.paper.to_dict() if session.paper else None
            sessions_data.append(session_dict)
        
        return jsonify({
            'success': True,
            'data': {
                'sessions': sessions_data,
                'total': total,
                'page': page,
                'page_size': page_size
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'LIST_SESSIONS_ERROR',
                'message': str(e)
            }
        }), 500


@exams_bp.route('/sessions/incomplete', methods=['GET'])
@jwt_required_with_user
def get_incomplete_sessions(current_user):
    """获取用户所有未完成的考试会话"""
    try:
        sessions = ExamService.get_user_incomplete_sessions(current_user.id)
        
        # 为每个会话添加试卷信息
        sessions_data = []
        for session in sessions:
            session_dict = session.to_dict()
            session_dict['paper'] = session.paper.to_dict() if session.paper else None
            sessions_data.append(session_dict)
        
        return jsonify({
            'success': True,
            'data': sessions_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_INCOMPLETE_SESSIONS_ERROR',
                'message': str(e)
            }
        }), 500


@exams_bp.route('/sessions/<int:session_id>/submit', methods=['POST'])
@jwt_required_with_user
def submit_exam(current_user, session_id):
    """提交整份试卷
    
    计算成绩并生成结果
    """
    try:
        # 验证会话属于当前用户
        session = ExamService.get_session(session_id)
        if not session or session.user_id != current_user.id:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': '无权访问此考试会话'
                }
            }), 403
        
        result = ExamService.submit_exam(session_id)
        
        return jsonify({
            'success': True,
            'data': result.to_dict(include_details=True),
            'message': '试卷提交成功'
        }), 200
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(e)
            }
        }), 400
    except RuntimeError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'OPERATION_ERROR',
                'message': str(e)
            }
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SUBMIT_EXAM_ERROR',
                'message': str(e)
            }
        }), 500


@exams_bp.route('/results/<int:result_id>', methods=['GET'])
@jwt_required_with_user
def get_exam_result(current_user, result_id):
    """获取考试结果
    
    Query Parameters:
        include_details: 是否包含详细结果（默认true）
    """
    try:
        include_details = request.args.get('include_details', 'true').lower() == 'true'
        
        result = ExamService.get_exam_result(result_id)
        
        if not result:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'RESULT_NOT_FOUND',
                    'message': '考试结果不存在'
                }
            }), 404
        
        # 验证结果属于当前用户
        if result.user_id != current_user.id:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'UNAUTHORIZED',
                    'message': '无权访问此考试结果'
                }
            }), 403
        
        return jsonify({
            'success': True,
            'data': result.to_dict(include_details=include_details)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'GET_RESULT_ERROR',
                'message': str(e)
            }
        }), 500


@exams_bp.route('/results', methods=['GET'])
@jwt_required_with_user
def list_exam_results(current_user):
    """获取用户考试历史
    
    Query Parameters:
        paper_id: 试卷ID筛选（可选）
        page: 页码（默认1）
        page_size: 每页数量（默认20）
    """
    try:
        paper_id = request.args.get('paper_id', type=int)
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        
        results, total = ExamService.list_user_exams(
            user_id=current_user.id,
            paper_id=paper_id,
            page=page,
            page_size=page_size
        )
        
        return jsonify({
            'success': True,
            'data': {
                'results': [result.to_dict() for result in results],
                'total': total,
                'page': page,
                'page_size': page_size
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'LIST_RESULTS_ERROR',
                'message': str(e)
            }
        }), 500
