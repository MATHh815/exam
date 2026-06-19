"""学习日程 API 测试脚本"""
import requests
import json
from datetime import datetime, date, timedelta

# API 基础 URL
BASE_URL = 'http://localhost:5000/api'

# 测试用户凭证
TEST_USER = {
    'username': 'test',
    'password': 'test123'
}

# 全局变量存储 token 和创建的日程 ID
access_token = None
schedule_id = None


def print_section(title):
    """打印分节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_result(success, message, data=None):
    """打印测试结果"""
    status = "✅" if success else "❌"
    print(f"\n{status} {message}")
    if data:
        print(json.dumps(data, indent=2, ensure_ascii=False))


def login():
    """登录获取 token"""
    global access_token
    
    print_section("1. 用户登录")
    
    try:
        response = requests.post(
            f'{BASE_URL}/auth/login',
            json=TEST_USER
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                access_token = data['data']['access_token']
                print_result(True, "登录成功", {
                    'username': data['data']['user']['username'],
                    'token': access_token[:20] + '...'
                })
                return True
        
        print_result(False, f"登录失败: {response.text}")
        return False
        
    except Exception as e:
        print_result(False, f"登录异常: {str(e)}")
        return False


def get_options():
    """获取活动类型和科目选项"""
    print_section("2. 获取选项")
    
    try:
        response = requests.get(f'{BASE_URL}/study-schedules/options')
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print_result(True, "获取选项成功", data['data'])
                return True
        
        print_result(False, f"获取选项失败: {response.text}")
        return False
        
    except Exception as e:
        print_result(False, f"获取选项异常: {str(e)}")
        return False


def create_schedule():
    """创建学习日程"""
    global schedule_id
    
    print_section("3. 创建学习日程")
    
    # 创建明天的日程
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    
    schedule_data = {
        'title': '背英语单词',
        'activity_type': 'memorize',
        'subject': 'english',
        'schedule_date': tomorrow,
        'start_time': '09:00',
        'end_time': '10:00',
        'description': '背诵考研英语核心词汇500个',
        'location': '图书馆',
        'reminder_minutes': 15
    }
    
    try:
        response = requests.post(
            f'{BASE_URL}/study-schedules',
            json=schedule_data,
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if response.status_code == 201:
            data = response.json()
            if data.get('success'):
                schedule_id = data['data']['schedule']['id']
                print_result(True, "创建日程成功", data['data']['schedule'])
                return True
        
        print_result(False, f"创建日程失败: {response.text}")
        return False
        
    except Exception as e:
        print_result(False, f"创建日程异常: {str(e)}")
        return False


def create_today_schedule():
    """创建今天的日程"""
    print_section("4. 创建今天的日程")
    
    today = date.today().isoformat()
    
    schedule_data = {
        'title': '做数据结构练习题',
        'activity_type': 'practice',
        'subject': 'data_structure',
        'schedule_date': today,
        'start_time': '14:00',
        'end_time': '16:00',
        'description': '完成第3章树的练习题',
        'location': '自习室'
    }
    
    try:
        response = requests.post(
            f'{BASE_URL}/study-schedules',
            json=schedule_data,
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if response.status_code == 201:
            data = response.json()
            if data.get('success'):
                print_result(True, "创建今日日程成功", data['data']['schedule'])
                return True
        
        print_result(False, f"创建今日日程失败: {response.text}")
        return False
        
    except Exception as e:
        print_result(False, f"创建今日日程异常: {str(e)}")
        return False


def get_today_schedules():
    """获取今天的日程"""
    print_section("5. 获取今天的日程")
    
    try:
        response = requests.get(
            f'{BASE_URL}/study-schedules/today',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print_result(True, f"获取今日日程成功 (共{data['data']['count']}个)", 
                           data['data']['schedules'])
                return True
        
        print_result(False, f"获取今日日程失败: {response.text}")
        return False
        
    except Exception as e:
        print_result(False, f"获取今日日程异常: {str(e)}")
        return False


def get_schedules_by_range():
    """获取日期范围内的日程"""
    print_section("6. 获取日期范围内的日程")
    
    # 获取本周的日程
    today = date.today()
    start_date = (today - timedelta(days=today.weekday())).isoformat()  # 本周一
    end_date = (today + timedelta(days=6-today.weekday())).isoformat()  # 本周日
    
    try:
        response = requests.get(
            f'{BASE_URL}/study-schedules',
            params={
                'start_date': start_date,
                'end_date': end_date
            },
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print_result(True, f"获取本周日程成功 (共{data['data']['count']}个)", 
                           data['data']['schedules'])
                return True
        
        print_result(False, f"获取日程失败: {response.text}")
        return False
        
    except Exception as e:
        print_result(False, f"获取日程异常: {str(e)}")
        return False


def update_schedule():
    """更新日程"""
    print_section("7. 更新日程")
    
    update_data = {
        'title': '背英语单词（更新）',
        'description': '背诵考研英语核心词汇800个',
        'location': '图书馆三楼'
    }
    
    try:
        response = requests.put(
            f'{BASE_URL}/study-schedules/{schedule_id}',
            json=update_data,
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print_result(True, "更新日程成功", data['data']['schedule'])
                return True
        
        print_result(False, f"更新日程失败: {response.text}")
        return False
        
    except Exception as e:
        print_result(False, f"更新日程异常: {str(e)}")
        return False


def complete_schedule():
    """完成日程"""
    print_section("8. 完成日程")
    
    try:
        response = requests.put(
            f'{BASE_URL}/study-schedules/{schedule_id}/complete',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print_result(True, "完成日程成功", data['data']['schedule'])
                return True
        
        print_result(False, f"完成日程失败: {response.text}")
        return False
        
    except Exception as e:
        print_result(False, f"完成日程异常: {str(e)}")
        return False


def get_statistics():
    """获取统计数据"""
    print_section("9. 获取统计数据")
    
    # 获取本月统计
    today = date.today()
    start_date = today.replace(day=1).isoformat()
    end_date = today.isoformat()
    
    try:
        response = requests.get(
            f'{BASE_URL}/study-schedules/statistics',
            params={
                'start_date': start_date,
                'end_date': end_date
            },
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print_result(True, "获取统计数据成功", data['data']['statistics'])
                return True
        
        print_result(False, f"获取统计数据失败: {response.text}")
        return False
        
    except Exception as e:
        print_result(False, f"获取统计数据异常: {str(e)}")
        return False


def test_time_conflict():
    """测试时间冲突检测"""
    print_section("10. 测试时间冲突检测")
    
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    
    # 尝试创建与已有日程冲突的日程
    conflict_schedule = {
        'title': '听高数网课',
        'activity_type': 'lecture',
        'subject': 'math',
        'schedule_date': tomorrow,
        'start_time': '09:30',  # 与 09:00-10:00 的日程冲突
        'end_time': '11:00',
        'location': '宿舍'
    }
    
    try:
        response = requests.post(
            f'{BASE_URL}/study-schedules',
            json=conflict_schedule,
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if response.status_code == 400:
            data = response.json()
            if '时间段已有其他日程' in data.get('error', {}).get('message', ''):
                print_result(True, "时间冲突检测正常", data['error'])
                return True
        
        print_result(False, f"时间冲突检测失败: {response.text}")
        return False
        
    except Exception as e:
        print_result(False, f"时间冲突检测异常: {str(e)}")
        return False


def create_repeat_schedule():
    """创建重复日程"""
    print_section("11. 创建重复日程（每周一三五）")
    
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    repeat_until = (date.today() + timedelta(days=14)).isoformat()  # 未来两周
    
    repeat_schedule = {
        'title': '晨读英语',
        'activity_type': 'reading',
        'subject': 'english',
        'schedule_date': tomorrow,
        'start_time': '07:00',
        'end_time': '08:00',
        'repeat_type': 'weekly',
        'repeat_days': '1,3,5',  # 周一、周三、周五
        'repeat_until': repeat_until,
        'location': '操场'
    }
    
    try:
        response = requests.post(
            f'{BASE_URL}/study-schedules',
            json=repeat_schedule,
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if response.status_code == 201:
            data = response.json()
            if data.get('success'):
                print_result(True, "创建重复日程成功", data['data']['schedule'])
                return True
        
        print_result(False, f"创建重复日程失败: {response.text}")
        return False
        
    except Exception as e:
        print_result(False, f"创建重复日程异常: {str(e)}")
        return False


def delete_schedule():
    """删除日程"""
    print_section("12. 删除日程")
    
    try:
        response = requests.delete(
            f'{BASE_URL}/study-schedules/{schedule_id}',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print_result(True, "删除日程成功", data['data'])
                return True
        
        print_result(False, f"删除日程失败: {response.text}")
        return False
        
    except Exception as e:
        print_result(False, f"删除日程异常: {str(e)}")
        return False


def run_all_tests():
    """运行所有测试"""
    print("\n" + "🚀" * 30)
    print("学习日程 API 测试")
    print("🚀" * 30)
    
    tests = [
        ("登录", login),
        ("获取选项", get_options),
        ("创建日程", create_schedule),
        ("创建今日日程", create_today_schedule),
        ("获取今日日程", get_today_schedules),
        ("获取日期范围日程", get_schedules_by_range),
        ("更新日程", update_schedule),
        ("完成日程", complete_schedule),
        ("获取统计数据", get_statistics),
        ("时间冲突检测", test_time_conflict),
        ("创建重复日程", create_repeat_schedule),
        ("删除日程", delete_schedule),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n❌ {name} 测试异常: {str(e)}")
            results.append((name, False))
    
    # 打印测试总结
    print_section("测试总结")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\n总计: {total} 个测试")
    print(f"通过: {passed} 个")
    print(f"失败: {total - passed} 个")
    print(f"成功率: {passed/total*100:.1f}%\n")
    
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    run_all_tests()
