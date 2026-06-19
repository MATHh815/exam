"""
番茄钟服务
"""
from datetime import datetime, timedelta, date
from app import db
from app.models.pomodoro import PomodoroSession, PomodoroStats
from app.services.points_service import PointsService

class PomodoroService:
    """番茄钟服务类"""
    
    # 积分奖励规则
    POINTS_RULES = {
        'focus_25': 10,      # 完成25分钟专注
        'focus_50': 25,      # 完成50分钟专注（连续2个）
        'daily_4': 50,       # 每日完成4个番茄钟
        'daily_8': 100,      # 每日完成8个番茄钟
        'streak_7': 200,     # 连续7天
        'streak_30': 1000,   # 连续30天
    }
    
    @staticmethod
    def complete_session(user_id, duration, session_type='focus', subject=None, notes=None):
        """
        完成一个番茄钟会话
        
        Args:
            user_id: 用户ID
            duration: 时长（分钟）
            session_type: 会话类型（focus/short_break/long_break）
            subject: 学习科目
            notes: 备注
            
        Returns:
            dict: 会话信息和奖励
        """
        now = datetime.utcnow()
        start_time = now - timedelta(minutes=duration)
        
        # 创建会话记录
        session = PomodoroSession(
            user_id=user_id,
            duration=duration,
            session_type=session_type,
            status='completed',
            subject=subject,
            notes=notes,
            start_time=start_time,
            end_time=now
        )
        
        # 计算积分奖励（仅专注时段）
        points_earned = 0
        achievements = []
        
        if session_type == 'focus':
            # 基础积分
            if duration >= 25:
                points_earned = PomodoroService.POINTS_RULES['focus_25']
            
            # 更新统计
            stats = PomodoroService._update_stats(user_id, duration)
            
            # 检查额外奖励
            extra_rewards = PomodoroService._check_achievements(stats)
            points_earned += extra_rewards['points']
            achievements = extra_rewards['achievements']
            
            # 记录积分
            session.points_earned = points_earned
            if points_earned > 0:
                PointsService.add_points(
                    user_id=user_id,
                    points=points_earned,
                    source='pomodoro',
                    description=f'完成{duration}分钟番茄钟'
                )
        
        db.session.add(session)
        db.session.commit()
        
        return {
            'session': session.to_dict(),
            'points_earned': points_earned,
            'achievements': achievements,
            'stats': stats.to_dict() if session_type == 'focus' else None
        }
    
    @staticmethod
    def interrupt_session(user_id, duration, session_type='focus', subject=None):
        """
        中断一个番茄钟会话
        
        Args:
            user_id: 用户ID
            duration: 已完成时长（分钟）
            session_type: 会话类型
            subject: 学习科目
            
        Returns:
            dict: 会话信息
        """
        now = datetime.utcnow()
        start_time = now - timedelta(minutes=duration)
        
        session = PomodoroSession(
            user_id=user_id,
            duration=duration,
            session_type=session_type,
            status='interrupted',
            subject=subject,
            start_time=start_time,
            end_time=now,
            points_earned=0
        )
        
        db.session.add(session)
        db.session.commit()
        
        return {
            'session': session.to_dict(),
            'message': '会话已中断，继续加油！'
        }
    
    @staticmethod
    def get_user_stats(user_id):
        """
        获取用户番茄钟统计
        
        Args:
            user_id: 用户ID
            
        Returns:
            dict: 统计信息
        """
        stats = PomodoroStats.query.filter_by(user_id=user_id).first()
        
        if not stats:
            # 创建初始统计
            stats = PomodoroStats(user_id=user_id)
            db.session.add(stats)
            db.session.commit()
        
        return stats.to_dict()
    
    @staticmethod
    def get_recent_sessions(user_id, days=7):
        """
        获取最近的番茄钟会话
        
        Args:
            user_id: 用户ID
            days: 天数
            
        Returns:
            list: 会话列表
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        sessions = PomodoroSession.query.filter(
            PomodoroSession.user_id == user_id,
            PomodoroSession.created_at >= start_date
        ).order_by(PomodoroSession.created_at.desc()).all()
        
        return [s.to_dict() for s in sessions]
    
    @staticmethod
    def get_daily_trend(user_id, days=30):
        """
        获取每日趋势数据
        
        Args:
            user_id: 用户ID
            days: 天数
            
        Returns:
            list: 每日统计
        """
        start_date = datetime.utcnow() - timedelta(days=days)
        
        sessions = PomodoroSession.query.filter(
            PomodoroSession.user_id == user_id,
            PomodoroSession.session_type == 'focus',
            PomodoroSession.status == 'completed',
            PomodoroSession.created_at >= start_date
        ).all()
        
        # 按日期分组统计
        daily_data = {}
        for session in sessions:
            date_key = session.created_at.date().isoformat()
            if date_key not in daily_data:
                daily_data[date_key] = {
                    'date': date_key,
                    'sessions': 0,
                    'focus_time': 0,
                    'points': 0
                }
            daily_data[date_key]['sessions'] += 1
            daily_data[date_key]['focus_time'] += session.duration
            daily_data[date_key]['points'] += session.points_earned
        
        # 填充缺失日期
        result = []
        for i in range(days):
            current_date = (datetime.utcnow() - timedelta(days=days-1-i)).date()
            date_key = current_date.isoformat()
            if date_key in daily_data:
                result.append(daily_data[date_key])
            else:
                result.append({
                    'date': date_key,
                    'sessions': 0,
                    'focus_time': 0,
                    'points': 0
                })
        
        return result
    
    @staticmethod
    def _update_stats(user_id, duration):
        """更新用户统计"""
        stats = PomodoroStats.query.filter_by(user_id=user_id).first()
        
        if not stats:
            stats = PomodoroStats(user_id=user_id)
            db.session.add(stats)
        
        today = date.today()
        
        # 检查是否是新的一天
        if stats.last_session_date != today:
            # 更新连续天数
            if stats.last_session_date == today - timedelta(days=1):
                stats.current_streak += 1
            else:
                stats.current_streak = 1
            
            if stats.current_streak > stats.longest_streak:
                stats.longest_streak = stats.current_streak
            
            # 重置今日统计
            stats.today_sessions = 0
            stats.today_focus_time = 0
            stats.last_session_date = today
        
        # 更新统计
        stats.total_sessions += 1
        stats.total_focus_time += duration
        stats.today_sessions += 1
        stats.today_focus_time += duration
        
        db.session.commit()
        
        return stats
    
    @staticmethod
    def _check_achievements(stats):
        """检查成就奖励"""
        points = 0
        achievements = []
        
        # 每日4个番茄钟
        if stats.today_sessions == 4:
            points += PomodoroService.POINTS_RULES['daily_4']
            achievements.append({
                'type': 'daily_4',
                'title': '专注达人',
                'description': '今日完成4个番茄钟',
                'points': PomodoroService.POINTS_RULES['daily_4']
            })
        
        # 每日8个番茄钟
        if stats.today_sessions == 8:
            points += PomodoroService.POINTS_RULES['daily_8']
            achievements.append({
                'type': 'daily_8',
                'title': '学习狂人',
                'description': '今日完成8个番茄钟',
                'points': PomodoroService.POINTS_RULES['daily_8']
            })
        
        # 连续7天
        if stats.current_streak == 7:
            points += PomodoroService.POINTS_RULES['streak_7']
            achievements.append({
                'type': 'streak_7',
                'title': '坚持不懈',
                'description': '连续7天使用番茄钟',
                'points': PomodoroService.POINTS_RULES['streak_7']
            })
        
        # 连续30天
        if stats.current_streak == 30:
            points += PomodoroService.POINTS_RULES['streak_30']
            achievements.append({
                'type': 'streak_30',
                'title': '习惯养成',
                'description': '连续30天使用番茄钟',
                'points': PomodoroService.POINTS_RULES['streak_30']
            })
        
        return {
            'points': points,
            'achievements': achievements
        }
