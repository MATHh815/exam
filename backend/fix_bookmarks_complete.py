"""完整修复收藏功能的脚本

此脚本会:
1. 检查数据库表结构
2. 运行迁移添加缺失字段
3. 验证修复结果
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from sqlalchemy import text, inspect

def check_database():
    """检查数据库状态"""
    print("=" * 60)
    print("检查数据库状态")
    print("=" * 60)
    print()
    
    app = create_app()
    
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            
            # 检查 question_bookmarks 表
            if 'question_bookmarks' not in inspector.get_table_names():
                print("✗ 错误: question_bookmarks 表不存在")
                return False
            
            columns = {col['name']: col for col in inspector.get_columns('question_bookmarks')}
            print(f"✓ question_bookmarks 表存在")
            print(f"  当前列: {', '.join(columns.keys())}")
            print()
            
            # 检查必需字段
            required_fields = ['id', 'user_id', 'question_id', 'tags', 'notes', 'created_at', 'updated_at']
            missing_fields = [field for field in required_fields if field not in columns]
            
            if missing_fields:
                print(f"⚠️  缺少字段: {', '.join(missing_fields)}")
                return False
            else:
                print("✓ 所有必需字段都存在")
                return True
                
        except Exception as e:
            print(f"✗ 检查失败: {e}")
            return False

def run_migration():
    """运行迁移"""
    print()
    print("=" * 60)
    print("运行数据库迁移")
    print("=" * 60)
    print()
    
    app = create_app()
    
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('question_bookmarks')]
            
            changes_made = False
            
            # 添加 notes 字段
            if 'notes' not in columns:
                print("添加 notes 字段...")
                db.session.execute(text(
                    "ALTER TABLE question_bookmarks ADD COLUMN notes TEXT"
                ))
                print("✓ notes 字段添加成功")
                changes_made = True
            else:
                print("⏭️  notes 字段已存在")
            
            # 添加 updated_at 字段
            if 'updated_at' not in columns:
                print("添加 updated_at 字段...")
                db.session.execute(text(
                    "ALTER TABLE question_bookmarks ADD COLUMN updated_at DATETIME DEFAULT CURRENT_TIMESTAMP"
                ))
                print("✓ updated_at 字段添加成功")
                changes_made = True
            else:
                print("⏭️  updated_at 字段已存在")
            
            if changes_made:
                db.session.commit()
                print()
                print("✓ 迁移完成")
            else:
                print()
                print("✓ 无需迁移，所有字段已存在")
            
            return True
            
        except Exception as e:
            print(f"✗ 迁移失败: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return False

def verify_fix():
    """验证修复结果"""
    print()
    print("=" * 60)
    print("验证修复结果")
    print("=" * 60)
    print()
    
    app = create_app()
    
    with app.app_context():
        try:
            from app.models.note import QuestionBookmark
            
            # 检查模型是否可以正常使用
            print("测试 QuestionBookmark 模型...")
            
            # 尝试查询（不会实际创建数据）
            count = QuestionBookmark.query.count()
            print(f"✓ 模型查询成功，当前收藏数: {count}")
            
            # 检查 to_dict 方法
            if count > 0:
                bookmark = QuestionBookmark.query.first()
                bookmark_dict = bookmark.to_dict()
                print(f"✓ to_dict() 方法正常")
                print(f"  返回字段: {', '.join(bookmark_dict.keys())}")
            
            print()
            print("✓ 所有验证通过")
            return True
            
        except Exception as e:
            print(f"✗ 验证失败: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """主函数"""
    print()
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 15 + "收藏功能完整修复脚本" + " " * 15 + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    # 步骤1: 检查数据库
    if check_database():
        print()
        print("✓ 数据库检查通过，无需迁移")
        print()
        print("=" * 60)
        print("修复完成！")
        print("=" * 60)
        print()
        print("后续步骤:")
        print("  1. 重启后端服务")
        print("  2. 刷新前端页面")
        print("  3. 测试收藏功能")
        print()
        return True
    
    # 步骤2: 运行迁移
    if not run_migration():
        print()
        print("✗ 迁移失败，请检查错误信息")
        return False
    
    # 步骤3: 验证修复
    if not verify_fix():
        print()
        print("✗ 验证失败，请检查错误信息")
        return False
    
    # 完成
    print()
    print("=" * 60)
    print("修复完成！")
    print("=" * 60)
    print()
    print("后续步骤:")
    print("  1. 重启后端服务 (运行 start_backend.bat)")
    print("  2. 刷新前端页面")
    print("  3. 测试收藏功能")
    print()
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ 发生未预期的错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
