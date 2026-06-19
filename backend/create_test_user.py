"""创建测试用户"""
from app import create_app, db
from app.models.user import User

def create_test_user():
    app = create_app()
    with app.app_context():
        # 检查用户是否已存在
        existing_user = User.query.filter_by(username='test').first()
        if existing_user:
            print("✅ 测试用户已存在，更新密码...")
            # 更新密码
            existing_user.set_password('test123')
            db.session.commit()
            print(f"   用户名: {existing_user.username}")
            print(f"   密码: test123")
            print(f"   邮箱: {existing_user.email}")
            return
        
        # 创建新用户
        test_user = User(
            username='test',
            email='test@example.com',
            nickname='测试用户',
            role='student',
            is_active=True
        )
        test_user.set_password('test123')
        
        db.session.add(test_user)
        db.session.commit()
        
        print("✅ 测试用户创建成功")
        print(f"   用户名: test")
        print(f"   密码: test123")
        print(f"   邮箱: test@example.com")

if __name__ == '__main__':
    create_test_user()
