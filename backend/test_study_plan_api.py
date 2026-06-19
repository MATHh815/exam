"""
测试学习计划 API
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = 'http://localhost:5000/api'

def test_study_plans():
    """测试学习计划功能"""
    
    # 1. 登录获取 token
    print("1. 登录...")
    login_data = {
        'username': 'test',
        'password': 'test123'
    }
    
    response = requests.post(f'{BASE_URL}/auth/login', json=login_data)
    print(f"登录响应: {response.status_code}")
    print(f"响应内容: {response.json()}")
    
    if response.status_code != 200:
        print("登录失败，请先创建测试用户")
        return
    
    token = response.json()['data']['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # 2. 创建学习计划
    print("\n2. 创建学习计划...")
    today = datetime.now()
    plan_data = {
        'name': '测试学习计划',
        'description': '这是一个测试计划',
        'exam_type': 'civil_service',
        'start_date': today.strftime('%Y-%m-%d'),
        'end_date': (today + timedelta(days=30)).strftime('%Y-%m-%d'),
        'goals': [
            {
                'goal_type': 'daily_practice',
                'target_value': 50
            },
            {
                'goal_type': 'weekly_practice',
                'target_value': 350
            }
        ]
    }
    
    response = requests.post(f'{BASE_URL}/study-plans', json=plan_data, headers=headers)
    print(f"创建计划响应: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    if response.status_code != 201:
        print("创建计划失败")
        return
    
    plan_id = response.json()['data']['plan']['id']
    print(f"创建的计划ID: {plan_id}")
    
    # 3. 获取学习计划列表
    print("\n3. 获取学习计划列表...")
    response = requests.get(f'{BASE_URL}/study-plans', headers=headers)
    print(f"获取列表响应: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    # 4. 获取单个计划详情
    print(f"\n4. 获取计划详情 (ID: {plan_id})...")
    response = requests.get(f'{BASE_URL}/study-plans/{plan_id}', headers=headers)
    print(f"获取详情响应: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
    print("\n✓ 测试完成！")

if __name__ == '__main__':
    test_study_plans()
