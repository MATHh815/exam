"""测试获取试卷详情 API"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

app = create_app()

with app.test_client() as client:
    print("=" * 60)
    print("测试获取试卷详情 API")
    print("=" * 60)
    
    # 1. 先登录获取 token
    print("\n1. 登录获取 token...")
    login_response = client.post('/api/auth/login', json={
        'username': 'admin',
        'password': 'admin123'
    })
    
    login_data = login_response.get_json()
    access_token = login_data.get('data', {}).get('access_token')
    
    if not access_token:
        print(f"   ❌ 登录失败: {login_data}")
        sys.exit(1)
    
    print(f"   ✅ 登录成功")
    
    headers = {'Authorization': f'Bearer {access_token}'}
    
    # 2. 获取试卷详情（不包含题目）
    print("\n2. 获取试卷详情（不包含题目）...")
    response = client.get('/api/exams/1', headers=headers)
    print(f"   状态码: {response.status_code}")
    data = response.get_json()
    print(f"   响应: {data}")
    
    # 3. 获取试卷详情（包含题目）
    print("\n3. 获取试卷详情（包含题目）...")
    response = client.get('/api/exams/1?include_questions=true', headers=headers)
    print(f"   状态码: {response.status_code}")
    data = response.get_json()
    
    if response.status_code == 200:
        print(f"   ✅ 成功")
        print(f"   试卷名称: {data.get('data', {}).get('name')}")
        questions = data.get('data', {}).get('questions', [])
        print(f"   题目数量: {len(questions)}")
        if questions:
            print(f"   第一道题: {questions[0].get('content', '')[:50]}...")
    else:
        print(f"   ❌ 失败")
        print(f"   错误: {data}")
