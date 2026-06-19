"""诊断成就API错误的脚本"""
import sys
import traceback
from app import create_app, db

def diagnose():
    """诊断成就API问题"""
    print("=" * 60)
    print("诊断成就API问题")
    print("=" * 60)
    print()
    
    app = create_app()
    
    with app.app_context():
        try:
            print("1. 检查数据库表...")
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            required_tables = [
                'achievements',
                'user_achievements',
                'user_points',
                'question_notes',
                'question_bookmarks',
                'study_plans',
                'practice_records',
                'exam_sessions'
            ]
            
            for table in required_tables:
                if table in tables:
                    print(f"  ✓ {table} 存在")
                else:
                    print(f"  ✗ {table} 不存在")
            
            print()
            print("2. 测试导入模型...")
            
            try:
                from app.models.achievement import Achievement, UserAchievement, UserPoints
                print("  ✓ Achievement 模型导入成功")
            except Exception as e:
                print(f"  ✗ Achievement 模型导入失败: {e}")
            
            try:
                from app.models.practice import PracticeRecord
                print("  ✓ PracticeRecord 模型导入成功")
            except Exception as e:
                print(f"  ✗ PracticeRecord 模型导入失败: {e}")
            
            try:
                from app.models.exam import ExamSession
                print("  ✓ ExamSession 模型导入成功")
            except Exception as e:
                print(f"  ✗ ExamSession 模型导入失败: {e}")
            
            print()
            print("3. 测试成就服务...")
            
            try:
                from app.services.achievement_service import AchievementService
                print("  ✓ AchievementService 导入成功")
                
                # 测试获取所有成就
                achievements = AchievementService.get_all_achievements()
                print(f"  ✓ 获取所有成就成功，共 {len(achievements)} 个")
                
                # 测试获取用户成就（使用测试用户ID 1）
                user_achievements = AchievementService.get_user_achievements(1)
                print(f"  ✓ 获取用户成就成功")
                print(f"    - 已解锁: {user_achievements['earned_count']}")
                print(f"    - 进行中: {user_achievements['in_progress_count']}")
                print(f"    - 未开始: {user_achievements['locked_count']}")
                
            except Exception as e:
                print(f"  ✗ 成就服务测试失败:")
                print(f"    错误: {e}")
                traceback.print_exc()
            
            print()
            print("=" * 60)
            print("诊断完成")
            print("=" * 60)
            
        except Exception as e:
            print(f"✗ 诊断失败: {e}")
            traceback.print_exc()
            return False
    
    return True

if __name__ == '__main__':
    try:
        diagnose()
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        traceback.print_exc()
        sys.exit(1)
