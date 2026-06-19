"""试卷管理服务"""
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from sqlalchemy import and_, or_
from sqlalchemy.orm import joinedload

from app import db
from app.models.exam import ExamPaper, ExamPaperQuestion
from app.models.question import Question


class ExamPaperService:
    """试卷管理服务类"""
    
    @staticmethod
    def create_paper(
        name: str,
        exam_type: str,
        created_by: int,
        duration: int,
        description: Optional[str] = None,
        total_score: Optional[int] = None,
        pass_score: Optional[int] = None
    ) -> ExamPaper:
        """创建试卷
        
        Args:
            name: 试卷名称
            exam_type: 考试类型
            created_by: 创建者ID
            duration: 考试时长（分钟）
            description: 试卷描述
            total_score: 总分
            pass_score: 及格分
            
        Returns:
            创建的试卷对象
            
        Raises:
            ValueError: 参数验证失败
        """
        if not name or not name.strip():
            raise ValueError('试卷名称不能为空')
        
        if exam_type not in ['civil_service', 'postgraduate', 'public_institution']:
            raise ValueError('无效的考试类型')
        
        if duration <= 0:
            raise ValueError('考试时长必须大于0')
        
        if total_score is not None and total_score < 0:
            raise ValueError('总分不能为负数')
        
        # 计算实际总分（如果未提供，默认为0）
        actual_total_score = total_score if total_score is not None else 0
        
        if pass_score is not None:
            if pass_score < 0:
                raise ValueError('及格分不能为负数')
            if pass_score > actual_total_score:
                raise ValueError('及格分不能大于总分')
        
        paper = ExamPaper(
            name=name.strip(),
            exam_type=exam_type,
            description=description.strip() if description else None,
            duration=duration,
            total_score=actual_total_score,
            pass_score=pass_score or 0,
            created_by=created_by,
            is_published=False,
            version=1
        )
        
        db.session.add(paper)
        db.session.commit()
        
        return paper

    
    @staticmethod
    def add_question_to_paper(
        paper_id: int,
        question_id: int,
        order: int,
        score: int
    ) -> ExamPaperQuestion:
        """添加题目到试卷
        
        Args:
            paper_id: 试卷ID
            question_id: 题目ID
            order: 题目顺序
            score: 题目分值
            
        Returns:
            试卷题目关联对象
            
        Raises:
            ValueError: 参数验证失败
            RuntimeError: 试卷已发布或题目不存在
        """
        # 验证试卷存在
        paper = ExamPaper.query.get(paper_id)
        if not paper:
            raise ValueError('试卷不存在')
        
        # 检查试卷是否已发布
        if paper.is_published:
            raise RuntimeError('已发布的试卷不能添加题目，请创建新版本')
        
        # 验证题目存在且未删除
        question = Question.query.get(question_id)
        if not question or question.is_deleted:
            raise ValueError('题目不存在或已删除')
        
        # 验证参数
        if order <= 0:
            raise ValueError('题目顺序必须大于0')
        
        if score <= 0:
            raise ValueError('题目分值必须大于0')
        
        # 检查题目是否已存在
        existing = ExamPaperQuestion.query.filter_by(
            paper_id=paper_id,
            question_id=question_id
        ).first()
        if existing:
            raise ValueError('题目已存在于试卷中')
        
        # 创建关联
        paper_question = ExamPaperQuestion(
            paper_id=paper_id,
            question_id=question_id,
            order=order,
            score=score
        )
        
        db.session.add(paper_question)
        
        # 更新试卷总分
        paper.total_score += score
        
        db.session.commit()
        
        return paper_question
    
    @staticmethod
    def publish_paper(paper_id: int) -> ExamPaper:
        """发布试卷
        
        Args:
            paper_id: 试卷ID
            
        Returns:
            发布后的试卷对象
            
        Raises:
            ValueError: 试卷不存在或已发布
            RuntimeError: 试卷没有题目
        """
        paper = ExamPaper.query.get(paper_id)
        if not paper:
            raise ValueError('试卷不存在')
        
        if paper.is_published:
            raise ValueError('试卷已发布')
        
        # 检查试卷是否有题目
        question_count = ExamPaperQuestion.query.filter_by(paper_id=paper_id).count()
        if question_count == 0:
            raise RuntimeError('试卷必须至少包含一道题目才能发布')
        
        paper.is_published = True
        db.session.commit()
        
        return paper

    
    @staticmethod
    def edit_paper(paper_id: int, **kwargs) -> ExamPaper:
        """编辑试卷（版本控制）
        
        如果试卷已发布，创建新版本；否则直接更新
        
        Args:
            paper_id: 试卷ID
            **kwargs: 要更新的字段
            
        Returns:
            更新后的试卷对象（可能是新版本）
            
        Raises:
            ValueError: 试卷不存在或参数无效
        """
        paper = ExamPaper.query.get(paper_id)
        if not paper:
            raise ValueError('试卷不存在')
        
        # 如果试卷已发布，创建新版本
        if paper.is_published:
            return ExamPaperService._create_new_version(paper, **kwargs)
        
        # 未发布的试卷直接更新
        allowed_fields = ['name', 'description', 'duration', 'pass_score']
        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                if field == 'name':
                    if not value or not value.strip():
                        raise ValueError('试卷名称不能为空')
                    paper.name = value.strip()
                elif field == 'description':
                    paper.description = value.strip() if value else None
                elif field == 'duration':
                    if value <= 0:
                        raise ValueError('考试时长必须大于0')
                    paper.duration = value
                elif field == 'pass_score':
                    if value < 0:
                        raise ValueError('及格分不能为负数')
                    if value > paper.total_score:
                        raise ValueError('及格分不能大于总分')
                    paper.pass_score = value
        
        paper.updated_at = datetime.utcnow()
        db.session.commit()
        
        return paper
    
    @staticmethod
    def _create_new_version(old_paper: ExamPaper, **kwargs) -> ExamPaper:
        """创建试卷新版本（内部方法）
        
        Args:
            old_paper: 原试卷对象
            **kwargs: 要更新的字段
            
        Returns:
            新版本试卷对象
        """
        # 创建新版本试卷
        new_paper = ExamPaper(
            name=kwargs.get('name', old_paper.name),
            exam_type=old_paper.exam_type,
            description=kwargs.get('description', old_paper.description),
            duration=kwargs.get('duration', old_paper.duration),
            total_score=old_paper.total_score,
            pass_score=kwargs.get('pass_score', old_paper.pass_score),
            created_by=old_paper.created_by,
            is_published=False,
            version=old_paper.version + 1
        )
        
        db.session.add(new_paper)
        db.session.flush()  # 获取新试卷ID
        
        # 复制题目关联
        old_questions = ExamPaperQuestion.query.filter_by(
            paper_id=old_paper.id
        ).all()
        
        for old_q in old_questions:
            new_q = ExamPaperQuestion(
                paper_id=new_paper.id,
                question_id=old_q.question_id,
                order=old_q.order,
                score=old_q.score
            )
            db.session.add(new_q)
        
        db.session.commit()
        
        return new_paper

    
    @staticmethod
    def delete_paper(paper_id: int) -> bool:
        """软删除试卷
        
        Args:
            paper_id: 试卷ID
            
        Returns:
            是否删除成功
            
        Raises:
            ValueError: 试卷不存在
        """
        paper = ExamPaper.query.get(paper_id)
        if not paper:
            raise ValueError('试卷不存在')
        
        # 软删除：标记为不可用
        paper.is_published = False
        paper.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return True
    
    @staticmethod
    def get_paper(paper_id: int, include_questions: bool = False) -> Optional[ExamPaper]:
        """获取试卷详情
        
        Args:
            paper_id: 试卷ID
            include_questions: 是否包含题目列表（此参数已弃用，题目通过 get_paper_questions 单独获取）
            
        Returns:
            试卷对象，不存在返回None
        """
        # 注意：由于 paper_questions 使用 lazy='dynamic'，不能使用 joinedload
        # 如果需要题目列表，请单独调用 get_paper_questions 方法
        return ExamPaper.query.get(paper_id)
    
    @staticmethod
    def list_papers(
        exam_type: Optional[str] = None,
        is_published: Optional[bool] = None,
        created_by: Optional[int] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[ExamPaper], int]:
        """获取试卷列表
        
        Args:
            exam_type: 考试类型筛选
            is_published: 发布状态筛选
            created_by: 创建者ID筛选
            page: 页码
            page_size: 每页数量
            
        Returns:
            (试卷列表, 总数)
        """
        query = ExamPaper.query
        
        # 应用筛选条件
        if exam_type:
            query = query.filter_by(exam_type=exam_type)
        
        if is_published is not None:
            query = query.filter_by(is_published=is_published)
        
        if created_by:
            query = query.filter_by(created_by=created_by)
        
        # 按创建时间倒序
        query = query.order_by(ExamPaper.created_at.desc())
        
        # 分页
        total = query.count()
        papers = query.offset((page - 1) * page_size).limit(page_size).all()
        
        return papers, total
    
    @staticmethod
    def get_paper_questions(paper_id: int) -> List[Dict]:
        """获取试卷的所有题目
        
        Args:
            paper_id: 试卷ID
            
        Returns:
            题目列表（包含顺序和分值）
        """
        paper_questions = ExamPaperQuestion.query.filter_by(
            paper_id=paper_id
        ).options(
            joinedload(ExamPaperQuestion.question)
        ).order_by(ExamPaperQuestion.order).all()
        
        result = []
        for pq in paper_questions:
            if pq.question and not pq.question.is_deleted:
                question_dict = pq.question.to_dict()
                question_dict['order'] = pq.order
                question_dict['score'] = pq.score
                result.append(question_dict)
        
        return result
    
    @staticmethod
    def remove_question_from_paper(paper_id: int, question_id: int) -> bool:
        """从试卷中移除题目
        
        Args:
            paper_id: 试卷ID
            question_id: 题目ID
            
        Returns:
            是否移除成功
            
        Raises:
            ValueError: 试卷不存在或题目不在试卷中
            RuntimeError: 试卷已发布
        """
        paper = ExamPaper.query.get(paper_id)
        if not paper:
            raise ValueError('试卷不存在')
        
        if paper.is_published:
            raise RuntimeError('已发布的试卷不能移除题目，请创建新版本')
        
        paper_question = ExamPaperQuestion.query.filter_by(
            paper_id=paper_id,
            question_id=question_id
        ).first()
        
        if not paper_question:
            raise ValueError('题目不在试卷中')
        
        # 更新试卷总分
        paper.total_score -= paper_question.score
        
        db.session.delete(paper_question)
        db.session.commit()
        
        return True
