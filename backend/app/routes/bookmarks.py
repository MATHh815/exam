"""题目收藏路由模块"""
from flask import Blueprint, request, jsonify
from app.services.bookmark_service import BookmarkService
from app.utils.decorators import jwt_required_with_user

bookmarks_bp = Blueprint('bookmarks', __name__)


@bookmarks_bp.route('', methods=['POST'])
@jwt_required_with_user
def create_bookmark(current_user):
    """收藏题目
    
    请求体:
    {
        "question_id": 1,
        "tags": ["重点", "易错"],
        "notes": "这道题需要重点复习"
    }
    
    响应:
    {
        "code": 200,
        "message": "收藏成功",
        "data": {
            "id": 1,
            "user_id": 1,
            "question_id": 1,
            "tags": ["重点", "易错"],
            "notes": "这道题需要重点复习",
            "created_at": "2025-12-26T10:00:00"
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
        
        bookmark = BookmarkService.bookmark_question(current_user.id, data)
        
        return jsonify({
            'code': 200,
            'message': '收藏成功',
            'data': bookmark.to_dict()
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


@bookmarks_bp.route('', methods=['GET'])
@jwt_required_with_user
def get_bookmarks(current_user):
    """获取收藏列表
    
    查询参数:
    - page: 页码（默认1）
    - per_page: 每页数量（默认20）
    - exam_type: 考试类型（可选）
    - subject: 科目（可选）
    - chapter: 章节（可选）
    - difficulty: 难度（可选）
    - tags: 标签（可选，逗号分隔）
    - sort_by: 排序方式（created_desc, created_asc, difficulty_desc, difficulty_asc）
    
    响应:
    {
        "code": 200,
        "message": "获取成功",
        "data": {
            "bookmarks": [...],
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
        exam_type = request.args.get('exam_type')
        subject = request.args.get('subject')
        chapter = request.args.get('chapter')
        difficulty = request.args.get('difficulty', type=int)
        tags_str = request.args.get('tags', '')
        sort_by = request.args.get('sort_by', 'created_desc')
        
        # 解析标签
        tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()] if tags_str else None
        
        result = BookmarkService.get_bookmarks(
            user_id=current_user.id,
            page=page,
            per_page=per_page,
            exam_type=exam_type,
            subject=subject,
            chapter=chapter,
            difficulty=difficulty,
            tags=tags,
            sort_by=sort_by
        )
        
        # 转换收藏为字典
        result['bookmarks'] = [bookmark.to_dict() for bookmark in result['bookmarks']]
        
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


@bookmarks_bp.route('/<int:bookmark_id>', methods=['GET'])
@jwt_required_with_user
def get_bookmark(current_user, bookmark_id):
    """获取收藏详情
    
    响应:
    {
        "code": 200,
        "message": "获取成功",
        "data": {
            "id": 1,
            "user_id": 1,
            "question_id": 1,
            "tags": ["重点", "易错"],
            "notes": "这道题需要重点复习",
            "created_at": "2025-12-26T10:00:00",
            "question": {
                "id": 1,
                "content": "题目内容...",
                "exam_type": "civil_service",
                "subject": "行测",
                "chapter": "数量关系",
                "difficulty": 3
            }
        }
    }
    """
    try:
        bookmark = BookmarkService.get_bookmark_by_id(bookmark_id, current_user.id)
        
        bookmark_dict = bookmark.to_dict()
        
        # 添加题目信息
        if bookmark.question:
            bookmark_dict['question'] = {
                'id': bookmark.question.id,
                'content': bookmark.question.content,
                'exam_type': bookmark.question.exam_type,
                'subject': bookmark.question.subject,
                'chapter': bookmark.question.chapter,
                'difficulty': bookmark.question.difficulty
            }
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': bookmark_dict
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


@bookmarks_bp.route('/<int:bookmark_id>', methods=['PUT'])
@jwt_required_with_user
def update_bookmark(current_user, bookmark_id):
    """更新收藏信息
    
    请求体:
    {
        "tags": ["重点", "已掌握"],
        "notes": "更新后的备注"
    }
    
    响应:
    {
        "code": 200,
        "message": "更新成功",
        "data": {
            "id": 1,
            "user_id": 1,
            "question_id": 1,
            "tags": ["重点", "已掌握"],
            "notes": "更新后的备注",
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
        
        bookmark = BookmarkService.update_bookmark(bookmark_id, current_user.id, data)
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': bookmark.to_dict()
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


@bookmarks_bp.route('/<int:bookmark_id>', methods=['DELETE'])
@jwt_required_with_user
def delete_bookmark(current_user, bookmark_id):
    """取消收藏
    
    响应:
    {
        "code": 200,
        "message": "取消收藏成功"
    }
    """
    try:
        BookmarkService.unbookmark_question(bookmark_id, current_user.id)
        
        return jsonify({
            'code': 200,
            'message': '取消收藏成功'
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


@bookmarks_bp.route('/question/<int:question_id>', methods=['GET'])
@jwt_required_with_user
def check_bookmark(current_user, question_id):
    """检查题目是否已收藏
    
    响应:
    {
        "code": 200,
        "message": "获取成功",
        "data": {
            "is_bookmarked": true
        }
    }
    """
    try:
        is_bookmarked = BookmarkService.is_bookmarked(current_user.id, question_id)
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'is_bookmarked': is_bookmarked
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(e)}'
        }), 500


@bookmarks_bp.route('/question/<int:question_id>', methods=['DELETE'])
@jwt_required_with_user
def unbookmark_by_question(current_user, question_id):
    """根据题目ID取消收藏
    
    响应:
    {
        "code": 200,
        "message": "取消收藏成功"
    }
    """
    try:
        BookmarkService.unbookmark_by_question(current_user.id, question_id)
        
        return jsonify({
            'code': 200,
            'message': '取消收藏成功'
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


@bookmarks_bp.route('/count', methods=['GET'])
@jwt_required_with_user
def get_bookmark_count(current_user):
    """获取收藏总数
    
    响应:
    {
        "code": 200,
        "message": "获取成功",
        "data": {
            "count": 42
        }
    }
    """
    try:
        count = BookmarkService.get_bookmark_count(current_user.id)
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'count': count
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'服务器错误: {str(e)}'
        }), 500
