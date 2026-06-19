"""完整的数据库设置脚本

此脚本将:
1. 创建所有数据库表
2. 初始化基础数据（管理员用户等）
3. 验证数据库设置
"""
import sys
from app import create_app, db
from app.models.user import User

def setup_database():
    """设置数据库"""
    print("=" * 60)
    print("数据库设置")
    print("=" * 60)
    print()
    
    app = create_app()
    
    with app.app_context():
        # 步骤 1: 创建所有表
        print("步骤 1/3: 创建数据库表...")
        print("-" * 60)
        try:
            db.create_all()
            print("✓ 数据库表创建成功")
        except Exception as e:
            print(f"✗ 创建数据库表失败: {e}")
            return False
        
        # 步骤 2: 创建管理员用户
        print("\n步骤 2/3: 创建初始用户...")
        print("-" * 60)
        
        # 检查是否已有管理员
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            try:
                admin = User(
                    username='admin',
                    email='admin@example.com',
                    nickname='系统管理员',
                    role='admin'
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("✓ 管理员用户创建成功")
                print(f"  用户名: admin")
                print(f"  密码: admin123")
            except Exception as e:
                print(f"✗ 创建管理员失败: {e}")
                db.session.rollback()
                return False
        else:
            print(f"✓ 管理员用户已存在: {admin.username}")
        
        # 创建测试学生用户
        student = User.query.filter_by(username='student').first()
        if not student:
            try:
                student = User(
                    username='student',
                    email='student@example.com',
                    nickname='测试学生',
                    role='user'
                )
                student.set_password('student123')
                db.session.add(student)
                db.session.commit()
                print("✓ 学生用户创建成功")
                print(f"  用户名: student")
                print(f"  密码: student123")
            except Exception as e:
                print(f"✗ 创建学生用户失败: {e}")
                db.session.rollback()
        else:
            print(f"✓ 学生用户已存在: {student.username}")
        
        # 步骤 3: 验证设置
        print("\n步骤 3/3: 验证数据库设置...")
        print("-" * 60)
        
        try:
            user_count = User.query.count()
            print(f"✓ 用户表正常，共有 {user_count} 个用户")
            
            # 测试登录
            from app.services.auth_service import AuthService
            user, access_token, refresh_token = AuthService.login('admin', 'admin123')
            print(f"✓ 登录测试成功")
            print(f"  用户: {user.username}")
            print(f"  令牌: {access_token[:30]}...")
            
        except Exception as e:
            print(f"✗ 验证失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        print("\n" + "=" * 60)
        print("✅ 数据库设置完成！")
        print("=" * 60)
        print("\n可以使用以下账号登录：")
        print("  管理员 - 用户名: admin, 密码: admin123")
        print("  学生   - 用户名: student, 密码: student123")
        print()
        
        return True

if __name__ == '__main__':
    success = setup_database()
    sys.exit(0 if success else 1)
