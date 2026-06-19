"""
测试学习计划改进功能

测试内容：
1. 创建包含多种目标类型的学习计划
2. 验证状态自动更新逻辑
3. 测试科目特定目标
"""

import sys
import os
import json
from datetime import datetime, date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.services.study_plan_service import StudyPlanService

def test_study_plan_improvements():
    """测试学习计划改进功能"""
    app = create_app()
    
    with app.app_context():
        print("=" * 70)
        print("学习计划改进功能测试")
        print("=" * 70)
        
        # 获取测试用户
        user = User.query.filter_by(username='student').first()
        if not user:
            user = User.query.first()
        if not user:
            print("\n❌ 没有可用的测试用户")
            return False
        
        print(f"\n✅ 使用测试用户: {user.username} (ID: {user.id})")
        
        # 测试1: 创建包含多种目标类型的计划
        print("\n" + "=" * 70)
        print("测试1: 创建包含多种目标类型的学习计划")
        print("=" * 70)
        
        today = date.today()
        end_date = today + timedelta(days=30)
        
        plan_data = {
            'name': '2024考研冲刺计划（测试）',
            'exam_type': 'postgraduate',
            'start_date': today.isoformat(),
            'end_date': end_date.isoformat(),
            'description': '测试多种目标类型',
            'goals': [
                {
                    'goal_type': 'daily_practice',
                    'target_value': 20,
                    'period_start': today.isoformat(),
                    'period_end': end_date.isoformat()
                },
                {
                    'goal_type': 'subject_daily_practice',
                    'subject': 'math',
                    'target_value': 30,
                    'period_start': today.isoformat(),
                    'period_end': end_date.isoformat()
                },
                {
                    'goal_type': 'subject_accuracy_rate',
                    'subject': 'math',
                    'target_value': 85,
                    'period_start': today.isoformat(),
                    'period_end': end_date.isoformat()
                },
                {
                    'goal_type': 'daily_duration',
                    'target_value': 120,
                    'period_start': today.isoformat(),
                    'period_end': end_date.isoformat()
                },
                {
                    'goal_type': 'exam_count',
                    'target_value': 5,
                    'period_start': today.isoformat(),
                    'period_end': end_date.isoformat()
                }
            ]
        }
        
        try:
            plan = StudyPlanService.create_plan(user.id, plan_data)
            print(f"\n✅ 计划创建成功")
            print(f"   ID: {plan.id}")
            print(f"   名称: {plan.name}")
            print(f"   状态: {plan.status}")
            print(f"   开始日期: {plan.start_date}")
            print(f"   结束日期: {plan.end_date}")
            print(f"\n   目标列表:")
            for i, goal in enumerate(plan.goals, 1):
                subject_info = f" (科目: {goal.subject})" if goal.subject else ""
                print(f"   {i}. {goal.goal_type}{subject_info}")
                print(f"      目标值: {goal.target_value}")
                print(f"      当前值: {goal.current_value}")
                print(f"      进度: {goal.current_value}/{goal.target_value} ({round((goal.current_value/goal.target_value*100) if goal.target_value > 0 else 0, 2)}%)")
        except Exception as e:
            print(f"\n❌ 创建失败: {str(e)}")
            return False
        
        # 测试2: 验证状态自动更新
        print("\n" + "=" * 70)
        print("测试2: 验证状态自动更新逻辑")
        print("=" * 70)
        
        # 创建一个已过期的计划
        past_start = today - timedelta(days=10)
        past_end = today - timedelta(days=1)
        
        past_plan_data = {
            'name': '已过期计划（测试）',
            'exam_type': 'civil_service',
            'start_date': past_start.isoformat(),
            'end_date': past_end.isoformat(),
            'goals': [
                {
                    'goal_type': 'daily_practice',
                    'target_value': 10,
                    'period_start': past_start.isoformat(),
                    'period_end': past_end.isoformat()
                }
            ]
        }
        
        try:
            past_plan = StudyPlanService.create_plan(user.id, past_plan_data)
            print(f"\n✅ 已过期计划创建成功")
            print(f"   ID: {past_plan.id}")
            print(f"   初始状态: {past_plan.status}")
            
            # 获取计划列表，触发状态更新
            plans = StudyPlanService.get_user_plans(user.id)
            
            # 重新查询计划查看状态
            db.session.refresh(past_plan)
            print(f"   更新后状态: {past_plan.status}")
            
            if past_plan.status == 'completed':
                print(f"   ✅ 状态自动更新为 'completed'（正确）")
            else:
                print(f"   ⚠️  状态未自动更新（当前: {past_plan.status}）")
        except Exception as e:
            print(f"\n❌ 测试失败: {str(e)}")
        
        # 测试3: 获取计划列表
        print("\n" + "=" * 70)
        print("测试3: 获取用户的所有学习计划")
        print("=" * 70)
        
        try:
            all_plans = StudyPlanService.get_user_plans(user.id)
            print(f"\n✅ 共找到 {len(all_plans)} 个学习计划")
            
            for plan in all_plans:
                print(f"\n   计划: {plan.name}")
                print(f"   状态: {plan.status}")
                print(f"   日期: {plan.start_date} ~ {plan.end_date}")
                print(f"   目标数: {len(plan.goals)}")
        except Exception as e:
            print(f"\n❌ 获取失败: {str(e)}")
        
        # 测试4: 按状态筛选
        print("\n" + "=" * 70)
        print("测试4: 按状态筛选计划")
        print("=" * 70)
        
        try:
            active_plans = StudyPlanService.get_user_plans(user.id, status='active')
            completed_plans = StudyPlanService.get_user_plans(user.id, status='completed')
            
            print(f"\n✅ 进行中的计划: {len(active_plans)} 个")
            for plan in active_plans:
                print(f"   - {plan.name}")
            
            print(f"\n✅ 已完成的计划: {len(completed_plans)} 个")
            for plan in completed_plans:
                print(f"   - {plan.name}")
        except Exception as e:
            print(f"\n❌ 筛选失败: {str(e)}")
        
        # 测试5: 验证目标类型
        print("\n" + "=" * 70)
        print("测试5: 验证所有新增目标类型")
        print("=" * 70)
        
        print(f"\n✅ 支持的目标类型 ({len(StudyPlanService.VALID_GOAL_TYPES)} 种):")
        
        goal_categories = {
            '练习数量': ['daily_practice', 'weekly_practice', 'monthly_practice', 
                       'subject_daily_practice', 'subject_weekly_practice'],
            '学习时长': ['daily_duration', 'weekly_duration', 'subject_daily_duration'],
            '正确率': ['accuracy_rate', 'subject_accuracy_rate'],
            '考试': ['exam_count', 'exam_score'],
            '章节': ['chapter_completion', 'subject_chapter_completion']
        }
        
        for category, types in goal_categories.items():
            print(f"\n   {category}:")
            for goal_type in types:
                status = "✅" if goal_type in StudyPlanService.VALID_GOAL_TYPES else "❌"
                print(f"      {status} {goal_type}")
        
        print("\n" + "=" * 70)
        print("✅ 所有测试完成！")
        print("=" * 70)
        
        return True

if __name__ == '__main__':
    success = test_study_plan_improvements()
    sys.exit(0 if success else 1)
