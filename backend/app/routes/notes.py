"""笔记管理路由模块"""
from flask import Blueprint, request, jsonify
from app.services.note_service import NoteService
from app.utils.decorators import jwt_required_with_user
from datetime import datetime

notes_bp = Blueprint('notes', __name__)


@notes_bp.route('', methods=['POST'])
@jwt_required_with_user
def create_note(current_user):
    """创建笔记
    
    请求体:
    {
        "question_id": 1,
        "content": "这道题的解题思路是...",
        "tags": ["重点", "易错"]
    }
    
    响应:
    {
        "code": 200,
        "message": "笔记创建成功",
        "data": {
            "id": 1,
            "user_id": 1,
            "question_id": 1,
            "content": "这道题的解题思路是...",
            "tags": ["重点", "易错"],
            "created_at": "2025-12-26T10:00:00",
            "updated_at": "2025-12-26T10:00:00"
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'code': 400,
                'message': '请求数据不能为空'
            }), 400
        
        note = NoteService.create_note(current_user.id, data)
        
        return jsonify({
            'code': 200,
            'message': '笔记创建成功',
            'data': note.to_dict()
        }), 200
        
    except ValueError as e:
        return jsonify({
            'code': 400,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(e)}'
        }), 500


@notes_bp.route('', methods=['GET'])
@jwt_required_with_user
def get_notes(current_user):
    """获取笔记列表
    
    查询参数:
    - page: 页码（默认1）
    - per_page: 每页数量（默认20）
    - subject_id: 科目ID（可选）
    - chapter_id: 章节ID（可选）
    - tags: 标签（可选，逗号分隔）
    
    响应:
    {
        "code": 200,
        "message": "获取成功",
        "data": {
            "notes": [...],
            "total": 100,
            "page": 1,
            "per_page": 20,
            "pages": 5
        }
    }
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        subject = request.args.get('subject')
        chapter = request.args.get('chapter')
        tags_str = request.args.get('tags', '')
        
        # 解析标签
        tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()] if tags_str else None
        
        result = NoteService.get_user_notes(
            user_id=current_user.id,
            page=page,
            per_page=per_page,
            subject=subject,
            chapter=chapter,
            tags=tags
        )
        
        # 转换笔记为字典
        result['notes'] = [note.to_dict() for note in result['notes']]
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(e)}'
        }), 500


@notes_bp.route('/<int:note_id>', methods=['GET'])
@jwt_required_with_user
def get_note(current_user, note_id):
    """获取笔记详情
    
    响应:
    {
        "code": 200,
        "message": "获取成功",
        "data": {
            "id": 1,
            "user_id": 1,
            "question_id": 1,
            "content": "这道题的解题思路是...",
            "tags": ["重点", "易错"],
            "created_at": "2025-12-26T10:00:00",
            "updated_at": "2025-12-26T10:00:00",
            "question": {
                "id": 1,
                "content": "题目内容...",
                "subject_name": "行测",
                "chapter_name": "数量关系"
            }
        }
    }
    """
    try:
        note = NoteService.get_note_by_id(note_id, current_user.id)
        
        note_dict = note.to_dict()
        
        # 添加题目信息
        if note.question:
            note_dict['question'] = {
                'id': note.question.id,
                'content': note.question.content,
                'subject_name': note.question.subject.name if note.question.subject else None,
                'chapter_name': note.question.chapter.name if note.question.chapter else None
            }
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': note_dict
        }), 200
        
    except ValueError as e:
        return jsonify({
            'code': 404,
            'message': str(e)
        }), 404
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(e)}'
        }), 500


