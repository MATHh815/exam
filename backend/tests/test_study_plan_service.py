"""学习计划服务单元测试"""
import pytest
from datetime import date, datetime, timedelta
from app import db
from app.models.user import User
from app.models.study_plan import StudyPlan, StudyGoal
from app.services.study_plan_service import StudyPlanService


@pytest.fixture
def test_user(db_session):
    """创建测试用户"""
    user = User(
        username='study_test_user',
        email='study@test.com',
        nickname='学习测试用户'
    )
    user.set_password('password123')
    db_session.session.add(user)
    db_session.session.commit()
    return user


class TestCreatePlan:
    """测试创建学习计划"""
    
    def test_create_plan_success(self, db_session, test_user):
        """测试成功创建学习计划"""
        plan_data = {
            'name': '2024国考冲刺',
            'description': '最后30天冲刺计划',
            'exam_type': 'civil_service',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31'
        }
        
        plan = StudyPlanService.create_plan(test_user.id, plan_data)
        
        assert plan.id is not None
        assert plan.name == '2024国考冲刺'
        assert plan.description == '最后30天冲刺计划'
        assert plan.exam_type == 'civil_service'
        assert plan.start_date == date(2024, 1, 1)
        assert plan.end_date == date(2024, 1, 31)
        assert plan.status == 'active'
        assert plan.is_deleted is False
        assert plan.user_id == test_user.id
    
    def test_create_plan_with_goals(self, db_session, test_user):
        """测试创建带目标的学习计划"""
        plan_data = {
            'name': '测试计划',
            'exam_type': 'civil_service',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
            'goals': [
                {
                    'goal_type': 'daily_practice',
                    'target_value': 50,
                    'period_start': '2024-01-01',
                    'period_end': '2024-01-01'
                },
                {
                    'goal_type': 'weekly_practice',
                    'target_value': 400,
                    'period_start': '2024-01-01',
                    'period_end': '2024-01-07'
                }
            ]
        }
        
        plan = StudyPlanService.create_plan(test_user.id, plan_data)
        
        assert len(plan.goals) == 2
        assert plan.goals[0].goal_type == 'daily_practice'
        assert plan.goals[0].target_value == 50
        assert plan.goals[1].goal_type == 'weekly_practice'
        assert plan.goals[1].target_value == 400
    
    def test_create_plan_missing_name(self, db_session, test_user):
        """测试缺少名称时创建失败"""
        plan_data = {
            'exam_type': 'civil_service',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31'
        }
        
        with pytest.raises(ValueError, match='计划名称不能为空'):
            StudyPlanService.create_plan(test_user.id, plan_data)
    
    def test_create_plan_missing_exam_type(self, db_session, test_user):
        """测试缺少考试类型时创建失败"""
        plan_data = {
            'name': '测试计划',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31'
        }
        
        with pytest.raises(ValueError, match='考试类型不能为空'):
            StudyPlanService.create_plan(test_user.id, plan_data)
    
    def test_create_plan_invalid_date_format(self, db_session, test_user):
        """测试无效日期格式"""
        plan_data = {
            'name': '测试计划',
            'exam_type': 'civil_service',
            'start_date': '2024/01/01',  # 错误格式
            'end_date': '2024-01-31'
        }
        
        with pytest.raises(ValueError, match='日期格式错误'):
            StudyPlanService.create_plan(test_user.id, plan_data)
    
    def test_create_plan_end_before_start(self, db_session, test_user):
        """测试结束日期早于开始日期"""
        plan_data = {
            'name': '测试计划',
            'exam_type': 'civil_service',
            'start_date': '2024-01-31',
            'end_date': '2024-01-01'
        }
        
        with pytest.raises(ValueError, match='结束日期不能早于开始日期'):
            StudyPlanService.create_plan(test_user.id, plan_data)
    
    def test_create_plan_name_too_long(self, db_session, test_user):
        """测试计划名称过长"""
        plan_data = {
            'name': 'A' * 201,  # 超过200字符
            'exam_type': 'civil_service',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31'
        }
        
        with pytest.raises(ValueError, match='计划名称长度不能超过200个字符'):
            StudyPlanService.create_plan(test_user.id, plan_data)


