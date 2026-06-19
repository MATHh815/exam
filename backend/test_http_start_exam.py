"""模拟前端 HTTP 请求测试开始考试"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

app = create_app()

with app.test_client() as client:
    print("=" * 60)
    print("HTTP 请求测试：开始考试")
    print("=" * 60)
    
    # 1. 先登录获取 token
    print("\n1. 登录获取 token...")
    login_response = client.post('/api/auth/login', json={
        'username': 'admin',
        'password': 'admin123'
    })
    
    print(f"   登录状态码: {login_response.status_code}")
    login_data = login_response.get_json()
    
    if login_response.status_code != 200 or not login_data.get('success'):
        print(f"   ❌ 登录失败: {login_data}")
        sys.exit(1)
    
    access_token = login_data.get('data', {}).get('access_token')
    if not access_token:
        print(f"   ❌ 没有获取到 access_token")
        print(f"   响应数据: {login_data}")
        sys.exit(1)
    
    print(f"   ✅ 登录成功，获取到 token")
    
    # 2. 获取试卷列表
    print("\n2. 获取试卷列表...")
    headers = {'Authorization': f'Bearer {access_token}'}
    papers_response = client.get('/api/exams?is_published=true', headers=headers)
    
    print(f"   状态码: {papers_response.status_code}")
    papers_data = papers_response.get_json()
    
    if papers_response.status_code != 200:
        print(f"   ❌ 获取试卷列表失败: {papers_data}")
        sys.exit(1)
    
    papers = papers_data.get('data', {}).get('papers', [])
    print(f"   ✅ 获取到 {len(papers)} 个试卷")
    
    if not papers:
        print("   ❌ 没有可用的试卷")
        sys.exit(1)
    
    paper = papers[0]
    paper_id = paper['id']
    print(f"   选择试卷: {paper['name']} (ID={paper_id})")
    
    # 3. 开始考试
    print(f"\n3. 开始考试 (POST /api/exams/{paper_id}/start)...")
    start_response = client.post(f'/api/exams/{paper_id}/start', headers=headers)
    
    print(f"   状态码: {start_response.status_code}")
    start_data = start_response.get_json()
    print(f"   响应数据: {start_data}")
    
    if start_response.status_code == 201:
        print(f"\n   ✅ 开始考试成功!")
        session = start_data.get('data', {})
        print(f"   会话 ID: {session.get('id')}")
        
        # 清理：将会话标记为超时
        from app import db
        from app.models.exam import ExamSession
        with app.app_context():
            s = ExamSession.query.get(session.get('id'))
            if s:
                s.status = 'timeout'
                db.session.commit()
                print("   已清理测试会话")
    else:
        print(f"\n   ❌ 开始考试失败!")
        print(f"   错误信息: {start_data.get('error', {}).get('message')}")
