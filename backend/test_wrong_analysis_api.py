"""测试错题分析 API"""
import requests
import json

BASE_URL = 'http://localhost:5000'

def login():
    """登录获取 token"""
    response = requests.post(f'{BASE_URL}/api/auth/login', json={
        'username': 'student',
        'password': 'student123'
    })
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            return data['data']['access_token']
    
    print('登录失败:', response.text)
    return None

def test_overview(token):
    """测试错题概览"""
    print('\n=== 测试错题概览 ===')
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(
        f'{BASE_URL}/api/statistics/wrong-questions/overview',
        headers=headers,
        params={'days': 30}
    )
    
    print(f'状态码: {response.status_code}')
    print(f'响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}')
    return response.status_code == 200

def test_distribution(token):
    """测试错题分布"""
    print('\n=== 测试错题分布 ===')
    headers = {'Authorization': f'Bearer {token}'}
    
    for dimension in ['subject', 'type', 'knowledge']:
        print(f'\n维度: {dimension}')
        response = requests.get(
            f'{BASE_URL}/api/statistics/wrong-questions/distribution',
            headers=headers,
            params={'dimension': dimension, 'days': 30}
        )
        
        print(f'状态码: {response.status_code}')
        data = response.json()
        if data.get('success'):
            print(f'数据: {json.dumps(data["data"][:3], indent=2, ensure_ascii=False)}...')
        else:
            print(f'错误: {data}')

def test_frequent(token):
    """测试高频错题"""
    print('\n=== 测试高频错题 ===')
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(
        f'{BASE_URL}/api/statistics/wrong-questions/frequent',
        headers=headers,
        params={'limit': 5}
    )
    
    print(f'状态码: {response.status_code}')
    data = response.json()
    if data.get('success'):
        print(f'数据: {json.dumps(data["data"], indent=2, ensure_ascii=False)}')
    else:
        print(f'错误: {data}')

def test_trend(token):
    """测试错题趋势"""
    print('\n=== 测试错题趋势 ===')
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(
        f'{BASE_URL}/api/statistics/wrong-questions/trend',
        headers=headers,
        params={'days': 7}
    )
    
    print(f'状态码: {response.status_code}')
    data = response.json()
    if data.get('success'):
        print(f'数据（前3天）: {json.dumps(data["data"][:3], indent=2, ensure_ascii=False)}...')
    else:
        print(f'错误: {data}')

def test_weak_points(token):
    """测试薄弱知识点"""
    print('\n=== 测试薄弱知识点 ===')
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(
        f'{BASE_URL}/api/statistics/wrong-questions/weak-points',
        headers=headers,
        params={'limit': 5}
    )
    
    print(f'状态码: {response.status_code}')
    data = response.json()
    if data.get('success'):
        print(f'数据: {json.dumps(data["data"], indent=2, ensure_ascii=False)}')
    else:
        print(f'错误: {data}')

def test_suggestions(token):
    """测试学习建议"""
    print('\n=== 测试学习建议 ===')
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(
        f'{BASE_URL}/api/statistics/wrong-questions/suggestions',
        headers=headers
    )
    
    print(f'状态码: {response.status_code}')
    data = response.json()
    if data.get('success'):
        print('建议:')
        for i, suggestion in enumerate(data['data'], 1):
            print(f'{i}. {suggestion}')
    else:
        print(f'错误: {data}')

def main():
    """主函数"""
    print('开始测试错题分析 API...')
    
    # 登录
    token = login()
    if not token:
        print('无法获取 token，测试终止')
        return
    
    print(f'\n✓ 登录成功，token: {token[:20]}...')
    
    # 测试所有 API
    try:
        test_overview(token)
        test_distribution(token)
        test_frequent(token)
        test_trend(token)
        test_weak_points(token)
        test_suggestions(token)
        
        print('\n' + '='*50)
        print('✓ 所有测试完成！')
        print('='*50)
        
    except Exception as e:
        print(f'\n✗ 测试失败: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
