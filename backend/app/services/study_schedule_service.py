"""学习日程服务模块"""
from datetime import datetime, date, time, timedelta
from typing import List, Dict, Optional
from sqlalchemy import and_, or_
from app import db
from app.models.study_schedule import StudySchedule, ACTIVITY_TYPES, SUBJECTS


class StudyScheduleService:
    """学习日程服务类
    
    提供学习日程的创建、更新、查询等功能
    """
    
    @staticmethod
    def create_schedule(user_id: int, schedule_data: dict) -> StudySchedule:
        """创建学习日程
        
        Args:
            user_id: 用户ID
            schedule_data: 日程数据
                - title: 标题（必填）
                - activity_type: 活动类型（必填）
                - subject: 科目（可选）
                - schedule_date: 日期（必填，格式：YYYY-MM-DD）
                - start_time: 开始时间（必填，格式：HH:MM）
                - end_time: 结束时间（必填，格式：HH:MM）
                - repeat_type: 重复类型（可选，默认once）
                - repeat_days: 重复的星期几（可选）
                - repeat_until: 重复截止日期（可选）
                - description: 描述（可选）
                - location: 地点（可选）
                - reminder_minutes: 提醒时间（可选，默认15分钟）
        
        Returns:
            StudySchedule: 创建的日程
        
        Raises:
            ValueError: 数据验证失败
        """
        # 验证必填字段
        if not schedule_data.get('title'):
            raise ValueError('标题不能为空')
        if not schedule_data.get('activity_type'):
            raise ValueError('活动类型不能为空')
        if not schedule_data.get('schedule_date'):
            raise ValueError('日期不能为空')
        if not schedule_data.get('start_time'):
            raise ValueError('开始时间不能为空')
        if not schedule_data.get('end_time'):
            raise ValueError('结束时间不能为空')
        
        # 验证活动类型
        activity_type = schedule_data['activity_type']
        if activity_type not in ACTIVITY_TYPES:
            raise ValueError(f'无效的活动类型: {activity_type}')
        
        # 验证科目（如果提供）
        subject = schedule_data.get('subject')
        if subject and subject not in SUBJECTS:
            raise ValueError(f'无效的科目: {subject}')
        
        # 解析日期和时间
        try:
            schedule_date = datetime.strptime(schedule_data['schedule_date'], '%Y-%m-%d').date()
            start_time = datetime.strptime(schedule_data['start_time'], '%H:%M').time()
            end_time = datetime.strptime(schedule_data['end_time'], '%H:%M').time()
        except ValueError as e:
            raise ValueError(f'日期或时间格式错误: {str(e)}')
        
        # 验证时间逻辑
        if start_time >= end_time:
            raise ValueError('结束时间必须晚于开始时间')
        
        # 检查时间冲突
        if StudyScheduleService._has_time_conflict(user_id, schedule_date, start_time, end_time):
            raise ValueError('该时间段已有其他日程安排')
        
        # 创建日程
        schedule = StudySchedule(
            user_id=user_id,
            title=schedule_data['title'],
            activity_type=activity_type,
            subject=subject,
            schedule_date=schedule_date,
            start_time=start_time,
            end_time=end_time,
            repeat_type=schedule_data.get('repeat_type', 'once'),
            repeat_days=schedule_data.get('repeat_days'),
            repeat_until=datetime.strptime(schedule_data['repeat_until'], '%Y-%m-%d').date() if schedule_data.get('repeat_until') else None,
            description=schedule_data.get('description', ''),
            location=schedule_data.get('location', ''),
            reminder_minutes=schedule_data.get('reminder_minutes', 15),
            is_reminder_enabled=schedule_data.get('is_reminder_enabled', True),
            status='pending'
        )
        
        db.session.add(schedule)
        db.session.commit()
        
        # 如果是重复日程，创建后续日程
        if schedule.repeat_type != 'once' and schedule.repeat_until:
            StudyScheduleService._create_repeat_schedules(schedule)
        
        return schedule
    
    @staticmethod
    def _has_time_conflict(user_id: int, schedule_date: date, start_time: time, end_time: time, exclude_id: int = None) -> bool:
        """检查时间冲突
        
        Args:
            user_id: 用户ID
            schedule_date: 日期
            start_time: 开始时间
            end_time: 结束时间
            exclude_id: 排除的日程ID（用于更新时）
        
        Returns:
            bool: 是否有冲突
        """
        query = StudySchedule.query.filter(
            StudySchedule.user_id == user_id,
            StudySchedule.schedule_date == schedule_date,
            StudySchedule.status != 'cancelled'
        )
        
        if exclude_id:
            query = query.filter(StudySchedule.id != exclude_id)
        
        schedules = query.all()
        
        for schedule in schedules:
            # 检查时间是否重叠
            if not (end_time <= schedule.start_time or start_time >= schedule.end_time):
                return True
        
        return False
    
    @staticmethod
    def _create_repeat_schedules(base_schedule: StudySchedule):
        """创建重复日程
        
        Args:
            base_schedule: 基础日程
        """
        if base_schedule.repeat_type == 'once':
            return
        
        current_date = base_schedule.schedule_date + timedelta(days=1)
        end_date = base_schedule.repeat_until
        
        while current_date <= end_date:
            should_create = False
            
            if base_schedule.repeat_type == 'daily':
                should_create = True
            elif base_schedule.repeat_type == 'weekly' and base_schedule.repeat_days:
                # 检查是否在指定的星期几
                weekday = str(current_date.weekday() + 1)  # 1-7 (周一到周日)
                if weekday in base_schedule.repeat_days.split(','):
                    should_create = True
            
            if should_create:
                # 检查时间冲突
                if not StudyScheduleService._has_time_conflict(
                    base_schedule.user_id,
                    current_date,
                    base_schedule.start_time,
                    base_schedule.end_time
                ):
                    repeat_schedule = StudySchedule(
                        user_id=base_schedule.user_id,
                        title=base_schedule.title,
                        activity_type=base_schedule.activity_type,
                        subject=base_schedule.subject,
                        schedule_date=current_date,
                        start_time=base_schedule.start_time,
                        end_time=base_schedule.end_time,
                        repeat_type='once',  # 重复生成的日程不再重复
                        description=base_schedule.description,
                        location=base_schedule.location,
                        reminder_minutes=base_schedule.reminder_minutes,
                        is_reminder_enabled=base_schedule.is_reminder_enabled,
                        status='pending'
                    )
                    db.session.add(repeat_schedule)
            
            current_date += timedelta(days=1)
        
        db.session.commit()
    
    @staticmethod
    def get_schedules_by_date_range(user_id: int, start_date: date, end_date: date) -> List[StudySchedule]:
        """获取日期范围内的日程
        
        Args:
            user_id: 用户ID
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            List[StudySchedule]: 日程列表
        """
        schedules = StudySchedule.query.filter(
            StudySchedule.user_id == user_id,
            StudySchedule.schedule_date >= start_date,
            StudySchedule.schedule_date <= end_date,
            StudySchedule.status != 'cancelled'
        ).order_by(
            StudySchedule.schedule_date,
            StudySchedule.start_time
        ).all()
        
        return schedules
    
    @staticmethod
    def get_today_schedules(user_id: int) -> List[StudySchedule]:
        """获取今天的日程
        
        Args:
            user_id: 用户ID
        
        Returns:
            List[StudySchedule]: 今天的日程列表
        """
        today = date.today()
        return StudyScheduleService.get_schedules_by_date_range(user_id, today, today)
    
    @staticmethod
    def update_schedule(schedule_id: int, user_id: int, schedule_data: dict) -> StudySchedule:
        """更新日程
        
        Args:
            schedule_id: 日程ID
            user_id: 用户ID
            schedule_data: 更新的数据
        
        Returns:
            StudySchedule: 更新后的日程
        
        Raises:
            ValueError: 日程不存在或无权限
        """
        schedule = StudySchedule.query.filter_by(
            id=schedule_id,
            user_id=user_id
        ).first()
        
        if not schedule:
            raise ValueError('日程不存在或无权限访问')
        
        # 更新字段
        if 'title' in schedule_data:
            schedule.title = schedule_data['title']
        
        if 'activity_type' in schedule_data:
            if schedule_data['activity_type'] not in ACTIVITY_TYPES:
                raise ValueError(f'无效的活动类型: {schedule_data["activity_type"]}')
            schedule.activity_type = schedule_data['activity_type']
        
        if 'subject' in schedule_data:
            if schedule_data['subject'] and schedule_data['subject'] not in SUBJECTS:
                raise ValueError(f'无效的科目: {schedule_data["subject"]}')
            schedule.subject = schedule_data['subject']
        
        if 'description' in schedule_data:
            schedule.description = schedule_data['description']
        
        if 'location' in schedule_data:
            schedule.location = schedule_data['location']
        
        if 'status' in schedule_data:
            schedule.status = schedule_data['status']
        
        schedule.updated_at = datetime.utcnow()
        db.session.commit()
        
        return schedule
    
    @staticmethod
    def complete_schedule(schedule_id: int, user_id: int) -> StudySchedule:
        """完成日程
        
        Args:
            schedule_id: 日程ID
            user_id: 用户ID
        
        Returns:
            StudySchedule: 更新后的日程
        """
        schedule = StudySchedule.query.filter_by(
            id=schedule_id,
            user_id=user_id
        ).first()
        
        if not schedule:
            raise ValueError('日程不存在或无权限访问')
        
        schedule.status = 'completed'
        schedule.is_completed = True
        schedule.completed_at = datetime.utcnow()
        schedule.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return schedule
    
    @staticmethod
    def delete_schedule(schedule_id: int, user_id: int) -> bool:
        """删除日程
        
        Args:
            schedule_id: 日程ID
            user_id: 用户ID
        
        Returns:
            bool: 是否成功删除
        """
        schedule = StudySchedule.query.filter_by(
            id=schedule_id,
            user_id=user_id
        ).first()
        
        if not schedule:
            raise ValueError('日程不存在或无权限访问')
        
        db.session.delete(schedule)
        db.session.commit()
        
        return True
    
    @staticmethod
    def get_statistics(user_id: int, start_date: date, end_date: date) -> dict:
        """获取日程统计
        
        Args:
            user_id: 用户ID
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            dict: 统计数据
        """
        schedules = StudyScheduleService.get_schedules_by_date_range(user_id, start_date, end_date)
        
        total_count = len(schedules)
        completed_count = sum(1 for s in schedules if s.is_completed)
        pending_count = sum(1 for s in schedules if s.status == 'pending')
        
        # 按活动类型统计
        activity_stats = {}
        for schedule in schedules:
            activity_type = schedule.activity_type
            if activity_type not in activity_stats:
                activity_stats[activity_type] = {
                    'count': 0,
                    'completed': 0,
                    'total_minutes': 0
                }
            activity_stats[activity_type]['count'] += 1
            if schedule.is_completed:
                activity_stats[activity_type]['completed'] += 1
            activity_stats[activity_type]['total_minutes'] += schedule.get_duration_minutes()
        
        # 按科目统计
        subject_stats = {}
        for schedule in schedules:
            if schedule.subject:
                subject = schedule.subject
                if subject not in subject_stats:
                    subject_stats[subject] = {
                        'count': 0,
                        'completed': 0,
                        'total_minutes': 0
                    }
                subject_stats[subject]['count'] += 1
                if schedule.is_completed:
                    subject_stats[subject]['completed'] += 1
                subject_stats[subject]['total_minutes'] += schedule.get_duration_minutes()
        
        return {
            'total_count': total_count,
            'completed_count': completed_count,
            'pending_count': pending_count,
            'completion_rate': round((completed_count / total_count * 100) if total_count > 0 else 0, 2),
            'activity_stats': activity_stats,
            'subject_stats': subject_stats
        }
