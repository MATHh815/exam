"""验证数据库索引

检查所有表的索引是否正确创建
"""
from app import create_app, db
from sqlalchemy import inspect

def verify_indexes():
    """验证数据库索引"""
    app = create_app()
    
    with app.app_context():
        inspector = inspect(db.engine)
        
        # 需要检查的表和预期索引
        expected_indexes = {
            'study_plans': ['user_id', 'status', 'is_deleted'],
            'study_goals': ['plan_id', 'is_completed'],
            'study_reminders': ['plan_id', 'is_enabled'],  # 字段名是 is_enabled 不是 is_active
            'question_notes': ['user_id', 'question_id', 'is_deleted'],
            'question_bookmarks': ['user_id', 'question_id'],
            'achievements': ['category', 'tier'],  # 字段名是 tier 不是 level
            'user_achievements': ['user_id', 'achievement_id', 'unlocked_at'],  # 字段名是 unlocked_at 不是 earned_at
            'user_points': ['user_id', 'current_level'],
            'point_transactions': ['user_id', 'created_at'],
            'daily_tasks': ['user_id', 'task_date', 'is_completed'],  # 字段名是 task_date 不是 date
            'questions': ['exam_type', 'question_type', 'subject', 'difficulty'],
            'practice_records': ['user_id', 'question_id', 'created_at'],
            'exam_results': ['user_id', 'paper_id', 'created_at'],
            'wrong_questions': ['user_id', 'question_id', 'mastered']
        }
        
        print("=" * 80)
        print("数据库索引验证报告")
        print("=" * 80)
        print()
        
        all_good = True
        
        for table_name, expected_cols in expected_indexes.items():
            print(f"表: {table_name}")
            print("-" * 80)
            
            # 获取表的所有索引
            indexes = inspector.get_indexes(table_name)
            
            if not indexes:
                print(f"  ⚠️  警告: 没有找到索引")
                all_good = False
            else:
                print(f"  ✓ 找到 {len(indexes)} 个索引:")
                for idx in indexes:
                    cols = ', '.join(idx['column_names'])
                    unique = " (UNIQUE)" if idx.get('unique') else ""
                    print(f"    - {idx['name']}: {cols}{unique}")
                
                # 检查预期的列是否有索引
                indexed_columns = set()
                for idx in indexes:
                    indexed_columns.update(idx['column_names'])
                
                missing_indexes = set(expected_cols) - indexed_columns
                if missing_indexes:
                    print(f"  ⚠️  缺少索引的列: {', '.join(missing_indexes)}")
                    all_good = False
                else:
                    print(f"  ✓ 所有预期列都有索引")
            
            print()
        
        print("=" * 80)
        if all_good:
            print("✓ 所有索引验证通过")
        else:
            print("⚠️  发现一些索引问题，建议优化")
        print("=" * 80)

if __name__ == '__main__':
    verify_indexes()
