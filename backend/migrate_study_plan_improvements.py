"""
学习计划改进 - 数据库迁移脚本

添加新字段：
1. StudyGoal.subject - 科目字段（用于科目特定目标）
2. StudyGoal.completed_at - 完成时间字段

运行方式：
    python migrate_study_plan_improvements.py
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
        print("=" * 60)
        print("学习计划改进 - 数据库迁移")
        print("=" * 60)
        
        try:
            # 检查 study_goals 表是否存在
            result = db.session.execute(text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='study_goals'"
            ))
            if not result.fetchone():
                print("❌ study_goals 表不存在，请先运行基础迁移")
                return False
            
            # 检查是否已经有 subject 字段
            result = db.session.execute(text("PRAGMA table_info(study_goals)"))
            columns = [row[1] for row in result.fetchall()]
            
            # 添加 subject 字段
            if 'subject' not in columns:
                print("\n📝 添加 subject 字段...")
                db.session.execute(text(
                    "ALTER TABLE study_goals ADD COLUMN subject VARCHAR(50)"
                ))
                print("✅ subject 字段添加成功")
            else:
                print("\n✓ subject 字段已存在")
            
            # 添加 completed_at 字段
            if 'completed_at' not in columns:
                print("\n📝 添加 completed_at 字段...")
                db.session.execute(text(
                    "ALTER TABLE study_goals ADD COLUMN completed_at DATETIME"
                ))
                print("✅ completed_at 字段添加成功")
            else:
                print("\n✓ completed_at 字段已存在")
            
            db.session.commit()
            
            print("\n" + "=" * 60)
            print("✅ 数据库迁移完成！")
            print("=" * 60)
            
            # 显示新的表结构
            print("\n📊 study_goals 表结构：")
            result = db.session.execute(text("PRAGMA table_info(study_goals)"))
            for row in result.fetchall():
                print(f"  - {row[1]} ({row[2]})")
            
            return True
            
        except Exception as e:
            print(f"\n❌ 迁移失败: {str(e)}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    success = migrate()
    sys.exit(0 if success else 1)
