#!/usr/bin/env python3
"""
数据库初始化脚本
创建必要的用户和数据
"""
import os
import sys
import sqlite3
import bcrypt
from datetime import datetime

def hash_password(password):
    """生成密码哈希"""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')

def init_database():
    """初始化数据库"""
    db_path = os.path.join(os.path.dirname(__file__), 'backend', 'exam.db')
    
    print(f"数据库路径: {db_path}")
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查users表是否存在
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='users'
        """)
        
        if not cursor.fetchone():
            print("创建users表...")
            cursor.execute("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(80) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    email VARCHAR(120) UNIQUE NOT NULL,
                    nickname VARCHAR(80),
                    avatar VARCHAR(255),
                    role VARCHAR(20) DEFAULT 'user' NOT NULL,
                    is_active BOOLEAN DEFAULT 1 NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
                )
            """)
            print("✅ users表创建成功")
        else:
            print("✅ users表已存在")
        
        # 检查现有用户
        cursor.execute("SELECT id, username, email, role FROM users")
        existing_users = cursor.fetchall()
        
        print(f"\n当前数据库中有 {len(existing_users)} 个用户:")
        for user in existing_users:
            print(f"  ID: {user[0]}, 用户名: {user[1]}, 邮箱: {user[2]}, 角色: {user[3]}")
        
        # 创建管理员用户
        cursor.execute("SELECT id FROM users WHERE username = ?", ('admin',))
        if not cursor.fetchone():
            print("\n创建管理员用户...")
            admin_password_hash = hash_password('123456')
            cursor.execute("""
                INSERT INTO users (username, password_hash, email, nickname, role, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ('admin', admin_password_hash, 'admin@example.com', '管理员', 'admin', True))
            print("✅ 管理员用户创建成功 (admin / 123456)")
        else:
            print("⚠️ 管理员用户已存在")
            # 确保管理员角色正确
            cursor.execute("UPDATE users SET role = 'admin' WHERE username = 'admin'")
            print("✅ 管理员角色已更新")
        
        # 创建测试用户
        cursor.execute("SELECT id FROM users WHERE username = ?", ('testuser',))
        if not cursor.fetchone():
            print("\n创建测试用户...")
            test_password_hash = hash_password('123456')
            cursor.execute("""
                INSERT INTO users (username, password_hash, email, nickname, role, is_active)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ('testuser', test_password_hash, 'test@example.com', '测试用户', 'user', True))
            print("✅ 测试用户创建成功 (testuser / 123456)")
        else:
            print("⚠️ 测试用户已存在")
        
        # 提交更改
        conn.commit()
        
        # 再次检查用户
        cursor.execute("SELECT id, username, email, role, is_active FROM users")
        all_users = cursor.fetchall()
        
        print(f"\n✅ 数据库初始化完成！当前有 {len(all_users)} 个用户:")
        for user in all_users:
            status = "激活" if user[4] else "禁用"
            print(f"  ID: {user[0]}, 用户名: {user[1]}, 邮箱: {user[2]}, 角色: {user[3]}, 状态: {status}")
        
        print("\n🎉 可以使用以下账户登录:")
        print("  管理员: admin / 123456")
        print("  测试用户: testuser / 123456")
        
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()
    
    return True

def check_database_structure():
    """检查数据库结构"""
    db_path = os.path.join(os.path.dirname(__file__), 'backend', 'exam.db')
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查表结构
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        print("users表结构:")
        for col in columns:
            print(f"  {col[1]} {col[2]} {'NOT NULL' if col[3] else ''} {'PRIMARY KEY' if col[5] else ''}")
        
        return True
        
    except Exception as e:
        print(f"❌ 检查数据库结构失败: {e}")
        return False
    
    finally:
        conn.close()

if __name__ == '__main__':
    print("🚀 开始数据库初始化...")
    
    # 检查数据库结构
    if check_database_structure():
        print("✅ 数据库结构检查通过")
    
    # 初始化数据库
    if init_database():
        print("\n🎉 数据库初始化成功！")
        print("\n📝 接下来的步骤:")
        print("1. 确保后端服务正在运行")
        print("2. 打开 exam/diagnose_auth_issue.html 进行测试")
        print("3. 使用 admin/123456 登录测试")
    else:
        print("\n❌ 数据库初始化失败！")
        sys.exit(1)