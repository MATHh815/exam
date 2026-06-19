"""用户模型测试"""
import pytest
from app import create_app, db
from app.models.user import User


@pytest.fixture
def app():
    """创建测试应用"""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()


def test_user_creation(app):
    """测试用户创建"""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            nickname='测试用户'
        )
        user.set_password('password123')
        
        db.session.add(user)
        db.session.commit()
        
        # 验证用户已创建
        assert user.id is not None
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.nickname == '测试用户'
        assert user.role == 'user'
        assert user.is_active is True


def test_password_hashing(app):
    """测试密码哈希"""
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        
        # 验证密码哈希不等于明文密码
        assert user.password_hash != 'password123'
        
        # 验证密码验证功能
        assert user.check_password('password123') is True
        assert user.check_password('wrongpassword') is False


def test_password_validation():
    """测试密码验证"""
    # 测试有效密码
    valid, error = User.validate_password('password123')
    assert valid is True
    assert error is None
    
    # 测试密码太短
    valid, error = User.validate_password('pass')
    assert valid is False
    assert '长度' in error
    
    # 测试密码缺少字母
    valid, error = User.validate_password('12345678')
    assert valid is False
    assert '字母' in error
    
    # 测试密码缺少数字
    valid, error = User.validate_password('password')
    assert valid is False
    assert '数字' in error


def test_username_validation():
    """测试用户名验证"""
    # 测试有效用户名
    valid, error = User.validate_username('testuser')
    assert valid is True
    assert error is None
    
    # 测试用户名太短
    valid, error = User.validate_username('ab')
    assert valid is False
    assert '长度' in error
    
    # 测试用户名太长
    valid, error = User.validate_username('a' * 81)
    assert valid is False
    assert '长度' in error


def test_user_to_dict(app):
    """测试用户转字典"""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            nickname='测试用户'
        )
        user.set_password('password123')
        
        # 不包含邮箱
        data = user.to_dict()
        assert 'username' in data
        assert 'nickname' in data
        assert 'email' not in data
        assert 'password_hash' not in data
        
        # 包含邮箱
        data = user.to_dict(include_email=True)
        assert 'email' in data
        assert data['email'] == 'test@example.com'


def test_user_unique_constraints(app):
    """测试用户唯一性约束"""
    with app.app_context():
        # 创建第一个用户
        user1 = User(username='testuser', email='test@example.com')
        user1.set_password('password123')
        db.session.add(user1)
        db.session.commit()
        
        # 尝试创建相同用户名的用户
        user2 = User(username='testuser', email='test2@example.com')
        user2.set_password('password123')
        db.session.add(user2)
        
        with pytest.raises(Exception):  # 应该抛出完整性错误
            db.session.commit()
        
        db.session.rollback()
        
        # 尝试创建相同邮箱的用户
        user3 = User(username='testuser2', email='test@example.com')
        user3.set_password('password123')
        db.session.add(user3)
        
        with pytest.raises(Exception):  # 应该抛出完整性错误
            db.session.commit()
