"""第一阶段数据库迁移脚本

此脚本用于生成和应用第一阶段功能增强的数据库迁移。

使用方法:
1. 确保虚拟环境已激活
2. 运行: python migrate_phase1.py
"""
import os
import sys
from flask import Flask
from flask_migrate import Migrate, init, migrate, upgrade
from app import create_app, db

def run_migration():
    """执行数据库迁移"""
    print("=" * 60)
    print("第一阶段功能增强 - 数据库迁移")
    print("=" * 60)
    print()
    
    # 创建应用实例
    app = create_app()
    
    with app.app_context():
        # 检查 migrations 目录是否存在
        migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
        
        if not os.path.exists(migrations_dir):
            print("错误: migrations 目录不存在")
            print("请先运行: flask db init")
            return False
        
        print("步骤 1/3: 生成迁移脚本...")
        print("-" * 60)
        
        # 生成迁移脚本
        try:
            from flask_migrate import migrate as flask_migrate
            flask_migrate(message='Add Phase 1 enhancement models')
            print("✓ 迁移脚本生成成功")
        except Exception as e:
            print(f"✗ 生成迁移脚本失败: {e}")
            return False
        
        print()
        print("步骤 2/3: 检查迁移脚本...")
        print("-" * 60)
        print("请检查 migrations/versions/ 目录中的最新迁移文件")
        print("确认以下表将被创建:")
        print("  - study_plans (学习计划)")
        print("  - study_goals (学习目标)")
        print("  - study_reminders (学习提醒)")
        print("  - question_notes (题目笔记)")
        print("  - question_bookmarks (题目收藏)")
        print("  - achievements (成就定义)")
        print("  - user_achievements (用户成就)")
        print("  - user_points (用户积分)")
        print("  - point_transactions (积分交易记录)")
        print("  - daily_tasks (每日任务)")
        print()
        
        response = input("是否继续应用迁移? (y/n): ")
        if response.lower() != 'y':
            print("迁移已取消")
            return False
        
        print()
        print("步骤 3/3: 应用迁移...")
        print("-" * 60)
        
        # 应用迁移
        try:
            from flask_migrate import upgrade as flask_upgrade
            flask_upgrade()
            print("✓ 迁移应用成功")
        except Exception as e:
            print(f"✗ 应用迁移失败: {e}")
            return False
        
        print()
        print("=" * 60)
        print("数据库迁移完成！")
        print("=" * 60)
        print()
        print("新增的表:")
        print("  ✓ study_plans")
        print("  ✓ study_goals")
        print("  ✓ study_reminders")
        print("  ✓ question_notes")
        print("  ✓ question_bookmarks")
        print("  ✓ achievements")
        print("  ✓ user_achievements")
        print("  ✓ user_points")
        print("  ✓ point_transactions")
        print("  ✓ daily_tasks")
        print()
        print("下一步:")
        print("  1. 运行测试确保迁移成功")
        print("  2. 继续实现服务层代码")
        print()
        
        return True

if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)
