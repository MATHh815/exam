"""统计服务

提供学习数据统计和分析功能
"""
from datetime import date, timedelta
from sqlalchemy import func, and_

from app import db
from app.models.statistics import StudyStatistics
from app.models.practice import PracticeRecord, WrongQuestion
from app.models.exam import ExamResult
from app.models.question import Question


class StatisticsService:
    """统计服务类
    
    提供学习概览、知识点分析、学习趋势、考试统计等功能
    """
    
    @staticmethod
    def get_overview(user_id, start_date=None, end_date=None):
        """获取学习概览统计
        
        统计总题数、正确率、学习时长等数据
        
        Args:
            user_id: 用户ID
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
            
        Returns:
            dict: 学习概览数据
                - total_practice: 总练习题数
                - total_correct: 总正确题数
                - total_duration: 总学习时长（分钟）
                - total_exams: 总考试次数
                - accuracy: 正确率（百分比）
                - study_days: 学习天数
                - wrong_count: 错题数量
        """
        # 获取统计数据
        stats_list = StudyStatistics.get_user_statistics(user_id, start_date, end_date)
        
        # 聚合数据
        total_practice = sum(s.practice_count for s in stats_list)
        total_correct = sum(s.correct_count for s in stats_list)
        total_duration = sum(s.study_duration for s in stats_list)
        total_exams = sum(s.exam_count for s in stats_list)
        
        # 计算正确率
        accuracy = 0.0
        if total_practice > 0:
            accuracy = round((total_correct / total_practice) * 100, 2)
        
        # 获取错题数量
        wrong_questions = WrongQuestion.query.filter_by(
            user_id=user_id,
            mastered=False
        ).count()
        
        return {
            'total_practice': total_practice,
            'total_correct': total_correct,
            'total_duration': total_duration,
            'total_exams': total_exams,
            'accuracy': accuracy,
            'study_days': len(stats_list),
            'wrong_count': wrong_questions
        }
    
    @staticmethod
    def get_knowledge_analysis(user_id, start_date=None, end_date=None):
        """获取知识点分析
        
        按知识点（科目+章节）统计正确率，标识薄弱环节
        
        Args:
            user_id: 用户ID
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
            
        Returns:
            list: 知识点分析数据列表
                每个元素包含：
                - subject: 科目
                - chapter: 章节
                - total_count: 总题数
                - correct_count: 正确题数
                - accuracy: 正确率（百分比）
                - is_weak: 是否为薄弱点（正确率<60%）
        """
        # 构建查询
        query = db.session.query(
            Question.subject,
            Question.chapter,
            func.count(PracticeRecord.id).label('total_count'),
            func.sum(func.cast(PracticeRecord.is_correct, db.Integer)).label('correct_count')
        ).join(
            PracticeRecord,
            PracticeRecord.question_id == Question.id
        ).filter(
            PracticeRecord.user_id == user_id
        )
        
        # 应用日期过滤
        if start_date:
            query = query.filter(func.date(PracticeRecord.created_at) >= start_date)
        if end_date:
            query = query.filter(func.date(PracticeRecord.created_at) <= end_date)
        
        # 按科目和章节分组
        query = query.group_by(Question.subject, Question.chapter)
        
        # 执行查询
        results = query.all()
        
        # 处理结果
        analysis = []
        for subject, chapter, total_count, correct_count in results:
            # 处理NULL值
            correct_count = correct_count or 0
            
            # 计算正确率
            accuracy = 0.0
            if total_count > 0:
                accuracy = round((correct_count / total_count) * 100, 2)
            
            # 判断是否为薄弱点
            is_weak = accuracy < 60.0
            
            analysis.append({
                'subject': subject,
                'chapter': chapter,
                'total_count': total_count,
                'correct_count': correct_count,
                'accuracy': accuracy,
                'is_weak': is_weak
            })
        
        # 按正确率排序（薄弱点优先）
        analysis.sort(key=lambda x: x['accuracy'])
        
        return analysis
    
    @staticmethod
    def get_trend(user_id, days=7):
        """获取学习趋势
        
        返回指定天数内的学习数据时间序列
        
        Args:
            user_id: 用户ID
            days: 天数（默认7天）
            
        Returns:
            list: 趋势数据列表
                每个元素包含：
                - date: 日期
                - practice_count: 练习题数
                - correct_count: 正确题数
                - accuracy: 正确率（百分比）
                - study_duration: 学习时长（分钟）
                - exam_count: 考试次数
                
        Raises:
            ValueError: 天数参数无效
        """
        if days <= 0:
            raise ValueError('天数必须大于0')
        
        # 使用StudyStatistics模型的get_trend方法
        return StudyStatistics.get_trend(user_id, days)
    
    @staticmethod
    def get_exam_statistics(user_id, start_date=None, end_date=None):
        """获取考试历史统计
        
        Args:
            user_id: 用户ID
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
            
        Returns:
            dict: 考试统计数据
                - total_exams: 总考试次数
                - average_score: 平均分
                - average_accuracy: 平均正确率
                - highest_score: 最高分
                - lowest_score: 最低分
                - recent_exams: 最近考试列表（最多10条）
        """
        # 构建查询
        query = ExamResult.query.filter_by(user_id=user_id)
        
        # 应用日期过滤
        if start_date:
            query = query.filter(func.date(ExamResult.created_at) >= start_date)
        if end_date:
            query = query.filter(func.date(ExamResult.created_at) <= end_date)
        
        # 获取所有考试结果
        results = query.order_by(ExamResult.created_at.desc()).all()
        
        # 计算统计数据
        total_exams = len(results)
        
        if total_exams == 0:
            return {
                'total_exams': 0,
                'average_score': 0.0,
                'average_accuracy': 0.0,
                'highest_score': 0.0,
                'lowest_score': 0.0,
                'recent_exams': []
            }
        
        # 计算平均分和正确率
        total_score = sum(r.score for r in results)
        total_accuracy = sum(r.accuracy for r in results)
        average_score = round(total_score / total_exams, 2)
        average_accuracy = round(total_accuracy / total_exams, 2)
        
        # 获取最高分和最低分
        highest_score = max(r.score for r in results)
        lowest_score = min(r.score for r in results)
        
        # 获取最近10次考试
        recent_exams = [r.to_dict() for r in results[:10]]
        
        return {
            'total_exams': total_exams,
            'average_score': average_score,
            'average_accuracy': average_accuracy,
            'highest_score': highest_score,
            'lowest_score': lowest_score,
            'recent_exams': recent_exams
        }
    
    @staticmethod
    def get_subject_statistics(user_id, start_date=None, end_date=None):
        """获取科目统计
        
        按科目统计练习情况
        
        Args:
            user_id: 用户ID
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
            
        Returns:
            list: 科目统计数据列表
                每个元素包含：
                - subject: 科目
                - total_count: 总题数
                - correct_count: 正确题数
                - wrong_count: 错误题数
                - accuracy: 正确率（百分比）
        """
        # 构建查询
        query = db.session.query(
            Question.subject,
            func.count(PracticeRecord.id).label('total_count'),
            func.sum(func.cast(PracticeRecord.is_correct, db.Integer)).label('correct_count')
        ).join(
            PracticeRecord,
            PracticeRecord.question_id == Question.id
        ).filter(
            PracticeRecord.user_id == user_id
        )
        
        # 应用日期过滤
        if start_date:
            query = query.filter(func.date(PracticeRecord.created_at) >= start_date)
        if end_date:
            query = query.filter(func.date(PracticeRecord.created_at) <= end_date)
        
        # 按科目分组
        query = query.group_by(Question.subject)
        
        # 执行查询
        results = query.all()
        
        # 处理结果
        statistics = []
        for subject, total_count, correct_count in results:
            # 处理NULL值
            correct_count = correct_count or 0
            wrong_count = total_count - correct_count
            
            # 计算正确率
            accuracy = 0.0
            if total_count > 0:
                accuracy = round((correct_count / total_count) * 100, 2)
            
            statistics.append({
                'subject': subject,
                'total_count': total_count,
                'correct_count': correct_count,
                'wrong_count': wrong_count,
                'accuracy': accuracy
            })
        
        # 按总题数排序
        statistics.sort(key=lambda x: x['total_count'], reverse=True)
        
        return statistics
    
    @staticmethod
    def get_difficulty_statistics(user_id, start_date=None, end_date=None):
        """获取难度统计
        
        按难度级别统计练习情况
        
        Args:
            user_id: 用户ID
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
            
        Returns:
            list: 难度统计数据列表
                每个元素包含：
                - difficulty: 难度级别（1-5）
                - difficulty_label: 难度标签
                - total_count: 总题数
                - correct_count: 正确题数
                - wrong_count: 错误题数
                - accuracy: 正确率（百分比）
        """
        # 难度标签映射
        difficulty_labels = {
            1: '非常简单',
            2: '简单',
            3: '中等',
            4: '困难',
            5: '非常困难'
        }
        
        # 构建查询
        query = db.session.query(
            Question.difficulty,
            func.count(PracticeRecord.id).label('total_count'),
            func.sum(func.cast(PracticeRecord.is_correct, db.Integer)).label('correct_count')
        ).join(
            PracticeRecord,
            PracticeRecord.question_id == Question.id
        ).filter(
            PracticeRecord.user_id == user_id
        )
        
        # 应用日期过滤
        if start_date:
            query = query.filter(func.date(PracticeRecord.created_at) >= start_date)
        if end_date:
            query = query.filter(func.date(PracticeRecord.created_at) <= end_date)
        
        # 按难度分组
        query = query.group_by(Question.difficulty)
        
        # 执行查询
        results = query.all()
        
        # 处理结果
        statistics = []
        for difficulty, total_count, correct_count in results:
            # 处理NULL值
            correct_count = correct_count or 0
            wrong_count = total_count - correct_count
            
            # 计算正确率
            accuracy = 0.0
            if total_count > 0:
                accuracy = round((correct_count / total_count) * 100, 2)
            
            statistics.append({
                'difficulty': difficulty,
                'difficulty_label': difficulty_labels.get(difficulty, '未知'),
                'total_count': total_count,
                'correct_count': correct_count,
                'wrong_count': wrong_count,
                'accuracy': accuracy
            })
        
        # 按难度排序
        statistics.sort(key=lambda x: x['difficulty'])
        
        return statistics
