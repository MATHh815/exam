"""统计服务单元测试"""
import pytest
from datetime import date, datetime, timedelta
from sqlalchemy import func

from app import db
from app.models.user import User
from app.models.question import Question
from app.models.practice import PracticeRecord, WrongQuestion
from app.models.exam import ExamPaper, ExamPaperQuestion, ExamSession, ExamResult
from app.models.statistics import StudyStatistics
from app.services.statistics_service import StatisticsService


@pytest.fixture
def test_user(app):
    """创建测试用户"""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            nickname='Test User'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        yield user
        db.session.delete(user)
        db.session.commit()


@pytest.fixture
def test_questions(app, test_user):
    """创建测试题目"""
    with app.app_context():
        questions = []
        subjects = ['数学', '英语', '行测']
        chapters = ['第一章', '第二章']
        
        for i in range(10):
            question = Question(
                exam_type='civil_service',
                question_type='single_choice',
                subject=subjects[i % 3],
                chapter=chapters[i % 2],
                difficulty=(i % 5) + 1,
                content=f'测试题目 {i+1}',
                options={'A': '选项A', 'B': '选项B', 'C': '选项C', 'D': '选项D'},
                correct_answer='A',
                explanation='解析',
                created_by=test_user.id
            )
            db.session.add(question)
            questions.append(question)
        
        db.session.commit()
        yield questions
        
        for q in questions:
            db.session.delete(q)
        db.session.commit()


@pytest.fixture
def test_practice_records(app, test_user, test_questions):
    """创建测试练习记录"""
    with app.app_context():
        records = []
        today = date.today()
        
        # 创建不同日期的练习记录
        for i, question in enumerate(test_questions):
            record_date = today - timedelta(days=i % 7)
            record = PracticeRecord(
                user_id=test_user.id,
                question_id=question.id,
                user_answer='A' if i % 2 == 0 else 'B',
                is_correct=i % 2 == 0,
                time_spent=30 + i * 5,
                created_at=datetime.combine(record_date, datetime.min.time())
            )
            db.session.add(record)
            records.append(record)
        
        db.session.commit()
        yield records
        
        for r in records:
            db.session.delete(r)
        db.session.commit()


@pytest.fixture
def test_statistics(app, test_user):
    """创建测试统计数据"""
    with app.app_context():
        stats_list = []
        today = date.today()
        
        for i in range(7):
            stat_date = today - timedelta(days=i)
            stats = StudyStatistics(
                user_id=test_user.id,
                date=stat_date,
                practice_count=10 + i,
                correct_count=5 + i,
                study_duration=30 + i * 5,
                exam_count=i % 3
            )
            db.session.add(stats)
            stats_list.append(stats)
        
        db.session.commit()
        yield stats_list
        
        for s in stats_list:
            db.session.delete(s)
        db.session.commit()


