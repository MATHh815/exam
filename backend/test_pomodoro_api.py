"""
番茄钟 API 测试脚本
"""
import requests
import json
from datetime import datetime

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
            token = data['data']['access_token']
            print(f"✓ 登录成功")
            return token
    
    print(f"✗ 登录失败: {response.text}")
    return None

def test_complete_session(token):
    """测试完成番茄钟会话"""
    print("\n测试: 完成番茄钟会话")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(
        f'{BASE_URL}/api/pomodoro/complete',
        headers=headers,
        json={
            'duration': 25,
            'session_type': 'focus',
            'subject': 'Python编程',
            'notes': '学习了装饰器和生成器'
        }
    )
    
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    if data.get('success'):
        print(f"✓ 完成会话成功")
        print(f"  - 获得积分: {data['data']['points_earned']}")
        if data['data']['achievements']:
            print(f"  - 解锁成就: {len(data['data']['achievements'])} 个")
    else:
        print(f"✗ 完成会话失败")

def test_interrupt_session(token):
    """测试中断番茄钟会话"""
    print("\n测试: 中断番茄钟会话")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(
        f'{BASE_URL}/api/pomodoro/interrupt',
        headers=headers,
        json={
            'duration': 15,
            'session_type': 'focus',
            'subject': '数学'
        }
    )
    
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    if data.get('success'):
        print(f"✓ 中断会话成功")
    else:
        print(f"✗ 中断会话失败")

def test_get_stats(token):
    """测试获取统计"""
    print("\n测试: 获取番茄钟统计")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(
        f'{BASE_URL}/api/pomodoro/stats',
        headers=headers
    )
    
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
    if data.get('success'):
        stats = data['data']
        print(f"✓ 获取统计成功")
        print(f"  - 今日完成: {stats['today_sessions']} 个")
        print(f"  - 今日专注: {stats['today_focus_time']} 分钟")
        print(f"  - 连续天数: {stats['current_streak']} 天")
        print(f"  - 累计完成: {stats['total_sessions']} 个")
    else:
        print(f"✗ 获取统计失败")

def test_get_recent_sessions(token):
    """测试获取最近会话"""
    print("\n测试: 获取最近会话")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(
        f'{BASE_URL}/api/pomodoro/sessions/recent?days=7',
        headers=headers
    )
    
    print(f"状态码: {response.status_code}")
    data = response.json()
    
    if data.get('success'):
        sessions = data['data']
        print(f"✓ 获取最近会话成功")
        print(f"  - 会话数量: {len(sessions)}")
        if sessions:
            print(f"  - 最近一次: {sessions[0]['subject']} ({sessions[0]['duration']}分钟)")
    else:
        print(f"✗ 获取最近会话失败")

def test_get_daily_trend(token):
    """测试获取每日趋势"""
    print("\n测试: 获取每日趋势")
    
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(
        f'{BASE_URL}/api/pomodoro/trend?days=14',
        headers=headers
    )
    
    print(f"状态码: {response.status_code}")
    data = response.json()
    
    if data.get('success'):
        trend = data['data']
        print(f"✓ 获取每日趋势成功")
        print(f"  - 数据点数: {len(trend)}")
        
        # 统计总数
        total_sessions = sum(d['sessions'] for d in trend)
        total_time = sum(d['focus_time'] for d in trend)
        print(f"  - 总完成数: {total_sessions}")
        print(f"  - 总专注时长: {total_time} 分钟")
    else:
        print(f"✗ 获取每日趋势失败")

def main():
    """主测试函数"""
    print("=" * 60)
    print("番茄钟 API 测试")
    print("=" * 60)
    
    # 登录
    token = login()
    if not token:
        print("无法继续测试，登录失败")
        return
    
    # 测试各个接口
    test_complete_session(token)
    test_interrupt_session(token)
    test_get_stats(token)
    test_get_recent_sessions(token)
    test_get_daily_trend(token)
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == '__main__':
    main()
