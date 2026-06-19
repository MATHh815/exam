"""安全性验证测试

测试系统的安全特性，包括权限控制、数据隔离、输入验证等
"""
import pytest
from app import create_app, db
from app.models.user import User
from app.models.study_plan import StudyPlan, StudyGoal
from app.models.note import QuestionNote, QuestionBookmark
from app.models.achievement import UserPoints, UserAchievement
from app.models.question import Question
from datetime import date, timedelta
import json

class TestSecurityValidation:
    """安全性验证测试类"""
    
    @pytest.fixture
    def app(self):
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
    def client(self, app):
        """创建测试客户端"""
        return app.test_client()
    
    @pytest.fixture
    def users(self, app):
        """创建测试用户"""
        with app.app_context():
            # 创建两个普通用户
            user1 = User(username='user1', email='user1@test.com')
            user1.set_password('password123')
            
            user2 = User(username='user2', email='user2@test.com')
            user2.set_password('password123')
            
            # 创建管理员用户
            admin = User(username='admin', email='admin@test.com', role='admin')
            admin.set_password('admin123')
            
            db.session.add_all([user1, user2, admin])
            db.session.commit()
            
            return {
                'user1': {'id': user1.id, 'username': 'user1', 'password': 'password123'},
                'user2': {'id': user2.id, 'username': 'user2', 'password': 'password123'},
                'admin': {'id': admin.id, 'username': 'admin', 'password': 'admin123'}
            }
    
    def login(self, client, username, password):
        """登录并获取token"""
        response = client.post('/api/auth/login', json={
            'username': username,
            'password': password
        })
        
        if response.status_code == 200:
            data = response.json
            if data.get('success') and 'data' in data:
                return data['data'].get('access_token')
        return None
    
    def get_auth_headers(self, token):
        """获取认证请求头"""
        return {'Authorization': f'Bearer {token}'}
    
    # ==================== 权限控制测试 ====================
    
    def test_unauthorized_access_returns_401(self, client):
        """测试未授权访问返回401"""
        # 测试需要认证的端点
        endpoints = [
            ('GET', '/api/study-plans'),
            ('GET', '/api/notes'),
            ('GET', '/api/bookmarks'),
            ('GET', '/api/points'),
            ('GET', '/api/achievements/user'),
            ('GET', '/api/daily-tasks'),
        ]
        
        for method, url in endpoints:
            if method == 'GET':
                response = client.get(url)
            elif method == 'POST':
                response = client.post(url, json={})
            
            assert response.status_code == 401, f"{method} {url} 应该返回401"
            print(f"✓ {method} {url} 正确返回401")
    
    def test_user_data_isolation(self, client, users, app):
        """测试用户数据隔离"""
        with app.app_context():
            # 为user1创建学习计划
            plan = StudyPlan(
                user_id=users['user1']['id'],
                name='User1的计划',
                exam_type='civil_service',
                start_date=date.today(),
                end_date=date.today() + timedelta(days=30)
            )
            db.session.add(plan)
            db.session.commit()
            plan_id = plan.id
        
        # user2登录
        token2 = self.login(client, users['user2']['username'], users['user2']['password'])
        headers2 = self.get_auth_headers(token2)
        
        # user2尝试访问user1的学习计划
        response = client.get(f'/api/study-plans/{plan_id}', headers=headers2)
        
        # 应该返回404（找不到）或403（禁止访问）
        assert response.status_code in [403, 404], "用户不应该能访问其他用户的数据"
        print("✓ 用户数据隔离测试通过")
    
    def test_cannot_modify_other_user_data(self, client, users, app):
        """测试不能修改其他用户的数据"""
        with app.app_context():
            # 为user1创建笔记
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
            
            note = QuestionNote(
                user_id=users['user1']['id'],
                question_id=question.id,
                content='User1的笔记'
            )
            db.session.add(note)
            db.session.commit()
            note_id = note.id
        
        # user2登录
        token2 = self.login(client, users['user2']['username'], users['user2']['password'])
        headers2 = self.get_auth_headers(token2)
        
        # user2尝试修改user1的笔记
        response = client.put(
            f'/api/notes/{note_id}',
            headers=headers2,
            json={'content': '被修改的内容'}
        )
        
        # 应该返回403或404
        assert response.status_code in [403, 404], "用户不应该能修改其他用户的数据"
        print("✓ 数据修改权限测试通过")
    
    def test_cannot_delete_other_user_data(self, client, users, app):
        """测试不能删除其他用户的数据"""
        with app.app_context():
            # 为user1创建收藏
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
            
            bookmark = QuestionBookmark(
                user_id=users['user1']['id'],
                question_id=question.id
            )
            db.session.add(bookmark)
            db.session.commit()
            bookmark_id = bookmark.id
        
        # user2登录
        token2 = self.login(client, users['user2']['username'], users['user2']['password'])
        headers2 = self.get_auth_headers(token2)
        
        # user2尝试删除user1的收藏
        response = client.delete(f'/api/bookmarks/{bookmark_id}', headers=headers2)
        
        # 应该返回403或404
        assert response.status_code in [403, 404], "用户不应该能删除其他用户的数据"
        print("✓ 数据删除权限测试通过")
    
    # ==================== 输入验证测试 ====================
    
    def test_required_fields_validation(self, client, users):
        """测试必填字段验证"""
        token = self.login(client, users['user1']['username'], users['user1']['password'])
        headers = self.get_auth_headers(token)
        
        # 测试创建学习计划缺少必填字段
        response = client.post('/api/study-plans', headers=headers, json={
            'name': '测试计划'
            # 缺少 exam_type, start_date, end_date
        })
        
        assert response.status_code == 400, "缺少必填字段应该返回400"
        print("✓ 必填字段验证测试通过")
    
    def test_field_type_validation(self, client, users):
        """测试字段类型验证"""
        token = self.login(client, users['user1']['username'], users['user1']['password'])
        headers = self.get_auth_headers(token)
        
        # 测试日期字段类型错误
        response = client.post('/api/study-plans', headers=headers, json={
            'name': '测试计划',
            'exam_type': 'civil_service',
            'start_date': 'invalid-date',  # 无效日期格式
            'end_date': '2025-12-31'
        })
        
        assert response.status_code == 400, "字段类型错误应该返回400"
        print("✓ 字段类型验证测试通过")
    
    def test_field_length_validation(self, client, users):
        """测试字段长度验证"""
        token = self.login(client, users['user1']['username'], users['user1']['password'])
        headers = self.get_auth_headers(token)
        
        # 测试笔记内容过长
        long_content = 'x' * 10000  # 超过5000字符限制
        
        with app.app_context():
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
        
        response = client.post('/api/notes', headers=headers, json={
            'question_id': question_id,
            'content': long_content
        })
        
        assert response.status_code == 400, "字段长度超限应该返回400"
        print("✓ 字段长度验证测试通过")
    
    def test_sql_injection_prevention(self, client, users):
        """测试SQL注入防护"""
        token = self.login(client, users['user1']['username'], users['user1']['password'])
        headers = self.get_auth_headers(token)
        
        # 尝试SQL注入
        malicious_input = "'; DROP TABLE users; --"
        
        response = client.post('/api/study-plans', headers=headers, json={
            'name': malicious_input,
            'exam_type': 'civil_service',
            'start_date': date.today().isoformat(),
            'end_date': (date.today() + timedelta(days=30)).isoformat()
        })
        
        # 应该正常处理（作为普通字符串）或返回验证错误
        assert response.status_code in [200, 201, 400], "SQL注入应该被防护"
        
        # 验证users表仍然存在
        with app.app_context():
            users_count = User.query.count()
            assert users_count > 0, "users表不应该被删除"
        
        print("✓ SQL注入防护测试通过")
    
    def test_xss_prevention(self, client, users, app):
        """测试XSS防护"""
        token = self.login(client, users['user1']['username'], users['user1']['password'])
        headers = self.get_auth_headers(token)
        
        # 尝试XSS攻击
        xss_input = '<script>alert("XSS")</script>'
        
        with app.app_context():
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
        
        response = client.post('/api/notes', headers=headers, json={
            'question_id': question_id,
            'content': xss_input
        })
        
        # 应该正常创建（后端存储原始内容，前端负责转义）
        assert response.status_code in [200, 201], "XSS内容应该被正常存储"
        
        # 获取笔记内容
        with app.app_context():
            note = QuestionNote.query.filter_by(question_id=question_id).first()
            # 内容应该被存储（不应该被执行）
            assert note is not None, "笔记应该被创建"
            assert xss_input in note.content, "XSS内容应该被存储为普通文本"
        
        print("✓ XSS防护测试通过")
    
    def test_email_validation(self, client):
        """测试邮箱格式验证"""
        # 测试无效邮箱格式
        invalid_emails = [
            'invalid',
            'invalid@',
            '@invalid.com',
            'invalid@.com',
            'invalid@com',
        ]
        
        for email in invalid_emails:
            response = client.post('/api/auth/register', json={
                'username': f'test_{email}',
                'email': email,
                'password': 'password123'
            })
            
            assert response.status_code == 400, f"无效邮箱 {email} 应该返回400"
        
        print("✓ 邮箱格式验证测试通过")
    
    # ==================== 边界值测试 ====================
    
    def test_boundary_values(self, client, users):
        """测试边界值"""
        token = self.login(client, users['user1']['username'], users['user1']['password'])
        headers = self.get_auth_headers(token)
        
        # 测试负数
        response = client.post('/api/study-plans', headers=headers, json={
            'name': '测试计划',
            'exam_type': 'civil_service',
            'start_date': date.today().isoformat(),
            'end_date': (date.today() + timedelta(days=30)).isoformat(),
            'goals': [{
                'goal_type': 'daily_practice',
                'target_value': -10,  # 负数
                'period_start': date.today().isoformat(),
                'period_end': (date.today() + timedelta(days=7)).isoformat()
            }]
        })
        
        assert response.status_code == 400, "负数目标值应该返回400"
        
        # 测试零值
        response = client.post('/api/study-plans', headers=headers, json={
            'name': '测试计划',
            'exam_type': 'civil_service',
            'start_date': date.today().isoformat(),
            'end_date': (date.today() + timedelta(days=30)).isoformat(),
            'goals': [{
                'goal_type': 'daily_practice',
                'target_value': 0,  # 零值
                'period_start': date.today().isoformat(),
                'period_end': (date.today() + timedelta(days=7)).isoformat()
            }]
        })
        
        assert response.status_code == 400, "零值目标应该返回400"
        
        print("✓ 边界值验证测试通过")
    
    def test_date_range_validation(self, client, users):
        """测试日期范围验证"""
        token = self.login(client, users['user1']['username'], users['user1']['password'])
        headers = self.get_auth_headers(token)
        
        # 测试结束日期早于开始日期
        response = client.post('/api/study-plans', headers=headers, json={
            'name': '测试计划',
            'exam_type': 'civil_service',
            'start_date': '2025-12-31',
            'end_date': '2025-01-01'  # 早于开始日期
        })
        
        assert response.status_code == 400, "结束日期早于开始日期应该返回400"
        print("✓ 日期范围验证测试通过")

def run_tests():
    """运行所有安全性测试"""
    print("=" * 80)
    print("安全性验证测试")
    print("=" * 80)
    print()
    
    pytest.main([__file__, '-v', '--tb=short'])

if __name__ == '__main__':
    run_tests()
