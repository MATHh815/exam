"""学习计划属性测试（Property-Based Testing）

使用 Hypothesis 进行基于属性的测试，验证学习计划系统的通用属性。
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
        username='prop_test_user',
        email='prop@test.com',
        nickname='属性测试用户'
    )
    user.set_password('password123')
    db_session.session.add(user)
    db_session.session.commit()
    return user


# 自定义策略
valid_exam_types = st.sampled_from(['civil_service', 'postgraduate', 'public_institution'])
valid_goal_types = st.sampled_from(['daily_practice', 'weekly_practice', 'daily_duration', 'exam_count'])
valid_statuses = st.sampled_from(['active', 'completed', 'paused'])

# 日期策略：生成合理的日期范围
def date_strategy():
    """生成2024-2025年的日期"""
    return st.dates(
        min_value=date(2024, 1, 1),
        max_value=date(2025, 12, 31)
    )


class TestProperty1StudyPlanDataPersistence:
    """
    Property 1: Study plan data persistence
    For any valid study plan data, creating a study plan should result in 
    all fields being correctly stored and retrievable
    
    Feature: exam-enhancements-phase1, Property 1
    Validates: Requirements 1.1
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        name=st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_categories=('Cs',))),
        description=st.text(max_size=500, alphabet=st.characters(blacklist_categories=('Cs',))),
        exam_type=valid_exam_types,
        start_date=date_strategy(),
        end_date=date_strategy()
    )
    def test_plan_data_persistence(self, db_session, test_user, name, description, 
                                   exam_type, start_date, end_date):
        """测试学习计划数据持久化"""
        # 确保结束日期不早于开始日期
        if end_date < start_date:
            start_date, end_date = end_date, start_date
        
        plan_data = {
            'name': name,
            'description': description,
            'exam_type': exam_type,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        }
        
        # 创建计划
        plan = StudyPlanService.create_plan(test_user.id, plan_data)
        
        # 验证所有字段都正确存储
        assert plan.name == name
        assert plan.description == description
        assert plan.exam_type == exam_type
        assert plan.start_date == start_date
        assert plan.end_date == end_date
        assert plan.user_id == test_user.id
        
        # 验证可以检索
        retrieved = StudyPlanService.get_plan_by_id(plan.id, test_user.id)
        assert retrieved is not None
        assert retrieved.name == name
        assert retrieved.exam_type == exam_type
        assert retrieved.start_date == start_date
        assert retrieved.end_date == end_date
        
        # 清理
        db_session.session.delete(plan)
        db_session.session.commit()


