"""添加收藏备注字段的迁移脚本

此脚本为 question_bookmarks 表添加 notes 和 updated_at 字段
"""
from app import create_app, db
from sqlalchemy import text

def migrate():
    """执行迁移"""
    print("=" * 60)
    print("添加收藏备注字段")
    print("=" * 60)
    print()
    
    app = create_app()
    
    with app.app_context():
        try:
            # 检查表是否存在
            inspector = db.inspect(db.engine)
            if 'question_bookmarks' not in inspector.get_table_names():
                print("✗ 错误: question_bookmarks 表不存在")
                print("  请先运行 migrate_phase1.py 创建表")
                return False
            
            # 获取现有列
            columns = [col['name'] for col in inspector.get_columns('question_bookmarks')]
            print(f"当前列: {', '.join(columns)}")
            print()
            
            # 添加 notes 字段
            if 'notes' not in columns:
                print("添加 notes 字段...")
                db.session.execute(text(
                    "ALTER TABLE question_bookmarks ADD COLUMN notes TEXT"
                ))
                print("✓ notes 字段添加成功")
            else:
                print("⏭️  notes 字段已存在，跳过")
            
            # 添加 updated_at 字段
            if 'updated_at' not in columns:
                print("添加 updated_at 字段...")
                db.session.execute(text(
                    "ALTER TABLE question_bookmarks ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP"
                ))
                print("✓ updated_at 字段添加成功")
            else:
                print("⏭️  updated_at 字段已存在，跳过")
            
            db.session.commit()
            
            print()
            print("=" * 60)
            print("迁移完成！")
            print("=" * 60)
            print()
            print("新增字段:")
            print("  ✓ notes (TEXT) - 收藏备注")
            print("  ✓ updated_at (DATETIME) - 更新时间")
            print()
            
            return True
            
        except Exception as e:
            print(f"✗ 迁移失败: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    import sys
    success = migrate()
    sys.exit(0 if success else 1)
