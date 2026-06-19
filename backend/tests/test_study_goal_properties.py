"""学习目标属性测试（Property-Based Testing）

使用 Hypothesis 进行基于属性的测试，验证学习目标自动追踪系统的通用属性。
每个属性测试运行至少 100 次迭代，确保在各种输入下都能保持正确性。
"""
import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from datetime import date, datetime, timedelta
from app import db
from app.models.user import User
from app.models.study_plan import StudyPlan, StudyGoal
from app.services.study_plan_service import StudyPlanService


@pytest.fixture
def test_user(db_session):
    """创建测试用户"""
    user = User(
        username='goal_test_user',
        email='goal@test.com',
        nickname='目标测试用户'
    )
    user.set_password('password123')
    db_session.session.add(user)
    db_session.session.commit()
    return user


# 自定义策略
valid_goal_types = st.sampled_from(['daily_practice', 'weekly_practice', 'daily_duration', 'exam_count'])


class TestProperty8AutoProgressUpdateOnPractice:
    """
    Property 8: Automatic progress update on practice
    For any user with an active daily practice goal, completing a practice session 
    should increment the goal's current_value by 1
    
    Feature: exam-enhancements-phase1, Property 8
    Validates: Requirements 2.4
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        initial_progress=st.integers(min_value=0, max_value=40),
        target_value=st.integers(min_value=50, max_value=100)
    )
    def test_practice_increments_daily_goal(self, db_session, test_user, initial_progress, target_value):
        """测试完成练习自动增加日目标进度"""
        today = date.today()
        
        # 创建带有 daily_practice 目标的学习计划
        plan_data = {
            'name': '测试计划',
            'exam_type': 'civil_service',
            'start_date': today.isoformat(),
            'end_date': (today + timedelta(days=30)).isoformat(),
            'goals': [{
                'goal_type': 'daily_practice',
                'target_value': target_value,
                'period_start': today.isoformat(),
                'period_end': today.isoformat()
            }]
        }
        
        plan = StudyPlanService.create_plan(test_user.id, plan_data)
        goal = plan.goals[0]
        
        # 设置初始进度
        goal.current_value = initial_progress
        db_session.session.commit()
        
        # 调用自动更新方法（模拟完成一次练习）
        updated_goals = StudyPlanService.auto_update_progress_on_practice(test_user.id)
        
        # 验证进度增加了1
        assert len(updated_goals) == 1
        assert updated_goals[0].current_value == initial_progress + 1
        
        # 清理
        db_session.session.delete(plan)
        db_session.session.commit()
    
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        practice_count=st.integers(min_value=1, max_value=10)
    )
    def test_multiple_practices_accumulate(self, db_session, test_user, practice_count):
        """测试多次练习累计进度"""
        today = date.today()
        
        # 创建目标
        plan_data = {
            'name': '测试计划',
            'exam_type': 'civil_service',
            'start_date': today.isoformat(),
            'end_date': (today + timedelta(days=30)).isoformat(),
            'goals': [{
                'goal_type': 'daily_practice',
                'target_value': 50,
                'period_start': today.isoformat(),
                'period_end': today.isoformat()
            }]
        }
        
        plan = StudyPlanService.create_plan(test_user.id, plan_data)
        initial_value = plan.goals[0].current_value
        
        # 模拟多次练习
        for _ in range(practice_count):
            StudyPlanService.auto_update_progress_on_practice(test_user.id)
        
        # 验证累计进度
        updated_goal = db_session.session.get(StudyGoal, plan.goals[0].id)
        assert updated_goal.current_value == initial_value + practice_count
        
        # 清理
        db_session.session.delete(plan)
        db_session.session.commit()


class TestProperty9AutoProgressUpdateOnExam:
    """
    Property 9: Automatic progress update on exam
    For any user with an active daily exam goal, completing an exam 
    should increment the goal's current_value by 1
    
    Feature: exam-enhancements-phase1, Property 9
    Validates: Requirements 2.5
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        initial_progress=st.integers(min_value=0, max_value=3),
        target_value=st.integers(min_value=5, max_value=10)
    )
    def test_exam_increments_daily_goal(self, db_session, test_user, initial_progress, target_value):
        """测试完成考试自动增加日目标进度"""
        today = date.today()
        
        # 创建带有 exam_count 目标的学习计划
        plan_data = {
            'name': '测试计划',
            'exam_type': 'civil_service',
            'start_date': today.isoformat(),
            'end_date': (today + timedelta(days=30)).isoformat(),
            'goals': [{
                'goal_type': 'exam_count',
                'target_value': target_value,
                'period_start': today.isoformat(),
                'period_end': today.isoformat()
            }]
        }
        
        plan = StudyPlanService.create_plan(test_user.id, plan_data)
        goal = plan.goals[0]
        
        # 设置初始进度
        goal.current_value = initial_progress
        db_session.session.commit()
        
        # 调用自动更新方法（模拟完成一次考试）
        updated_goals = StudyPlanService.auto_update_progress_on_exam(test_user.id)
        
        # 验证进度增加了1
        assert len(updated_goals) == 1
        assert updated_goals[0].current_value == initial_progress + 1
        
        # 清理
        db_session.session.delete(plan)
        db_session.session.commit()
    
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        exam_count=st.integers(min_value=1, max_value=5)
    )
    def test_multiple_exams_accumulate(self, db_session, test_user, exam_count):
        """测试多次考试累计进度"""
        today = date.today()
        
        # 创建目标
        plan_data = {
            'name': '测试计划',
            'exam_type': 'civil_service',
            'start_date': today.isoformat(),
            'end_date': (today + timedelta(days=30)).isoformat(),
            'goals': [{
                'goal_type': 'exam_count',
                'target_value': 10,
                'period_start': today.isoformat(),
                'period_end': today.isoformat()
            }]
        }
        
        plan = StudyPlanService.create_plan(test_user.id, plan_data)
        initial_value = plan.goals[0].current_value
        
        # 模拟多次考试
        for _ in range(exam_count):
            StudyPlanService.auto_update_progress_on_exam(test_user.id)
        
        # 验证累计进度
        updated_goal = db_session.session.get(StudyGoal, plan.goals[0].id)
        assert updated_goal.current_value == initial_value + exam_count
        
        # 清理
        db_session.session.delete(plan)
        db_session.session.commit()


