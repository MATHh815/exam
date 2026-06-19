"""学习日程表迁移脚本

创建 study_schedules 表
"""
import sys
from datetime import datetime
from app import create_app, db
from app.models.study_schedule import StudySchedule

def migrate():
    """执行迁移"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("学习日程表迁移")
        print("=" * 60)
        
        try:
            # 检查表是否已存在
            inspector = db.inspect(db.engine)
            if 'study_schedules' in inspector.get_table_names():
                print("\n⚠️  study_schedules 表已存在")
                response = input("是否要删除并重新创建？(yes/no): ")
                if response.lower() != 'yes':
                    print("❌ 迁移已取消")
                    return
                
                print("\n🗑️  删除现有表...")
                StudySchedule.__table__.drop(db.engine)
                print("✅ 表已删除")
            
            # 创建表
            print("\n📝 创建 study_schedules 表...")
            StudySchedule.__table__.create(db.engine)
            print("✅ 表创建成功")
            
            # 验证表结构
            print("\n🔍 验证表结构...")
            columns = inspector.get_columns('study_schedules')
            print(f"✅ 表包含 {len(columns)} 个字段:")
            for col in columns:
                print(f"   - {col['name']}: {col['type']}")
            
            # 验证索引
            indexes = inspector.get_indexes('study_schedules')
            print(f"\n✅ 表包含 {len(indexes)} 个索引:")
            for idx in indexes:
                print(f"   - {idx['name']}: {idx['column_names']}")
            
            print("\n" + "=" * 60)
            print("✅ 迁移完成！")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n❌ 迁移失败: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    migrate()
