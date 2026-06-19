"""积分服务

提供积分管理、等级计算、连续学习追踪等功能
"""
import math
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy import desc
from app import db
from app.models.achievement import UserPoints, PointTransaction


class PointsService:
    """积分服务类"""
    
    @staticmethod
    def get_or_create_user_points(user_id: int) -> UserPoints:
        """获取或创建用户积分记录
        
        Args:
            user_id: 用户ID
            
        Returns:
            UserPoints: 用户积分对象
        """
        user_points = UserPoints.query.filter_by(user_id=user_id).first()
        
        if not user_points:
            user_points = UserPoints(
                user_id=user_id,
                total_points=0,
                current_level=1,
                streak_days=0,
                last_activity_date=None
            )
            db.session.add(user_points)
            db.session.commit()
        
        return user_points
    
    @staticmethod
    def calculate_level(total_points: int) -> int:
        """计算等级
        
        等级计算公式: level = floor(sqrt(total_points / 100))
        
        Args:
            total_points: 总积分
            
        Returns:
            int: 等级（最小为1）
        """
        if total_points < 0:
            return 1
        
        level = math.floor(math.sqrt(total_points / 100))
        return max(1, level)
    
    @staticmethod
    def calculate_next_level_points(current_level: int) -> int:
        """计算升到下一级所需的总积分
        
        Args:
            current_level: 当前等级
            
        Returns:
            int: 下一级所需的总积分
        """
        next_level = current_level + 1
        return (next_level ** 2) * 100
    
    @staticmethod
    def update_streak(user_id: int) -> int:
        """更新连续学习天数
        
        Args:
            user_id: 用户ID
            
        Returns:
            int: 更新后的连续天数
        """
        user_points = PointsService.get_or_create_user_points(user_id)
        today = date.today()
        
        # 如果今天已经更新过，直接返回
        if user_points.last_activity_date == today:
            return user_points.streak_days
        
        # 如果昨天有活动，连续天数+1
        if user_points.last_activity_date == today - timedelta(days=1):
            user_points.streak_days += 1
        # 如果不是昨天，重置为1
        elif user_points.last_activity_date != today:
            user_points.streak_days = 1
        
        user_points.last_activity_date = today
        db.session.commit()
        
        return user_points.streak_days
    
    @staticmethod
    def calculate_streak_bonus(streak_days: int) -> int:
        """计算连续学习奖励积分
        
        Args:
            streak_days: 连续学习天数
            
        Returns:
            int: 奖励积分 (streak_days * 5)
        """
        return streak_days * 5
    
    @staticmethod
    def award_points(
        user_id: int,
        points: int,
        reason: str,
        reference_type: Optional[str] = None,
        reference_id: Optional[int] = None
    ) -> Dict:
        """奖励积分
        
        Args:
            user_id: 用户ID
            points: 积分数量
            reason: 获得积分的原因
            reference_type: 关联类型 (practice, exam, achievement, daily_task)
            reference_id: 关联ID
            
        Returns:
            Dict: 包含积分变化和等级信息的字典
        """
        # 获取或创建用户积分记录
        user_points = PointsService.get_or_create_user_points(user_id)
        
        # 记录旧等级
        old_level = user_points.current_level
        old_points = user_points.total_points
        
        # 更新积分
        user_points.total_points += points
        
        # 重新计算等级
        new_level = PointsService.calculate_level(user_points.total_points)
        user_points.current_level = new_level
        
        # 创建积分交易记录
        transaction = PointTransaction(
            user_id=user_id,
            points=points,
            reason=reason,
            reference_type=reference_type,
            reference_id=reference_id
        )
        db.session.add(transaction)
        
        # 提交事务
        db.session.commit()
        
        # 检查是否升级
        level_up = new_level > old_level
        
        return {
            'old_points': old_points,
            'new_points': user_points.total_points,
            'points_awarded': points,
            'old_level': old_level,
            'new_level': new_level,
            'level_up': level_up,
            'transaction_id': transaction.id
        }
    
    @staticmethod
    def get_user_points(user_id: int) -> Dict:
        """获取用户积分信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict: 用户积分详细信息
        """
        user_points = PointsService.get_or_create_user_points(user_id)
        
        # 计算下一级所需积分
        next_level_points = PointsService.calculate_next_level_points(user_points.current_level)
        points_to_next_level = next_level_points - user_points.total_points
        
        # 计算当前等级进度百分比
        current_level_points = (user_points.current_level ** 2) * 100
        level_progress = 0
        if next_level_points > current_level_points:
            level_progress = round(
                (user_points.total_points - current_level_points) / 
                (next_level_points - current_level_points) * 100,
                2
            )
        
        return {
            'user_id': user_points.user_id,
            'total_points': user_points.total_points,
            'current_level': user_points.current_level,
            'next_level': user_points.current_level + 1,
            'points_to_next_level': max(0, points_to_next_level),
            'level_progress_percentage': level_progress,
            'streak_days': user_points.streak_days,
            'last_activity_date': user_points.last_activity_date.isoformat() if user_points.last_activity_date else None,
            'created_at': user_points.created_at.isoformat() if user_points.created_at else None,
            'updated_at': user_points.updated_at.isoformat() if user_points.updated_at else None
        }
    
    @staticmethod
    def get_point_history(
        user_id: int,
        limit: int = 50,
        offset: int = 0
    ) -> Dict:
        """获取积分历史记录
        
        Args:
            user_id: 用户ID
            limit: 返回记录数量限制
            offset: 偏移量
            
        Returns:
            Dict: 包含历史记录和总数的字典
        """
        # 查询积分交易记录
        query = PointTransaction.query.filter_by(user_id=user_id)
        
        # 获取总数
        total = query.count()
        
        # 分页查询，按时间倒序
        transactions = query.order_by(desc(PointTransaction.created_at))\
            .limit(limit)\
            .offset(offset)\
            .all()
        
        return {
            'transactions': [t.to_dict() for t in transactions],
            'total': total,
            'limit': limit,
            'offset': offset
        }
    
    @staticmethod
    def award_practice_points(user_id: int, practice_id: int, score: int) -> Dict:
        """奖励练习积分
        
        Args:
            user_id: 用户ID
            practice_id: 练习ID
            score: 练习得分
            
        Returns:
            Dict: 积分奖励结果
        """
        # 更新连续学习天数
        streak_days = PointsService.update_streak(user_id)
        
        # 基础积分 = 得分
        base_points = score
        
        # 连续学习奖励
        streak_bonus = PointsService.calculate_streak_bonus(streak_days)
        
        # 总积分
        total_points = base_points + streak_bonus
        
        # 奖励积分
        result = PointsService.award_points(
            user_id=user_id,
            points=total_points,
            reason=f"完成练习 (得分: {score}, 连续{streak_days}天)",
            reference_type='practice',
            reference_id=practice_id
        )
        
        result['base_points'] = base_points
        result['streak_bonus'] = streak_bonus
        result['streak_days'] = streak_days
        
        return result
    
    @staticmethod
    def award_exam_points(user_id: int, exam_id: int, score: int) -> Dict:
        """奖励考试积分
        
        考试积分 = 得分 * 2
        
        Args:
            user_id: 用户ID
            exam_id: 考试ID
            score: 考试得分
            
        Returns:
            Dict: 积分奖励结果
        """
        # 更新连续学习天数
        streak_days = PointsService.update_streak(user_id)
        
        # 考试积分是得分的2倍
        base_points = score * 2
        
        # 连续学习奖励
        streak_bonus = PointsService.calculate_streak_bonus(streak_days)
        
        # 总积分
        total_points = base_points + streak_bonus
        
        # 奖励积分
        result = PointsService.award_points(
            user_id=user_id,
            points=total_points,
            reason=f"完成考试 (得分: {score}, 连续{streak_days}天)",
            reference_type='exam',
            reference_id=exam_id
        )
        
        result['base_points'] = base_points
        result['streak_bonus'] = streak_bonus
        result['streak_days'] = streak_days
        
        return result
    
    @staticmethod
    def award_achievement_points(user_id: int, achievement_id: int, points: int) -> Dict:
        """奖励成就积分
        
        Args:
            user_id: 用户ID
            achievement_id: 成就ID
            points: 积分数量
            
        Returns:
            Dict: 积分奖励结果
        """
        return PointsService.award_points(
            user_id=user_id,
            points=points,
            reason=f"解锁成就",
            reference_type='achievement',
            reference_id=achievement_id
        )
    
    @staticmethod
    def award_daily_task_points(user_id: int, task_id: int, points: int) -> Dict:
        """奖励每日任务积分
        
        Args:
            user_id: 用户ID
            task_id: 任务ID
            points: 积分数量
            
        Returns:
            Dict: 积分奖励结果
        """
        return PointsService.award_points(
            user_id=user_id,
            points=points,
            reason=f"完成每日任务",
            reference_type='daily_task',
            reference_id=task_id
        )
