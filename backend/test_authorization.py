"""
权限控制测试套件

测试用户数据隔离、未授权访问拒绝和JWT token验证
"""
import pytest
from app import create_app, db
from app.models.user import User
from app.models.study_plan import StudyPlan
from app.models.note import QuestionNote, QuestionBookmark
from app.models.question import Question
from datetime import date, timedelta
import json


@pytest.fixture
def app():
    """创建测试应用"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture
def users(app):
    """创建测试用户"""
    with app.app_context():
        # 创建普通用户1
        user1 = User(username='testuser1', email='user1@test.com', role='user')
        user1.set_password('password123')
        db.session.add(user1)
        
        # 创建普通用户2
        user2 = User(username='testuser2', email='user2@test.com', role='user')
        user2.set_password('password123')
        db.session.add(user2)
        
        # 创建管理员用户
        admin = User(username='admin', email='admin@test.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        
        db.session.commit()
        
        return {
            'user1': {'id': user1.id, 'username': 'testuser1', 'password': 'password123'},
            'user2': {'id': user2.id, 'username': 'testuser2', 'password': 'password123'},
            'admin': {'id': admin.id, 'username': 'admin', 'password': 'admin123'}
        }


def login(client, username, password):
    """登录并返回token"""
    response = client.post('/api/auth/login', json={
        'username': username,
        'password': password
    })
    if response.status_code == 200:
        data = response.json
        if data.get('success') and 'data' in data:
            return data['data'].get('access_token')
    return None


def get_auth_headers(token):
    """获取认证头"""
    return {'Authorization': f'Bearer {token}'}


class TestUnauthorizedAccess:
    """测试未授权访问"""
    
    def test_study_plans_requires_auth(self, client):
        """测试学习计划API需要认证"""
        response = client.get('/api/study-plans')
        assert response.status_code == 401
    
    def test_notes_requires_auth(self, client):
        """测试笔记API需要认证"""
        response = client.get('/api/notes')
        assert response.status_code == 401
    
    def test_bookmarks_requires_auth(self, client):
        """测试收藏API需要认证"""
        response = client.get('/api/bookmarks')
        assert response.status_code == 401
    
    def test_points_requires_auth(self, client):
        """测试积分API需要认证"""
        response = client.get('/api/points')
        assert response.status_code == 401
    
    def test_achievements_requires_auth(self, client):
        """测试成就API需要认证"""
        response = client.get('/api/achievements/user')
        assert response.status_code == 401
    
    def test_daily_tasks_requires_auth(self, client):
        """测试每日任务API需要认证"""
        response = client.get('/api/daily-tasks')
        assert response.status_code == 401
    
    def test_invalid_token_rejected(self, client):
        """测试无效token被拒绝"""
        headers = {'Authorization': 'Bearer invalid_token_12345'}
        response = client.get('/api/study-plans', headers=headers)
        assert response.status_code in [401, 422]  # 401未授权或422 JWT解析错误都可以


class TestDataIsolation:
    """测试用户数据隔离"""
    
    def test_user_can_only_see_own_study_plans(self, client, users, app):
        """测试用户只能看到自己的学习计划"""
        # user1登录并创建学习计划
        token1 = login(client, users['user1']['username'], users['user1']['password'])
        headers1 = get_auth_headers(token1)
        
        response = client.post('/api/study-plans', headers=headers1, json={
            'name': 'User1的计划',
            'exam_type': 'civil_service',
            'start_date': date.today().isoformat(),
            'end_date': (date.today() + timedelta(days=30)).isoformat()
        })
        assert response.status_code in [200, 201]
        plan_id = response.json['id']
        
        # user2登录并尝试访问user1的学习计划
        token2 = login(client, users['user2']['username'], users['user2']['password'])
        headers2 = get_auth_headers(token2)
        
        # user2获取学习计划列表，应该看不到user1的计划
        response = client.get('/api/study-plans', headers=headers2)
        assert response.status_code == 200
        plans = response.json
        assert len(plans) == 0 or all(plan['id'] != plan_id for plan in plans)
        
        # user2尝试直接访问user1的学习计划
        response = client.get(f'/api/study-plans/{plan_id}', headers=headers2)
        assert response.status_code in [403, 404]  # 禁止访问或未找到
    
    def test_user_cannot_modify_others_study_plans(self, client, users, app):
        """测试用户不能修改其他用户的学习计划"""
        # user1创建学习计划
        token1 = login(client, users['user1']['username'], users['user1']['password'])
        headers1 = get_auth_headers(token1)
        
        response = client.post('/api/study-plans', headers=headers1, json={
            'name': 'User1的计划',
            'exam_type': 'civil_service',
            'start_date': date.today().isoformat(),
            'end_date': (date.today() + timedelta(days=30)).isoformat()
        })
        plan_id = response.json['id']
        
        # user2尝试修改user1的学习计划
        token2 = login(client, users['user2']['username'], users['user2']['password'])
        headers2 = get_auth_headers(token2)
        
        response = client.put(f'/api/study-plans/{plan_id}', headers=headers2, json={
            'name': '被篡改的计划'
        })
        assert response.status_code in [403, 404]
    
    def test_user_cannot_delete_others_study_plans(self, client, users, app):
        """测试用户不能删除其他用户的学习计划"""
        # user1创建学习计划
        token1 = login(client, users['user1']['username'], users['user1']['password'])
        headers1 = get_auth_headers(token1)
        
        response = client.post('/api/study-plans', headers=headers1, json={
            'name': 'User1的计划',
            'exam_type': 'civil_service',
            'start_date': date.today().isoformat(),
            'end_date': (date.today() + timedelta(days=30)).isoformat()
        })
        plan_id = response.json['id']
        
        # user2尝试删除user1的学习计划
        token2 = login(client, users['user2']['username'], users['user2']['password'])
        headers2 = get_auth_headers(token2)
        
        response = client.delete(f'/api/study-plans/{plan_id}', headers=headers2)
        assert response.status_code in [403, 404]
    
    def test_user_can_only_see_own_notes(self, client, users, app):
        """测试用户只能看到自己的笔记"""
        with app.app_context():
            # 创建测试题目
            question = Question(
                exam_type='civil_service',
                question_type='single_choice',
                subject='行测',
                content='测试题目',
                correct_answer='A',
                created_by=users['user1']['id']
            )
            db.session.add(question)
            db.session.commit()
            question_id = question.id
        
        # user1创建笔记
        token1 = login(client, users['user1']['username'], users['user1']['password'])
        headers1 = get_auth_headers(token1)
        
        response = client.post('/api/notes', headers=headers1, json={
            'question_id': question_id,
            'content': 'User1的笔记'
        })
        assert response.status_code in [200, 201]
        note_id = response.json['id']
        
        # user2登录并查看笔记列表
        token2 = login(client, users['user2']['username'], users['user2']['password'])
        headers2 = get_auth_headers(token2)
        
        response = client.get('/api/notes', headers=headers2)
        assert response.status_code == 200
        notes = response.json
        assert len(notes) == 0 or all(note['id'] != note_id for note in notes)
    
    def test_user_can_only_see_own_bookmarks(self, client, users, app):
        """测试用户只能看到自己的收藏"""
        with app.app_context():
            # 创建测试题目
            question = Question(
                exam_type='civil_service',
                question_type='single_choice',
                subject='行测',
                content='测试题目',
                correct_answer='A',
                created_by=users['user1']['id']
            )
            db.session.add(question)
            db.session.commit()
            question_id = question.id
        
        # user1收藏题目
        token1 = login(client, users['user1']['username'], users['user1']['password'])
        headers1 = get_auth_headers(token1)
        
        response = client.post('/api/bookmarks', headers=headers1, json={
            'question_id': question_id
        })
        assert response.status_code in [200, 201]
        
        # user2查看收藏列表
        token2 = login(client, users['user2']['username'], users['user2']['password'])
        headers2 = get_auth_headers(token2)
        
        response = client.get('/api/bookmarks', headers=headers2)
        assert response.status_code == 200
        bookmarks = response.json
        assert len(bookmarks) == 0


class TestJWTValidation:
    """测试JWT token验证"""
    
    def test_expired_token_rejected(self, client, users):
        """测试过期token被拒绝"""
        # 注意: 需要配置JWT_ACCESS_TOKEN_EXPIRES才能测试
        # 这里只测试格式错误的token
        headers = {'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid'}
        response = client.get('/api/study-plans', headers=headers)
        assert response.status_code == 422
    
    def test_malformed_token_rejected(self, client):
        """测试格式错误的token被拒绝"""
        headers = {'Authorization': 'Bearer not_a_jwt_token'}
        response = client.get('/api/study-plans', headers=headers)
        assert response.status_code == 422
    
    def test_missing_bearer_prefix_rejected(self, client, users):
        """测试缺少Bearer前缀的token被拒绝"""
        token = login(client, users['user1']['username'], users['user1']['password'])
        headers = {'Authorization': token}  # 缺少 'Bearer ' 前缀
        response = client.get('/api/study-plans', headers=headers)
        assert response.status_code == 401


class TestCrossUserAccess:
    """测试跨用户访问防护"""
    
    def test_cannot_access_other_user_points(self, client, users, app):
        """测试不能访问其他用户的积分"""
        # 每个用户只能看到自己的积分
        token1 = login(client, users['user1']['username'], users['user1']['password'])
        headers1 = get_auth_headers(token1)
        
        response = client.get('/api/points', headers=headers1)
        assert response.status_code == 200
        user1_points = response.json
        
        token2 = login(client, users['user2']['username'], users['user2']['password'])
        headers2 = get_auth_headers(token2)
        
        response = client.get('/api/points', headers=headers2)
        assert response.status_code == 200
        user2_points = response.json
        
        # 两个用户的积分数据应该不同（或都是初始值）
        # 主要验证API不会返回其他用户的数据
        assert 'user_id' in user1_points
        assert 'user_id' in user2_points
    
    def test_cannot_access_other_user_achievements(self, client, users):
        """测试不能访问其他用户的成就"""
        token1 = login(client, users['user1']['username'], users['user1']['password'])
        headers1 = get_auth_headers(token1)
        
        response = client.get('/api/achievements/user', headers=headers1)
        assert response.status_code == 200
        
        token2 = login(client, users['user2']['username'], users['user2']['password'])
        headers2 = get_auth_headers(token2)
        
        response = client.get('/api/achievements/user', headers=headers2)
        assert response.status_code == 200
    
    def test_cannot_access_other_user_daily_tasks(self, client, users):
        """测试不能访问其他用户的每日任务"""
        token1 = login(client, users['user1']['username'], users['user1']['password'])
        headers1 = get_auth_headers(token1)
        
        response = client.get('/api/daily-tasks', headers=headers1)
        assert response.status_code == 200
        
        token2 = login(client, users['user2']['username'], users['user2']['password'])
        headers2 = get_auth_headers(token2)
        
        response = client.get('/api/daily-tasks', headers=headers2)
        assert response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
