"""认证服务单元测试"""
import pytest
from app.services.auth_service import AuthService
from app.models.user import User


class TestAuthService:
    """认证服务测试类"""
    
    def test_register_success(self, app, db_session):
        """测试用户注册成功"""
        with app.app_context():
            user = AuthService.register(
                username='newuser',
                password='password123',
                email='newuser@example.com',
                nickname='New User'
            )
            
            assert user.id is not None
            assert user.username == 'newuser'
            assert user.email == 'newuser@example.com'
            assert user.nickname == 'New User'
            assert user.check_password('password123')
            assert user.is_active is True
            assert user.role == 'user'
    
    def test_register_duplicate_username(self, app, db_session, sample_user):
        """测试注册重复用户名"""
        with app.app_context():
            with pytest.raises(ValueError, match='用户名已存在'):
                AuthService.register(
                    username='testuser',
                    password='password123',
                    email='another@example.com'
                )
    
    def test_register_duplicate_email(self, app, db_session, sample_user):
        """测试注册重复邮箱"""
        with app.app_context():
            with pytest.raises(ValueError, match='邮箱已被注册'):
                AuthService.register(
                    username='anotheruser',
                    password='password123',
                    email='test@example.com'
                )
    
    def test_login_success(self, app, db_session, sample_user):
        """测试登录成功"""
        with app.app_context():
            user, access_token, refresh_token = AuthService.login(
                username='testuser',
                password='password123'
            )
            
            assert user.id == sample_user.id
            assert user.username == 'testuser'
            assert access_token is not None
            assert refresh_token is not None
            assert isinstance(access_token, str)
            assert isinstance(refresh_token, str)
    
    def test_login_wrong_password(self, app, db_session, sample_user):
        """测试登录密码错误"""
        with app.app_context():
            with pytest.raises(ValueError, match='用户名或密码错误'):
                AuthService.login(
                    username='testuser',
                    password='wrongpassword'
                )
    
    def test_login_nonexistent_user(self, app, db_session):
        """测试登录不存在的用户"""
        with app.app_context():
            with pytest.raises(ValueError, match='用户名或密码错误'):
                AuthService.login(
                    username='nonexistent',
                    password='password123'
                )
    
    def test_login_inactive_user(self, app, db_session, sample_user):
        """测试登录已禁用用户"""
        with app.app_context():
            # 禁用用户
            user = User.query.filter_by(username='testuser').first()
            user.is_active = False
            db_session.session.commit()
            
            with pytest.raises(ValueError, match='账户已被禁用'):
                AuthService.login(
                    username='testuser',
                    password='password123'
                )
    
    def test_update_profile_success(self, app, db_session, sample_user):
        """测试更新用户信息成功"""
        with app.app_context():
            updated_user = AuthService.update_profile(
                user_id=sample_user.id,
                nickname='Updated Name',
                email='updated@example.com'
            )
            
            assert updated_user.nickname == 'Updated Name'
            assert updated_user.email == 'updated@example.com'
    
    def test_update_profile_duplicate_email(self, app, db_session, sample_user, admin_user):
        """测试更新为已存在的邮箱"""
        with app.app_context():
            with pytest.raises(ValueError, match='邮箱已被使用'):
                AuthService.update_profile(
                    user_id=sample_user.id,
                    email='admin@example.com'
                )
    
    def test_update_profile_nonexistent_user(self, app, db_session):
        """测试更新不存在的用户"""
        with app.app_context():
            with pytest.raises(ValueError, match='用户不存在'):
                AuthService.update_profile(
                    user_id=99999,
                    nickname='New Name'
                )
    
    def test_change_password_success(self, app, db_session, sample_user):
        """测试修改密码成功"""
        with app.app_context():
            result = AuthService.change_password(
                user_id=sample_user.id,
                old_password='password123',
                new_password='newpassword456'
            )
            
            assert result is True
            
            # 验证新密码可以登录
            user, _, _ = AuthService.login('testuser', 'newpassword456')
            assert user.id == sample_user.id
    
    def test_change_password_wrong_old_password(self, app, db_session, sample_user):
        """测试修改密码时旧密码错误"""
        with app.app_context():
            with pytest.raises(ValueError, match='旧密码错误'):
                AuthService.change_password(
                    user_id=sample_user.id,
                    old_password='wrongpassword',
                    new_password='newpassword456'
                )
    
    def test_reset_password_success(self, app, db_session, sample_user):
        """测试重置密码成功"""
        with app.app_context():
            result = AuthService.reset_password(
                email='test@example.com',
                new_password='resetpassword789'
            )
            
            assert result is True
            
            # 验证新密码可以登录
            user, _, _ = AuthService.login('testuser', 'resetpassword789')
            assert user.id == sample_user.id
    
    def test_reset_password_nonexistent_email(self, app, db_session):
        """测试重置不存在的邮箱"""
        with app.app_context():
            with pytest.raises(ValueError, match='邮箱不存在'):
                AuthService.reset_password(
                    email='nonexistent@example.com',
                    new_password='newpassword'
                )
    
    def test_deactivate_user_success(self, app, db_session, sample_user):
        """测试停用用户成功"""
        with app.app_context():
            result = AuthService.deactivate_user(sample_user.id)
            
            assert result is True
            
            # 验证用户已被停用
            user = User.query.get(sample_user.id)
            assert user.is_active is False
    
    def test_deactivate_nonexistent_user(self, app, db_session):
        """测试停用不存在的用户"""
        with app.app_context():
            with pytest.raises(ValueError, match='用户不存在'):
                AuthService.deactivate_user(99999)
    
    def test_get_user_by_id_success(self, app, db_session, sample_user):
        """测试根据ID获取用户成功"""
        with app.app_context():
            user = AuthService.get_user_by_id(sample_user.id)
            
            assert user.id == sample_user.id
            assert user.username == 'testuser'
    
    def test_get_user_by_id_nonexistent(self, app, db_session):
        """测试获取不存在的用户"""
        with app.app_context():
            with pytest.raises(ValueError, match='用户不存在'):
                AuthService.get_user_by_id(99999)