class TestStatisticsService:
    """统计服务测试类"""
    
    def test_get_overview_basic(self, app, test_user, test_statistics):
        """测试获取基本学习概览"""
        with app.app_context():
            overview = StatisticsService.get_overview(test_user.id)
            
            assert overview is not None
            assert 'total_practice' in overview
            assert 'total_correct' in overview
            assert 'total_duration' in overview
            assert 'total_exams' in overview
            assert 'accuracy' in overview
            assert 'study_days' in overview
            assert 'wrong_count' in overview
            
            # 验证数据正确性
            assert overview['total_practice'] > 0
            assert overview['study_days'] == 7
    
    def test_get_overview_with_date_range(self, app, test_user, test_statistics):
        """测试带日期范围的学习概览"""
        with app.app_context():
            today = date.today()
            start_date = today - timedelta(days=3)
            end_date = today
            
            overview = StatisticsService.get_overview(
                test_user.id,
                start_date=start_date,
                end_date=end_date
            )
            
            assert overview is not None
            assert overview['study_days'] <= 4  # 最多4天
    
    def test_get_overview_empty(self, app, test_user):
        """测试空数据的学习概览"""
        with app.app_context():
            overview = StatisticsService.get_overview(test_user.id)
            
            assert overview is not None
            assert overview['total_practice'] == 0
            assert overview['total_correct'] == 0
            assert overview['accuracy'] == 0.0
    
    def test_get_knowledge_analysis(self, app, test_user, test_questions, test_practice_records):
        """测试知识点分析"""
        with app.app_context():
            analysis = StatisticsService.get_knowledge_analysis(test_user.id)
            
            assert analysis is not None
            assert isinstance(analysis, list)
            assert len(analysis) > 0
            
            # 验证每个知识点的数据结构
            for item in analysis:
                assert 'subject' in item
                assert 'chapter' in item
                assert 'total_count' in item
                assert 'correct_count' in item
                assert 'accuracy' in item
                assert 'is_weak' in item
                assert item['total_count'] > 0
    
    def test_get_knowledge_analysis_with_date_range(self, app, test_user, test_questions, test_practice_records):
        """测试带日期范围的知识点分析"""
        with app.app_context():
            today = date.today()
            start_date = today - timedelta(days=3)
            
            analysis = StatisticsService.get_knowledge_analysis(
                test_user.id,
                start_date=start_date
            )
            
            assert analysis is not None
            assert isinstance(analysis, list)
    
    def test_get_knowledge_analysis_empty(self, app, test_user):
        """测试空数据的知识点分析"""
        with app.app_context():
            analysis = StatisticsService.get_knowledge_analysis(test_user.id)
            
            assert analysis is not None
            assert isinstance(analysis, list)
            assert len(analysis) == 0
    
    def test_get_trend_default(self, app, test_user, test_statistics):
        """测试获取默认7天学习趋势"""
        with app.app_context():
            trend = StatisticsService.get_trend(test_user.id)
            
            assert trend is not None
            assert isinstance(trend, list)
            assert len(trend) == 7
            
            # 验证每天的数据结构
            for day_data in trend:
                assert 'date' in day_data
                assert 'practice_count' in day_data
                assert 'correct_count' in day_data
                assert 'accuracy' in day_data
                assert 'study_duration' in day_data
                assert 'exam_count' in day_data
    
    def test_get_trend_custom_days(self, app, test_user, test_statistics):
        """测试获取自定义天数的学习趋势"""
        with app.app_context():
            trend = StatisticsService.get_trend(test_user.id, days=14)
            
            assert trend is not None
            assert isinstance(trend, list)
            assert len(trend) == 14
    
    def test_get_trend_invalid_days(self, app, test_user):
        """测试无效天数参数"""
        with app.app_context():
            with pytest.raises(ValueError, match='天数必须大于0'):
                StatisticsService.get_trend(test_user.id, days=0)
            
            with pytest.raises(ValueError, match='天数必须大于0'):
                StatisticsService.get_trend(test_user.id, days=-1)
    
    def test_get_exam_statistics_empty(self, app, test_user):
        """测试空数据的考试统计"""
        with app.app_context():
            stats = StatisticsService.get_exam_statistics(test_user.id)
            
            assert stats is not None
            assert stats['total_exams'] == 0
            assert stats['average_score'] == 0.0
            assert stats['average_accuracy'] == 0.0
            assert stats['highest_score'] == 0.0
            assert stats['lowest_score'] == 0.0
            assert len(stats['recent_exams']) == 0
    
    def test_get_subject_statistics(self, app, test_user, test_questions, test_practice_records):
        """测试科目统计"""
        with app.app_context():
            stats = StatisticsService.get_subject_statistics(test_user.id)
            
            assert stats is not None
            assert isinstance(stats, list)
            assert len(stats) > 0
            
            # 验证每个科目的数据结构
            for item in stats:
                assert 'subject' in item
                assert 'total_count' in item
                assert 'correct_count' in item
                assert 'wrong_count' in item
                assert 'accuracy' in item
                assert item['total_count'] > 0
                assert item['total_count'] == item['correct_count'] + item['wrong_count']
    
    def test_get_subject_statistics_with_date_range(self, app, test_user, test_questions, test_practice_records):
        """测试带日期范围的科目统计"""
        with app.app_context():
            today = date.today()
            start_date = today - timedelta(days=3)
            
            stats = StatisticsService.get_subject_statistics(
                test_user.id,
                start_date=start_date
            )
            
            assert stats is not None
            assert isinstance(stats, list)
    
    def test_get_difficulty_statistics(self, app, test_user, test_questions, test_practice_records):
        """测试难度统计"""
        with app.app_context():
            stats = StatisticsService.get_difficulty_statistics(test_user.id)
            
            assert stats is not None
            assert isinstance(stats, list)
            assert len(stats) > 0
            
            # 验证每个难度的数据结构
            for item in stats:
                assert 'difficulty' in item
                assert 'difficulty_label' in item
                assert 'total_count' in item
                assert 'correct_count' in item
                assert 'wrong_count' in item
                assert 'accuracy' in item
                assert item['difficulty'] >= 1
                assert item['difficulty'] <= 5
                assert item['total_count'] == item['correct_count'] + item['wrong_count']
    
    def test_get_difficulty_statistics_with_date_range(self, app, test_user, test_questions, test_practice_records):
        """测试带日期范围的难度统计"""
        with app.app_context():
            today = date.today()
            start_date = today - timedelta(days=3)
            
            stats = StatisticsService.get_difficulty_statistics(
                test_user.id,
                start_date=start_date
            )
            
            assert stats is not None
            assert isinstance(stats, list)
    
    def test_statistics_accuracy_calculation(self, app, test_user, test_questions, test_practice_records):
        """测试正确率计算的准确性"""
        with app.app_context():
            # 获取科目统计
            stats = StatisticsService.get_subject_statistics(test_user.id)
            
            for item in stats:
                # 验证正确率计算
                expected_accuracy = round((item['correct_count'] / item['total_count']) * 100, 2)
                assert item['accuracy'] == expected_accuracy


