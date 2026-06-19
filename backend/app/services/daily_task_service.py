"""每日任务服务

提供每日任务生成、进度更新、完成等功能
"""
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy import and_
from app import db
from app.models.achievement import DailyTask
from app.services.points_service import PointsService


# 任务模板定义
TASK_TEMPLATES = [
    {
        'task_type': 'daily_practice',
        'task_description': '完成{target}次练习',
        'target_value': 3,
        'points_reward': 20
    },
    {
        'task_type': 'daily_questions',
        'task_description': '答对{target}道题目',
        'target_value': 10,
        'points_reward': 30
    },
    {
        'task_type': 'daily_study_time',
        'task_description': '学习{target}分钟',
        'target_value': 30,
        'points_reward': 25
    },
    {
        'task_type': 'daily_notes',
        'task_description': '创建{target}条笔记',
        'target_value': 2,
        'points_reward': 15
    },
    {
        'task_type': 'daily_review',
        'task_description': '复习{target}道错题',
        'target_value': 5,
        'points_reward': 20
    },
]


class DailyTaskService:
    """每日任务服务类"""
    
    @staticmethod
    def generate_daily_tasks(user_id: int, task_date: Optional[date] = None) -> List[Dict]:
        """为用户生成每日任务
        
        Args:
            user_id: 用户ID
            task_date: 任务日期，默认为今天
            
        Returns:
            List[Dict]: 生成的任务列表
        """
        if task_date is None:
            task_date = date.today()
        
        # 检查今天是否已经生成任务
        existing_tasks = DailyTask.query.filter_by(
            user_id=user_id,
            task_date=task_date
        ).all()
        
        if existing_tasks:
            return [task.to_dict() for task in existing_tasks]
        
        # 生成新任务
        created_tasks = []
        for template in TASK_TEMPLATES:
            task = DailyTask(
                user_id=user_id,
                task_date=task_date,
                task_type=template['task_type'],
                task_description=template['task_description'].format(
                    target=template['target_value']
                ),
                target_value=template['target_value'],
                current_value=0,
                points_reward=template['points_reward'],
                is_completed=False
            )
            db.session.add(task)
            created_tasks.append(task)
        
        db.session.commit()
        
        return [task.to_dict() for task in created_tasks]
    
    @staticmethod
    def get_today_tasks(user_id: int) -> List[Dict]:
        """获取用户今日任务
        
        Args:
            user_id: 用户ID
            
        Returns:
            List[Dict]: 今日任务列表
        """
        today = date.today()
        
        # 获取今日任务
        tasks = DailyTask.query.filter_by(
            user_id=user_id,
            task_date=today
        ).all()
        
        # 如果没有任务，自动生成
        if not tasks:
            return DailyTaskService.generate_daily_tasks(user_id, today)
        
        return [task.to_dict() for task in tasks]
    
    @staticmethod
    def update_task_progress(
        user_id: int,
        task_type: str,
        increment: int = 1
    ) -> Optional[Dict]:
        """更新任务进度
        
        Args:
            user_id: 用户ID
            task_type: 任务类型
            increment: 增量值
            
        Returns:
            Dict: 更新后的任务信息，如果任务不存在返回None
        """
        today = date.today()
        
        # 查找任务
        task = DailyTask.query.filter_by(
            user_id=user_id,
            task_date=today,
            task_type=task_type
        ).first()
        
        if not task:
            return None
        
        # 如果已完成，不再更新
        if task.is_completed:
            return task.to_dict()
        
        # 更新进度
        task.current_value += increment
        
        # 检查是否完成
        if task.current_value >= task.target_value:
            task.current_value = task.target_value
            task.is_completed = True
            
            # 奖励积分
            PointsService.award_daily_task_points(
                user_id=user_id,
                task_id=task.id,
                points=task.points_reward
            )
        
        db.session.commit()
        
        return task.to_dict()
    
    @staticmethod
    def complete_task(task_id: int) -> Optional[Dict]:
        """手动完成任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            Dict: 完成后的任务信息，如果任务不存在或已完成返回None
        """
        task = DailyTask.query.get(task_id)
        
        if not task or task.is_completed:
            return None
        
        # 标记为完成
        task.current_value = task.target_value
        task.is_completed = True
        
        # 奖励积分
        PointsService.award_daily_task_points(
            user_id=task.user_id,
            task_id=task.id,
            points=task.points_reward
        )
        
        db.session.commit()
        
        return task.to_dict()
    
    @staticmethod
    def reset_daily_tasks() -> int:
        """重置所有用户的每日任务（定时任务）
        
        删除昨天及之前的任务，为所有活跃用户生成新任务
        
        Returns:
            int: 重置的用户数量
        """
        from app.models.user import User
        
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        # 删除昨天及之前的任务
        DailyTask.query.filter(DailyTask.task_date < today).delete()
        db.session.commit()
        
        # 获取所有活跃用户（最近7天有活动的用户）
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        active_users = User.query.filter(
            User.last_login >= seven_days_ago
        ).all()
        
        # 为每个活跃用户生成今日任务
        reset_count = 0
        for user in active_users:
            DailyTaskService.generate_daily_tasks(user.id, today)
            reset_count += 1
        
        return reset_count
    
    @staticmethod
    def get_task_stats(user_id: int) -> Dict:
        """获取用户任务统计
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict: 任务统计信息
        """
        today = date.today()
        
        # 今日任务
        today_tasks = DailyTask.query.filter_by(
            user_id=user_id,
            task_date=today
        ).all()
        
        total_tasks = len(today_tasks)
        completed_tasks = sum(1 for task in today_tasks if task.is_completed)
        completion_rate = round(completed_tasks / total_tasks * 100, 2) if total_tasks > 0 else 0
        
        # 今日可获得的总积分
        total_points = sum(task.points_reward for task in today_tasks)
        earned_points = sum(task.points_reward for task in today_tasks if task.is_completed)
        
        # 历史统计（最近7天）
        seven_days_ago = today - timedelta(days=7)
        historical_tasks = DailyTask.query.filter(
            and_(
                DailyTask.user_id == user_id,
                DailyTask.task_date >= seven_days_ago,
                DailyTask.task_date < today
            )
        ).all()
        
        historical_completed = sum(1 for task in historical_tasks if task.is_completed)
        historical_total = len(historical_tasks)
        
        # 连续完成天数
        streak_days = DailyTaskService._calculate_streak(user_id)
        
        return {
            'today': {
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'completion_rate': completion_rate,
                'total_points': total_points,
                'earned_points': earned_points
            },
            'last_7_days': {
                'total_tasks': historical_total,
                'completed_tasks': historical_completed,
                'completion_rate': round(historical_completed / historical_total * 100, 2) if historical_total > 0 else 0
            },
            'streak_days': streak_days
        }
    
    @staticmethod
    def _calculate_streak(user_id: int) -> int:
        """计算连续完成任务的天数
        
        Args:
            user_id: 用户ID
            
        Returns:
            int: 连续天数
        """
        today = date.today()
        streak = 0
        check_date = today
        
        # 向前检查，直到找到未完成的一天
        while True:
            # 获取该天的任务
            tasks = DailyTask.query.filter_by(
                user_id=user_id,
                task_date=check_date
            ).all()
            
            if not tasks:
                # 没有任务，停止检查
                break
            
            # 检查是否全部完成
            all_completed = all(task.is_completed for task in tasks)
            
            if not all_completed:
                # 有未完成的任务，停止检查
                break
            
            streak += 1
            check_date -= timedelta(days=1)
            
            # 最多检查30天
            if streak >= 30:
                break
        
        return streak
    
    @staticmethod
    def get_task_templates() -> List[Dict]:
        """获取任务模板列表
        
        Returns:
            List[Dict]: 任务模板列表
        """
        return TASK_TEMPLATES.copy()
