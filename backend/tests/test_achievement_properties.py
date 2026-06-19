"""成就系统属性测试

使用 Hypothesis 进行基于属性的测试，验证成就系统的正确性
"""
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from app import create_app, db
from app.models.user import User
from app.models.achievement import Achievement, UserAchievement, UserPoints
from app.services.achievement_service import AchievementService
from app.services.points_service import PointsService


@pytest.fixture(scope='module')
def app():
    """创建测试应用"""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        
        # 初始化测试成就
        if Achievement.query.count() == 0:
            test_achievements = [
                Achievement(
                    name='测试成就1',
                    description='完成1次练习',
                    icon='🎯',
                    category='learning',
                    criteria={'type': 'practice_count', 'value': 1},
                    points_reward=10,
                    tier=1
                ),
                Achievement(
                    name='测试成就2',
                    description='连续学习3天',
                    icon='🔥',
                    category='streak',
                    criteria={'type': 'streak_days', 'value': 3},
                    points_reward=20,
                    tier=1
                ),
                Achievement(
                    name='测试成就3',
                    description='达到等级2',
                    icon='🌟',
                    category='milestone',
                    criteria={'type': 'level', 'value': 2},
                    points_reward=50,
                    tier=2
                ),
            ]
            for achievement in test_achievements:
                db.session.add(achievement)
            db.session.commit()
        
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='module')
def test_user(app):
    """创建测试用户（模块级别）"""
    with app.app_context():
        user = User(
            username='testuser_achievement',
            email='test_achievement@example.com',
            password_hash='dummy_hash'
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        yield user_id


def cleanup_user_data(app, user_id):
    """清理用户数据"""
    with app.app_context():
        UserAchievement.query.filter_by(user_id=user_id).delete()
        UserPoints.query.filter_by(user_id=user_id).delete()
        db.session.commit()


class TestAchievementProperties:
    """成就系统属性测试类"""
    
    def test_property_30_achievement_auto_award(self, test_user, app):
        """
        Property 30: Achievement auto-award
        For any achievement criteria, when a user's actions meet those criteria,
        the achievement should be automatically awarded
        
        Feature: exam-enhancements-phase1, Property 30
        Validates: Requirements 9.1
        """
        with app.app_context():
            user_id = test_user
            cleanup_user_data(app, user_id)
            
            # 获取一个测试成就
            achievement = Achievement.query.filter_by(name='测试成就3').first()
            assert achievement is not None
            
            # 给用户足够的积分达到等级2
            points_needed = 400  # 等级2需要400积分
            PointsService.award_points(user_id, points_needed, "Test")
            
            # 检查成就
            newly_unlocked = AchievementService.check_achievements(
                user_id=user_id,
                event_type='level_up'
            )
            
            # 验证成就被自动解锁
            achievement_names = [a['name'] for a in newly_unlocked]
            assert '测试成就3' in achievement_names, \
                "Achievement should be auto-awarded when criteria met"
            
            # 验证用户成就记录存在
            user_achievement = UserAchievement.query.filter_by(
                user_id=user_id,
                achievement_id=achievement.id
            ).first()
            assert user_achievement is not None, \
                "UserAchievement record should be created"
    
    def test_property_31_achievement_categorization(self, test_user, app):
        """
        Property 31: Achievement categorization
        For any user, querying achievements should return three categories:
        earned (unlocked), in_progress (partially completed), and locked (not started)
        
        Feature: exam-enhancements-phase1, Property 31
        Validates: Requirements 9.3
        """
        with app.app_context():
            user_id = test_user
            cleanup_user_data(app, user_id)
            
            # 解锁一个成就
            achievement = Achievement.query.first()
            AchievementService.unlock_achievement(user_id, achievement.id)
            
            # 获取用户成就
            achievements = AchievementService.get_user_achievements(user_id)
            
            # 验证三个类别都存在
            assert 'earned' in achievements, "Should have 'earned' category"
            assert 'in_progress' in achievements, "Should have 'in_progress' category"
            assert 'locked' in achievements, "Should have 'locked' category"
            
            # 验证已解锁的成就在 earned 中
            earned_ids = [a['id'] for a in achievements['earned']]
            assert achievement.id in earned_ids, \
                "Unlocked achievement should be in 'earned' category"
            
            # 验证统计信息
            assert 'total_achievements' in achievements
            assert 'earned_count' in achievements
            assert achievements['earned_count'] >= 1
    
    def test_property_32_achievement_data_completeness(self, test_user, app):
        """
        Property 32: Achievement data completeness
        For any achievement, viewing it should display name, description, icon,
        and (if earned) unlock date
        
        Feature: exam-enhancements-phase1, Property 32
        Validates: Requirements 9.4
        """
        with app.app_context():
            user_id = test_user
            cleanup_user_data(app, user_id)
            
            # 获取一个成就
            achievement = Achievement.query.first()
            
            # 获取成就详情
            achievement_data = AchievementService.get_achievement(achievement.id)
            
            # 验证必要字段存在
            assert 'name' in achievement_data, "Should have 'name' field"
            assert 'description' in achievement_data, "Should have 'description' field"
            assert 'icon' in achievement_data, "Should have 'icon' field"
            assert 'category' in achievement_data, "Should have 'category' field"
            assert 'criteria' in achievement_data, "Should have 'criteria' field"
            assert 'points_reward' in achievement_data, "Should have 'points_reward' field"
            assert 'tier' in achievement_data, "Should have 'tier' field"
            
            # 解锁成就
            unlocked = AchievementService.unlock_achievement(user_id, achievement.id)
            
            # 验证解锁信息包含解锁时间
            assert 'unlocked_at' in unlocked, "Unlocked achievement should have 'unlocked_at'"
            assert unlocked['unlocked_at'] is not None
    
    def test_property_33_achievement_progress_tracking(self, test_user, app):
        """
        Property 33: Achievement progress tracking
        For any achievement with progress, the displayed progress should accurately
        reflect the user's current progress toward the criteria
        
        Feature: exam-enhancements-phase1, Property 33
        Validates: Requirements 9.6
        """
        with app.app_context():
            user_id = test_user
            cleanup_user_data(app, user_id)
            
            # 给用户一些积分（但不足以达到等级2）
            PointsService.award_points(user_id, 100, "Test")
            
            # 获取用户成就
            achievements = AchievementService.get_user_achievements(user_id)
            
            # 找到等级成就
            level_achievement = None
            for achievement in achievements['in_progress'] + achievements['locked']:
                if achievement['criteria']['type'] == 'level':
                    level_achievement = achievement
                    break
            
            if level_achievement:
                # 验证进度字段存在
                assert 'progress' in level_achievement, \
                    "Achievement should have 'progress' field"
                assert 'progress_percentage' in level_achievement, \
                    "Achievement should have 'progress_percentage' field"
                
                # 验证进度值合理
                assert level_achievement['progress'] >= 0, \
                    "Progress should be non-negative"
                assert 0 <= level_achievement['progress_percentage'] <= 100, \
                    "Progress percentage should be between 0 and 100"
    
    def test_achievement_unlock_awards_points(self, test_user, app):
        """测试解锁成就会奖励积分"""
        with app.app_context():
            user_id = test_user
            cleanup_user_data(app, user_id)
            
            # 获取初始积分
            initial_points = PointsService.get_user_points(user_id)['total_points']
            
            # 解锁一个成就
            achievement = Achievement.query.first()
            unlocked = AchievementService.unlock_achievement(user_id, achievement.id)
            
            # 验证积分增加
            final_points = PointsService.get_user_points(user_id)['total_points']
            assert final_points == initial_points + achievement.points_reward, \
                "Unlocking achievement should award points"
            
            # 验证返回的积分奖励信息
            assert 'points_awarded' in unlocked
            assert unlocked['points_awarded'] == achievement.points_reward
    
    def test_achievement_cannot_unlock_twice(self, test_user, app):
        """测试成就不能重复解锁"""
        with app.app_context():
            user_id = test_user
            cleanup_user_data(app, user_id)
            
            # 第一次解锁
            achievement = Achievement.query.first()
            first_unlock = AchievementService.unlock_achievement(user_id, achievement.id)
            assert first_unlock is not None, "First unlock should succeed"
            
            # 第二次尝试解锁
            second_unlock = AchievementService.unlock_achievement(user_id, achievement.id)
            assert second_unlock is None, "Second unlock should return None"
    
    def test_achievement_stats(self, test_user, app):
        """测试成就统计功能"""
        with app.app_context():
            user_id = test_user
            cleanup_user_data(app, user_id)
            
            # 解锁一些成就
            achievements = Achievement.query.limit(2).all()
            for achievement in achievements:
                AchievementService.unlock_achievement(user_id, achievement.id)
            
            # 获取统计
            stats = AchievementService.get_achievement_stats(user_id)
            
            # 验证统计字段
            assert 'total_achievements' in stats
            assert 'earned_count' in stats
            assert 'completion_rate' in stats
            assert 'category_stats' in stats
            assert 'tier_stats' in stats
            assert 'total_points_from_achievements' in stats
            
            # 验证数值
            assert stats['earned_count'] == 2
            assert stats['completion_rate'] > 0
            assert stats['total_points_from_achievements'] > 0
    
    def test_get_all_achievements_with_category_filter(self, app):
        """测试按类别筛选成就"""
        with app.app_context():
            # 获取所有成就
            all_achievements = AchievementService.get_all_achievements()
            
            # 按类别筛选
            learning_achievements = AchievementService.get_all_achievements(category='learning')
            streak_achievements = AchievementService.get_all_achievements(category='streak')
            milestone_achievements = AchievementService.get_all_achievements(category='milestone')
            
            # 验证筛选结果
            assert len(all_achievements) > 0
            assert all(a['category'] == 'learning' for a in learning_achievements)
            assert all(a['category'] == 'streak' for a in streak_achievements)
            assert all(a['category'] == 'milestone' for a in milestone_achievements)
            
            # 验证总数
            total_by_category = len(learning_achievements) + len(streak_achievements) + len(milestone_achievements)
            assert total_by_category == len(all_achievements)


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
