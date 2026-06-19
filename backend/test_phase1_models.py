"""测试第一阶段模型导入

此脚本用于测试所有新模型是否可以正确导入
"""
import sys

def test_model_imports():
    """测试模型导入"""
    print("=" * 60)
    print("测试第一阶段模型导入")
    print("=" * 60)
    print()
    
    errors = []
    
    # 测试学习计划模型
    print("测试学习计划模型...")
    try:
        from app.models.study_plan import StudyPlan, StudyGoal, StudyReminder
        print("  ✓ StudyPlan")
        print("  ✓ StudyGoal")
        print("  ✓ StudyReminder")
    except Exception as e:
        print(f"  ✗ 导入失败: {e}")
        errors.append(f"study_plan: {e}")
    
    # 测试笔记模型
    print("\n测试笔记模型...")
    try:
        from app.models.note import QuestionNote, QuestionBookmark
        print("  ✓ QuestionNote")
        print("  ✓ QuestionBookmark")
    except Exception as e:
        print(f"  ✗ 导入失败: {e}")
        errors.append(f"note: {e}")
    
    # 测试成就模型
    print("\n测试成就模型...")
    try:
        from app.models.achievement import (
            Achievement, UserAchievement, UserPoints, 
            PointTransaction, DailyTask
        )
        print("  ✓ Achievement")
        print("  ✓ UserAchievement")
        print("  ✓ UserPoints")
        print("  ✓ PointTransaction")
        print("  ✓ DailyTask")
    except Exception as e:
        print(f"  ✗ 导入失败: {e}")
        errors.append(f"achievement: {e}")
    
    # 测试从 __init__ 导入
    print("\n测试从 models 包导入...")
    try:
        from app.models import (
            StudyPlan, StudyGoal, StudyReminder,
            QuestionNote, QuestionBookmark,
            Achievement, UserAchievement, UserPoints, 
            PointTransaction, DailyTask
        )
        print("  ✓ 所有模型都可以从 app.models 导入")
    except Exception as e:
        print(f"  ✗ 导入失败: {e}")
        errors.append(f"models.__init__: {e}")
    
    # 测试模型方法
    print("\n测试模型方法...")
    try:
        from app.models import StudyPlan
        
        # 测试 to_dict 方法
        plan = StudyPlan()
        plan.id = 1
        plan.user_id = 1
        plan.name = "测试计划"
        plan.exam_type = "公务员"
        
        data = plan.to_dict()
        assert 'id' in data
        assert 'name' in data
        assert data['name'] == "测试计划"
        print("  ✓ StudyPlan.to_dict() 方法正常")
        
    except Exception as e:
        print(f"  ✗ 方法测试失败: {e}")
        errors.append(f"method test: {e}")
    
    print()
    print("=" * 60)
    
    if errors:
        print("✗ 测试失败，发现以下错误:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("✓ 所有测试通过！")
        print()
        print("下一步:")
        print("  1. 运行 migrate_phase1.bat 执行数据库迁移")
        print("  2. 运行 verify_phase1_migration.py 验证迁移")
        return True

if __name__ == '__main__':
    success = test_model_imports()
    sys.exit(0 if success else 1)
