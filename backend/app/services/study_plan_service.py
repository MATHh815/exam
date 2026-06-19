"""学习计划服务模块"""
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
from sqlalchemy import and_, or_
from app import db
from app.models.study_plan import StudyPlan, StudyGoal, StudyReminder
from app.models.practice import PracticeRecord
from app.models.exam import ExamResult


class StudyPlanService:
    """学习计划服务类
    
    提供学习计划的创建、更新、查询、进度追踪和报告生成等功能
    """
    
    # 有效的目标类型
    VALID_GOAL_TYPES = [
        # 练习数量类
        'daily_practice',           # 每日练习题数
        'weekly_practice',          # 每周练习题数
        'monthly_practice',         # 每月练习题数
        'subject_daily_practice',   # 科目每日练习题数
        'subject_weekly_practice',  # 科目每周练习题数
        
        # 学习时长类
        'daily_duration',           # 每日学习时长（分钟）
        'weekly_duration',          # 每周学习时长（分钟）
        'subject_daily_duration',   # 科目每日学习时长
        
        # 正确率类
        'accuracy_rate',            # 总体正确率（百分比）
        'subject_accuracy_rate',    # 科目正确率
        
        # 考试类
        'exam_count',               # 考试次数
        'exam_score',               # 考试目标分数
        
        # 章节类
        'chapter_completion',       # 章节完成数
        'subject_chapter_completion', # 科目章节完成数
    ]
    
    # 有效的计划状态
    VALID_STATUSES = ['active', 'completed', 'paused']
    
    # 需要科目的目标类型
    SUBJECT_REQUIRED_TYPES = [
        'subject_daily_practice',
        'subject_weekly_practice',
        'subject_daily_duration',
        'subject_accuracy_rate',
        'subject_chapter_completion'
    ]
    
    @staticmethod
    def create_plan(user_id: int, plan_data: dict) -> StudyPlan:
        """创建学习计划
        
        Args:
            user_id: 用户ID
            plan_data: 计划数据
                - name: 计划名称（必填）
                - description: 计划描述
                - exam_type: 考试类型（必填）
                - start_date: 开始日期（必填，格式：YYYY-MM-DD）
                - end_date: 结束日期（必填，格式：YYYY-MM-DD）
                - goals: 目标列表（可选）
                    - goal_type: 目标类型
                    - target_value: 目标值
                    - period_start: 周期开始日期
                    - period_end: 周期结束日期
        
        Returns:
            StudyPlan: 创建的学习计划
        
        Raises:
            ValueError: 数据验证失败
        """
        # 验证必填字段
        if not plan_data.get('name'):
            raise ValueError('计划名称不能为空')
        if not plan_data.get('exam_type'):
            raise ValueError('考试类型不能为空')
        if not plan_data.get('start_date'):
            raise ValueError('开始日期不能为空')
        if not plan_data.get('end_date'):
            raise ValueError('结束日期不能为空')
        
        # 验证名称长度
        if len(plan_data['name']) > 200:
            raise ValueError('计划名称长度不能超过200个字符')
        
        # 解析日期
        try:
            start_date = datetime.strptime(plan_data['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(plan_data['end_date'], '%Y-%m-%d').date()
        except ValueError:
            raise ValueError('日期格式错误，应为 YYYY-MM-DD')
        
        # 验证日期逻辑
        if end_date < start_date:
            raise ValueError('结束日期不能早于开始日期')
        
        # 创建学习计划
        plan = StudyPlan(
            user_id=user_id,
            name=plan_data['name'],
            description=plan_data.get('description', ''),
            exam_type=plan_data['exam_type'],
            start_date=start_date,
            end_date=end_date,
            status='active'
        )
        
        db.session.add(plan)
        db.session.flush()  # 获取 plan.id
        
        # 创建目标
        if 'goals' in plan_data and plan_data['goals']:
            for goal_data in plan_data['goals']:
                goal = StudyPlanService._create_goal(plan.id, goal_data)
                db.session.add(goal)
        
        db.session.commit()
        return plan
    
    @staticmethod
    def _create_goal(plan_id: int, goal_data: dict) -> StudyGoal:
        """创建学习目标（内部方法）
        
        Args:
            plan_id: 计划ID
            goal_data: 目标数据
        
        Returns:
            StudyGoal: 创建的目标
        
        Raises:
            ValueError: 数据验证失败
        """
        # 验证目标类型
        goal_type = goal_data.get('goal_type')
        if goal_type not in StudyPlanService.VALID_GOAL_TYPES:
            raise ValueError(f'无效的目标类型: {goal_type}')
        
        # 验证科目（如果需要）
        subject = goal_data.get('subject')
        if goal_type in StudyPlanService.SUBJECT_REQUIRED_TYPES:
            if not subject:
                raise ValueError(f'目标类型 {goal_type} 需要指定科目')
        
        # 验证目标值
        target_value = goal_data.get('target_value')
        if not isinstance(target_value, int) or target_value <= 0:
            raise ValueError('目标值必须是正整数')
        
        # 根据目标类型验证范围
        if 'practice' in goal_type and not (1 <= target_value <= 1000):
            raise ValueError('练习题目数量必须在 1-1000 之间')
        elif 'duration' in goal_type and not (5 <= target_value <= 1440):
            raise ValueError('学习时长必须在 5-1440 分钟之间')
        elif 'accuracy' in goal_type and not (1 <= target_value <= 100):
            raise ValueError('正确率必须在 1-100 之间')
        elif goal_type == 'exam_score' and not (0 <= target_value <= 150):
            raise ValueError('考试分数必须在 0-150 之间')
        
        # 解析日期
        try:
            period_start = datetime.strptime(goal_data['period_start'], '%Y-%m-%d').date()
            period_end = datetime.strptime(goal_data['period_end'], '%Y-%m-%d').date()
        except (ValueError, KeyError):
            raise ValueError('目标周期日期格式错误或缺失')
        
        return StudyGoal(
            plan_id=plan_id,
            goal_type=goal_type,
            subject=subject,
            target_value=target_value,
            current_value=0,
            period_start=period_start,
            period_end=period_end,
            is_completed=False
        )
    
    @staticmethod
    def update_plan(plan_id: int, user_id: int, plan_data: dict) -> StudyPlan:
        """更新学习计划
        
        Args:
            plan_id: 计划ID
            user_id: 用户ID
            plan_data: 更新的数据
        
        Returns:
            StudyPlan: 更新后的计划
        
        Raises:
            ValueError: 计划不存在或无权限
        """
        plan = StudyPlan.query.filter_by(
            id=plan_id,
            user_id=user_id,
            is_deleted=False
        ).first()
        
        if not plan:
            raise ValueError('学习计划不存在或无权限访问')
        
        # 更新基本信息（不影响进度数据）
        if 'name' in plan_data:
            if not plan_data['name']:
                raise ValueError('计划名称不能为空')
            if len(plan_data['name']) > 200:
                raise ValueError('计划名称长度不能超过200个字符')
            plan.name = plan_data['name']
        
        if 'description' in plan_data:
            plan.description = plan_data['description']
        
        if 'status' in plan_data:
            if plan_data['status'] not in StudyPlanService.VALID_STATUSES:
                raise ValueError(f'无效的状态: {plan_data["status"]}')
            plan.status = plan_data['status']
        
        if 'end_date' in plan_data:
            try:
                end_date = datetime.strptime(plan_data['end_date'], '%Y-%m-%d').date()
                if end_date < plan.start_date:
                    raise ValueError('结束日期不能早于开始日期')
                plan.end_date = end_date
            except ValueError as e:
                raise ValueError(f'日期格式错误: {str(e)}')
        
        plan.updated_at = datetime.utcnow()
        db.session.commit()
        
        return plan
    
    @staticmethod
    def get_user_plans(user_id: int, status: Optional[str] = None) -> List[StudyPlan]:
        """获取用户的学习计划列表
        
        Args:
            user_id: 用户ID
            status: 状态筛选（可选）
        
        Returns:
            List[StudyPlan]: 学习计划列表
        """
        query = StudyPlan.query.filter_by(
            user_id=user_id,
            is_deleted=False
        )
        
        plans = query.order_by(StudyPlan.created_at.desc()).all()
        
        # 自动更新计划状态
        for plan in plans:
            StudyPlanService._update_plan_status(plan)
        
        # 如果指定了状态筛选，在更新后再过滤
        if status:
            plans = [p for p in plans if p.status == status]
        
        return plans
    
    @staticmethod
    def _update_plan_status(plan: StudyPlan) -> None:
        """自动更新计划状态（内部方法）
        
        根据日期和目标完成情况自动更新计划状态
        
        Args:
            plan: 学习计划对象
        """
        if plan.status == 'paused':
            # 暂停状态不自动更新
            return
        
        today = date.today()
        
        # 检查是否所有目标都已完成
        all_goals_completed = all(goal.is_completed for goal in plan.goals) if plan.goals else False
        
        # 状态判断逻辑
        if today > plan.end_date or all_goals_completed:
            # 已过结束日期或所有目标完成 -> completed
            if plan.status != 'completed':
                plan.status = 'completed'
                plan.updated_at = datetime.utcnow()
                db.session.commit()
        elif plan.start_date <= today <= plan.end_date:
            # 在计划期间内 -> active
            if plan.status != 'active':
                plan.status = 'active'
                plan.updated_at = datetime.utcnow()
                db.session.commit()
    
    @staticmethod
    def get_plan_by_id(plan_id: int, user_id: int) -> Optional[StudyPlan]:
        """获取学习计划详情
        
        Args:
            plan_id: 计划ID
            user_id: 用户ID
        
        Returns:
            StudyPlan: 学习计划，如果不存在返回 None
        """
        plan = StudyPlan.query.filter_by(
            id=plan_id,
            user_id=user_id,
            is_deleted=False
        ).first()
        
        return plan
    
    @staticmethod
    def delete_plan(plan_id: int, user_id: int) -> bool:
        """删除学习计划（软删除）
        
        Args:
            plan_id: 计划ID
            user_id: 用户ID
        
        Returns:
            bool: 是否成功删除
        
        Raises:
            ValueError: 计划不存在或无权限
        """
        plan = StudyPlan.query.filter_by(
            id=plan_id,
            user_id=user_id,
            is_deleted=False
        ).first()
        
        if not plan:
            raise ValueError('学习计划不存在或无权限访问')
        
        # 软删除
        plan.is_deleted = True
        plan.updated_at = datetime.utcnow()
        db.session.commit()
        
        return True
    
    @staticmethod
    def update_progress(plan_id: int, user_id: int, goal_type: str, increment: int = 1) -> List[StudyGoal]:
        """更新学习进度
        
        Args:
            plan_id: 计划ID
            user_id: 用户ID
            goal_type: 目标类型
            increment: 增量（默认为1）
        
        Returns:
            List[StudyGoal]: 更新后的目标列表
        
        Raises:
            ValueError: 计划不存在或目标不存在
        """
        plan = StudyPlan.query.filter_by(
            id=plan_id,
            user_id=user_id,
            is_deleted=False,
            status='active'
        ).first()
        
        if not plan:
            raise ValueError('学习计划不存在或未激活')
        
        # 查找当前周期的目标
        today = date.today()
        goals = StudyGoal.query.filter(
            StudyGoal.plan_id == plan_id,
            StudyGoal.goal_type == goal_type,
            StudyGoal.period_start <= today,
            StudyGoal.period_end >= today,
            StudyGoal.is_completed == False
        ).all()
        
        if not goals:
            # 没有找到匹配的目标，返回空列表
            return []
        
        # 更新所有匹配的目标
        for goal in goals:
            goal.current_value += increment
            
            # 检查是否完成
            if goal.current_value >= goal.target_value:
                goal.is_completed = True
            
            goal.updated_at = datetime.utcnow()
        
        plan.updated_at = datetime.utcnow()
        db.session.commit()
        
        return goals
    
    @staticmethod
    def generate_report(plan_id: int, user_id: int) -> dict:
        """生成学习报告
        
        Args:
            plan_id: 计划ID
            user_id: 用户ID
        
        Returns:
            dict: 学习报告数据
        
        Raises:
            ValueError: 计划不存在
        """
        plan = StudyPlan.query.filter_by(
            id=plan_id,
            user_id=user_id,
            is_deleted=False
        ).first()
        
        if not plan:
            raise ValueError('学习计划不存在')
        
        # 获取所有目标
        goals = StudyGoal.query.filter_by(plan_id=plan_id).all()
        
        # 计算总体进度
        total_goals = len(goals)
        completed_goals = sum(1 for g in goals if g.is_completed)
        completion_rate = (completed_goals / total_goals * 100) if total_goals > 0 else 0
        
        # 获取练习记录统计
        practice_stats = StudyPlanService._get_practice_stats(
            user_id,
            plan.start_date,
            plan.end_date
        )
        
        # 获取考试记录统计
        exam_stats = StudyPlanService._get_exam_stats(
            user_id,
            plan.start_date,
            plan.end_date
        )
        
        # 计算学习天数
        today = date.today()
        end_date = min(plan.end_date, today)
        study_days = (end_date - plan.start_date).days + 1
        
        # 构建报告
        report = {
            'plan': {
                'id': plan.id,
                'name': plan.name,
                'exam_type': plan.exam_type,
                'start_date': plan.start_date.isoformat(),
                'end_date': plan.end_date.isoformat(),
                'status': plan.status,
                'study_days': study_days
            },
            'progress': {
                'total_goals': total_goals,
                'completed_goals': completed_goals,
                'completion_rate': round(completion_rate, 2),
                'goals': [
                    {
                        'goal_type': g.goal_type,
                        'target_value': g.target_value,
                        'current_value': g.current_value,
                        'progress_percentage': round((g.current_value / g.target_value * 100) if g.target_value > 0 else 0, 2),
                        'is_completed': g.is_completed,
                        'period': f"{g.period_start.isoformat()} ~ {g.period_end.isoformat()}"
                    }
                    for g in goals
                ]
            },
            'practice': practice_stats,
            'exam': exam_stats
        }
        
        return report
    
    @staticmethod
    def _get_practice_stats(user_id: int, start_date: date, end_date: date) -> dict:
        """获取练习统计（内部方法）
        
        Args:
            user_id: 用户ID
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            dict: 练习统计数据
        """
        records = PracticeRecord.query.filter(
            PracticeRecord.user_id == user_id,
            PracticeRecord.created_at >= datetime.combine(start_date, datetime.min.time()),
            PracticeRecord.created_at <= datetime.combine(end_date, datetime.max.time())
        ).all()
        
        total_count = len(records)
        correct_count = sum(1 for r in records if r.is_correct)
        correct_rate = (correct_count / total_count * 100) if total_count > 0 else 0
        total_time = sum(r.time_spent for r in records if r.time_spent)
        
        return {
            'total_count': total_count,
            'correct_count': correct_count,
            'wrong_count': total_count - correct_count,
            'correct_rate': round(correct_rate, 2),
            'total_time_minutes': round(total_time / 60, 2) if total_time else 0
        }
    
    @staticmethod
    def _get_exam_stats(user_id: int, start_date: date, end_date: date) -> dict:
        """获取考试统计（内部方法）
        
        Args:
            user_id: 用户ID
            start_date: 开始日期
            end_date: 结束日期
        
        Returns:
            dict: 考试统计数据
        """
        results = ExamResult.query.filter(
            ExamResult.user_id == user_id,
            ExamResult.created_at >= datetime.combine(start_date, datetime.min.time()),
            ExamResult.created_at <= datetime.combine(end_date, datetime.max.time())
        ).all()
        
        total_count = len(results)
        total_score = sum(r.score for r in results if r.score is not None)
        avg_score = (total_score / total_count) if total_count > 0 else 0
        
        return {
            'total_count': total_count,
            'total_score': total_score,
            'average_score': round(avg_score, 2)
        }

    @staticmethod
    def auto_update_progress_on_practice(user_id: int) -> List[StudyGoal]:
        """练习完成时自动更新进度
        
        当用户完成一次练习时调用此方法，自动更新所有匹配的学习目标进度。
        
        Args:
            user_id: 用户ID
        
        Returns:
            List[StudyGoal]: 更新的目标列表
        
        Raises:
            ValueError: 用户ID无效
        """
        if not user_id:
            raise ValueError('用户ID不能为空')
        
        today = date.today()
        
        # 查找所有活跃的、匹配今天日期的 daily_practice 目标
        goals = StudyGoal.query.join(StudyPlan).filter(
            StudyPlan.user_id == user_id,
            StudyPlan.is_deleted == False,
            StudyPlan.status == 'active',
            StudyGoal.goal_type == 'daily_practice',
            StudyGoal.period_start <= today,
            StudyGoal.period_end >= today,
            StudyGoal.is_completed == False
        ).all()
        
        updated_goals = []
        for goal in goals:
            # 增加当前值
            goal.current_value += 1
            
            # 检查是否完成
            if goal.current_value >= goal.target_value:
                goal.is_completed = True
                goal.completed_at = datetime.utcnow()
                
                # TODO: 触发积分奖励（在积分系统实现后集成）
                # PointsService.award_points(user_id, 'goal_completed', goal.id)
            
            updated_goals.append(goal)
        
        if updated_goals:
            db.session.commit()
        
        return updated_goals
    
    @staticmethod
    def auto_update_progress_on_exam(user_id: int) -> List[StudyGoal]:
        """考试完成时自动更新进度
        
        当用户完成一次考试时调用此方法，自动更新所有匹配的学习目标进度。
        
        Args:
            user_id: 用户ID
        
        Returns:
            List[StudyGoal]: 更新的目标列表
        
        Raises:
            ValueError: 用户ID无效
        """
        if not user_id:
            raise ValueError('用户ID不能为空')
        
        today = date.today()
        
        # 查找所有活跃的、匹配今天日期的 exam_count 目标
        goals = StudyGoal.query.join(StudyPlan).filter(
            StudyPlan.user_id == user_id,
            StudyPlan.is_deleted == False,
            StudyPlan.status == 'active',
            StudyGoal.goal_type == 'exam_count',
            StudyGoal.period_start <= today,
            StudyGoal.period_end >= today,
            StudyGoal.is_completed == False
        ).all()
        
        updated_goals = []
        for goal in goals:
            # 增加当前值
            goal.current_value += 1
            
            # 检查是否完成
            if goal.current_value >= goal.target_value:
                goal.is_completed = True
                goal.completed_at = datetime.utcnow()
                
                # TODO: 触发积分奖励（在积分系统实现后集成）
                # PointsService.award_points(user_id, 'goal_completed', goal.id)
            
            updated_goals.append(goal)
        
        if updated_goals:
            db.session.commit()
        
        return updated_goals
    
    @staticmethod
    def auto_update_progress_on_study_duration(user_id: int, duration_minutes: int) -> List[StudyGoal]:
        """学习时长累计时自动更新进度
        
        当用户累计学习时长时调用此方法，自动更新所有匹配的学习目标进度。
        
        Args:
            user_id: 用户ID
            duration_minutes: 学习时长（分钟）
        
        Returns:
            List[StudyGoal]: 更新的目标列表
        
        Raises:
            ValueError: 参数无效
        """
        if not user_id:
            raise ValueError('用户ID不能为空')
        if duration_minutes <= 0:
            raise ValueError('学习时长必须大于0')
        
        today = date.today()
        
        # 查找所有活跃的、匹配今天日期的 daily_duration 目标
        goals = StudyGoal.query.join(StudyPlan).filter(
            StudyPlan.user_id == user_id,
            StudyPlan.is_deleted == False,
            StudyPlan.status == 'active',
            StudyGoal.goal_type == 'daily_duration',
            StudyGoal.period_start <= today,
            StudyGoal.period_end >= today,
            StudyGoal.is_completed == False
        ).all()
        
        updated_goals = []
        for goal in goals:
            # 增加当前值
            goal.current_value += duration_minutes
            
            # 检查是否完成
            if goal.current_value >= goal.target_value:
                goal.is_completed = True
                goal.completed_at = datetime.utcnow()
                
                # TODO: 触发积分奖励（在积分系统实现后集成）
                # PointsService.award_points(user_id, 'goal_completed', goal.id)
            
            updated_goals.append(goal)
        
        if updated_goals:
            db.session.commit()
        
        return updated_goals
