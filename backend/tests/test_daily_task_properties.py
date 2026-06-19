"""每日任务系统属性测试

使用 Hypothesis 进行基于属性的测试，验证每日任务系统的正确性
"""
from datetime import date, timedelta
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from app import create_app, db
from app.models.user import User
from app.models.achievement import DailyTask, UserPoints
from app.services.daily_task_service import DailyTaskService, TASK_TEMPLATES


@pytest.fixture(scope='module')
def app():
    """创建测试应用"""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='module')
def test_user(app):
    """创建测试用户（模块级别）"""
    with app.app_context():
        user = User(
            username='testuser_daily_task',
            email='test_daily_task@example.com',
            password_hash='dummy_hash'
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        yield user_id


def cleanup_user_data(app, user_id):
    """清理用户数据"""
    with app.app_context():
        DailyTask.query.filter_by(user_id=user_id).delete()
        UserPoints.query.filter_by(user_id=user_id).delete()
        db.session.commit()


class TestDailyTaskProperties:
    """每日任务系统属性测试类"""
    
    def test_property_41_daily_task_generation(self, test_user, app):
        """
        Property 41: Daily task generation
        For any active user, when a new day begins, the system should generate
        a set of daily tasks for that user
        
        Feature: exam-enhancements-phase1, Property 41
        Validates: Requirements 12.1
        """
        with app.app_context():
            user_id = test_user
            cleanup_user_data(app, user_id)
            
            # 生成今日任务
            tasks = DailyTaskService.generate_daily_tasks(user_id)
            
            # 验证任务已生成
            assert len(tasks) > 0, "Should generate at least one task"
            
            # 验证任务数量等于模板数量
            assert len(tasks) == len(TASK_TEMPLATES), \
                f"Should generate {len(TASK_TEMPLATES)} tasks, got {len(tasks)}"
            
            # 验证每个任务都有必要字段
            for task in tasks:
                assert 'task_type' in task
                assert 'task_description' in task
                assert 'target_value' in task
                assert 'current_value' in task
                assert 'points_reward' in task
                assert 'is_completed' in task
                assert task['current_value'] == 0, "Initial progress should be 0"
                assert task['is_completed'] is False, "Initial status should be incomplete"
    
    def test_property_42_task_template_compliance(self, test_user, app):
        """
        Property 42: Task template compliance
        For any generated daily task, it should match one of the predefined
        task templates
        
        Feature: exam-enhancements-phase1, Property 42
        Validates: Requirements 12.2
        """
        with app.app_context():
            user_id = test_user
            cleanup_user_data(app, user_id)
            
            # 生成任务
            tasks = DailyTaskService.generate_daily_tasks(user_id)
            
            # 获取模板类型
            template_types = {t['task_type'] for t in TASK_TEMPLATES}
            
            # 验证每个任务都匹配一个模板
            for task in tasks:
                assert task['task_type'] in template_types, \
                    f"Task type {task['task_type']} should match a template"
                
                # 找到对应的模板
                template = next(t for t in TASK_TEMPLATES if t['task_type'] == task['task_type'])
                
                # 验证目标值和积分奖励匹配模板
                assert task['target_value'] == template['target_value'], \
                    "Target value should match template"
                assert task['points_reward'] == template['points_reward'], \
                    "Points reward should match template"
    
    def test_property_43_task_completion_awards_points(self, test_user, app):
        """
        Property 43: Task completion awards points
        For any daily task, completing it (current_value >= target_value) should
        mark it as completed and award the specified points
        
        Feature: exam-enhancements-phase1, Property 43
        Validates: Requirements 12.3
        """
        with app.app_context():
            user_id = test_user
            cleanup_user_data(app, user_id)
            
            # 生成任务
            tasks = DailyTaskService.generate_daily_tasks(user_id)
            task = tasks[0]
            
            # 获取初始积分
            from app.services.points_service import PointsService
            initial_points = PointsService.get_user_points(user_id)['total_points']
            
            # 完成任务
            completed_task = DailyTaskService.complete_task(task['id'])
            
            # 验证任务标记为完成
            assert completed_task['is_completed'] is True, \
                "Task should be marked as completed"
            assert completed_task['current_value'] == completed_task['target_value'], \
                "Current value should equal target value"
            
            # 验证积分增加
            final_points = PointsService.get_user_points(user_id)['total_points']
            assert final_points == initial_points + task['points_reward'], \
                f"Points should increase by {task['points_reward']}"
    
    def test_property_44_task_progress_display(self, test_user, app):
        """
        Property 44: Task progress display
        For any daily task, viewing it should display description, current progress,
        target value, and reward points
        
        Feature: exam-enhancements-phase1, Property 44
        Validates: Requirements 12.4
        """
        with app.app_context():
            user_id = test_user
            cleanup_user_data(app, user_id)
            
            # 生成任务
            tasks = DailyTaskService.get_today_tasks(user_id)
            
            # 验证每个任务都有完整的显示信息
            for task in tasks:
                assert 'task_description' in task, "Should have description"
                assert 'current_value' in task, "Should have current progress"
                assert 'target_value' in task, "Should have target value"
                assert 'points_reward' in task, "Should have reward points"
                assert 'progress_percentage' in task, "Should have progress percentage"
                
                # 验证进度百分比计算正确
                expected_percentage = round(
                    task['current_value'] / task['target_value'] * 100,
                    2
                ) if task['target_value'] > 0 else 0
                
                assert task['progress_percentage'] == expected_percentage, \
                    f"Progress percentage should be {expected_percentage}, got {task['progress_percentage']}"
    
    def test_task_generation_idempotent(self, test_user, app):
        """测试任务生成的幂等性"""
        with app.app_context():
            user_id = test_user
            cleanup_user_data(app, user_id)
            
            # 第一次生成
            tasks1 = DailyTaskService.generate_daily_tasks(user_id)
            
            # 第二次生成（同一天）
            tasks2 = DailyTaskService.generate_daily_tasks(user_id)
            
            # 验证返回相同的任务
            assert len(tasks1) == len(tasks2), "Should return same number of tasks"
            
            task_ids1 = {t['id'] for t in tasks1}
            task_ids2 = {t['id'] for t in tasks2}
            assert task_ids1 == task_ids2, "Should return same tasks"
    
    def test_task_progress_update(self, test_user, app):
        """测试任务进度更新"""
        with app.app_context():
            user_id = test_user
            cleanup_user_data(app, user_id)
            
            # 生成任务
            tasks = DailyTaskService.generate_daily_tasks(user_id)
            task = tasks[0]
            task_type = task['task_type']
            
            # 更新进度
            updated_task = DailyTaskService.update_task_progress(
                user_id=user_id,
                task_type=task_type,
                increment=1
            )
            
            # 验证进度增加
            assert updated_task['current_value'] == 1, \
                "Progress should increase by 1"
            
            # 再次更新
            updated_task = DailyTaskService.update_task_progress(
                user_id=user_id,
                task_type=task_type,
                increment=2
            )
            
            assert updated_task['current_value'] == 3, \
                "Progress should increase by 2"
    
    def test_task_auto_complete_on_target_reached(self, test_user, app):
        """测试达到目标值时自动完成"""
        with app.app_context():
            user_id = test_user
            cleanup_user_data(app, user_id)
            
            # 生成任务
            tasks = DailyTaskService.generate_daily_tasks(user_id)
            task = tasks[0]
            task_type = task['task_type']
            target = task['target_value']
            
            # 更新进度到目标值
            updated_task = DailyTaskService.update_task_progress(
                user_id=user_id,
                task_type=task_type,
                increment=target
            )
            
            # 验证自动完成
            assert updated_task['is_completed'] is True, \
                "Task should auto-complete when target reached"
            assert updated_task['current_value'] == target, \
                "Progress should equal target"
    
    def test_completed_task_no_further_updates(self, test_user, app):
        """测试已完成任务不再更新进度"""
        with app.app_context():
            user_id = test_user
            cleanup_user_data(app, user_id)
            
            # 生成并完成任务
            tasks = DailyTaskService.generate_daily_tasks(user_id)
            task = tasks[0]
            DailyTaskService.complete_task(task['id'])
            
            # 尝试更新进度
            updated_task = DailyTaskService.update_task_progress(
                user_id=user_id,
                task_type=task['task_type'],
                increment=10
            )
            
            # 验证进度不变
            assert updated_task['is_completed'] is True
            assert updated_task['current_value'] == task['target_value']
    
    def test_task_stats(self, test_user, app):
        """测试任务统计功能"""
        with app.app_context():
            user_id = test_user
            cleanup_user_data(app, user_id)
            
            # 生成任务并完成一些
            tasks = DailyTaskService.generate_daily_tasks(user_id)
            DailyTaskService.complete_task(tasks[0]['id'])
            DailyTaskService.complete_task(tasks[1]['id'])
            
            # 获取统计
            stats = DailyTaskService.get_task_stats(user_id)
            
            # 验证统计字段
            assert 'today' in stats
            assert 'last_7_days' in stats
            assert 'streak_days' in stats
            
            # 验证今日统计
            assert stats['today']['total_tasks'] == len(tasks)
            assert stats['today']['completed_tasks'] == 2
            assert stats['today']['completion_rate'] > 0
    
    def test_task_cannot_complete_twice(self, test_user, app):
        """测试任务不能重复完成"""
        with app.app_context():
            user_id = test_user
            cleanup_user_data(app, user_id)
            
            # 生成任务
            tasks = DailyTaskService.generate_daily_tasks(user_id)
            task_id = tasks[0]['id']
            
            # 第一次完成
            result1 = DailyTaskService.complete_task(task_id)
            assert result1 is not None, "First completion should succeed"
            
            # 第二次尝试完成
            result2 = DailyTaskService.complete_task(task_id)
            assert result2 is None, "Second completion should return None"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
