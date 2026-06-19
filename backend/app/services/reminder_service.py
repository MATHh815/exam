"""学习提醒服务模块"""
from datetime import datetime, time, date
from typing import Optional, List
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app import db
from app.models.study_plan import StudyReminder, StudyPlan, StudyGoal


class ReminderService:
    """学习提醒服务类
    
    提供学习提醒的创建、调度、发送和取消等功能。
    使用 APScheduler 进行定时任务管理。
    """
    
    # 类级别的调度器实例（单例模式）
    _scheduler = None
    
    @classmethod
    def get_scheduler(cls):
        """获取调度器实例（单例模式）"""
        if cls._scheduler is None:
            cls._scheduler = BackgroundScheduler()
            cls._scheduler.start()
        return cls._scheduler
    
    @staticmethod
    def create_reminder(user_id: int, plan_id: int, reminder_data: dict) -> StudyReminder:
        """创建学习提醒
        
        Args:
            user_id: 用户ID
            plan_id: 学习计划ID
            reminder_data: 提醒数据
                - reminder_time: 提醒时间（格式：HH:MM）
                - frequency: 提醒频率（daily, weekly, custom）
                - is_enabled: 是否启用
                - message: 提醒消息（可选）
        
        Returns:
            StudyReminder: 创建的提醒对象
        
        Raises:
            ValueError: 数据验证失败
        """
        # 验证必填字段
        if not reminder_data.get('reminder_time'):
            raise ValueError('提醒时间不能为空')
        
        # 验证学习计划存在且属于该用户
        plan = StudyPlan.query.filter_by(
            id=plan_id,
            user_id=user_id,
            is_deleted=False
        ).first()
        
        if not plan:
            raise ValueError('学习计划不存在或无权访问')
        
        # 解析提醒时间
        try:
            time_str = reminder_data['reminder_time']
            hour, minute = map(int, time_str.split(':'))
            reminder_time = time(hour=hour, minute=minute)
        except (ValueError, AttributeError):
            raise ValueError('提醒时间格式无效，应为 HH:MM')
        
        # 验证频率
        frequency = reminder_data.get('frequency', 'daily')
        if frequency not in ['daily', 'weekly', 'custom']:
            raise ValueError('无效的提醒频率')
        
        # 创建提醒记录
        reminder = StudyReminder(
            user_id=user_id,
            plan_id=plan_id,
            reminder_time=reminder_time,
            frequency=frequency,
            is_enabled=reminder_data.get('is_enabled', True),
            message=reminder_data.get('message', '该学习了！完成今天的学习目标吧！')
        )
        
        db.session.add(reminder)
        db.session.commit()
        
        # 如果启用，则调度提醒任务
        if reminder.is_enabled:
            ReminderService.schedule_reminder(reminder.id)
        
        return reminder
    
    @staticmethod
    def update_reminder(reminder_id: int, user_id: int, update_data: dict) -> StudyReminder:
        """更新学习提醒
        
        Args:
            reminder_id: 提醒ID
            user_id: 用户ID
            update_data: 更新数据
        
        Returns:
            StudyReminder: 更新后的提醒对象
        
        Raises:
            ValueError: 提醒不存在或无权访问
        """
        reminder = StudyReminder.query.filter_by(
            id=reminder_id,
            user_id=user_id
        ).first()
        
        if not reminder:
            raise ValueError('提醒不存在或无权访问')
        
        # 更新字段
        if 'reminder_time' in update_data:
            try:
                time_str = update_data['reminder_time']
                hour, minute = map(int, time_str.split(':'))
                reminder.reminder_time = time(hour=hour, minute=minute)
            except (ValueError, AttributeError):
                raise ValueError('提醒时间格式无效，应为 HH:MM')
        
        if 'frequency' in update_data:
            if update_data['frequency'] not in ['daily', 'weekly', 'custom']:
                raise ValueError('无效的提醒频率')
            reminder.frequency = update_data['frequency']
        
        if 'is_enabled' in update_data:
            old_enabled = reminder.is_enabled
            reminder.is_enabled = update_data['is_enabled']
            
            # 如果启用状态改变，更新调度
            if old_enabled != reminder.is_enabled:
                if reminder.is_enabled:
                    ReminderService.schedule_reminder(reminder.id)
                else:
                    ReminderService.cancel_reminder(reminder.id)
        
        if 'message' in update_data:
            reminder.message = update_data['message']
        
        db.session.commit()
        
        # 如果提醒时间或频率改变且启用，重新调度
        if reminder.is_enabled and ('reminder_time' in update_data or 'frequency' in update_data):
            ReminderService.cancel_reminder(reminder.id)
            ReminderService.schedule_reminder(reminder.id)
        
        return reminder
    
    @staticmethod
    def delete_reminder(reminder_id: int, user_id: int) -> bool:
        """删除学习提醒
        
        Args:
            reminder_id: 提醒ID
            user_id: 用户ID
        
        Returns:
            bool: 是否删除成功
        
        Raises:
            ValueError: 提醒不存在或无权访问
        """
        reminder = StudyReminder.query.filter_by(
            id=reminder_id,
            user_id=user_id
        ).first()
        
        if not reminder:
            raise ValueError('提醒不存在或无权访问')
        
        # 取消调度
        ReminderService.cancel_reminder(reminder.id)
        
        # 删除记录
        db.session.delete(reminder)
        db.session.commit()
        
        return True
    
    @staticmethod
    def get_user_reminders(user_id: int, plan_id: Optional[int] = None) -> List[StudyReminder]:
        """获取用户的提醒列表
        
        Args:
            user_id: 用户ID
            plan_id: 学习计划ID（可选，用于过滤）
        
        Returns:
            List[StudyReminder]: 提醒列表
        """
        query = StudyReminder.query.filter_by(user_id=user_id)
        
        if plan_id:
            query = query.filter_by(plan_id=plan_id)
        
        return query.all()
    
    @staticmethod
    def schedule_reminder(reminder_id: int) -> None:
        """调度学习提醒任务
        
        Args:
            reminder_id: 提醒ID
        """
        reminder = StudyReminder.query.get(reminder_id)
        if not reminder or not reminder.is_enabled:
            return
        
        scheduler = ReminderService.get_scheduler()
        job_id = f'reminder_{reminder_id}'
        
        # 移除已存在的任务
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
        
        # 根据频率创建触发器
        if reminder.frequency == 'daily':
            # 每天在指定时间触发
            trigger = CronTrigger(
                hour=reminder.reminder_time.hour,
                minute=reminder.reminder_time.minute
            )
        elif reminder.frequency == 'weekly':
            # 每周一在指定时间触发
            trigger = CronTrigger(
                day_of_week='mon',
                hour=reminder.reminder_time.hour,
                minute=reminder.reminder_time.minute
            )
        else:
            # custom 频率暂不支持，使用每天
            trigger = CronTrigger(
                hour=reminder.reminder_time.hour,
                minute=reminder.reminder_time.minute
            )
        
        # 添加任务
        scheduler.add_job(
            func=ReminderService.send_reminder,
            trigger=trigger,
            args=[reminder_id],
            id=job_id,
            name=f'Study Reminder {reminder_id}',
            replace_existing=True
        )
    
    @staticmethod
    def send_reminder(reminder_id: int) -> None:
        """发送学习提醒通知
        
        Args:
            reminder_id: 提醒ID
        """
        reminder = StudyReminder.query.get(reminder_id)
        if not reminder or not reminder.is_enabled:
            return
        
        # 检查用户今天是否已完成目标
        if ReminderService._check_daily_goal_completed(reminder.user_id, reminder.plan_id):
            print(f"用户 {reminder.user_id} 已完成今日目标，跳过提醒")
            return
        
        # 获取当前进度和剩余目标
        progress_info = ReminderService._get_progress_info(reminder.user_id, reminder.plan_id)
        
        # 构建提醒消息
        message = reminder.message
        if progress_info:
            message += f"\n\n当前进度：{progress_info['completed']}/{progress_info['total']} 个目标已完成"
            if progress_info['remaining'] > 0:
                message += f"\n还有 {progress_info['remaining']} 个目标待完成"
        
        # TODO: 集成实际的通知系统（邮件、推送等）
        # 目前只记录日志
        print(f"[提醒通知] 用户ID: {reminder.user_id}, 消息: {message}")
        
        # 更新最后发送时间
        reminder.last_sent_at = datetime.utcnow()
        db.session.commit()
    
    @staticmethod
    def cancel_reminder(reminder_id: int) -> None:
        """取消学习提醒任务
        
        Args:
            reminder_id: 提醒ID
        """
        scheduler = ReminderService.get_scheduler()
        job_id = f'reminder_{reminder_id}'
        
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
    
    @staticmethod
    def _check_daily_goal_completed(user_id: int, plan_id: int) -> bool:
        """检查用户今天的目标是否已完成（内部方法）
        
        Args:
            user_id: 用户ID
            plan_id: 学习计划ID
        
        Returns:
            bool: 是否已完成
        """
        today = date.today()
        
        # 查找今天的目标
        goals = StudyGoal.query.filter_by(
            plan_id=plan_id
        ).filter(
            StudyGoal.period_start <= today,
            StudyGoal.period_end >= today
        ).all()
        
        if not goals:
            return False
        
        # 检查是否所有目标都已完成
        return all(goal.is_completed for goal in goals)
    
    @staticmethod
    def _get_progress_info(user_id: int, plan_id: int) -> Optional[dict]:
        """获取学习进度信息（内部方法）
        
        Args:
            user_id: 用户ID
            plan_id: 学习计划ID
        
        Returns:
            dict: 进度信息
                - total: 总目标数
                - completed: 已完成数
                - remaining: 剩余数
        """
        today = date.today()
        
        # 查找今天的目标
        goals = StudyGoal.query.filter_by(
            plan_id=plan_id
        ).filter(
            StudyGoal.period_start <= today,
            StudyGoal.period_end >= today
        ).all()
        
        if not goals:
            return None
        
        total = len(goals)
        completed = sum(1 for goal in goals if goal.is_completed)
        remaining = total - completed
        
        return {
            'total': total,
            'completed': completed,
            'remaining': remaining
        }
    
    @staticmethod
    def shutdown_scheduler():
        """关闭调度器（用于应用关闭时）"""
        if ReminderService._scheduler:
            ReminderService._scheduler.shutdown()
            ReminderService._scheduler = None
