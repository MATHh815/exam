#!/usr/bin/env python3
"""测试后端API"""
import requests
import json

API_BASE = 'http://localhost:5000/api'

def test_backend_connection():
    """测试后端连接"""
    print("=== 测试后端连接 ===")
    try:
        response = requests.get(f'{API_BASE}/auth/profile', timeout=5)
        print(f"后端响应状态: {response.status_code}")
        if response.status_code == 401:
            print("后端正常运行，但需要认证")
        return True
    except requests.exceptions.ConnectionError:
        print("后端连接失败 - 后端可能未启动")
        return False
    except Exception as e:
        print(f"连接测试失败: {e}")
        return False

def test_register():
    """测试注册"""
    print("\n=== 测试用户注册 ===")
    
    # 注册管理员用户
    admin_data = {
        "username": "admin",
        "password": "123456",
        "email": "admin@example.com",
        "nickname": "管理员"
    }
    
    try:
        response = requests.post(f'{API_BASE}/auth/register', 
                               json=admin_data, 
                               timeout=10)
        print(f"注册管理员响应状态: {response.status_code}")
        data = response.json()
        print(f"注册管理员响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        if response.status_code == 201:
            print("管理员注册成功")
        elif response.status_code == 400 and "已存在" in str(data):
            print("管理员已存在")
        
    except Exception as e:
        print(f"注册管理员失败: {e}")
    
    # 注册测试用户
    test_data = {
        "username": "testuser",
        "password": "123456",
        "email": "test@example.com",
        "nickname": "测试用户"
    }
    
    try:
        response = requests.post(f'{API_BASE}/auth/register', 
                               json=test_data, 
                               timeout=10)
        print(f"注册测试用户响应状态: {response.status_code}")
        data = response.json()
        print(f"注册测试用户响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        if response.status_code == 201:
            print("测试用户注册成功")
        elif response.status_code == 400 and "已存在" in str(data):
            print("测试用户已存在")
            
    except Exception as e:
        print(f"注册测试用户失败: {e}")

def test_login():
    """测试登录"""
    print("\n=== 测试用户登录 ===")
    
    login_data = {
        "username": "admin",
        "password": "123456"
    }
    
    try:
        response = requests.post(f'{API_BASE}/auth/login', 
                               json=login_data, 
                               timeout=10)
        print(f"登录响应状态: {response.status_code}")
        data = response.json()
        print(f"登录响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        if response.status_code == 200 and data.get('success'):
            print("登录成功！")
            token = data['data']['access_token']
            print(f"获得Token: {token[:50]}...")
            return token
        else:
            print("登录失败")
            return None
            
    except Exception as e:
        print(f"登录测试失败: {e}")
        return None

def test_profile(token):
    """测试获取用户信息"""
    print("\n=== 测试获取用户信息 ===")
    
    if not token:
        print("没有Token，跳过测试")
        return
    
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    try:
        response = requests.get(f'{API_BASE}/auth/profile', 
                              headers=headers, 
                              timeout=10)
        print(f"获取用户信息响应状态: {response.status_code}")
        data = response.json()
        print(f"用户信息响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        if response.status_code == 200:
            print("获取用户信息成功")
        else:
            print("获取用户信息失败")
            
    except Exception as e:
        print(f"获取用户信息失败: {e}")

def main():
    """主测试函数"""
    print("开始后端API测试...")
    
    # 测试连接
    if not test_backend_connection():
        print("后端连接失败，请确保后端服务正在运行")
        return
    
    # 测试注册
    test_register()
    
    # 测试登录
    token = test_login()
    
    # 测试获取用户信息
    test_profile(token)
    
    print("\n=== 测试完成 ===")

if __name__ == '__main__':
    main()