@notes_bp.route('/<int:note_id>', methods=['PUT'])
@jwt_required_with_user
def update_note(current_user, note_id):
    """更新笔记
    
    请求体:
    {
        "content": "更新后的笔记内容...",
        "tags": ["重点", "已掌握"]
    }
    
    响应:
    {
        "code": 200,
        "message": "笔记更新成功",
        "data": {
            "id": 1,
            "user_id": 1,
            "question_id": 1,
            "content": "更新后的笔记内容...",
            "tags": ["重点", "已掌握"],
            "created_at": "2025-12-26T10:00:00",
            "updated_at": "2025-12-26T11:00:00"
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'code': 400,
                'message': '请求数据不能为空'
            }), 400
        
        note = NoteService.update_note(note_id, current_user.id, data)
        
        return jsonify({
            'code': 200,
            'message': '笔记更新成功',
            'data': note.to_dict()
        }), 200
        
    except ValueError as e:
        return jsonify({
            'code': 400,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(e)}'
        }), 500


@notes_bp.route('/<int:note_id>', methods=['DELETE'])
@jwt_required_with_user
def delete_note(current_user, note_id):
    """删除笔记
    
    响应:
    {
        "code": 200,
        "message": "笔记删除成功"
    }
    """
    try:
        NoteService.delete_note(note_id, current_user.id)
        
        return jsonify({
            'code': 200,
            'message': '笔记删除成功'
        }), 200
        
    except ValueError as e:
        return jsonify({
            'code': 404,
            'message': str(e)
        }), 404
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(e)}'
        }), 500


@notes_bp.route('/search', methods=['GET'])
@jwt_required_with_user
def search_notes(current_user):
    """搜索笔记
    
    查询参数:
    - keyword: 搜索关键词（必填）
    - page: 页码（默认1）
    - per_page: 每页数量（默认20）
    - subject_id: 科目ID（可选）
    - chapter_id: 章节ID（可选）
    - date_from: 开始日期（可选，格式：YYYY-MM-DD）
    - date_to: 结束日期（可选，格式：YYYY-MM-DD）
    - sort_by: 排序方式（relevance, date_desc, date_asc，默认relevance）
    
    响应:
    {
        "code": 200,
        "message": "搜索成功",
        "data": {
            "notes": [...],
            "total": 50,
            "page": 1,
            "per_page": 20,
            "pages": 3,
            "keyword": "解题思路"
        }
    }
    """
    try:
        keyword = request.args.get('keyword', '').strip()
        
        if not keyword:
            return jsonify({
                'code': 400,
                'message': '搜索关键词不能为空'
            }), 400
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        subject = request.args.get('subject')
        chapter = request.args.get('chapter')
        sort_by = request.args.get('sort_by', 'relevance')
        
        # 解析日期
        date_from = None
        date_to = None
        
        date_from_str = request.args.get('date_from')
        if date_from_str:
            try:
                date_from = datetime.strptime(date_from_str, '%Y-%m-%d')
            except ValueError:
                return jsonify({
                    'code': 400,
                    'message': '开始日期格式无效，应为 YYYY-MM-DD'
                }), 400
        
        date_to_str = request.args.get('date_to')
        if date_to_str:
            try:
                date_to = datetime.strptime(date_to_str, '%Y-%m-%d')
            except ValueError:
                return jsonify({
                    'code': 400,
                    'message': '结束日期格式无效，应为 YYYY-MM-DD'
                }), 400
        
        result = NoteService.search_notes(
            user_id=current_user.id,
            keyword=keyword,
            page=page,
            per_page=per_page,
            subject=subject,
            chapter=chapter,
            date_from=date_from,
            date_to=date_to,
            sort_by=sort_by
        )
        
        # 转换笔记为字典
        result['notes'] = [note.to_dict() for note in result['notes']]
        
        return jsonify({
            'code': 200,
            'message': '搜索成功',
            'data': result
        }), 200
        
    except ValueError as e:
        return jsonify({
            'code': 400,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(e)}'
        }), 500


@notes_bp.route('/question/<int:question_id>', methods=['GET'])
@jwt_required_with_user
def get_question_note(current_user, question_id):
    """获取指定题目的笔记
    
    响应:
    {
        "code": 200,
        "message": "获取成功",
        "data": {
            "has_note": true,
            "note": {...}
        }
    }
    """
    try:
        note = NoteService.get_question_notes(current_user.id, question_id)
        
        if note:
            return jsonify({
                'code': 200,
                'message': '获取成功',
                'data': {
                    'has_note': True,
                    'note': note.to_dict()
                }
            }), 200
        else:
            return jsonify({
                'code': 200,
                'message': '该题目暂无笔记',
                'data': {
                    'has_note': False,
                    'note': None
                }
            }), 200
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(e)}'
        }), 500
