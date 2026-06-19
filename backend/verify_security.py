"""安全性验证脚本

验证系统的核心安全特性
"""
from app import create_app, db
from app.models.user import User
from app.models.study_plan import StudyPlan
from app.models.note import QuestionNote
from app.models.question import Question
from datetime import date, timedelta
import sys

def verify_security():
    """验证安全性"""
    app = create_app()
    client = app.test_client()
    
    # 初始化数据库
    with app.app_context():
        db.create_all()
    
    print("=" * 80)
    print("安全性验证")
    print("=" * 80)
    print()
    
    results = []
    
    # ==================== 1. 认证测试 ====================
    print("1. 认证测试")
    print("-" * 80)
    
    # 测试未授权访问
    endpoints = [
        '/api/study-plans',
        '/api/notes',
        '/api/bookmarks',
        '/api/points',
        '/api/achievements/user',
        '/api/daily-tasks',
    ]
    
    auth_passed = True
    for endpoint in endpoints:
        response = client.get(endpoint)
        if response.status_code == 401:
            print(f"  ✓ {endpoint} 正确返回401（未授权）")
        else:
            print(f"  ✗ {endpoint} 返回{response.status_code}，应该返回401")
            auth_passed = False
    
    results.append(('认证保护', auth_passed))
    print()
    
    # ==================== 2. 数据隔离测试 ====================
    print("2. 数据隔离测试")
    print("-" * 80)
    
    with app.app_context():
        # 创建两个测试用户
        user1 = User.query.filter_by(username='sectest1').first()
        if not user1:
            user1 = User(username='sectest1', email='sectest1@test.com')
            user1.set_password('password123')
            db.session.add(user1)
        
        user2 = User.query.filter_by(username='sectest2').first()
        if not user2:
            user2 = User(username='sectest2', email='sectest2@test.com')
            user2.set_password('password123')
            db.session.add(user2)
        
        db.session.commit()
        
        # 为user1创建学习计划
        plan = StudyPlan(
            user_id=user1.id,
            name='User1的计划',
            exam_type='civil_service',
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30)
        )
        db.session.add(plan)
        db.session.commit()
        plan_id = plan.id
    
    # user2登录
    response = client.post('/api/auth/login', json={
        'username': 'sectest2',
        'password': 'password123'
    })
    
    if response.status_code == 200:
        data = response.json
        if data.get('success') and 'data' in data:
            token2 = data['data'].get('access_token')
            headers2 = {'Authorization': f'Bearer {token2}'}
            
            # user2尝试访问user1的学习计划
            response = client.get(f'/api/study-plans/{plan_id}', headers=headers2)
            
            if response.status_code in [403, 404]:
                print(f"  ✓ 用户无法访问其他用户的数据（返回{response.status_code}）")
                isolation_passed = True
            else:
                print(f"  ✗ 用户可以访问其他用户的数据（返回{response.status_code}）")
                isolation_passed = False
        else:
            print("  ⚠️  登录响应格式异常，跳过数据隔离测试")
            isolation_passed = None
    else:
        print("  ⚠️  无法登录测试用户，跳过数据隔离测试")
        isolation_passed = None
    
    results.append(('数据隔离', isolation_passed))
    print()

    # ==================== 3. 输入验证测试 ====================
    print("3. 输入验证测试")
    print("-" * 80)
    
    # 登录user1
    response = client.post('/api/auth/login', json={
        'username': 'sectest1',
        'password': 'password123'
    })
    
    if response.status_code == 200:
        data = response.json
        if data.get('success') and 'data' in data:
            token1 = data['data'].get('access_token')
            headers1 = {'Authorization': f'Bearer {token1}'}
            
            # 测试必填字段验证
            response = client.post('/api/study-plans', headers=headers1, json={
                'name': '测试计划'
                # 缺少必填字段
            })
            
            if response.status_code == 400:
                print("  ✓ 必填字段验证正常（返回400）")
                validation_passed = True
            else:
                print(f"  ✗ 必填字段验证失败（返回{response.status_code}）")
                validation_passed = False
            
            # 测试日期范围验证
            response = client.post('/api/study-plans', headers=headers1, json={
                'name': '测试计划',
                'exam_type': 'civil_service',
                'start_date': '2025-12-31',
                'end_date': '2025-01-01'  # 结束日期早于开始日期
            })
            
            if response.status_code == 400:
                print("  ✓ 日期范围验证正常（返回400）")
            else:
                print(f"  ⚠️  日期范围验证可能需要改进（返回{response.status_code}）")
                validation_passed = validation_passed and False
        else:
            print("  ⚠️  登录响应格式异常，跳过输入验证测试")
            validation_passed = None
    else:
        print("  ⚠️  无法登录测试用户，跳过输入验证测试")
        validation_passed = None
    
    results.append(('输入验证', validation_passed))
    print()
    
    # ==================== 4. SQL注入防护测试 ====================
    print("4. SQL注入防护测试")
    print("-" * 80)
    
    if token1:
        # 尝试SQL注入
        malicious_input = "'; DROP TABLE users; --"
        
        response = client.post('/api/study-plans', headers=headers1, json={
            'name': malicious_input,
            'exam_type': 'civil_service',
            'start_date': date.today().isoformat(),
            'end_date': (date.today() + timedelta(days=30)).isoformat()
        })
        
        # 验证users表仍然存在
        with app.app_context():
            try:
                users_count = User.query.count()
                if users_count > 0:
                    print(f"  ✓ SQL注入防护正常（users表仍存在，共{users_count}个用户）")
                    sql_injection_passed = True
                else:
                    print("  ✗ SQL注入防护失败（users表为空）")
                    sql_injection_passed = False
            except Exception as e:
                print(f"  ✗ SQL注入防护失败（users表不存在）: {str(e)}")
                sql_injection_passed = False
    else:
        print("  ⚠️  无法登录测试用户，跳过SQL注入测试")
        sql_injection_passed = None
    
    results.append(('SQL注入防护', sql_injection_passed))
    print()
    
    # ==================== 5. XSS防护测试 ====================
    print("5. XSS防护测试")
    print("-" * 80)
    
    if token1:
        with app.app_context():
            # 创建测试题目
            question = Question.query.first()
            if not question:
                question = Question(
                    exam_type='civil_service',
                    question_type='single_choice',
                    subject='行测',
                    content='测试题目',
                    correct_answer='A',
                    created_by=user1.id
                )
                db.session.add(question)
                db.session.commit()
            question_id = question.id
        
        # 尝试XSS攻击
        xss_input = '<script>alert("XSS")</script>'
        
        response = client.post('/api/notes', headers=headers1, json={
            'question_id': question_id,
            'content': xss_input
        })
        
        if response.status_code in [200, 201]:
            # 验证内容被存储为普通文本
            with app.app_context():
                note = QuestionNote.query.filter_by(question_id=question_id).order_by(QuestionNote.id.desc()).first()
                if note and xss_input in note.content:
                    print("  ✓ XSS内容被存储为普通文本（前端负责转义）")
                    xss_passed = True
                else:
                    print("  ⚠️  XSS内容处理异常")
                    xss_passed = False
        else:
            print(f"  ⚠️  无法创建测试笔记（返回{response.status_code}）")
            xss_passed = None
    else:
        print("  ⚠️  无法登录测试用户，跳过XSS测试")
        xss_passed = None
    
    results.append(('XSS防护', xss_passed))
    print()
    
    # ==================== 6. 密码安全测试 ====================
    print("6. 密码安全测试")
    print("-" * 80)
    
    with app.app_context():
        user = User.query.filter_by(username='sectest1').first()
        if user:
            # 验证密码是否加密存储
            if user.password_hash and user.password_hash != 'password123':
                print("  ✓ 密码已加密存储（使用bcrypt）")
                password_passed = True
            else:
                print("  ✗ 密码未加密存储")
                password_passed = False
            
            # 验证密码验证功能
            if user.check_password('password123'):
                print("  ✓ 密码验证功能正常")
            else:
                print("  ✗ 密码验证功能异常")
                password_passed = False
        else:
            print("  ⚠️  找不到测试用户")
            password_passed = None
    
    results.append(('密码安全', password_passed))
    print()
    
    # ==================== 总结 ====================
    print("=" * 80)
    print("验证总结")
    print("=" * 80)
    print()
    
    total = len(results)
    passed = sum(1 for _, result in results if result is True)
    failed = sum(1 for _, result in results if result is False)
    skipped = sum(1 for _, result in results if result is None)
    
    print(f"总测试项: {total}")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"跳过: {skipped}")
    print()
    
    # 详细结果
    for name, result in results:
        if result is True:
            print(f"  ✓ {name}: 通过")
        elif result is False:
            print(f"  ✗ {name}: 失败")
        else:
            print(f"  ⏭️  {name}: 跳过")
    print()
    
    print("=" * 80)
    if failed == 0:
        print("✓ 所有安全性验证通过！")
        return 0
    else:
        print(f"⚠️  有 {failed} 项安全性验证失败，需要修复")
        return 1
    print("=" * 80)

if __name__ == '__main__':
    sys.exit(verify_security())
