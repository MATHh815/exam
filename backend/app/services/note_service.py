"""笔记管理服务模块"""
from datetime import datetime
from typing import Optional, List, Dict
from sqlalchemy import or_, and_
from app import db
from app.models.note import QuestionNote, QuestionBookmark
from app.models.question import Question
import re


class NoteService:
    """笔记管理服务类
    
    提供题目笔记的创建、更新、删除、查询和搜索等功能。
    支持 Markdown 格式的笔记内容和题目链接。
    """
    
    # Markdown 格式验证的简单正则（检查是否包含常见 Markdown 语法）
    MARKDOWN_PATTERN = re.compile(r'[#*_`\[\]()>-]')
    
    # 题目链接正则：[[Q:123]] 或 [[题:关键词]]
    QUESTION_LINK_PATTERN = re.compile(r'\[\[Q:(\d+)\]\]')
    
    @staticmethod
    def extract_linked_questions(content: str) -> List[int]:
        """从笔记内容中提取链接的题目ID
        
        Args:
            content: 笔记内容
        
        Returns:
            List[int]: 题目ID列表
        """
        matches = NoteService.QUESTION_LINK_PATTERN.findall(content)
        return [int(qid) for qid in matches]
    
    @staticmethod
    def create_note(user_id: int, note_data: dict) -> QuestionNote:
        """创建题目笔记
        
        Args:
            user_id: 用户ID
            note_data: 笔记数据
                - question_id: 题目ID（必填）
                - content: 笔记内容（必填，1-5000字符）
                - tags: 标签列表（可选）
        
        Returns:
            QuestionNote: 创建的笔记对象
        
        Raises:
            ValueError: 数据验证失败
        """
        # 验证必填字段
        if not note_data.get('question_id'):
            raise ValueError('题目ID不能为空')
        
        if not note_data.get('content'):
            raise ValueError('笔记内容不能为空')
        
        # 验证题目存在
        question = Question.query.get(note_data['question_id'])
        if not question:
            raise ValueError('题目不存在')
        
        # 验证内容长度
        content = note_data['content'].strip()
        if len(content) < 1:
            raise ValueError('笔记内容不能为空')
        if len(content) > 5000:
            raise ValueError('笔记内容不能超过5000个字符')
        
        # 检查是否已存在该题目的笔记
        existing_note = QuestionNote.query.filter_by(
            user_id=user_id,
            question_id=note_data['question_id'],
            is_deleted=False
        ).first()
        
        if existing_note:
            raise ValueError('该题目已有笔记，请使用更新功能')
        
        # 提取链接的题目ID
        linked_questions = NoteService.extract_linked_questions(content)
        
        # 创建笔记
        note = QuestionNote(
            user_id=user_id,
            question_id=note_data['question_id'],
            content=content,
            tags=note_data.get('tags', []),
            linked_questions=linked_questions
        )
        
        db.session.add(note)
        db.session.commit()
        
        return note
    
    @staticmethod
    def update_note(note_id: int, user_id: int, update_data: dict) -> QuestionNote:
        """更新题目笔记
        
        Args:
            note_id: 笔记ID
            user_id: 用户ID
            update_data: 更新数据
                - content: 笔记内容（可选）
                - tags: 标签列表（可选）
        
        Returns:
            QuestionNote: 更新后的笔记对象
        
        Raises:
            ValueError: 笔记不存在或无权访问
        """
        note = QuestionNote.query.filter_by(
            id=note_id,
            user_id=user_id,
            is_deleted=False
        ).first()
        
        if not note:
            raise ValueError('笔记不存在或无权访问')
        
        # 更新内容
        if 'content' in update_data:
            content = update_data['content'].strip()
            if len(content) < 1:
                raise ValueError('笔记内容不能为空')
            if len(content) > 5000:
                raise ValueError('笔记内容不能超过5000个字符')
            note.content = content
            
            # 更新链接的题目ID
            note.linked_questions = NoteService.extract_linked_questions(content)
        
        # 更新标签
        if 'tags' in update_data:
            note.tags = update_data['tags']
        
        note.updated_at = datetime.utcnow()
        db.session.commit()
        
        return note
    
    @staticmethod
    def delete_note(note_id: int, user_id: int) -> bool:
        """删除题目笔记（软删除）
        
        Args:
            note_id: 笔记ID
            user_id: 用户ID
        
        Returns:
            bool: 是否删除成功
        
        Raises:
            ValueError: 笔记不存在或无权访问
        """
        note = QuestionNote.query.filter_by(
            id=note_id,
            user_id=user_id,
            is_deleted=False
        ).first()
        
        if not note:
            raise ValueError('笔记不存在或无权访问')
        
        note.is_deleted = True
        note.updated_at = datetime.utcnow()
        db.session.commit()
        
        return True
    
    @staticmethod
    def get_question_notes(user_id: int, question_id: int) -> Optional[QuestionNote]:
        """获取指定题目的笔记
        
        Args:
            user_id: 用户ID
            question_id: 题目ID
        
        Returns:
            Optional[QuestionNote]: 笔记对象，如果不存在则返回 None
        """
        return QuestionNote.query.filter_by(
            user_id=user_id,
            question_id=question_id,
            is_deleted=False
        ).first()
    
    @staticmethod
    def get_user_notes(
        user_id: int,
        page: int = 1,
        per_page: int = 20,
        subject: Optional[str] = None,
        chapter: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Dict:
        """获取用户的笔记列表（支持分页和过滤）
        
        Args:
            user_id: 用户ID
            page: 页码（从1开始）
            per_page: 每页数量
            subject: 科目名称（可选）
            chapter: 章节名称（可选）
            tags: 标签列表（可选）
        
        Returns:
            Dict: 包含笔记列表和分页信息
                - notes: 笔记列表
                - total: 总数
                - page: 当前页
                - per_page: 每页数量
                - pages: 总页数
        """
        query = QuestionNote.query.filter_by(
            user_id=user_id,
            is_deleted=False
        ).join(Question)
        
        # 科目过滤
        if subject:
            query = query.filter(Question.subject == subject)
        
        # 章节过滤
        if chapter:
            query = query.filter(Question.chapter == chapter)
        
        # 标签过滤
        if tags:
            for tag in tags:
                query = query.filter(QuestionNote.tags.contains([tag]))
        
        # 按更新时间倒序
        query = query.order_by(QuestionNote.updated_at.desc())
        
        # 分页
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return {
            'notes': pagination.items,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
    
    @staticmethod
    def search_notes(
        user_id: int,
        keyword: str,
        page: int = 1,
        per_page: int = 20,
        subject: Optional[str] = None,
        chapter: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        sort_by: str = 'relevance'
    ) -> Dict:
        """搜索笔记
        
        Args:
            user_id: 用户ID
            keyword: 搜索关键词
            page: 页码（从1开始）
            per_page: 每页数量
            subject: 科目名称（可选）
            chapter: 章节名称（可选）
            date_from: 开始日期（可选）
            date_to: 结束日期（可选）
            sort_by: 排序方式（relevance, date_desc, date_asc）
        
        Returns:
            Dict: 包含搜索结果和分页信息
                - notes: 笔记列表
                - total: 总数
                - page: 当前页
                - per_page: 每页数量
                - pages: 总页数
                - keyword: 搜索关键词
        """
        if not keyword or not keyword.strip():
            raise ValueError('搜索关键词不能为空')
        
        keyword = keyword.strip()
        
        # 构建基础查询
        query = QuestionNote.query.filter_by(
            user_id=user_id,
            is_deleted=False
        ).join(Question)
        
        # 关键词搜索（不区分大小写）
        search_pattern = f'%{keyword}%'
        query = query.filter(
            or_(
                QuestionNote.content.ilike(search_pattern),
                Question.content.ilike(search_pattern)
            )
        )
        
        # 科目过滤
        if subject:
            query = query.filter(Question.subject == subject)
        
        # 章节过滤
        if chapter:
            query = query.filter(Question.chapter == chapter)
        
        # 日期范围过滤
        if date_from:
            query = query.filter(QuestionNote.created_at >= date_from)
        if date_to:
            query = query.filter(QuestionNote.created_at <= date_to)
        
        # 排序
        if sort_by == 'date_desc':
            query = query.order_by(QuestionNote.updated_at.desc())
        elif sort_by == 'date_asc':
            query = query.order_by(QuestionNote.updated_at.asc())
        else:  # relevance - 默认按更新时间倒序
            query = query.order_by(QuestionNote.updated_at.desc())
        
        # 分页
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return {
            'notes': pagination.items,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages,
            'keyword': keyword
        }
    
    @staticmethod
    def get_note_by_id(note_id: int, user_id: int) -> QuestionNote:
        """根据ID获取笔记
        
        Args:
            note_id: 笔记ID
            user_id: 用户ID
        
        Returns:
            QuestionNote: 笔记对象
        
        Raises:
            ValueError: 笔记不存在或无权访问
        """
        note = QuestionNote.query.filter_by(
            id=note_id,
            user_id=user_id,
            is_deleted=False
        ).first()
        
        if not note:
            raise ValueError('笔记不存在或无权访问')
        
        return note
    
    @staticmethod
    def has_note_for_question(user_id: int, question_id: int) -> bool:
        """检查用户是否为指定题目创建了笔记
        
        Args:
            user_id: 用户ID
            question_id: 题目ID
        
        Returns:
            bool: 是否存在笔记
        """
        return QuestionNote.query.filter_by(
            user_id=user_id,
            question_id=question_id,
            is_deleted=False
        ).count() > 0
    
    @staticmethod
    def validate_markdown(content: str) -> bool:
        """验证内容是否包含 Markdown 格式
        
        Args:
            content: 笔记内容
        
        Returns:
            bool: 是否包含 Markdown 语法
        """
        return bool(NoteService.MARKDOWN_PATTERN.search(content))