class TestGoalValidation:
    """测试目标值验证"""
    
    def test_goal_value_positive_integer(self, db_session, test_user):
        """测试目标值必须是正整数"""
        plan_data = {
            'name': '测试计划',
            'exam_type': 'civil_service',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
            'goals': [{
                'goal_type': 'daily_practice',
                'target_value': -5,  # 负数
                'period_start': '2024-01-01',
                'period_end': '2024-01-01'
            }]
        }
        
        with pytest.raises(ValueError, match='目标值必须是正整数'):
            StudyPlanService.create_plan(test_user.id, plan_data)
    
    def test_goal_value_zero(self, db_session, test_user):
        """测试目标值不能为0"""
        plan_data = {
            'name': '测试计划',
            'exam_type': 'civil_service',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
            'goals': [{
                'goal_type': 'daily_practice',
                'target_value': 0,
                'period_start': '2024-01-01',
                'period_end': '2024-01-01'
            }]
        }
        
        with pytest.raises(ValueError, match='目标值必须是正整数'):
            StudyPlanService.create_plan(test_user.id, plan_data)
    
    def test_practice_count_range(self, db_session, test_user):
        """测试练习数量范围验证"""
        # 测试超出上限
        plan_data = {
            'name': '测试计划',
            'exam_type': 'civil_service',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
            'goals': [{
                'goal_type': 'daily_practice',
                'target_value': 501,  # 超过500
                'period_start': '2024-01-01',
                'period_end': '2024-01-01'
            }]
        }
        
        with pytest.raises(ValueError, match='练习题目数量必须在 1-500 之间'):
            StudyPlanService.create_plan(test_user.id, plan_data)
    
    def test_study_duration_range(self, db_session, test_user):
        """测试学习时长范围验证"""
        # 测试低于下限
        plan_data = {
            'name': '测试计划',
            'exam_type': 'civil_service',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
            'goals': [{
                'goal_type': 'daily_duration',
                'target_value': 3,  # 低于5分钟
                'period_start': '2024-01-01',
                'period_end': '2024-01-01'
            }]
        }
        
        with pytest.raises(ValueError, match='学习时长必须在 5-720 分钟之间'):
            StudyPlanService.create_plan(test_user.id, plan_data)
    
    def test_invalid_goal_type(self, db_session, test_user):
        """测试无效的目标类型"""
        plan_data = {
            'name': '测试计划',
            'exam_type': 'civil_service',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
            'goals': [{
                'goal_type': 'invalid_type',
                'target_value': 50,
                'period_start': '2024-01-01',
                'period_end': '2024-01-01'
            }]
        }
        
        with pytest.raises(ValueError, match='无效的目标类型'):
            StudyPlanService.create_plan(test_user.id, plan_data)


class TestWeeklyGoalConstraint:
    """测试周目标约束"""
    
    def test_weekly_goal_constraint_valid(self, db_session, test_user):
        """测试周目标 >= 日目标 * 7（有效）"""
        plan_data = {
            'name': '测试计划',
            'exam_type': 'civil_service',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
            'goals': [{
                'goal_type': 'weekly_practice',
                'target_value': 350,  # >= 50 * 7
                'daily_target': 50,
                'period_start': '2024-01-01',
                'period_end': '2024-01-07'
            }]
        }
        
        plan = StudyPlanService.create_plan(test_user.id, plan_data)
        assert plan.goals[0].target_value == 350
    
    def test_weekly_goal_constraint_invalid(self, db_session, test_user):
        """测试周目标 < 日目标 * 7（无效）"""
        plan_data = {
            'name': '测试计划',
            'exam_type': 'civil_service',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
            'goals': [{
                'goal_type': 'weekly_practice',
                'target_value': 300,  # < 50 * 7
                'daily_target': 50,
                'period_start': '2024-01-01',
                'period_end': '2024-01-07'
            }]
        }
        
        with pytest.raises(ValueError, match='周目标必须大于等于日目标的7倍'):
            StudyPlanService.create_plan(test_user.id, plan_data)


