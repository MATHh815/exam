"""测试修复后的 API 端点"""
import requests
import json

BASE_URL = 'http://127.0.0.1:5000/api'

# 测试用户凭证（需要先登录）
TEST_USER = {
    'username': 'test',
    'password': 'test123'
}

def login():
    """登录获取 token"""
    print("🔐 正在登录...")
    response = requests.post(f'{BASE_URL}/auth/login', json=TEST_USER)
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            token = data['data']['access_token']
            print(f"✅ 登录成功！Token: {token[:20]}...")
            return token
        else:
            print(f"❌ 登录失败: {data.get('error', {}).get('message')}")
    else:
        print(f"❌ 登录请求失败: {response.status_code}")
        print(f"   响应: {response.text}")
    return None

def test_bookmarks(token):
    """测试收藏 API"""
    print("\n📚 测试收藏 API...")
    headers = {'Authorization': f'Bearer {token}'}
    
    # 测试获取收藏列表
    response = requests.get(f'{BASE_URL}/bookmarks', headers=headers)
    print(f"   GET /api/bookmarks - 状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        # 支持两种响应格式：success 或 code
        if data.get('success') or data.get('code') == 200:
            bookmarks = data.get('data', {}).get('bookmarks', [])
            print(f"   ✅ 成功！收藏数量: {len(bookmarks)}")
            return True
        else:
            error_msg = data.get('error', {}).get('message') or data.get('message')
            print(f"   ❌ 失败: {error_msg}")
    else:
        print(f"   ❌ 请求失败: {response.text}")
    
    return False

def test_notes(token):
    """测试笔记 API"""
    print("\n📝 测试笔记 API...")
    headers = {'Authorization': f'Bearer {token}'}
    
    # 测试获取笔记列表
    response = requests.get(f'{BASE_URL}/notes', headers=headers)
    print(f"   GET /api/notes - 状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        # 支持两种响应格式：success 或 code
        if data.get('success') or data.get('code') == 200:
            notes = data.get('data', {}).get('notes', [])
            print(f"   ✅ 成功！笔记数量: {len(notes)}")
            return True
        else:
            error_msg = data.get('error', {}).get('message') or data.get('message')
            print(f"   ❌ 失败: {error_msg}")
    else:
        print(f"   ❌ 请求失败: {response.text}")
    
    return False

def test_achievements(token):
    """测试成就 API"""
    print("\n🏆 测试成就 API...")
    headers = {'Authorization': f'Bearer {token}'}
    
    # 测试获取成就列表
    response = requests.get(f'{BASE_URL}/achievements', headers=headers)
    print(f"   GET /api/achievements - 状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            achievements = data.get('data', {}).get('achievements', [])
            print(f"   ✅ 成功！成就数量: {len(achievements)}")
            return True
        else:
            print(f"   ❌ 失败: {data.get('error', {}).get('message')}")
    else:
        print(f"   ❌ 请求失败: {response.text}")
    
    return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("🧪 测试修复后的 API 端点")
    print("=" * 60)
    
    # 登录
    token = login()
    if not token:
        print("\n❌ 无法获取 token，测试终止")
        return
    
    # 测试各个 API
    results = {
        '收藏': test_bookmarks(token),
        '笔记': test_notes(token),
        '成就': test_achievements(token)
    }
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("📊 测试结果汇总")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"   {name} API: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 所有测试通过！修复成功！")
    else:
        print("⚠️  部分测试失败，请检查错误日志")
    print("=" * 60)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
