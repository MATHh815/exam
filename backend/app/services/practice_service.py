"""练习服务模块"""
from datetime import datetime
from app import db
from app.models.practice import PracticeRecord, WrongQuestion
from app.models.question import Question
from app.models.statistics import StudyStatistics
from app.services.question_service import QuestionService


class PracticeService:
    """练习服务类
    
    提供练习题目抽取、答案提交、历史查询和错题本管理等功能
    """
    
    @staticmethod
    def start_practice(user_id, filters=None, count=10):
        """开始练习（根据筛选条件抽题）
        
        Args:
            user_id: 用户ID
            filters: 筛选条件字典
                - exam_type: 考试类型
                - question_type: 题目类型
                - subject: 科目
                - chapter: 章节
                - difficulty: 难度
                - from_wrong_book: 是否从错题本抽题
            count: 抽取题目数量
        
        Returns:
            list: 题目列表
        """
        # 如果从错题本抽题
        if filters and filters.get('from_wrong_book'):
            wrong_questions = WrongQuestion.query.filter_by(
                user_id=user_id,
                mastered=False
            ).limit(count).all()
            
            question_ids = [wq.question_id for wq in wrong_questions]
            questions = Question.query.filter(
                Question.id.in_(question_ids),
                Question.is_deleted == False
            ).all()
            
            return questions
        
        # 否则随机抽题
        exam_type = filters.get('exam_type') if filters else None
        filter_dict = {}
        
        if filters:
            if 'question_type' in filters:
                filter_dict['question_type'] = filters['question_type']
            if 'subject' in filters:
                filter_dict['subject'] = filters['subject']
            if 'chapter' in filters:
                filter_dict['chapter'] = filters['chapter']
            if 'difficulty' in filters:
                filter_dict['difficulty'] = filters['difficulty']
        
        questions = QuestionService.random_questions(
            exam_type=exam_type,
            count=count,
            filters=filter_dict if filter_dict else None
        )
        
        return questions
    
    @staticmethod
    def submit_answer(user_id, question_id, user_answer, time_spent=0):
        """提交答案（判断正误并记录）
        
        Args:
            user_id: 用户ID
            question_id: 题目ID
            user_answer: 用户答案（可以是字符串或数组）
            time_spent: 答题时长（秒）
        
        Returns:
            dict: 判题结果
                - is_correct: 是否正确
                - correct_answer: 正确答案
                - explanation: 解析
                - question: 题目信息
        
        Raises:
            ValueError: 题目不存在
        """
        # 获取题目
        question = Question.query.get(question_id)
        if not question or question.is_deleted:
            raise ValueError('题目不存在')
        
        # 判断答案是否正确
        is_correct = PracticeService._check_answer(
            user_answer,
            question.correct_answer,
            question.question_type
        )
        
        # 将答案转换为字符串存储（如果是数组则用逗号连接）
        answer_str = user_answer
        if isinstance(user_answer, list):
            answer_str = ','.join(sorted(user_answer))
        
        # 记录练习记录
        practice_record = PracticeRecord(
            user_id=user_id,
            question_id=question_id,
            user_answer=answer_str,
            is_correct=is_correct,
            time_spent=time_spent
        )
        db.session.add(practice_record)
        
        # 如果答错，自动添加到错题本
        if not is_correct:
            PracticeService._add_to_wrong_book(user_id, question_id)
        else:
            # 如果答对且在错题本中，更新掌握状态
            PracticeService._update_wrong_question_status(user_id, question_id, True)
        
        # 更新学习统计
        PracticeService._update_statistics(user_id, is_correct, time_spent)
        
        # 自动更新学习计划进度
        try:
            from app.services.study_plan_service import StudyPlanService
            StudyPlanService.auto_update_progress_on_practice(user_id)
        except Exception as e:
            # 进度更新失败不影响练习提交
            print(f"自动更新学习计划进度失败: {str(e)}")
        
        db.session.commit()
        
        return {
            'is_correct': is_correct,
            'correct_answer': question.correct_answer,
            'explanation': question.explanation,
            'question': question.to_dict()
        }
    
    @staticmethod
    def _check_answer(user_answer, correct_answer, question_type):
        """检查答案是否正确
        
        Args:
            user_answer: 用户答案（可以是字符串或数组）
            correct_answer: 正确答案
            question_type: 题目类型
        
        Returns:
            bool: 是否正确
        """
        if not user_answer:
            return False
        
        # 处理用户答案
        if isinstance(user_answer, list):
            # 如果是数组，排序后转为大写字符串列表
            user_parts = sorted([str(p).strip().upper() for p in user_answer])
        else:
            # 如果是字符串，标准化处理
            user_ans = str(user_answer).strip().upper()
            user_parts = sorted([p.strip() for p in user_ans.replace('，', ',').split(',')])
        
        # 标准化正确答案
        correct_ans = str(correct_answer).strip().upper()
        correct_parts = sorted([p.strip() for p in correct_ans.replace('，', ',').split(',')])
        
        # 多选题需要排序后比较
        if question_type == 'multiple_choice':
            return user_parts == correct_parts
        
        # 其他题型直接比较（单选、判断等）
        # 对于单选题，user_parts 应该只有一个元素
        if len(user_parts) == 1 and len(correct_parts) == 1:
            return user_parts[0] == correct_parts[0]
        
        return user_parts == correct_parts
    
    @staticmethod
    def _add_to_wrong_book(user_id, question_id):
        """添加到错题本（内部方法）
        
        Args:
            user_id: 用户ID
            question_id: 题目ID
        """
        # 检查是否已存在
        wrong_question = WrongQuestion.query.filter_by(
            user_id=user_id,
            question_id=question_id
        ).first()
        
        if wrong_question:
            # 已存在，增加错误次数
            wrong_question.wrong_count += 1
            wrong_question.mastered = False
            wrong_question.last_wrong_at = datetime.utcnow()
        else:
            # 不存在，创建新记录
            wrong_question = WrongQuestion(
                user_id=user_id,
                question_id=question_id,
                wrong_count=1,
                mastered=False
            )
            db.session.add(wrong_question)
    
    @staticmethod
    def _update_wrong_question_status(user_id, question_id, is_correct):
        """更新错题本中题目的掌握状态
        
        Args:
            user_id: 用户ID
            question_id: 题目ID
            is_correct: 是否答对
        """
        wrong_question = WrongQuestion.query.filter_by(
            user_id=user_id,
            question_id=question_id
        ).first()
        
        if wrong_question and is_correct:
            wrong_question.mastered = True
    
    @staticmethod
    def _update_statistics(user_id, is_correct, time_spent):
        """更新学习统计
        
        Args:
            user_id: 用户ID
            is_correct: 是否正确
            time_spent: 答题时长（秒）
        """
        today = datetime.utcnow().date()
        
        # 获取或创建今日统计
        stats = StudyStatistics.query.filter_by(
            user_id=user_id,
            date=today
        ).first()
        
        if not stats:
            stats = StudyStatistics(
                user_id=user_id,
                date=today
            )
            db.session.add(stats)
        
        # 更新统计数据
        stats.add_practice(is_correct, time_spent)
    
    @staticmethod
    def get_practice_history(user_id, page=1, page_size=20, filters=None):
        """获取练习历史
        
        Args:
            user_id: 用户ID
            page: 页码
            page_size: 每页数量
            filters: 筛选条件
                - is_correct: 是否正确
                - start_date: 开始日期
                - end_date: 结束日期
        
        Returns:
            tuple: (练习记录列表, 总数)
        """
        query = PracticeRecord.query.filter_by(user_id=user_id)
        
        # 应用筛选条件
        if filters:
            if 'is_correct' in filters:
                query = query.filter_by(is_correct=filters['is_correct'])
            
            if 'start_date' in filters and filters['start_date']:
                query = query.filter(PracticeRecord.created_at >= filters['start_date'])
            
            if 'end_date' in filters and filters['end_date']:
                query = query.filter(PracticeRecord.created_at <= filters['end_date'])
        
        # 获取总数
        total = query.count()
        
        # 分页查询
        records = query.order_by(PracticeRecord.created_at.desc()) \
                      .offset((page - 1) * page_size) \
                      .limit(page_size) \
                      .all()
        
        return records, total
    
    @staticmethod
    def get_wrong_book(user_id, filters=None):
        """获取错题本
        
        Args:
            user_id: 用户ID
            filters: 筛选条件
                - mastered: 是否已掌握
                - exam_type: 考试类型
                - subject: 科目
        
        Returns:
            list: 错题列表（包含题目信息）
        """
        query = WrongQuestion.query.filter_by(user_id=user_id)
        
        # 应用筛选条件
        if filters:
            if 'mastered' in filters:
                query = query.filter_by(mastered=filters['mastered'])
        
        wrong_questions = query.order_by(WrongQuestion.last_wrong_at.desc()).all()
        
        # 获取题目详情
        result = []
        for wq in wrong_questions:
            question = Question.query.get(wq.question_id)
            if question and not question.is_deleted:
                # 如果有额外筛选条件，检查题目是否符合
                if filters:
                    if 'exam_type' in filters and question.exam_type != filters['exam_type']:
                        continue
                    if 'subject' in filters and question.subject != filters['subject']:
                        continue
                
                result.append({
                    'wrong_question': wq.to_dict(),
                    'question': question.to_dict()
                })
        
        return result
    
    @staticmethod
    def remove_from_wrong_book(user_id, wrong_question_id):
        """从错题本移除
        
        Args:
            user_id: 用户ID
            wrong_question_id: 错题记录ID
        
        Returns:
            bool: 是否成功
        
        Raises:
            ValueError: 错题记录不存在或无权限
        """
        wrong_question = WrongQuestion.query.get(wrong_question_id)
        
        if not wrong_question:
            raise ValueError('错题记录不存在')
        
        if wrong_question.user_id != user_id:
            raise ValueError('无权限操作此错题记录')
        
        db.session.delete(wrong_question)
        db.session.commit()
        
        return True
    
    @staticmethod
    def get_practice_summary(user_id, days=7):
        """获取练习概览统计
        
        Args:
            user_id: 用户ID
            days: 统计天数
        
        Returns:
            dict: 统计信息
                - total_practice: 总练习题数
                - correct_count: 正确题数
                - accuracy: 正确率
                - total_time: 总学习时长（分钟）
                - wrong_book_count: 错题本题数
                - daily_stats: 每日统计
        """
        from datetime import timedelta
        
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days-1)
        
        # 获取期间内的统计数据
        stats_list = StudyStatistics.query.filter(
            StudyStatistics.user_id == user_id,
            StudyStatistics.date >= start_date,
            StudyStatistics.date <= end_date
        ).order_by(StudyStatistics.date).all()
        
        # 汇总统计
        total_practice = sum(s.practice_count for s in stats_list)
        correct_count = sum(s.correct_count for s in stats_list)
        total_time = sum(s.study_duration for s in stats_list)
        
        accuracy = (correct_count / total_practice * 100) if total_practice > 0 else 0
        
        # 错题本统计
        wrong_book_count = WrongQuestion.query.filter_by(
            user_id=user_id,
            mastered=False
        ).count()
        
        # 每日统计
        daily_stats = [s.to_dict() for s in stats_list]
        
        return {
            'total_practice': total_practice,
            'correct_count': correct_count,
            'accuracy': round(accuracy, 2),
            'total_time': total_time,
            'wrong_book_count': wrong_book_count,
            'daily_stats': daily_stats
        }