class TestUpdatePlan:
    """测试更新学习计划"""
    
    def test_update_plan_name(self, db_session, test_user):
        """测试更新计划名称"""
        # 创建计划
        plan_data = {
            'name': '原始名称',
            'exam_type': 'civil_service',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31'
        }
        plan = StudyPlanService.create_plan(test_user.id, plan_data)
        
        # 更新名称
        update_data = {'name': '更新后的名称'}
        updated_plan = StudyPlanService.update_plan(plan.id, test_user.id, update_data)
        
        assert updated_plan.name == '更新后的名称'
    
    def test_update_plan_preserves_progress(self, db_session, test_user):
        """测试更新计划保留进度数据"""
        # 创建带目标的计划
        plan_data = {
            'name': '测试计划',
            'exam_type': 'civil_service',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31',
            'goals': [{
                'goal_type': 'daily_practice',
                'target_value': 50,
                'period_start': '2024-01-01',
                'period_end': '2024-01-01'
            }]
        }
        plan = StudyPlanService.create_plan(test_user.id, plan_data)
        
        # 手动设置进度
        goal = plan.goals[0]
        goal.current_value = 25
        db_session.session.commit()
        
        # 更新计划元数据
        update_data = {'name': '更新后的名称', 'description': '新描述'}
        updated_plan = StudyPlanService.update_plan(plan.id, test_user.id, update_data)
        
        # 验证进度未改变
        assert updated_plan.goals[0].current_value == 25
    
    def test_update_plan_invalid_status(self, db_session, test_user):
        """测试更新为无效状态"""
        plan_data = {
            'name': '测试计划',
            'exam_type': 'civil_service',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31'
        }
        plan = StudyPlanService.create_plan(test_user.id, plan_data)
        
        update_data = {'status': 'invalid_status'}
        
        with pytest.raises(ValueError, match='无效的状态'):
            StudyPlanService.update_plan(plan.id, test_user.id, update_data)


class TestSoftDelete:
    """测试软删除行为"""
    
    def test_soft_delete_sets_flag(self, db_session, test_user):
        """测试软删除设置 is_deleted 标志"""
        # 创建计划
        plan_data = {
            'name': '测试计划',
            'exam_type': 'civil_service',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31'
        }
        plan = StudyPlanService.create_plan(test_user.id, plan_data)
        plan_id = plan.id
        
        # 删除计划
        StudyPlanService.delete_plan(plan_id, test_user.id)
        
        # 验证记录仍存在但标记为已删除
        deleted_plan = StudyPlan.query.get(plan_id)
        assert deleted_plan is not None
        assert deleted_plan.is_deleted is True
    
    def test_soft_deleted_not_in_list(self, db_session, test_user):
        """测试软删除的计划不出现在列表中"""
        # 创建两个计划
        plan1_data = {
            'name': '计划1',
            'exam_type': 'civil_service',
            'start_date': '2024-01-01',
            'end_date': '2024-01-31'
        }
        plan1 = StudyPlanService.create_plan(test_user.id, plan1_data)
        
        plan2_data = {
            'name': '计划2',
            'exam_type': 'civil_service',
            'start_date': '2024-02-01',
            'end_date': '2024-02-28'
        }
        plan2 = StudyPlanService.create_plan(test_user.id, plan2_data)
        
        # 删除第一个计划
        StudyPlanService.delete_plan(plan1.id, test_user.id)
        
        # 获取计划列表
        plans = StudyPlanService.get_user_plans(test_user.id)
        
        # 验证只返回未删除的计划
        assert len(plans) == 1
        assert plans[0].id == plan2.id


class TestProgressCalculation:
    """测试进度计算"""
    
    def test_progress_calculation_accuracy(self, db_session, test_user):
        """测试进度百分比计算准确性"""
        # 创建带目标的计划
        plan_data = {
            'name': '测试计划',
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
        
        # 设置当前值
        goal = plan.goals[0]
        goal.current_value = 75
        db_session.session.commit()
        
        # 计算进度百分比
        progress_percentage = (goal.current_value / goal.target_value) * 100
        
        assert progress_percentage == 75.0
        assert goal.to_dict()['progress_percentage'] == 75.0
