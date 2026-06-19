"""验证第一阶段数据库迁移

此脚本用于验证所有新表是否正确创建
"""
from app import create_app, db
from sqlalchemy import inspect

def verify_migration():
    """验证迁移是否成功"""
    print("=" * 60)
    print("验证第一阶段数据库迁移")
    print("=" * 60)
    print()
    
    app = create_app()
    
    with app.app_context():
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        # 需要检查的表
        required_tables = {
            'study_plans': '学习计划',
            'study_goals': '学习目标',
            'study_reminders': '学习提醒',
            'question_notes': '题目笔记',
            'question_bookmarks': '题目收藏',
            'achievements': '成就定义',
            'user_achievements': '用户成就',
            'user_points': '用户积分',
            'point_transactions': '积分交易记录',
            'daily_tasks': '每日任务'
        }
        
        print("检查表是否存在:")
        print("-" * 60)
        
        all_exist = True
        for table_name, description in required_tables.items():
            exists = table_name in existing_tables
            status = "✓" if exists else "✗"
            print(f"{status} {table_name:25} ({description})")
            if not exists:
                all_exist = False
        
        print()
        
        if all_exist:
            print("=" * 60)
            print("✓ 所有表都已成功创建！")
            print("=" * 60)
            print()
            
            # 检查索引
            print("检查关键索引:")
            print("-" * 60)
            
            # 检查 study_plans 表的索引
            indexes = inspector.get_indexes('study_plans')
            has_user_id_index = any('user_id' in idx['column_names'] for idx in indexes)
            has_is_deleted_index = any('is_deleted' in idx['column_names'] for idx in indexes)
            
            print(f"{'✓' if has_user_id_index else '✗'} study_plans.user_id 索引")
            print(f"{'✓' if has_is_deleted_index else '✗'} study_plans.is_deleted 索引")
            
            # 检查 question_notes 表的复合索引
            indexes = inspector.get_indexes('question_notes')
            has_composite_index = any(
                set(idx['column_names']) == {'user_id', 'question_id'} 
                for idx in indexes
            )
            print(f"{'✓' if has_composite_index else '✗'} question_notes (user_id, question_id) 复合索引")
            
            # 检查唯一约束
            print()
            print("检查唯一约束:")
            print("-" * 60)
            
            # 检查 question_bookmarks 的唯一约束
            unique_constraints = inspector.get_unique_constraints('question_bookmarks')
            has_bookmark_constraint = any(
                set(uc['column_names']) == {'user_id', 'question_id'}
                for uc in unique_constraints
            )
            print(f"{'✓' if has_bookmark_constraint else '✗'} question_bookmarks (user_id, question_id) 唯一约束")
            
            # 检查 user_achievements 的唯一约束
            unique_constraints = inspector.get_unique_constraints('user_achievements')
            has_achievement_constraint = any(
                set(uc['column_names']) == {'user_id', 'achievement_id'}
                for uc in unique_constraints
            )
            print(f"{'✓' if has_achievement_constraint else '✗'} user_achievements (user_id, achievement_id) 唯一约束")
            
            # 检查 daily_tasks 的唯一约束
            unique_constraints = inspector.get_unique_constraints('daily_tasks')
            has_task_constraint = any(
                set(uc['column_names']) == {'user_id', 'task_date', 'task_type'}
                for uc in unique_constraints
            )
            print(f"{'✓' if has_task_constraint else '✗'} daily_tasks (user_id, task_date, task_type) 唯一约束")
            
            print()
            print("迁移验证完成！可以继续下一步开发。")
            return True
        else:
            print("=" * 60)
            print("✗ 部分表未创建，请检查迁移脚本")
            print("=" * 60)
            return False

if __name__ == '__main__':
    verify_migration()
