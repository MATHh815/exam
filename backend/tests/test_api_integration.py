"""API 集成测试

测试完整的用户流程：
- 用户注册登录流程
- 练习流程
- 考试流程
"""
import pytest
import json
from app.models.question import Question
from app.models.exam import ExamPaper, ExamPaperQuestion


class TestUserAuthFlow:
    """测试用户注册登录流程 - 需求 1.1, 1.2"""
    
    def test_complete_registration_and_login_flow(self, client, app):
        """测试完整的注册和登录流程"""
        with app.app_context():
            # 1. 注册新用户
            register_data = {
                'username': 'integrationuser',
                'password': 'testpass123',
                'email': 'integration@example.com',
                'nickname': 'Integration User'
            }
            
            response = client.post(
                '/api/auth/register',
                data=json.dumps(register_data),
                content_type='application/json'
            )
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['user']['username'] == 'integrationuser'
            # Email is not included in response for privacy
            assert 'id' in data['data']['user']
            
            # 2. 使用注册的凭证登录
            login_data = {
                'username': 'integrationuser',
                'password': 'testpass123'
            }
            
            response = client.post(
                '/api/auth/login',
                data=json.dumps(login_data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'access_token' in data['data']
            assert 'refresh_token' in data['data']
            assert data['data']['user']['username'] == 'integrationuser'
            
            access_token = data['data']['access_token']
            
            # 3. 使用访问令牌获取用户信息
            response = client.get(
                '/api/auth/profile',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['user']['username'] == 'integrationuser'
            
            # 4. 更新用户信息
            update_data = {
                'nickname': 'Updated Integration User'
            }
            
            response = client.put(
                '/api/auth/profile',
                data=json.dumps(update_data),
                content_type='application/json',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['user']['nickname'] == 'Updated Integration User'
            
            # 5. 验证更新后的信息
            response = client.get(
                '/api/auth/profile',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['data']['user']['nickname'] == 'Updated Integration User'
    
    def test_registration_with_duplicate_username(self, client, app, sample_user):
        """测试注册重复用户名"""
        with app.app_context():
            register_data = {
                'username': 'testuser',  # 已存在的用户名
                'password': 'testpass123',
                'email': 'newemail@example.com'
            }
            
            response = client.post(
                '/api/auth/register',
                data=json.dumps(register_data),
                content_type='application/json'
            )
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['success'] is False
            assert '用户名已存在' in data['error']['message']
    
    def test_login_with_wrong_password(self, client, app, sample_user):
        """测试使用错误密码登录"""
        with app.app_context():
            login_data = {
                'username': 'testuser',
                'password': 'wrongpassword'
            }
            
            response = client.post(
                '/api/auth/login',
                data=json.dumps(login_data),
                content_type='application/json'
            )
            
            assert response.status_code == 401
            data = json.loads(response.data)
            assert data['success'] is False


class TestPracticeFlow:
    """测试练习流程 - 需求 3.1, 3.2"""
    
    def test_complete_practice_flow(self, client, app, sample_user, db_session):
        """测试完整的练习流程"""
        with app.app_context():
            # 1. 登录获取令牌
            login_data = {
                'username': 'testuser',
                'password': 'password123'
            }
            
            response = client.post(
                '/api/auth/login',
                data=json.dumps(login_data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            access_token = data['data']['access_token']
            
            # 2. 创建测试题目
            from app.models.question import Question
            questions = []
            for i in range(5):
                question = Question(
                    exam_type='civil_service',
                    question_type='single_choice',
                    subject='行测',
                    chapter='数量关系',
                    difficulty=3,
                    content=f'测试题目 {i+1}',
                    options={'A': '选项A', 'B': '选项B', 'C': '选项C', 'D': '选项D'},
                    correct_answer='A',
                    explanation='这是解析',
                    tags=['测试'],
                    created_by=sample_user.id
                )
                db_session.session.add(question)
                questions.append(question)
            
            db_session.session.commit()
            
            # 3. 开始练习
            practice_data = {
                'count': 3,
                'exam_type': 'civil_service',
                'subject': '行测'
            }
            
            response = client.post(
                '/api/practice/start',
                data=json.dumps(practice_data),
                content_type='application/json',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert len(data['data']['questions']) <= 3
            assert data['data']['count'] <= 3
            
            practice_questions = data['data']['questions']
            
            # 4. 提交答案（正确答案）
            if practice_questions:
                question_id = practice_questions[0]['id']
                submit_data = {
                    'question_id': question_id,
                    'user_answer': 'A',  # 正确答案
                    'time_spent': 30
                }
                
                response = client.post(
                    '/api/practice/submit',
                    data=json.dumps(submit_data),
                    content_type='application/json',
                    headers={'Authorization': f'Bearer {access_token}'}
                )
                
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['success'] is True
                assert data['data']['is_correct'] is True
                assert data['data']['correct_answer'] == 'A'
                assert 'explanation' in data['data']
            
            # 5. 提交错误答案
            if len(practice_questions) > 1:
                question_id = practice_questions[1]['id']
                submit_data = {
                    'question_id': question_id,
                    'user_answer': 'B',  # 错误答案
                    'time_spent': 25
                }
                
                response = client.post(
                    '/api/practice/submit',
                    data=json.dumps(submit_data),
                    content_type='application/json',
                    headers={'Authorization': f'Bearer {access_token}'}
                )
                
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['success'] is True
                assert data['data']['is_correct'] is False
                assert data['data']['correct_answer'] == 'A'
            
            # 6. 查看练习历史
            response = client.get(
                '/api/practice/history?page=1&page_size=10',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'records' in data['data']
            assert data['data']['total'] >= 2  # 至少有两条记录
            
            # 7. 查看错题本（应该包含错误的题目）
            response = client.get(
                '/api/practice/wrong-book',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert 'wrong_questions' in data['data']
            # 应该至少有一个错题
            if len(practice_questions) > 1:
                assert data['data']['count'] >= 1


class TestExamFlow:
    """测试考试流程 - 需求 4.1, 4.3"""
    
    def test_complete_exam_flow(self, client, app, sample_user, admin_user, db_session):
        """测试完整的考试流程"""
        with app.app_context():
            # 1. 管理员登录
            login_data = {
                'username': 'admin',
                'password': 'admin123'
            }
            
            response = client.post(
                '/api/auth/login',
                data=json.dumps(login_data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            admin_token = data['data']['access_token']
            
            # 2. 创建测试题目
            questions = []
            for i in range(5):
                question = Question(
                    exam_type='civil_service',
                    question_type='single_choice',
                    subject='行测',
                    chapter='数量关系',
                    difficulty=3,
                    content=f'考试题目 {i+1}',
                    options={'A': '选项A', 'B': '选项B', 'C': '选项C', 'D': '选项D'},
                    correct_answer='A',
                    explanation='这是解析',
                    tags=['考试'],
                    created_by=admin_user.id
                )
                db_session.session.add(question)
                questions.append(question)
            
            db_session.session.commit()
            
            # 3. 创建试卷
            paper_data = {
                'name': '集成测试试卷',
                'exam_type': 'civil_service',
                'duration': 60,
                'description': '这是一个测试试卷',
                'total_score': 100,
                'pass_score': 60
            }
            
            response = client.post(
                '/api/exams',
                data=json.dumps(paper_data),
                content_type='application/json',
                headers={'Authorization': f'Bearer {admin_token}'}
            )
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['success'] is True
            paper_id = data['data']['id']
            
            # 4. 添加题目到试卷
            for idx, question in enumerate(questions):
                question_data = {
                    'question_id': question.id,
                    'order': idx + 1,
                    'score': 20
                }
                
                response = client.post(
                    f'/api/exams/{paper_id}/questions',
                    data=json.dumps(question_data),
                    content_type='application/json',
                    headers={'Authorization': f'Bearer {admin_token}'}
                )
                
                assert response.status_code == 201
            
            # 5. 发布试卷
            response = client.post(
                f'/api/exams/{paper_id}/publish',
                headers={'Authorization': f'Bearer {admin_token}'}
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['is_published'] is True
            
            # 6. 普通用户登录
            login_data = {
                'username': 'testuser',
                'password': 'password123'
            }
            
            response = client.post(
                '/api/auth/login',
                data=json.dumps(login_data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            user_token = data['data']['access_token']
            
            # 7. 开始考试
            response = client.post(
                f'/api/exams/{paper_id}/start',
                headers={'Authorization': f'Bearer {user_token}'}
            )
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['success'] is True
            session_id = data['data']['id']
            assert data['data']['status'] == 'in_progress'
            
            # 8. 提交答案
            for question in questions[:3]:  # 提交前3题
                answer_data = {
                    'question_id': question.id,
                    'answer': 'A'  # 正确答案
                }
                
                response = client.post(
                    f'/api/exams/sessions/{session_id}/answer',
                    data=json.dumps(answer_data),
                    content_type='application/json',
                    headers={'Authorization': f'Bearer {user_token}'}
                )
                
                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['success'] is True
            
            # 9. 提交试卷
            response = client.post(
                f'/api/exams/sessions/{session_id}/submit',
                headers={'Authorization': f'Bearer {user_token}'}
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            result_id = data['data']['id']
            assert 'score' in data['data']
            assert 'correct_count' in data['data']
            assert 'accuracy' in data['data']
            
            # 验证成绩计算
            # 前3题答对，每题20分，应该得60分
            assert data['data']['score'] == 60
            assert data['data']['correct_count'] == 3
            
            # 10. 查看考试结果
            response = client.get(
                f'/api/exams/results/{result_id}',
                headers={'Authorization': f'Bearer {user_token}'}
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['score'] == 60
            assert 'details' in data['data']
            
            # 11. 查看考试历史
            response = client.get(
                '/api/exams/results?page=1&page_size=10',
                headers={'Authorization': f'Bearer {user_token}'}
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['data']['total'] >= 1
            assert len(data['data']['results']) >= 1


class TestAuthenticationAndAuthorization:
    """测试认证和授权"""
    
    def test_access_protected_route_without_token(self, client, app):
        """测试未提供令牌访问受保护路由"""
        with app.app_context():
            response = client.get('/api/auth/profile')
            
            assert response.status_code == 401
    
    def test_access_admin_route_as_regular_user(self, client, app, sample_user):
        """测试普通用户访问管理员路由"""
        with app.app_context():
            # 登录普通用户
            login_data = {
                'username': 'testuser',
                'password': 'password123'
            }
            
            response = client.post(
                '/api/auth/login',
                data=json.dumps(login_data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            user_token = data['data']['access_token']
            
            # 尝试创建试卷（管理员权限）
            paper_data = {
                'name': '测试试卷',
                'exam_type': 'civil_service',
                'duration': 60
            }
            
            response = client.post(
                '/api/exams',
                data=json.dumps(paper_data),
                content_type='application/json',
                headers={'Authorization': f'Bearer {user_token}'}
            )
            
            assert response.status_code == 403


class TestErrorHandling:
    """测试错误处理"""
    
    def test_missing_required_fields_in_registration(self, client, app):
        """测试注册时缺少必填字段"""
        with app.app_context():
            register_data = {
                'username': 'testuser'
                # 缺少 password 和 email
            }
            
            response = client.post(
                '/api/auth/register',
                data=json.dumps(register_data),
                content_type='application/json'
            )
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['success'] is False
            assert 'error' in data
    
    def test_submit_answer_for_nonexistent_question(self, client, app, sample_user):
        """测试提交不存在题目的答案"""
        with app.app_context():
            # 登录
            login_data = {
                'username': 'testuser',
                'password': 'password123'
            }
            
            response = client.post(
                '/api/auth/login',
                data=json.dumps(login_data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            access_token = data['data']['access_token']
            
            # 提交不存在的题目
            submit_data = {
                'question_id': 99999,
                'user_answer': 'A',
                'time_spent': 30
            }
            
            response = client.post(
                '/api/practice/submit',
                data=json.dumps(submit_data),
                content_type='application/json',
                headers={'Authorization': f'Bearer {access_token}'}
            )
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['success'] is False