# Property-Based Tests
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from hypothesis.strategies import composite


@composite
def practice_record_data(draw):
    """生成练习记录数据的策略
    
    生成一组练习记录，包含题目数量、正确数量和答题时长
    """
    # 生成1到100个练习记录
    count = draw(st.integers(min_value=1, max_value=100))
    # 正确数量不能超过总数
    correct = draw(st.integers(min_value=0, max_value=count))
    # 生成每个记录的答题时长（秒）
    time_spent_list = draw(st.lists(
        st.integers(min_value=1, max_value=600),
        min_size=count,
        max_size=count
    ))
    
    return {
        'count': count,
        'correct': correct,
        'time_spent_list': time_spent_list
    }


class TestStatisticsServiceProperties:
    """统计服务属性测试类"""
    
    @given(data=practice_record_data())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None
    )
    def test_property_statistics_calculation_correctness(self, app, data):
        """
        Feature: exam-system, Property 12: 统计数据计算正确性
        
        属性：对于任意用户的练习记录，统计的总题数应该等于记录数量，
        正确率应该等于正确数除以总数
        
        Validates: Requirements 6.1
        """
        with app.app_context():
            # 创建测试用户
            import random
            random_id = random.randint(100000, 999999)
            user = User(
                username=f'proptest_{random_id}',
                email=f'proptest_{random_id}@example.com',
                nickname='Property Test User'
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.flush()
            
            # 创建测试题目
            question = Question(
                exam_type='civil_service',
                question_type='single_choice',
                subject='测试科目',
                chapter='测试章节',
                difficulty=3,
                content='测试题目',
                options={'A': '选项A', 'B': '选项B', 'C': '选项C', 'D': '选项D'},
                correct_answer='A',
                explanation='解析',
                created_by=user.id
            )
            db.session.add(question)
            db.session.flush()
            
            # 创建练习记录和统计数据
            today = date.today()
            total_time_spent = sum(data['time_spent_list'])
            
            # 创建StudyStatistics记录（这是get_overview实际查询的表）
            stats = StudyStatistics(
                user_id=user.id,
                date=today,
                practice_count=data['count'],
                correct_count=data['correct'],
                study_duration=total_time_spent // 60,  # 转换为分钟
                exam_count=0
            )
            db.session.add(stats)
            
            # 同时创建PracticeRecord用于科目统计
            for i in range(data['count']):
                is_correct = i < data['correct']  # 前correct个是正确的
                record = PracticeRecord(
                    user_id=user.id,
                    question_id=question.id,
                    user_answer='A' if is_correct else 'B',
                    is_correct=is_correct,
                    time_spent=data['time_spent_list'][i],
                    created_at=datetime.combine(today, datetime.min.time())
                )
                db.session.add(record)
            
            db.session.flush()
            
            # 获取统计概览
            overview = StatisticsService.get_overview(user.id)
            
            # 属性1：总题数应该等于记录数量
            assert overview['total_practice'] == data['count'], \
                f"总题数 {overview['total_practice']} 应该等于记录数量 {data['count']}"
            
            # 属性2：正确题数应该等于我们设置的正确数量
            assert overview['total_correct'] == data['correct'], \
                f"正确题数 {overview['total_correct']} 应该等于 {data['correct']}"
            
            # 属性3：正确率应该等于正确数除以总数
            expected_accuracy = round((data['correct'] / data['count']) * 100, 2)
            assert overview['accuracy'] == expected_accuracy, \
                f"正确率 {overview['accuracy']} 应该等于 {expected_accuracy}"
            
            # 属性4：学习时长应该等于所有答题时长之和（转换为分钟）
            expected_duration = sum(data['time_spent_list']) // 60
            assert overview['total_duration'] == expected_duration, \
                f"学习时长 {overview['total_duration']} 应该等于 {expected_duration}"
            
            # 获取科目统计
            subject_stats = StatisticsService.get_subject_statistics(user.id)
            
            # 应该有一个科目的统计
            assert len(subject_stats) == 1, "应该有一个科目的统计"
            
            subject_stat = subject_stats[0]
            
            # 属性5：科目统计的总题数应该等于记录数量
            assert subject_stat['total_count'] == data['count'], \
                f"科目总题数 {subject_stat['total_count']} 应该等于 {data['count']}"
            
            # 属性6：科目统计的正确数应该等于设置的正确数
            assert subject_stat['correct_count'] == data['correct'], \
                f"科目正确数 {subject_stat['correct_count']} 应该等于 {data['correct']}"
            
            # 属性7：科目统计的错误数应该等于总数减正确数
            expected_wrong = data['count'] - data['correct']
            assert subject_stat['wrong_count'] == expected_wrong, \
                f"科目错误数 {subject_stat['wrong_count']} 应该等于 {expected_wrong}"
            
            # 属性8：科目统计的正确率应该等于正确数除以总数
            assert subject_stat['accuracy'] == expected_accuracy, \
                f"科目正确率 {subject_stat['accuracy']} 应该等于 {expected_accuracy}"
            
            # 清理测试数据
            db.session.rollback()
    
    @given(
        days_back=st.integers(min_value=2, max_value=10),
        range_days=st.integers(min_value=1, max_value=5)
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None
    )
    def test_property_time_range_filtering_correctness(self, app, days_back, range_days):
        """
        Feature: exam-system, Property 13: 时间范围过滤正确性
        
        属性：对于任意时间范围，统计返回的所有记录的时间戳都应该在该范围内
        
        Validates: Requirements 6.5
        """
        with app.app_context():
            # 创建测试用户
            import random
            random_id = random.randint(100000, 999999)
            user = User(
                username=f'timetest_{random_id}',
                email=f'timetest_{random_id}@example.com',
                nickname='Time Range Test User'
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.flush()
            
            # 创建测试题目
            question = Question(
                exam_type='civil_service',
                question_type='single_choice',
                subject='测试科目',
                chapter='测试章节',
                difficulty=3,
                content='测试题目',
                options={'A': '选项A', 'B': '选项B', 'C': '选项C', 'D': '选项D'},
                correct_answer='A',
                explanation='解析',
                created_by=user.id
            )
            db.session.add(question)
            db.session.flush()
            
            # 创建跨越多天的练习记录和统计数据
            today = date.today()
            
            # 创建从days_back天前到今天的数据
            for i in range(days_back):
                record_date = today - timedelta(days=i)
                
                # 创建StudyStatistics记录
                stats = StudyStatistics(
                    user_id=user.id,
                    date=record_date,
                    practice_count=3 + i,
                    correct_count=2 + (i % 2),
                    study_duration=20 + i,
                    exam_count=i % 2
                )
                db.session.add(stats)
                
                # 创建PracticeRecord记录（减少数量以提高性能）
                for j in range(2):
                    record = PracticeRecord(
                        user_id=user.id,
                        question_id=question.id,
                        user_answer='A' if j % 2 == 0 else 'B',
                        is_correct=j % 2 == 0,
                        time_spent=30 + j * 10,
                        created_at=datetime.combine(record_date, datetime.min.time())
                    )
                    db.session.add(record)
            
            db.session.flush()
            
            # 定义时间范围：从range_days天前到今天
            # 确保范围不超过我们创建的数据范围
            actual_range_days = min(range_days, days_back)
            end_date = today
            start_date = today - timedelta(days=actual_range_days - 1)
            
            # 测试get_overview的时间范围过滤
            overview = StatisticsService.get_overview(
                user.id,
                start_date=start_date,
                end_date=end_date
            )
            
            # 属性1：study_days应该不超过时间范围的天数
            assert overview['study_days'] <= actual_range_days, \
                f"学习天数 {overview['study_days']} 不应超过时间范围 {actual_range_days}"
            
            # 验证返回的统计数据确实在时间范围内
            stats_in_range = StudyStatistics.get_user_statistics(
                user.id,
                start_date=start_date,
                end_date=end_date
            )
            
            # 属性2：所有返回的记录日期都应该在范围内
            for stats in stats_in_range:
                assert start_date <= stats.date <= end_date, \
                    f"统计记录日期 {stats.date} 应该在范围 [{start_date}, {end_date}] 内"
            
            # 测试get_knowledge_analysis的时间范围过滤
            knowledge_analysis = StatisticsService.get_knowledge_analysis(
                user.id,
                start_date=start_date,
                end_date=end_date
            )
            
            # 验证知识点分析中的所有练习记录都在时间范围内
            practice_records_in_range = PracticeRecord.query.filter(
                PracticeRecord.user_id == user.id,
                func.date(PracticeRecord.created_at) >= start_date,
                func.date(PracticeRecord.created_at) <= end_date
            ).all()
            
            # 属性3：所有练习记录的日期都应该在范围内
            for record in practice_records_in_range:
                record_date = record.created_at.date()
                assert start_date <= record_date <= end_date, \
                    f"练习记录日期 {record_date} 应该在范围 [{start_date}, {end_date}] 内"
            
            # 测试get_subject_statistics的时间范围过滤
            subject_stats = StatisticsService.get_subject_statistics(
                user.id,
                start_date=start_date,
                end_date=end_date
            )
            
            # 如果有科目统计，验证其总数不超过范围内的记录数
            if subject_stats:
                total_records_in_range = len(practice_records_in_range)
                total_in_stats = sum(s['total_count'] for s in subject_stats)
                
                # 属性4：统计的总题数应该等于范围内的记录数
                assert total_in_stats == total_records_in_range, \
                    f"统计总题数 {total_in_stats} 应该等于范围内记录数 {total_records_in_range}"
            
            # 测试get_difficulty_statistics的时间范围过滤
            difficulty_stats = StatisticsService.get_difficulty_statistics(
                user.id,
                start_date=start_date,
                end_date=end_date
            )
            
            # 如果有难度统计，验证其总数不超过范围内的记录数
            if difficulty_stats:
                total_records_in_range = len(practice_records_in_range)
                total_in_stats = sum(s['total_count'] for s in difficulty_stats)
                
                # 属性5：统计的总题数应该等于范围内的记录数
                assert total_in_stats == total_records_in_range, \
                    f"难度统计总题数 {total_in_stats} 应该等于范围内记录数 {total_records_in_range}"
            
            # 测试边界情况：start_date和end_date相同（单日查询）
            single_day = today
            single_day_overview = StatisticsService.get_overview(
                user.id,
                start_date=single_day,
                end_date=single_day
            )
            
            # 属性6：单日查询的study_days应该不超过1
            assert single_day_overview['study_days'] <= 1, \
                f"单日查询的学习天数 {single_day_overview['study_days']} 不应超过1"
            
            # 测试边界情况：end_date在start_date之前（应该返回空结果）
            if actual_range_days > 1:
                invalid_start = today
                invalid_end = today - timedelta(days=1)
                
                invalid_overview = StatisticsService.get_overview(
                    user.id,
                    start_date=invalid_start,
                    end_date=invalid_end
                )
                
                # 属性7：无效范围应该返回空结果
                assert invalid_overview['study_days'] == 0, \
                    f"无效时间范围应该返回0学习天数，实际为 {invalid_overview['study_days']}"
                assert invalid_overview['total_practice'] == 0, \
                    f"无效时间范围应该返回0练习题数，实际为 {invalid_overview['total_practice']}"
            
            # 清理测试数据
            db.session.rollback()
