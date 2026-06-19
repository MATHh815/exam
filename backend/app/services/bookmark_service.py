"""题目收藏服务模块"""
from datetime import datetime
from typing import Optional, List, Dict
from sqlalchemy import or_, and_
from app import db
from app.models.note import QuestionBookmark
from app.models.question import Question


class BookmarkService:
    """题目收藏服务类
    
    提供题目收藏的创建、删除、查询和管理等功能。
    """
    
    @staticmethod
    def bookmark_question(user_id: int, bookmark_data: dict) -> QuestionBookmark:
        """收藏题目
        
        Args:
            user_id: 用户ID
            bookmark_data: 收藏数据
                - question_id: 题目ID（必填）
                - tags: 标签列表（可选）
                - notes: 备注（可选）
        
        Returns:
            QuestionBookmark: 创建的收藏对象
        
        Raises:
            ValueError: 数据验证失败
        """
        # 验证必填字段
        if not bookmark_data.get('question_id'):
            raise ValueError('题目ID不能为空')
        
        question_id = bookmark_data['question_id']
        
        # 验证题目存在
        question = Question.query.get(question_id)
        if not question or question.is_deleted:
            raise ValueError('题目不存在')
        
        # 检查是否已收藏
        existing_bookmark = QuestionBookmark.query.filter_by(
            user_id=user_id,
            question_id=question_id
        ).first()
        
        if existing_bookmark:
            raise ValueError('该题目已收藏')
        
        # 创建收藏
        bookmark = QuestionBookmark(
            user_id=user_id,
            question_id=question_id,
            tags=bookmark_data.get('tags', []),
            notes=bookmark_data.get('notes', '')
        )
        
        db.session.add(bookmark)
        db.session.commit()
        
        return bookmark
    
    @staticmethod
    def unbookmark_question(bookmark_id: int, user_id: int) -> bool:
        """取消收藏题目
        
        Args:
            bookmark_id: 收藏ID
            user_id: 用户ID
        
        Returns:
            bool: 是否取消成功
        
        Raises:
            ValueError: 收藏不存在或无权访问
        """
        bookmark = QuestionBookmark.query.filter_by(
            id=bookmark_id,
            user_id=user_id
        ).first()
        
        if not bookmark:
            raise ValueError('收藏不存在或无权访问')
        
        db.session.delete(bookmark)
        db.session.commit()
        
        return True
    
    @staticmethod
    def unbookmark_by_question(user_id: int, question_id: int) -> bool:
        """根据题目ID取消收藏
        
        Args:
            user_id: 用户ID
            question_id: 题目ID
        
        Returns:
            bool: 是否取消成功
        
        Raises:
            ValueError: 收藏不存在
        """
        bookmark = QuestionBookmark.query.filter_by(
            user_id=user_id,
            question_id=question_id
        ).first()
        
        if not bookmark:
            raise ValueError('该题目未收藏')
        
        db.session.delete(bookmark)
        db.session.commit()
        
        return True
    
    @staticmethod
    def get_bookmarks(
        user_id: int,
        page: int = 1,
        per_page: int = 20,
        exam_type: Optional[str] = None,
        subject: Optional[str] = None,
        chapter: Optional[str] = None,
        difficulty: Optional[int] = None,
        tags: Optional[List[str]] = None,
        sort_by: str = 'created_desc'
    ) -> Dict:
        """获取用户的收藏列表（支持分页和过滤）
        
        Args:
            user_id: 用户ID
            page: 页码（从1开始）
            per_page: 每页数量
            exam_type: 考试类型（可选）
            subject: 科目（可选）
            chapter: 章节（可选）
            difficulty: 难度（可选）
            tags: 标签列表（可选）
            sort_by: 排序方式（created_desc, created_asc, difficulty_desc, difficulty_asc）
        
        Returns:
            Dict: 包含收藏列表和分页信息
                - bookmarks: 收藏列表
                - total: 总数
                - page: 当前页
                - per_page: 每页数量
                - pages: 总页数
        """
        query = QuestionBookmark.query.filter_by(
            user_id=user_id
        ).join(Question)
        
        # 考试类型过滤
        if exam_type:
            query = query.filter(Question.exam_type == exam_type)
        
        # 科目过滤
        if subject:
            query = query.filter(Question.subject == subject)
        
        # 章节过滤
        if chapter:
            query = query.filter(Question.chapter == chapter)
        
        # 难度过滤
        if difficulty:
            query = query.filter(Question.difficulty == difficulty)
        
        # 标签过滤
        if tags:
            for tag in tags:
                query = query.filter(QuestionBookmark.tags.contains([tag]))
        
        # 排序
        if sort_by == 'created_asc':
            query = query.order_by(QuestionBookmark.created_at.asc())
        elif sort_by == 'difficulty_desc':
            query = query.order_by(Question.difficulty.desc())
        elif sort_by == 'difficulty_asc':
            query = query.order_by(Question.difficulty.asc())
        else:  # created_desc - 默认
            query = query.order_by(QuestionBookmark.created_at.desc())
        
        # 分页
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return {
            'bookmarks': pagination.items,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
    
    @staticmethod
    def get_bookmark_by_id(bookmark_id: int, user_id: int) -> QuestionBookmark:
        """根据ID获取收藏
        
        Args:
            bookmark_id: 收藏ID
            user_id: 用户ID
        
        Returns:
            QuestionBookmark: 收藏对象
        
        Raises:
            ValueError: 收藏不存在或无权访问
        """
        bookmark = QuestionBookmark.query.filter_by(
            id=bookmark_id,
            user_id=user_id
        ).first()
        
        if not bookmark:
            raise ValueError('收藏不存在或无权访问')
        
        return bookmark
    
    @staticmethod
    def is_bookmarked(user_id: int, question_id: int) -> bool:
        """检查题目是否已收藏
        
        Args:
            user_id: 用户ID
            question_id: 题目ID
        
        Returns:
            bool: 是否已收藏
        """
        return QuestionBookmark.query.filter_by(
            user_id=user_id,
            question_id=question_id
        ).count() > 0
    
    @staticmethod
    def update_bookmark(bookmark_id: int, user_id: int, update_data: dict) -> QuestionBookmark:
        """更新收藏信息
        
        Args:
            bookmark_id: 收藏ID
            user_id: 用户ID
            update_data: 更新数据
                - tags: 标签列表（可选）
                - notes: 备注（可选）
        
        Returns:
            QuestionBookmark: 更新后的收藏对象
        
        Raises:
            ValueError: 收藏不存在或无权访问
        """
        bookmark = QuestionBookmark.query.filter_by(
            id=bookmark_id,
            user_id=user_id
        ).first()
        
        if not bookmark:
            raise ValueError('收藏不存在或无权访问')
        
        # 更新标签
        if 'tags' in update_data:
            bookmark.tags = update_data['tags']
        
        # 更新备注
        if 'notes' in update_data:
            bookmark.notes = update_data['notes']
        
        bookmark.updated_at = datetime.utcnow()
        db.session.commit()
        
        return bookmark
    
    @staticmethod
    def get_bookmark_count(user_id: int) -> int:
        """获取用户收藏总数
        
        Args:
            user_id: 用户ID
        
        Returns:
            int: 收藏总数
        """
        return QuestionBookmark.query.filter_by(user_id=user_id).count()
    
    @staticmethod
    def get_bookmarks_by_tag(user_id: int, tag: str) -> List[QuestionBookmark]:
        """根据标签获取收藏列表
        
        Args:
            user_id: 用户ID
            tag: 标签
        
        Returns:
            List[QuestionBookmark]: 收藏列表
        """
        return QuestionBookmark.query.filter_by(
            user_id=user_id
        ).filter(
            QuestionBookmark.tags.contains([tag])
        ).order_by(QuestionBookmark.created_at.desc()).all()
