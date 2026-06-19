"""诊断认证问题的脚本"""
import sys
from app import create_app, db
from app.models.user import User

def diagnose_auth():
    """诊断认证问题"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("认证诊断报告")
        print("=" * 60)
        
        # 1. 检查数据库连接
        print("\n1. 检查数据库连接...")
        try:
            db.session.execute(db.text('SELECT 1'))
            print("   ✓ 数据库连接正常")
        except Exception as e:
            print(f"   ✗ 数据库连接失败: {e}")
            return
        
        # 2. 检查用户表
        print("\n2. 检查用户表...")
        try:
            user_count = User.query.count()
            print(f"   ✓ 用户表存在，共有 {user_count} 个用户")
        except Exception as e:
            print(f"   ✗ 用户表访问失败: {e}")
            return
        
        # 3. 列出所有用户
        print("\n3. 用户列表:")
        users = User.query.all()
        if not users:
            print("   ⚠ 没有找到任何用户")
            print("\n   建议: 运行 init_data.py 创建测试用户")
        else:
            print(f"   {'ID':<5} {'用户名':<15} {'邮箱':<25} {'角色':<10} {'状态':<10}")
            print("   " + "-" * 70)
            for user in users:
                status = "激活" if user.is_active else "禁用"
                print(f"   {user.id:<5} {user.username:<15} {user.email:<25} {user.role:<10} {status:<10}")
        
        # 4. 测试密码验证
        print("\n4. 测试密码验证...")
        test_username = "admin"
        test_password = "admin123"
        
        user = User.query.filter_by(username=test_username).first()
        if user:
            print(f"   找到用户: {test_username}")
            print(f"   - 邮箱: {user.email}")
            print(f"   - 角色: {user.role}")
            print(f"   - 状态: {'激活' if user.is_active else '禁用'}")
            
            # 测试密码
            if user.check_password(test_password):
                print(f"   ✓ 密码 '{test_password}' 验证成功")
            else:
                print(f"   ✗ 密码 '{test_password}' 验证失败")
                print(f"   提示: 请确认正确的密码")
        else:
            print(f"   ⚠ 用户 '{test_username}' 不存在")
        
        # 5. 测试登录流程
        print("\n5. 测试登录流程...")
        from app.services.auth_service import AuthService
        
        try:
            user, access_token, refresh_token = AuthService.login(test_username, test_password)
            print(f"   ✓ 登录成功")
            print(f"   - 用户ID: {user.id}")
            print(f"   - 用户名: {user.username}")
            print(f"   - 访问令牌: {access_token[:50]}...")
            print(f"   - 刷新令牌: {refresh_token[:50]}...")
        except ValueError as e:
            print(f"   ✗ 登录失败: {e}")
        except Exception as e:
            print(f"   ✗ 登录异常: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 60)
        print("诊断完成")
        print("=" * 60)

if __name__ == '__main__':
    diagnose_auth()
