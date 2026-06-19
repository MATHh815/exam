"""Pytest 配置和 fixtures"""
import pytest
from app import create_app, db
from app.models.user import User


@pytest.fixture(scope='function')
def app():
    """创建测试应用"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """创建数据库会话"""
    with app.app_context():
        yield db


@pytest.fixture
def sample_user(db_session):
    """创建示例用户"""
    user = User(
        username='testuser',
        email='test@example.com',
        nickname='Test User'
    )
    user.set_password('password123')
    db_session.session.add(user)
    db_session.session.commit()
    return user


@pytest.fixture
def admin_user(db_session):
    """创建管理员用户"""
    user = User(
        username='admin',
        email='admin@example.com',
        nickname='Admin',
        role='admin'
    )
    user.set_password('admin123')
    db_session.session.add(user)
    db_session.session.commit()
    return user



@pytest.fixture
def sample_question(db_session, admin_user):
    """创建示例题目"""
    from app.models.question import Question
    
    question = Question(
        exam_type='civil_service',
        question_type='single_choice',
        subject='行测',
        chapter='数量关系',
        difficulty=3,
        content='某工厂生产一批零件，甲单独做需要10天，乙单独做需要15天，两人合作需要多少天？',
        options={
            'A': '5天',
            'B': '6天',
            'C': '7天',
            'D': '8天'
        },
        correct_answer='B',
        explanation='甲的效率为1/10，乙的效率为1/15，合作效率为1/10+1/15=1/6，所以需要6天',
        tags=['数量关系', '工程问题'],
        created_by=admin_user.id
    )
    db_session.session.add(question)
    db_session.session.commit()
    return question
