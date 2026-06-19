"""添加数据库索引迁移脚本

为Phase 1的表添加性能优化索引
"""
from app import create_app, db
from sqlalchemy import text

def add_indexes():
    """添加数据库索引"""
    app = create_app()
    
    with app.app_context():
        print("=" * 80)
        print("开始添加数据库索引...")
        print("=" * 80)
        print()
        
        # 定义需要添加的索引
        indexes = [
            # study_plans 表
            ("idx_study_plans_status", "study_plans", "status"),
            
            # study_goals 表
            ("idx_study_goals_is_completed", "study_goals", "is_completed"),
            
            # study_reminders 表
            ("idx_study_reminders_plan_id", "study_reminders", "plan_id"),
            ("idx_study_reminders_is_enabled", "study_reminders", "is_enabled"),
            
            # question_notes 表
            ("idx_question_notes_is_deleted", "question_notes", "is_deleted"),
            
            # achievements 表
            ("idx_achievements_category", "achievements", "category"),
            ("idx_achievements_tier", "achievements", "tier"),
            
            # user_achievements 表
            ("idx_user_achievements_unlocked_at", "user_achievements", "unlocked_at"),
            
            # user_points 表
            ("idx_user_points_current_level", "user_points", "current_level"),
            
            # daily_tasks 表
            ("idx_daily_tasks_is_completed", "daily_tasks", "is_completed"),
            
            # questions 表
            ("idx_questions_difficulty", "questions", "difficulty"),
            
            # exam_results 表
            ("idx_exam_results_created_at", "exam_results", "created_at"),
        ]
        
        success_count = 0
        skip_count = 0
        error_count = 0
        
        for index_name, table_name, column_name in indexes:
            try:
                # 检查索引是否已存在
                check_sql = text(f"""
                    SELECT name FROM sqlite_master 
                    WHERE type='index' AND name=:index_name
                """)
                result = db.session.execute(check_sql, {"index_name": index_name}).fetchone()
                
                if result:
                    print(f"⏭️  跳过: {index_name} (已存在)")
                    skip_count += 1
                    continue
                
                # 创建索引
                create_sql = text(f"CREATE INDEX {index_name} ON {table_name}({column_name})")
                db.session.execute(create_sql)
                db.session.commit()
                
                print(f"✓ 创建索引: {index_name} ON {table_name}({column_name})")
                success_count += 1
                
            except Exception as e:
                print(f"✗ 创建索引失败: {index_name} - {str(e)}")
                error_count += 1
                db.session.rollback()
        
        print()
        print("=" * 80)
        print(f"索引添加完成:")
        print(f"  ✓ 成功: {success_count}")
        print(f"  ⏭️  跳过: {skip_count}")
        print(f"  ✗ 失败: {error_count}")
        print("=" * 80)
        
        if error_count == 0:
            print("\n✓ 所有索引添加成功！")
        else:
            print(f"\n⚠️  有 {error_count} 个索引添加失败，请检查错误信息")

if __name__ == '__main__':
    add_indexes()