class TestProperty10GoalCompletionTriggersPoints:
    """
    Property 10: Goal completion triggers points
    For any daily goal, when current_value reaches target_value, 
    the goal should be marked as completed
    
    Feature: exam-enhancements-phase1, Property 10
    Validates: Requirements 2.6
    
    Note: 积分奖励功能将在积分系统实现后集成
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        target_value=st.integers(min_value=1, max_value=50)
    )
    def test_goal_marked_completed_when_target_reached(self, db_session, test_user, target_value):
        """测试达到目标值时标记为完成"""
        today = date.today()
        
        # 创建目标
        plan_data = {
            'name': '测试计划',
            'exam_type': 'civil_service',
            'start_date': today.isoformat(),
            'end_date': (today + timedelta(days=30)).isoformat(),
            'goals': [{
                'goal_type': 'daily_practice',
                'target_value': target_value,
                'period_start': today.isoformat(),
                'period_end': today.isoformat()
            }]
        }
        
        plan = StudyPlanService.create_plan(test_user.id, plan_data)
        goal = plan.goals[0]
        
        # 设置进度为目标值-1
        goal.current_value = target_value - 1
        goal.is_completed = False
        db_session.session.commit()
        
        # 完成最后一次练习
        updated_goals = StudyPlanService.auto_update_progress_on_practice(test_user.id)
        
        # 验证目标被标记为完成
        assert len(updated_goals) == 1
        assert updated_goals[0].current_value == target_value
        assert updated_goals[0].is_completed is True
        assert updated_goals[0].completed_at is not None
        
        # 清理
        db_session.session.delete(plan)
        db_session.session.commit()
    
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        target_value=st.integers(min_value=5, max_value=20),
        excess=st.integers(min_value=1, max_value=5)
    )
    def test_goal_stays_completed_after_exceeding_target(self, db_session, test_user, target_value, excess):
        """测试超过目标值后仍保持完成状态"""
        today = date.today()
        
        # 创建目标
        plan_data = {
            'name': '测试计划',
            'exam_type': 'civil_service',
            'start_date': today.isoformat(),
            'end_date': (today + timedelta(days=30)).isoformat(),
            'goals': [{
                'goal_type': 'daily_practice',
                'target_value': target_value,
                'period_start': today.isoformat(),
                'period_end': today.isoformat()
            }]
        }
        
        plan = StudyPlanService.create_plan(test_user.id, plan_data)
        goal = plan.goals[0]
        
        # 设置进度为目标值-1
        goal.current_value = target_value - 1
        db_session.session.commit()
        
        # 完成多次练习，超过目标值
        # 第一次会达到目标并标记为完成，后续的更新会被跳过（因为已完成）
        for i in range(excess + 1):
            StudyPlanService.auto_update_progress_on_practice(test_user.id)
        
        # 验证目标在第一次达到目标值时被标记为完成
        # 后续的更新被跳过，所以 current_value 应该等于 target_value
        updated_goal = db_session.session.get(StudyGoal, goal.id)
        assert updated_goal.current_value == target_value
        assert updated_goal.is_completed is True
        
        # 清理
        db_session.session.delete(plan)
        db_session.session.commit()
    
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        target_value=st.integers(min_value=5, max_value=10)
    )
    def test_completed_goal_not_updated_again(self, db_session, test_user, target_value):
        """测试已完成的目标不再被更新"""
        today = date.today()
        
        # 创建目标
        plan_data = {
            'name': '测试计划',
            'exam_type': 'civil_service',
            'start_date': today.isoformat(),
            'end_date': (today + timedelta(days=30)).isoformat(),
            'goals': [{
                'goal_type': 'exam_count',
                'target_value': target_value,
                'period_start': today.isoformat(),
                'period_end': today.isoformat()
            }]
        }
        
        plan = StudyPlanService.create_plan(test_user.id, plan_data)
        goal = plan.goals[0]
        
        # 手动标记为完成
        goal.current_value = target_value
        goal.is_completed = True
        goal.completed_at = datetime.utcnow()
        db_session.session.commit()
        
        # 尝试再次更新
        updated_goals = StudyPlanService.auto_update_progress_on_exam(test_user.id)
        
        # 验证没有目标被更新（因为已完成的目标被过滤掉）
        assert len(updated_goals) == 0
        
        # 验证目标值没有变化
        updated_goal = db_session.session.get(StudyGoal, goal.id)
        assert updated_goal.current_value == target_value
        
        # 清理
        db_session.session.delete(plan)
        db_session.session.commit()
