"""数据导入导出服务测试"""
import pytest
import json
from hypothesis import given, settings, strategies as st, HealthCheck
from datetime import datetime

from app import db
from app.models import User, Question, ExamPaper, PracticeRecord, WrongQuestion
from app.services import DataService


# 生成器策略
@st.composite
def user_data(draw):
    """生成用户数据"""
    username = draw(st.text(min_size=3, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd'))))
    email = f"{username.lower()}@example.com"
    return {
        'username': username,
        'email': email,
        'nickname': draw(st.text(min_size=1, max_size=50)),
        'role': draw(st.sampled_from(['user', 'admin'])),
        'password': 'test123456'
    }


@st.composite
def question_data(draw, user_id):
    """生成题目数据"""
    return {
        'exam_type': draw(st.sampled_from(['civil_service', 'postgraduate', 'public_institution'])),
        'question_type': draw(st.sampled_from(['single_choice', 'multiple_choice', 'true_false'])),
        'subject': draw(st.sampled_from(['行测', '申论', '数学', '英语'])),
        'chapter': draw(st.text(min_size=1, max_size=50)),
        'difficulty': draw(st.integers(min_value=1, max_value=5)),
        'content': draw(st.text(min_size=10, max_size=200)),
        'options': {'A': '选项A', 'B': '选项B', 'C': '选项C', 'D': '选项D'},
        'correct_answer': draw(st.sampled_from(['A', 'B', 'C', 'D'])),
        'explanation': draw(st.text(min_size=5, max_size=100)),
        'tags': draw(st.lists(st.text(min_size=1, max_size=20), min_size=0, max_size=5)),
        'created_by': user_id
    }


class TestDataService:
    """数据服务测试类"""
    
    def test_export_json_basic(self, app, db_session, admin_user, sample_question):
        """测试基本 JSON 导出功能"""
        with app.app_context():
            json_data = DataService.export_to_json()
            
            # 验证是有效的 JSON
            data = json.loads(json_data)
            
            # 验证结构
            assert 'metadata' in data
            assert 'data' in data
            assert 'export_time' in data['metadata']
            assert 'version' in data['metadata']
            
            # 验证包含用户和题目数据
            assert 'users' in data['data']
            assert 'questions' in data['data']
            assert len(data['data']['users']) >= 1
            assert len(data['data']['questions']) >= 1
    
    def test_export_sql_basic(self, app, db_session, admin_user, sample_question):
        """测试基本 SQL 导出功能"""
        with app.app_context():
            sql_data = DataService.export_to_sql()
            
            # 验证包含 SQL 语句
            assert 'INSERT INTO' in sql_data
            assert 'users' in sql_data
            assert 'questions' in sql_data
    
    def test_import_json_basic(self, app, db_session, admin_user):
        """测试基本 JSON 导入功能"""
        with app.app_context():
            # 先导出
            json_data = DataService.export_to_json()
            
            # 清空数据
            User.query.delete()
            db.session.commit()
            
            # 导入
            stats = DataService.import_from_json(json_data)
            
            # 验证导入成功
            assert 'users' in stats
            assert stats['users'] >= 1
            assert User.query.count() >= 1
    
    # Feature: exam-system, Property 15: 数据导出往返一致性
    # **Validates: Requirements 8.5**
    @settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=2000)
    @given(
        user_count=st.integers(min_value=1, max_value=3),
        question_count=st.integers(min_value=1, max_value=5)
    )
    def test_property_json_roundtrip_consistency(self, app, db_session, user_count, question_count):
        """属性测试：JSON 导出导入往返一致性
        
        对于任意数据集，导出后再导入应该得到相同的数据
        """
        with app.app_context():
            # 清空数据库
            db.session.query(Question).delete()
            db.session.query(User).delete()
            db.session.commit()
            
            # 生成随机用户
            users = []
            for i in range(user_count):
                user = User(
                    username=f'user_{i}_{datetime.utcnow().timestamp()}',
                    email=f'user_{i}_{datetime.utcnow().timestamp()}@example.com',
                    nickname=f'User {i}',
                    role='user' if i > 0 else 'admin'
                )
                user.set_password('password123')
                db.session.add(user)
                users.append(user)
            
            db.session.commit()
            
            # 生成随机题目
            questions = []
            for i in range(question_count):
                question = Question(
                    exam_type='civil_service',
                    question_type='single_choice',
                    subject='行测',
                    chapter=f'章节{i}',
                    difficulty=(i % 5) + 1,
                    content=f'题目内容{i}',
                    options={'A': '选项A', 'B': '选项B'},
                    correct_answer='A',
                    explanation=f'解析{i}',
                    tags=[f'标签{i}'],
                    created_by=users[0].id
                )
                db.session.add(question)
                questions.append(question)
            
            db.session.commit()
            
            # 记录原始数据
            original_user_count = User.query.count()
            original_question_count = Question.query.count()
            original_usernames = {u.username for u in User.query.all()}
            original_question_contents = {q.content for q in Question.query.all()}
            
            # 导出为 JSON
            json_data = DataService.export_to_json()
            
            # 清空数据库
            db.session.query(Question).delete()
            db.session.query(User).delete()
            db.session.commit()
            
            # 验证数据已清空
            assert User.query.count() == 0
            assert Question.query.count() == 0
            
            # 导入数据
            import_stats = DataService.import_from_json(json_data)
            
            # 验证数据一致性
            assert User.query.count() == original_user_count, \
                f"用户数量不一致: 期望 {original_user_count}, 实际 {User.query.count()}"
            
            assert Question.query.count() == original_question_count, \
                f"题目数量不一致: 期望 {original_question_count}, 实际 {Question.query.count()}"
            
            # 验证用户名一致
            imported_usernames = {u.username for u in User.query.all()}
            assert imported_usernames == original_usernames, \
                "用户名集合不一致"
            
            # 验证题目内容一致
            imported_question_contents = {q.content for q in Question.query.all()}
            assert imported_question_contents == original_question_contents, \
                "题目内容集合不一致"
    
    # Feature: exam-system, Property 15: 数据导出往返一致性
    # **Validates: Requirements 8.5**
    @settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=2000)
    @given(
        user_count=st.integers(min_value=1, max_value=3),
        question_count=st.integers(min_value=1, max_value=5)
    )
    def test_property_sql_roundtrip_consistency(self, app, db_session, user_count, question_count):
        """属性测试：SQL 导出导入往返一致性
        
        对于任意数据集，导出为 SQL 后再导入应该得到相同的数据
        """
        with app.app_context():
            # 清空数据库
            db.session.query(Question).delete()
            db.session.query(User).delete()
            db.session.commit()
            
            # 生成随机用户
            users = []
            for i in range(user_count):
                user = User(
                    username=f'sqluser_{i}_{datetime.utcnow().timestamp()}',
                    email=f'sqluser_{i}_{datetime.utcnow().timestamp()}@example.com',
                    nickname=f'SQL User {i}',
                    role='user' if i > 0 else 'admin'
                )
                user.set_password('password123')
                db.session.add(user)
                users.append(user)
            
            db.session.commit()
            
            # 生成随机题目
            questions = []
            for i in range(question_count):
                question = Question(
                    exam_type='postgraduate',
                    question_type='multiple_choice',
                    subject='数学',
                    chapter=f'SQL章节{i}',
                    difficulty=(i % 5) + 1,
                    content=f'SQL题目内容{i}',
                    options={'A': '选项A', 'B': '选项B', 'C': '选项C'},
                    correct_answer='A',
                    explanation=f'SQL解析{i}',
                    tags=[f'SQL标签{i}'],
                    created_by=users[0].id
                )
                db.session.add(question)
                questions.append(question)
            
            db.session.commit()
            
            # 记录原始数据
            original_user_count = User.query.count()
            original_question_count = Question.query.count()
            original_usernames = {u.username for u in User.query.all()}
            original_question_contents = {q.content for q in Question.query.all()}
            
            # 导出为 SQL
            sql_data = DataService.export_to_sql()
            
            # 清空数据库
            db.session.query(Question).delete()
            db.session.query(User).delete()
            db.session.commit()
            
            # 验证数据已清空
            assert User.query.count() == 0
            assert Question.query.count() == 0
            
            # 导入数据
            import_stats = DataService.import_from_sql(sql_data)
            
            # 验证数据一致性
            assert User.query.count() == original_user_count, \
                f"用户数量不一致: 期望 {original_user_count}, 实际 {User.query.count()}"
            
            assert Question.query.count() == original_question_count, \
                f"题目数量不一致: 期望 {original_question_count}, 实际 {Question.query.count()}"
            
            # 验证用户名一致
            imported_usernames = {u.username for u in User.query.all()}
            assert imported_usernames == original_usernames, \
                "用户名集合不一致"
            
            # 验证题目内容一致
            imported_question_contents = {q.content for q in Question.query.all()}
            assert imported_question_contents == original_question_contents, \
                "题目内容集合不一致"
