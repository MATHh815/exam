#!/usr/bin/env python3
"""创建测试用户脚本"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import create_app, db
from app.models.user import User

def create_test_users():
    """创建测试用户"""
    app = create_app()
    
    with app.app_context():
        # 检查是否已有用户
        existing_users = User.query.all()
        print(f"当前数据库中有 {len(existing_users)} 个用户")
        
        for user in existing_users:
            print(f"- {user.username} ({user.email}) - {user.role}")
        
        # 创建管理员用户
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@example.com',
                nickname='管理员',
                role='admin'
            )
            admin_user.set_password('123456')
            db.session.add(admin_user)
            print("创建管理员用户: admin / 123456")
        else:
            print("管理员用户已存在")
        
        # 创建测试用户
        test_user = User.query.filter_by(username='testuser').first()
        if not test_user:
            test_user = User(
                username='testuser',
                email='test@example.com',
                nickname='测试用户',
                role='user'
            )
            test_user.set_password('123456')
            db.session.add(test_user)
            print("创建测试用户: testuser / 123456")
        else:
            print("测试用户已存在")
        
        # 提交更改
        try:
            db.session.commit()
            print("用户创建成功！")
        except Exception as e:
            db.session.rollback()
            print(f"创建用户失败: {e}")
        
        # 再次检查用户
        all_users = User.query.all()
        print(f"\n创建后数据库中有 {len(all_users)} 个用户:")
        for user in all_users:
            print(f"- {user.username} ({user.email}) - {user.role}")

if __name__ == '__main__':
    create_test_users()