class TestProperty2GoalValueValidation:
    """
    Property 2: Goal value validation
    For any goal value, the system should accept it if and only if it is a positive integer (> 0)
    
    Feature: exam-enhancements-phase1, Property 2
    Validates: Requirements 1.2
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        goal_value=st.integers(min_value=1, max_value=1000)
    )
    def test_positive_goal_values_accepted(self, db_session, test_user, goal_value):
        """测试正整数目标值被接受"""
        # 根据值选择合适的目标类型
        if goal_value <= 500:
            goal_type = 'daily_practice'
        elif goal_value <= 720:
            goal_type = 'daily_duration'
        else:
            goal_type = 'exam_count'
        
        plan_data = {
            'name': '测试计划',
            'exam_type': 'civil_service',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
            'goals': [{
                'goal_type': goal_type,
                'target_value': goal_value,
                'period_start': '2024-01-01',
                'period_end': '2024-01-01'
            }]
        }
        
        plan = StudyPlanService.create_plan(test_user.id, plan_data)
        assert plan.goals[0].target_value == goal_value
        
        # 清理
        db_session.session.delete(plan)
        db_session.session.commit()
    
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        goal_value=st.integers(max_value=0)
    )
    def test_non_positive_goal_values_rejected(self, db_session, test_user, goal_value):
        """测试非正整数目标值被拒绝"""
        plan_data = {
            'name': '测试计划',
            'exam_type': 'civil_service',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
            'goals': [{
                'goal_type': 'daily_practice',
                'target_value': goal_value,
                'period_start': '2024-01-01',
                'period_end': '2024-01-01'
            }]
        }
        
        with pytest.raises(ValueError, match='目标值必须是正整数'):
            StudyPlanService.create_plan(test_user.id, plan_data)


class TestProperty3WeeklyGoalConstraint:
    """
    Property 3: Weekly goal constraint
    For any daily goal value D and weekly goal value W, 
    the system should accept W if and only if W >= D * 7
    
    Feature: exam-enhancements-phase1, Property 3
    Validates: Requirements 1.3
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        daily_target=st.integers(min_value=1, max_value=50)
    )
    def test_weekly_goal_constraint_valid(self, db_session, test_user, daily_target):
        """测试周目标 >= 日目标 * 7 时被接受"""
        weekly_target = daily_target * 7  # 正好等于
        
        plan_data = {
            'name': '测试计划',
            'exam_type': 'civil_service',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
            'goals': [{
                'goal_type': 'weekly_practice',
                'target_value': weekly_target,
                'daily_target': daily_target,
                'period_start': '2024-01-01',
                'period_end': '2024-01-07'
            }]
        }
        
        plan = StudyPlanService.create_plan(test_user.id, plan_data)
        assert plan.goals[0].target_value == weekly_target
        
        # 清理
        db_session.session.delete(plan)
        db_session.session.commit()
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        daily_target=st.integers(min_value=2, max_value=50),
        deficit=st.integers(min_value=1, max_value=6)
    )
    def test_weekly_goal_constraint_invalid(self, db_session, test_user, daily_target, deficit):
        """测试周目标 < 日目标 * 7 时被拒绝"""
        weekly_target = daily_target * 7 - deficit  # 小于要求但仍为正整数
        
        # 确保 weekly_target 是正整数
        assume(weekly_target > 0)
        
        plan_data = {
            'name': '测试计划',
            'exam_type': 'civil_service',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
            'goals': [{
                'goal_type': 'weekly_practice',
                'target_value': weekly_target,
                'daily_target': daily_target,
                'period_start': '2024-01-01',
                'period_end': '2024-01-07'
            }]
        }
        
        with pytest.raises(ValueError, match='周目标必须大于等于日目标的7倍'):
            StudyPlanService.create_plan(test_user.id, plan_data)


class TestProperty4ProgressCalculationAccuracy:
    """
    Property 4: Progress calculation accuracy
    For any study plan with known current and target values, 
    the displayed progress percentage should equal (current_value / target_value) * 100
    
    Feature: exam-enhancements-phase1, Property 4
    Validates: Requirements 1.4
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        target_value=st.integers(min_value=1, max_value=500),
        current_value=st.integers(min_value=0, max_value=500)
    )
    def test_progress_calculation(self, db_session, test_user, target_value, current_value):
        """测试进度百分比计算准确性"""
        # 确保 current_value 不超过 target_value
        if current_value > target_value:
            current_value = target_value
        
        # 创建计划
        plan_data = {
            'name': '测试计划',
            'exam_type': 'civil_service',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
            'goals': [{
                'goal_type': 'daily_practice',
                'target_value': target_value,
                'period_start': '2024-01-01',
                'period_end': '2024-01-01'
            }]
        }
        
        plan = StudyPlanService.create_plan(test_user.id, plan_data)
        
        # 设置当前值
        goal = plan.goals[0]
        goal.current_value = current_value
        db_session.session.commit()
        
        # 计算期望的进度百分比
        expected_percentage = (current_value / target_value) * 100
        
        # 验证计算准确性
        goal_dict = goal.to_dict()
        assert abs(goal_dict['progress_percentage'] - expected_percentage) < 0.01
        
        # 清理
        db_session.session.delete(plan)
        db_session.session.commit()


class TestProperty5UpdatePreservesProgress:
    """
    Property 5: Update preserves progress
    For any study plan with existing progress data, 
    updating the plan's metadata should not change the progress values
    
    Feature: exam-enhancements-phase1, Property 5
    Validates: Requirements 1.6
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        original_name=st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',))),
        new_name=st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',))),
        new_description=st.text(max_size=200, alphabet=st.characters(blacklist_categories=('Cs',))),
        progress_value=st.integers(min_value=0, max_value=100)
    )
    def test_update_preserves_progress(self, db_session, test_user, original_name, 
                                      new_name, new_description, progress_value):
        """测试更新计划保留进度数据"""
        # 创建带目标的计划
        plan_data = {
            'name': original_name,
            'exam_type': 'civil_service',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
            'goals': [{
                'goal_type': 'daily_practice',
                'target_value': 100,
                'period_start': '2024-01-01',
                'period_end': '2024-01-01'
            }]
        }
        
        plan = StudyPlanService.create_plan(test_user.id, plan_data)
        
        # 设置进度
        goal = plan.goals[0]
        goal.current_value = progress_value
        db_session.session.commit()
        
        # 更新计划元数据
        update_data = {
            'name': new_name,
            'description': new_description
        }
        updated_plan = StudyPlanService.update_plan(plan.id, test_user.id, update_data)
        
        # 验证进度未改变
        assert updated_plan.goals[0].current_value == progress_value
        assert updated_plan.goals[0].target_value == 100
        
        # 清理
        db_session.session.delete(updated_plan)
        db_session.session.commit()


