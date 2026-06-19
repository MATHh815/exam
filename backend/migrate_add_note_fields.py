"""添加笔记缺失字段的迁移脚本

此脚本为 question_notes 表添加 tags 和 linked_questions 字段
"""
from app import create_app, db
from sqlalchemy import text

def migrate():
    """执行迁移"""
    print("=" * 60)
    print("添加笔记缺失字段")
    print("=" * 60)
    print()
    
    app = create_app()
    
    with app.app_context():
        try:
            # 检查表是否存在
            inspector = db.inspect(db.engine)
            if 'question_notes' not in inspector.get_table_names():
                print("✗ 错误: question_notes 表不存在")
                return False
            
            # 获取现有列
            columns = [col['name'] for col in inspector.get_columns('question_notes')]
            print(f"当前列: {', '.join(columns)}")
            print()
            
            changes_made = False
            
            # 添加 tags 字段
            if 'tags' not in columns:
                print("添加 tags 字段...")
                db.session.execute(text(
                    "ALTER TABLE question_notes ADD COLUMN tags JSON"
                ))
                print("✓ tags 字段添加成功")
                changes_made = True
            else:
                print("⏭️  tags 字段已存在")
            
            # 添加 linked_questions 字段
            if 'linked_questions' not in columns:
                print("添加 linked_questions 字段...")
                db.session.execute(text(
                    "ALTER TABLE question_notes ADD COLUMN linked_questions JSON"
                ))
                print("✓ linked_questions 字段添加成功")
                changes_made = True
            else:
                print("⏭️  linked_questions 字段已存在")
            
            if changes_made:
                db.session.commit()
                print()
                print("=" * 60)
                print("迁移完成！")
                print("=" * 60)
                print()
                print("新增字段:")
                if 'tags' not in columns:
                    print("  ✓ tags (JSON) - 笔记标签")
                if 'linked_questions' not in columns:
                    print("  ✓ linked_questions (JSON) - 链接的题目ID列表")
                print()
            else:
                print()
                print("=" * 60)
                print("无需迁移，所有字段已存在")
                print("=" * 60)
                print()
            
            return True
            
        except Exception as e:
            print(f"✗ 迁移失败: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    import sys
    success = migrate()
    sys.exit(0 if success else 1)
