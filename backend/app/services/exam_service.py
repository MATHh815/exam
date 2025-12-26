"""考试服务"""
from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import joinedload

from app import db
from app.models.exam import ExamPaper, ExamSession, ExamResult
from app.models.user import User


class ExamService:
    """考试服务类"""
    
    @staticmethod
    def start_exam(user_id: int, paper_id: int) -> ExamSession:
        """开始考试（创建会话）
        
        Args:
            user_id: 用户ID
            paper_id: 试卷ID
            
        Returns:
            考试会话对象
            
        Raises:
            ValueError: 参数验证失败
            RuntimeError: 试卷未发布或用户不存在
        """
        # 验证用户存在
        user = User.query.get(user_id)
        if not user:
            raise ValueError('用户不存在')
        
        # 验证试卷存在且已发布
        paper = ExamPaper.query.get(paper_id)
        if not paper:
            raise ValueError('试卷不存在')
        
        if not paper.is_published:
            raise RuntimeError('试卷未发布，无法开始考试')
        
        # 验证试卷是否有题目
        from app.models.exam import ExamPaperQuestion
        question_count = ExamPaperQuestion.query.filter_by(paper_id=paper_id).count()
        if question_count == 0:
            raise RuntimeError('该试卷暂无题目，无法开始考试')
        
        # 检查是否有进行中的考试
        existing_session = ExamSession.query.filter_by(
            user_id=user_id,
            paper_id=paper_id,
            status='in_progress'
        ).first()
        
        if existing_session:
            raise RuntimeError('已有进行中的考试，请先完成或提交')
        
        # 创建考试会话
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(minutes=paper.duration)
        
        session = ExamSession(
            user_id=user_id,
            paper_id=paper_id,
            start_time=start_time,
            end_time=end_time,
            status='in_progress',
            answers={}
        )
        
        db.session.add(session)
        db.session.commit()
        
        return session
    
    @staticmethod
    def submit_answer(session_id: int, question_id: int, answer: str, question_index: int = None) -> bool:
        """提交单题答案（实时保存）
        
        Args:
            session_id: 考试会话ID
            question_id: 题目ID
            answer: 用户答案
            question_index: 当前题目索引（可选）
            
        Returns:
            是否保存成功
            
        Raises:
            ValueError: 会话不存在
            RuntimeError: 考试已结束或超时
        """
        session = ExamSession.query.get(session_id)
        if not session:
            raise ValueError('考试会话不存在')
        
        if session.status not in ['in_progress', 'paused']:
            raise RuntimeError('考试已结束，无法提交答案')
        
        # 检查是否超时
        if datetime.utcnow() > session.end_time:
            # 自动超时提交
            ExamService._timeout_submit(session)
            raise RuntimeError('考试时间已到，已自动提交')
        
        # 保存答案
        session.save_answer(question_id, answer)
        
        # 更新进度
        if question_index is not None:
            session.update_progress(question_index)
        
        # 如果是暂停状态，恢复为进行中
        if session.status == 'paused':
            session.status = 'in_progress'
        
        db.session.commit()
        
        return True
    
    @staticmethod
    def save_progress(session_id: int, question_index: int) -> bool:
        """保存考试进度（当前做到第几题）
        
        Args:
            session_id: 考试会话ID
            question_index: 当前题目索引
            
        Returns:
            是否保存成功
        """
        session = ExamSession.query.get(session_id)
        if not session:
            raise ValueError('考试会话不存在')
        
        if session.status not in ['in_progress', 'paused']:
            return False
        
        session.update_progress(question_index)
        db.session.commit()
        
        return True
    
    @staticmethod
    def pause_exam(session_id: int) -> ExamSession:
        """暂停考试（用于断点续考）
        
        Args:
            session_id: 考试会话ID
            
        Returns:
            考试会话对象
        """
        session = ExamSession.query.get(session_id)
        if not session:
            raise ValueError('考试会话不存在')
        
        if session.status != 'in_progress':
            raise RuntimeError('只能暂停进行中的考试')
        
        session.pause()
        db.session.commit()
        
        return session
    
    @staticmethod
    def resume_exam(session_id: int) -> ExamSession:
        """恢复暂停的考试
        
        Args:
            session_id: 考试会话ID
            
        Returns:
            考试会话对象
        """
        session = ExamSession.query.get(session_id)
        if not session:
            raise ValueError('考试会话不存在')
        
        if session.status not in ['paused', 'in_progress']:
            raise RuntimeError('该考试无法恢复')
        
        # 检查是否已超时
        if datetime.utcnow() > session.end_time:
            raise RuntimeError('考试时间已过，无法恢复')
        
        session.status = 'in_progress'
        session.last_active_time = datetime.utcnow()
        db.session.commit()
        
        return session
    
    @staticmethod
    def submit_exam(session_id: int) -> ExamResult:
        """提交试卷（计算成绩）
        
        Args:
            session_id: 考试会话ID
            
        Returns:
            考试结果对象
            
        Raises:
            ValueError: 会话不存在
            RuntimeError: 考试已提交
        """
        session = ExamSession.query.get(session_id)
        if not session:
            raise ValueError('考试会话不存在')
        
        if session.status != 'in_progress':
            raise RuntimeError('考试已提交，无法重复提交')
        
        # 标记会话为已提交
        session.submit()
        
        # 计算成绩
        score_data = ExamResult.calculate_score(session)
        
        # 创建考试结果
        result = ExamResult(
            session_id=session.id,
            user_id=session.user_id,
            paper_id=session.paper_id,
            total_score=score_data['total_score'],
            score=score_data['score'],
            correct_count=score_data['correct_count'],
            wrong_count=score_data['wrong_count'],
            accuracy=score_data['accuracy'],
            time_spent=score_data['time_spent'],
            details=score_data['details']
        )
        
        db.session.add(result)
        db.session.commit()
        
        return result
    
    @staticmethod
    def _timeout_submit(session: ExamSession) -> ExamResult:
        """考试超时自动提交（内部方法）
        
        Args:
            session: 考试会话对象
            
        Returns:
            考试结果对象
        """
        # 标记会话为超时
        session.timeout()
        
        # 计算成绩
        score_data = ExamResult.calculate_score(session)
        
        # 创建考试结果
        result = ExamResult(
            session_id=session.id,
            user_id=session.user_id,
            paper_id=session.paper_id,
            total_score=score_data['total_score'],
            score=score_data['score'],
            correct_count=score_data['correct_count'],
            wrong_count=score_data['wrong_count'],
            accuracy=score_data['accuracy'],
            time_spent=score_data['time_spent'],
            details=score_data['details']
        )
        
        db.session.add(result)
        db.session.commit()
        
        return result
    
    @staticmethod
    def get_exam_result(result_id: int, include_details: bool = False) -> Optional[ExamResult]:
        """获取考试结果
        
        Args:
            result_id: 结果ID
            include_details: 是否包含详细信息
            
        Returns:
            考试结果对象，不存在返回None
        """
        result = ExamResult.query.get(result_id)
        return result
    
    @staticmethod
    def get_session_result(session_id: int) -> Optional[ExamResult]:
        """根据会话ID获取考试结果
        
        Args:
            session_id: 会话ID
            
        Returns:
            考试结果对象，不存在返回None
        """
        result = ExamResult.query.filter_by(session_id=session_id).first()
        return result
    
    @staticmethod
    def list_user_exams(
        user_id: int,
        paper_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[ExamResult], int]:
        """获取用户考试历史
        
        Args:
            user_id: 用户ID
            paper_id: 试卷ID筛选（可选）
            page: 页码
            page_size: 每页数量
            
        Returns:
            (考试结果列表, 总数)
        """
        query = ExamResult.query.filter_by(user_id=user_id)
        
        if paper_id:
            query = query.filter_by(paper_id=paper_id)
        
        # 按创建时间倒序
        query = query.order_by(ExamResult.created_at.desc())
        
        # 分页
        total = query.count()
        results = query.offset((page - 1) * page_size).limit(page_size).all()
        
        return results, total
    
    @staticmethod
    def list_user_sessions(
        user_id: int,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[ExamSession], int]:
        """获取用户所有考试会话（包括未完成的）
        
        Args:
            user_id: 用户ID
            status: 状态筛选（可选）: in_progress, paused, submitted, timeout
            page: 页码
            page_size: 每页数量
            
        Returns:
            (考试会话列表, 总数)
        """
        query = ExamSession.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        
        # 按开始时间倒序
        query = query.order_by(ExamSession.start_time.desc())
        
        # 分页
        total = query.count()
        sessions = query.offset((page - 1) * page_size).limit(page_size).all()
        
        return sessions, total
    
    @staticmethod
    def get_user_incomplete_sessions(user_id: int) -> List[ExamSession]:
        """获取用户所有未完成的考试会话
        
        Args:
            user_id: 用户ID
            
        Returns:
            未完成的考试会话列表
        """
        return ExamSession.query.filter(
            ExamSession.user_id == user_id,
            ExamSession.status.in_(['in_progress', 'paused'])
        ).order_by(ExamSession.last_active_time.desc()).all()
    
    @staticmethod
    def get_session(session_id: int) -> Optional[ExamSession]:
        """获取考试会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            考试会话对象，不存在返回None
        """
        return ExamSession.query.get(session_id)
    
    @staticmethod
    def check_timeout_and_submit(session_id: int) -> Optional[ExamResult]:
        """检查考试是否超时并自动提交
        
        Args:
            session_id: 会话ID
            
        Returns:
            如果超时则返回考试结果，否则返回None
            
        Raises:
            ValueError: 会话不存在
        """
        session = ExamSession.query.get(session_id)
        if not session:
            raise ValueError('考试会话不存在')
        
        # 如果已经结束，直接返回
        if session.status != 'in_progress':
            return None
        
        # 检查是否超时
        if datetime.utcnow() > session.end_time:
            return ExamService._timeout_submit(session)
        
        return None