class TestProperty6SoftDeleteBehavior:
    """
    Property 6: Soft delete behavior
    For any study plan, deleting it should set is_deleted=True 
    without removing the record from the database
    
    Feature: exam-enhancements-phase1, Property 6
    Validates: Requirements 1.7
    """
    
    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        name=st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',)))
    )
    def test_soft_delete_preserves_record(self, db_session, test_user, name):
        """测试软删除保留数据库记录"""
        # 创建计划
        plan_data = {
            'name': name,
            'exam_type': 'civil_service',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31'
        }
        
        plan = StudyPlanService.create_plan(test_user.id, plan_data)
        plan_id = plan.id
        
        # 删除计划
        StudyPlanService.delete_plan(plan_id, test_user.id)
        
        # 验证记录仍存在
        deleted_plan = db_session.session.get(StudyPlan, plan_id)
        assert deleted_plan is not None
        assert deleted_plan.is_deleted is True
        assert deleted_plan.name == name
        
        # 验证不出现在查询列表中
        plans = StudyPlanService.get_user_plans(test_user.id)
        assert plan_id not in [p.id for p in plans]
        
        # 清理
        db_session.session.delete(deleted_plan)
        db_session.session.commit()


class TestProperty7GoalTypeValidation:
    """
    Property 7: Goal type validation
    For any goal type string, the system should accept it if and only if 
    it is one of: daily_practice, weekly_practice, daily_duration, exam_count
    
    Feature: exam-enhancements-phase1, Property 7
    Validates: Requirements 2.1
    """
    
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        goal_type=valid_goal_types
    )
    def test_valid_goal_types_accepted(self, db_session, test_user, goal_type):
        """测试有效的目标类型被接受"""
        # 根据类型选择合适的目标值
        if goal_type in ['daily_practice', 'weekly_practice']:
            target_value = 50
        elif goal_type == 'daily_duration':
            target_value = 60
        else:  # exam_count
            target_value = 5
        
        plan_data = {
            'name': '测试计划',
            'exam_type': 'civil_service',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
            'goals': [{
                'goal_type': goal_type,
                'target_value': target_value,
                'period_start': '2024-01-01',
                'period_end': '2024-01-01'
            }]
        }
        
        plan = StudyPlanService.create_plan(test_user.id, plan_data)
        assert plan.goals[0].goal_type == goal_type
        
        # 清理
        db_session.session.delete(plan)
        db_session.session.commit()
    
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        invalid_goal_type=st.text(min_size=1, max_size=50).filter(
            lambda x: x not in ['daily_practice', 'weekly_practice', 'daily_duration', 'exam_count']
        )
    )
    def test_invalid_goal_types_rejected(self, db_session, test_user, invalid_goal_type):
        """测试无效的目标类型被拒绝"""
        plan_data = {
            'name': '测试计划',
            'exam_type': 'civil_service',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
            'goals': [{
                'goal_type': invalid_goal_type,
                'target_value': 50,
                'period_start': '2024-01-01',
                'period_end': '2024-01-01'
            }]
        }
        
        with pytest.raises(ValueError, match='无效的目标类型'):
            StudyPlanService.create_plan(test_user.id, plan_data)
