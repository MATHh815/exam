"""
添加考试进度相关字段的数据库迁移脚本

运行方式：
cd exam/backend
python add_exam_progress_fields.py
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text

def add_progress_fields():
    """添加考试进度相关字段"""
    app = create_app()
    
    with app.app_context():
        # 检查字段是否已存在
        try:
            result = db.session.execute(text("PRAGMA table_info(exam_sessions)"))
            columns = [row[1] for row in result.fetchall()]
            
            # 添加 last_active_time 字段
            if 'last_active_time' not in columns:
                print("添加 last_active_time 字段...")
                db.session.execute(text(
                    "ALTER TABLE exam_sessions ADD COLUMN last_active_time DATETIME"
                ))
                print("✓ last_active_time 字段添加成功")
            else:
                print("✓ last_active_time 字段已存在")
            
            # 添加 current_question_index 字段
            if 'current_question_index' not in columns:
                print("添加 current_question_index 字段...")
                db.session.execute(text(
                    "ALTER TABLE exam_sessions ADD COLUMN current_question_index INTEGER DEFAULT 0"
                ))
                print("✓ current_question_index 字段添加成功")
            else:
                print("✓ current_question_index 字段已存在")
            
            db.session.commit()
            print("\n数据库迁移完成！")
            
        except Exception as e:
            db.session.rollback()
            print(f"迁移失败: {e}")
            raise

if __name__ == '__main__':
    add_progress_fields()
