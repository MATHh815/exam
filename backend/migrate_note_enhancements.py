"""
数据库迁移脚本：笔记增强功能
添加 tags 和 linked_questions 字段到 question_notes 表
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text

def migrate():
    """执行数据库迁移"""
    app = create_app()
    
    with app.app_context():
        print("开始迁移数据库...")
        
        try:
            # 检查 tags 列是否存在
            result = db.session.execute(text("""
                SELECT COUNT(*) as count
                FROM information_schema.columns 
                WHERE table_name = 'question_notes' 
                AND column_name = 'tags'
            """))
            tags_exists = result.fetchone()[0] > 0
            
            if not tags_exists:
                print("添加 tags 列...")
                db.session.execute(text("""
                    ALTER TABLE question_notes 
                    ADD COLUMN tags JSON DEFAULT NULL
                """))
                print("✓ tags 列添加成功")
            else:
                print("✓ tags 列已存在，跳过")
            
            # 检查 linked_questions 列是否存在
            result = db.session.execute(text("""
                SELECT COUNT(*) as count
                FROM information_schema.columns 
                WHERE table_name = 'question_notes' 
                AND column_name = 'linked_questions'
            """))
            linked_exists = result.fetchone()[0] > 0
            
            if not linked_exists:
                print("添加 linked_questions 列...")
                db.session.execute(text("""
                    ALTER TABLE question_notes 
                    ADD COLUMN linked_questions JSON DEFAULT NULL
                """))
                print("✓ linked_questions 列添加成功")
            else:
                print("✓ linked_questions 列已存在，跳过")
            
            db.session.commit()
            print("\n✓ 数据库迁移完成！")
            
            # 显示表结构
            print("\n当前 question_notes 表结构：")
            result = db.session.execute(text("""
                DESCRIBE question_notes
            """))
            for row in result:
                print(f"  {row[0]}: {row[1]}")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n✗ 迁移失败: {str(e)}")
            raise

if __name__ == '__main__':
    migrate()
