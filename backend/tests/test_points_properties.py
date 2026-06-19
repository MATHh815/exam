"""积分系统属性测试

使用 Hypothesis 进行基于属性的测试，验证积分系统的正确性
"""
import math
from datetime import date, timedelta
import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from app import create_app, db
from app.models.user import User
from app.models.achievement import UserPoints, PointTransaction
from app.services.points_service import PointsService


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
            username='testuser',
            email='test@example.com',
            password_hash='dummy_hash'
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        yield user_id


def cleanup_user_data(app, user_id):
    """清理用户数据"""
    with app.app_context():
        PointTransaction.query.filter_by(user_id=user_id).delete()
        UserPoints.query.filter_by(user_id=user_id).delete()
        db.session.commit()


class TestPointsProperties:
    """积分系统属性测试类"""
    
    @given(total_points=st.integers(min_value=0, max_value=100000))
    @settings(max_examples=100)
    def test_property_38_level_calculation_formula(self, total_points, app):
        """
        Property 38: Level calculation formula
        For any total points value P, the calculated level should equal floor(sqrt(P / 100))
        
        Feature: exam-enhancements-phase1, Property 38
        Validates: Requirements 11.2
        """
        with app.app_context():
            calculated_level = PointsService.calculate_level(total_points)
            expected_level = max(1, math.floor(math.sqrt(total_points / 100)))
            
            assert calculated_level == expected_level, \
                f"Level calculation incorrect: {calculated_level} != {expected_level} for {total_points} points"
    
    @given(
        points=st.integers(min_value=1, max_value=1000),
        reason=st.text(min_size=1, max_size=100)
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_property_36_points_update_triggers_level_recalculation(
        self, points, reason, test_user, app
    ):
        """
        Property 36: Points update triggers level recalculation
        For any point award, the user's total points and level should be updated,
        where level = floor(sqrt(total_points / 100))
        
        Feature: exam-enhancements-phase1, Property 36
        Validates: Requirements 10.6
        """
        with app.app_context():
            user_id = test_user
            cleanup_user_data(app, user_id)
            
            # 获取初始状态
            initial_points_info = PointsService.get_user_points(user_id)
            initial_total = initial_points_info['total_points']
            initial_level = initial_points_info['current_level']
            
            # 奖励积分
            result = PointsService.award_points(
                user_id=user_id,
                points=points,
                reason=reason
            )
            
            # 验证积分更新
            assert result['new_points'] == initial_total + points, \
                "Total points not updated correctly"
            
            # 验证等级重新计算
            expected_level = PointsService.calculate_level(result['new_points'])
            assert result['new_level'] == expected_level, \
                f"Level not recalculated correctly: {result['new_level']} != {expected_level}"
            
            # 验证升级标志
            if expected_level > initial_level:
                assert result['level_up'] is True, "Level up flag should be True"
            else:
                assert result['level_up'] is False, "Level up flag should be False"
    
    @given(
        score=st.integers(min_value=0, max_value=100)
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_property_34_exam_points_calculation(self, score, test_user, app):
        """
        Property 34: Exam points calculation
        For any exam with score S, completing it should award S * 2 points to the user
        
        Feature: exam-enhancements-phase1, Property 34
        Validates: Requirements 10.3
        """
        with app.app_context():
            user_id = test_user
            cleanup_user_data(app, user_id)
            exam_id = 1
            
            # 获取初始积分
            initial_points = PointsService.get_user_points(user_id)['total_points']
            
            # 奖励考试积分
            result = PointsService.award_exam_points(
                user_id=user_id,
                exam_id=exam_id,
                score=score
            )
            
            # 验证基础积分是得分的2倍
            assert result['base_points'] == score * 2, \
                f"Exam base points should be score * 2: {result['base_points']} != {score * 2}"
            
            # 验证总积分包含基础积分和连续奖励
            expected_total = score * 2 + result['streak_bonus']
            assert result['points_awarded'] == expected_total, \
                f"Total points awarded incorrect: {result['points_awarded']} != {expected_total}"
    
    @given(
        streak_days=st.integers(min_value=1, max_value=365)
    )
    @settings(max_examples=100)
    def test_property_35_streak_bonus_calculation(self, streak_days, app):
        """
        Property 35: Streak bonus calculation
        For any learning streak of N days, the streak bonus should equal N * 5 points
        
        Feature: exam-enhancements-phase1, Property 35
        Validates: Requirements 10.5
        """
        with app.app_context():
            bonus = PointsService.calculate_streak_bonus(streak_days)
            expected_bonus = streak_days * 5
            
            assert bonus == expected_bonus, \
                f"Streak bonus incorrect: {bonus} != {expected_bonus} for {streak_days} days"
    
    @given(
        points_list=st.lists(
            st.integers(min_value=1, max_value=100),
            min_size=1,
            max_size=20
        )
    )
    @settings(
        max_examples=50,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_property_37_point_history_completeness(self, points_list, test_user, app):
        """
        Property 37: Point history completeness
        For any user, querying point history should return all point transactions
        with timestamps and reasons
        
        Feature: exam-enhancements-phase1, Property 37
        Validates: Requirements 10.7
        """
        with app.app_context():
            user_id = test_user
            cleanup_user_data(app, user_id)
            
            # 创建多个积分交易
            for i, points in enumerate(points_list):
                PointsService.award_points(
                    user_id=user_id,
                    points=points,
                    reason=f"Test transaction {i}"
                )
            
            # 获取积分历史
            history = PointsService.get_point_history(user_id, limit=100)
            
            # 验证记录数量
            assert history['total'] == len(points_list), \
                f"History count mismatch: {history['total']} != {len(points_list)}"
            
            # 验证每条记录都有必要字段
            for transaction in history['transactions']:
                assert 'points' in transaction, "Transaction missing points field"
                assert 'reason' in transaction, "Transaction missing reason field"
                assert 'created_at' in transaction, "Transaction missing timestamp"
                assert transaction['user_id'] == user_id, "Transaction user_id mismatch"
            
            # 验证积分总和
            total_awarded = sum(points_list)
            user_points = PointsService.get_user_points(user_id)
            assert user_points['total_points'] == total_awarded, \
                f"Total points mismatch: {user_points['total_points']} != {total_awarded}"
    
    @given(
        current_level=st.integers(min_value=1, max_value=50)
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_property_40_level_display_completeness(self, current_level, test_user, app):
        """
        Property 40: Level display completeness
        For any user profile view, it should display current level, total points,
        and points needed to reach the next level
        
        Feature: exam-enhancements-phase1, Property 40
        Validates: Requirements 11.5
        """
        with app.app_context():
            user_id = test_user
            cleanup_user_data(app, user_id)
            
            # 设置用户到指定等级
            target_points = (current_level ** 2) * 100
            PointsService.award_points(
                user_id=user_id,
                points=target_points,
                reason="Level test"
            )
            
            # 获取积分信息
            points_info = PointsService.get_user_points(user_id)
            
            # 验证必要字段存在
            assert 'current_level' in points_info, "Missing current_level"
            assert 'total_points' in points_info, "Missing total_points"
            assert 'next_level' in points_info, "Missing next_level"
            assert 'points_to_next_level' in points_info, "Missing points_to_next_level"
            assert 'level_progress_percentage' in points_info, "Missing level_progress_percentage"
            
            # 验证等级正确
            assert points_info['current_level'] >= current_level, \
                f"Current level incorrect: {points_info['current_level']} < {current_level}"
            
            # 验证下一级是当前级+1
            assert points_info['next_level'] == points_info['current_level'] + 1, \
                "Next level should be current level + 1"
            
            # 验证升级所需积分计算正确
            next_level_total = ((points_info['current_level'] + 1) ** 2) * 100
            expected_points_needed = next_level_total - points_info['total_points']
            assert points_info['points_to_next_level'] == expected_points_needed, \
                f"Points to next level incorrect: {points_info['points_to_next_level']} != {expected_points_needed}"
    
    def test_streak_update_same_day(self, test_user, app):
        """测试同一天多次更新连续天数"""
        with app.app_context():
            user_id = test_user
            cleanup_user_data(app, user_id)
            
            # 第一次更新
            streak1 = PointsService.update_streak(user_id)
            assert streak1 == 1, "First streak should be 1"
            
            # 同一天再次更新
            streak2 = PointsService.update_streak(user_id)
            assert streak2 == 1, "Streak should not increase on same day"
    
    def test_streak_consecutive_days(self, test_user, app):
        """测试连续天数的累积"""
        with app.app_context():
            user_id = test_user
            cleanup_user_data(app, user_id)
            
            # 第一天
            user_points = PointsService.get_or_create_user_points(user_id)
            user_points.last_activity_date = date.today() - timedelta(days=2)
            user_points.streak_days = 5
            db.session.commit()
            
            # 昨天活动
            user_points.last_activity_date = date.today() - timedelta(days=1)
            db.session.commit()
            
            # 今天更新
            streak = PointsService.update_streak(user_id)
            assert streak == 6, f"Streak should increment to 6, got {streak}"
    
    def test_streak_reset_after_gap(self, test_user, app):
        """测试中断后连续天数重置"""
        with app.app_context():
            user_id = test_user
            cleanup_user_data(app, user_id)
            
            # 设置上次活动是3天前
            user_points = PointsService.get_or_create_user_points(user_id)
            user_points.last_activity_date = date.today() - timedelta(days=3)
            user_points.streak_days = 10
            db.session.commit()
            
            # 今天更新（中断了）
            streak = PointsService.update_streak(user_id)
            assert streak == 1, f"Streak should reset to 1 after gap, got {streak}"
    
    @given(
        points=st.integers(min_value=-1000, max_value=-1)
    )
    @settings(
        max_examples=50,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_negative_points_handling(self, points, test_user, app):
        """测试负积分的处理"""
        with app.app_context():
            user_id = test_user
            cleanup_user_data(app, user_id)
            
            # 先给一些正积分
            PointsService.award_points(user_id, 1000, "Initial points")
            
            # 尝试扣除积分（负数）
            result = PointsService.award_points(
                user_id=user_id,
                points=points,
                reason="Penalty"
            )
            
            # 验证积分可以为负
            assert result['points_awarded'] == points
            assert result['new_points'] == 1000 + points
    
    def test_level_never_below_one(self, app):
        """测试等级永远不会低于1"""
        with app.app_context():
            # 测试0积分
            level = PointsService.calculate_level(0)
            assert level == 1, "Level should be at least 1 for 0 points"
            
            # 测试负积分（虽然不应该发生）
            level = PointsService.calculate_level(-100)
            assert level == 1, "Level should be at least 1 for negative points"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
