"""成就服务

提供成就检查、解锁、进度追踪等功能
"""
from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy import and_, or_
from app import db
from app.models.achievement import Achievement, UserAchievement, UserPoints
from app.models.note import QuestionNote, QuestionBookmark
from app.models.study_plan import StudyPlan
from app.services.points_service import PointsService


class AchievementService:
    """成就服务类"""
    
    @staticmethod
    def get_all_achievements(category: Optional[str] = None) -> List[Dict]:
        """获取所有成就定义
        
        Args:
            category: 成就类别筛选 (learning, streak, milestone)
            
        Returns:
            List[Dict]: 成就列表
        """
        query = Achievement.query.filter_by(is_active=True)
        
        if category:
            query = query.filter_by(category=category)
        
        achievements = query.order_by(Achievement.tier, Achievement.id).all()
        return [achievement.to_dict() for achievement in achievements]
    
    @staticmethod
    def get_achievement(achievement_id: int) -> Optional[Dict]:
        """获取成就详情
        
        Args:
            achievement_id: 成就ID
            
        Returns:
            Dict: 成就信息，不存在返回None
        """
        achievement = Achievement.query.filter_by(
            id=achievement_id,
            is_active=True
        ).first()
        
        return achievement.to_dict() if achievement else None
    
    @staticmethod
    def get_user_achievements(user_id: int) -> Dict:
        """获取用户成就信息
        
        返回三个类别：
        - earned: 已解锁的成就
        - in_progress: 进行中的成就（有进度但未完成）
        - locked: 未开始的成就
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict: 包含三个类别的成就列表
        """
        # 获取所有活跃成就
        all_achievements = Achievement.query.filter_by(is_active=True).all()
        
        # 获取用户已解锁的成就
        user_achievements = UserAchievement.query.filter_by(user_id=user_id).all()
        unlocked_ids = {ua.achievement_id for ua in user_achievements}
        
        # 获取用户当前状态
        user_stats = AchievementService._get_user_stats(user_id)
        
        earned = []
        in_progress = []
        locked = []
        
        for achievement in all_achievements:
            achievement_dict = achievement.to_dict()
            
            # 计算进度
            progress = AchievementService._calculate_progress(
                achievement.criteria,
                user_stats
            )
            achievement_dict['progress'] = progress
            achievement_dict['progress_percentage'] = min(100, round(progress / achievement.criteria['value'] * 100, 2))
            
            if achievement.id in unlocked_ids:
                # 已解锁
                user_achievement = next(ua for ua in user_achievements if ua.achievement_id == achievement.id)
                achievement_dict['unlocked_at'] = user_achievement.unlocked_at.isoformat() if user_achievement.unlocked_at else None
                earned.append(achievement_dict)
            elif progress > 0:
                # 进行中
                in_progress.append(achievement_dict)
            else:
                # 未开始
                locked.append(achievement_dict)
        
        return {
            'earned': earned,
            'in_progress': in_progress,
            'locked': locked,
            'total_achievements': len(all_achievements),
            'earned_count': len(earned),
            'in_progress_count': len(in_progress),
            'locked_count': len(locked)
        }
    
    @staticmethod
    def _get_user_stats(user_id: int) -> Dict:
        """获取用户统计数据
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict: 用户统计信息
        """
        from app.models.practice import PracticeRecord
        from app.models.exam import ExamSession
        
        # 获取积分信息
        user_points = UserPoints.query.filter_by(user_id=user_id).first()
        
        # 获取练习统计
        practice_count = PracticeRecord.query.filter_by(user_id=user_id).count()
        
        # 获取考试统计
        exam_count = ExamSession.query.filter_by(user_id=user_id).count()
        
        # 获取笔记数量
        note_count = QuestionNote.query.filter(
            and_(
                QuestionNote.user_id == user_id,
                QuestionNote.is_deleted == False
            )
        ).count()
        
        # 获取收藏数量
        bookmark_count = QuestionBookmark.query.filter_by(user_id=user_id).count()
        
        # 获取完成的学习计划数量
        plan_completed_count = StudyPlan.query.filter(
            and_(
                StudyPlan.user_id == user_id,
                StudyPlan.status == 'completed',
                StudyPlan.is_deleted == False
            )
        ).count()
        
        return {
            'practice_count': practice_count,
            'exam_count': exam_count,
            'perfect_score': 0,  # 暂时不支持，需要额外的成绩记录表
            'high_score_count': 0,  # 暂时不支持，需要额外的成绩记录表
            'streak_days': user_points.streak_days if user_points else 0,
            'level': user_points.current_level if user_points else 1,
            'total_points': user_points.total_points if user_points else 0,
            'note_count': note_count,
            'bookmark_count': bookmark_count,
            'plan_completed': plan_completed_count
        }
    
    @staticmethod
    def _calculate_progress(criteria: Dict, user_stats: Dict) -> int:
        """计算成就进度
        
        Args:
            criteria: 成就条件
            user_stats: 用户统计数据
            
        Returns:
            int: 当前进度值
        """
        criteria_type = criteria['type']
        
        # 映射条件类型到统计字段
        type_mapping = {
            'practice_count': 'practice_count',
            'exam_count': 'exam_count',
            'perfect_score': 'perfect_score',
            'high_score_count': 'high_score_count',
            'streak_days': 'streak_days',
            'level': 'level',
            'total_points': 'total_points',
            'note_count': 'note_count',
            'bookmark_count': 'bookmark_count',
            'plan_completed': 'plan_completed'
        }
        
        stat_key = type_mapping.get(criteria_type)
        if stat_key:
            return user_stats.get(stat_key, 0)
        
        return 0
    
    @staticmethod
    def check_achievements(user_id: int, event_type: str, event_data: Dict = None) -> List[Dict]:
        """检查并触发成就
        
        Args:
            user_id: 用户ID
            event_type: 事件类型 (practice_completed, exam_completed, level_up, etc.)
            event_data: 事件数据
            
        Returns:
            List[Dict]: 新解锁的成就列表
        """
        # 获取用户统计
        user_stats = AchievementService._get_user_stats(user_id)
        
        # 获取所有未解锁的成就
        unlocked_achievement_ids = {
            ua.achievement_id 
            for ua in UserAchievement.query.filter_by(user_id=user_id).all()
        }
        
        pending_achievements = Achievement.query.filter(
            and_(
                Achievement.is_active == True,
                ~Achievement.id.in_(unlocked_achievement_ids) if unlocked_achievement_ids else True
            )
        ).all()
        
        # 检查每个成就是否满足条件
        newly_unlocked = []
        for achievement in pending_achievements:
            if AchievementService._check_criteria(achievement.criteria, user_stats):
                # 解锁成就
                unlocked = AchievementService.unlock_achievement(user_id, achievement.id)
                if unlocked:
                    newly_unlocked.append(unlocked)
        
        return newly_unlocked
    
    @staticmethod
    def _check_criteria(criteria: Dict, user_stats: Dict) -> bool:
        """检查是否满足成就条件
        
        Args:
            criteria: 成就条件
            user_stats: 用户统计数据
            
        Returns:
            bool: 是否满足条件
        """
        criteria_type = criteria['type']
        required_value = criteria['value']
        
        # 获取当前进度
        current_value = AchievementService._calculate_progress(criteria, user_stats)
        
        # 特殊处理：高分次数需要检查阈值
        if criteria_type == 'high_score_count' and 'threshold' in criteria:
            # 这个已经在统计中处理了
            pass
        
        return current_value >= required_value
    
    @staticmethod
    def unlock_achievement(user_id: int, achievement_id: int) -> Optional[Dict]:
        """解锁成就
        
        Args:
            user_id: 用户ID
            achievement_id: 成就ID
            
        Returns:
            Dict: 解锁的成就信息，如果已解锁或不存在返回None
        """
        # 检查成就是否存在
        achievement = Achievement.query.filter_by(
            id=achievement_id,
            is_active=True
        ).first()
        
        if not achievement:
            return None
        
        # 检查是否已解锁
        existing = UserAchievement.query.filter_by(
            user_id=user_id,
            achievement_id=achievement_id
        ).first()
        
        if existing:
            return None  # 已解锁
        
        # 创建用户成就记录
        user_achievement = UserAchievement(
            user_id=user_id,
            achievement_id=achievement_id,
            unlocked_at=datetime.utcnow()
        )
        db.session.add(user_achievement)
        
        # 奖励积分
        if achievement.points_reward > 0:
            PointsService.award_achievement_points(
                user_id=user_id,
                achievement_id=achievement_id,
                points=achievement.points_reward
            )
        
        db.session.commit()
        
        # 返回成就信息
        result = achievement.to_dict()
        result['unlocked_at'] = user_achievement.unlocked_at.isoformat()
        result['points_awarded'] = achievement.points_reward
        
        return result
    
    @staticmethod
    def get_achievement_stats(user_id: int) -> Dict:
        """获取用户成就统计
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict: 成就统计信息
        """
        # 总成就数
        total_achievements = Achievement.query.filter_by(is_active=True).count()
        
        # 已解锁数
        earned_count = UserAchievement.query.filter_by(user_id=user_id).count()
        
        # 完成率
        completion_rate = round(earned_count / total_achievements * 100, 2) if total_achievements > 0 else 0
        
        # 各类别统计
        category_stats = {}
        for category in ['learning', 'streak', 'milestone']:
            total = Achievement.query.filter_by(
                is_active=True,
                category=category
            ).count()
            
            earned = db.session.query(UserAchievement).join(Achievement).filter(
                and_(
                    UserAchievement.user_id == user_id,
                    Achievement.category == category,
                    Achievement.is_active == True
                )
            ).count()
            
            category_stats[category] = {
                'total': total,
                'earned': earned,
                'completion_rate': round(earned / total * 100, 2) if total > 0 else 0
            }
        
        # 各等级统计
        tier_stats = {}
        for tier in [1, 2, 3]:
            total = Achievement.query.filter_by(
                is_active=True,
                tier=tier
            ).count()
            
            earned = db.session.query(UserAchievement).join(Achievement).filter(
                and_(
                    UserAchievement.user_id == user_id,
                    Achievement.tier == tier,
                    Achievement.is_active == True
                )
            ).count()
            
            tier_name = {1: 'bronze', 2: 'silver', 3: 'gold'}.get(tier, f'tier_{tier}')
            tier_stats[tier_name] = {
                'total': total,
                'earned': earned
            }
        
        # 总积分奖励
        total_points_from_achievements = db.session.query(
            db.func.sum(Achievement.points_reward)
        ).join(UserAchievement).filter(
            and_(
                UserAchievement.user_id == user_id,
                Achievement.is_active == True
            )
        ).scalar() or 0
        
        return {
            'total_achievements': total_achievements,
            'earned_count': earned_count,
            'completion_rate': completion_rate,
            'category_stats': category_stats,
            'tier_stats': tier_stats,
            'total_points_from_achievements': total_points_from_achievements
        }
