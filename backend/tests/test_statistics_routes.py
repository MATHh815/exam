"""统计路由测试"""
import pytest
from datetime import date, timedelta
from flask_jwt_extended import create_access_token
from app.models.practice import PracticeRecord
from app.models.statistics import StudyStatistics
from app.models.exam import ExamPaper, ExamSession, ExamResult


@pytest.fixture
def auth_headers(app, sample_user):
    """创建认证头"""
    with app.app_context():
        access_token = create_access_token(identity=sample_user.id)
    return {'Authorization': f'Bearer {access_token}'}


@pytest.fixture
def sample_practice_records(db_session, sample_user, sample_question):
    """创建示例练习记录"""
    records = []
    for i in range(5):
        record = PracticeRecord(
            user_id=sample_user.id,
            question_id=sample_question.id,
            user_answer='B' if i < 3 else 'A',
            is_correct=i < 3,
            time_spent=30
        )
        records.append(record)
        db_session.session.add(record)
    
    db_session.session.commit()
    return records


@pytest.fixture
def sample_statistics(db_session, sample_user):
    """创建示例统计数据"""
    stats = []
    today = date.today()
    for i in range(7):
        stat = StudyStatistics(
            user_id=sample_user.id,
            date=today - timedelta(days=i),
            practice_count=10,
            correct_count=8,
            study_duration=30,
            exam_count=1
        )
        stats.append(stat)
        db_session.session.add(stat)
    
    db_session.session.commit()
    return stats


class TestStatisticsRoutes:
    """统计路由测试类"""
    
    def test_get_overview_success(self, client, auth_headers, sample_practice_records, sample_statistics):
        """测试获取学习概览成功"""
        response = client.get('/api/statistics/overview', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
        assert 'total_practice' in data['data']
        assert 'accuracy' in data['data']
        assert 'study_days' in data['data']
    
    def test_get_overview_with_date_range(self, client, auth_headers, sample_statistics):
        """测试带日期范围的学习概览"""
        today = date.today()
        start_date = (today - timedelta(days=3)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        
        response = client.get(
            f'/api/statistics/overview?start_date={start_date}&end_date={end_date}',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_get_overview_invalid_date_format(self, client, auth_headers):
        """测试无效日期格式"""
        response = client.get(
            '/api/statistics/overview?start_date=invalid-date',
            headers=auth_headers
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'INVALID_DATE_FORMAT' in data['error']['code']
    
    def test_get_overview_invalid_date_range(self, client, auth_headers):
        """测试无效日期范围"""
        today = date.today()
        start_date = today.strftime('%Y-%m-%d')
        end_date = (today - timedelta(days=1)).strftime('%Y-%m-%d')
        
        response = client.get(
            f'/api/statistics/overview?start_date={start_date}&end_date={end_date}',
            headers=auth_headers
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'INVALID_DATE_RANGE' in data['error']['code']
    
    def test_get_overview_unauthorized(self, client):
        """测试未授权访问"""
        response = client.get('/api/statistics/overview')
        
        assert response.status_code == 401
    
    def test_get_knowledge_analysis_success(self, client, auth_headers, sample_practice_records):
        """测试获取知识点分析成功"""
        response = client.get('/api/statistics/knowledge', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
        assert 'knowledge_points' in data['data']
        assert 'count' in data['data']
    
    def test_get_knowledge_analysis_with_date_range(self, client, auth_headers, sample_practice_records):
        """测试带日期范围的知识点分析"""
        today = date.today()
        start_date = (today - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        
        response = client.get(
            f'/api/statistics/knowledge?start_date={start_date}&end_date={end_date}',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_get_trend_success(self, client, auth_headers, sample_statistics):
        """测试获取学习趋势成功"""
        response = client.get('/api/statistics/trend?days=7', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
        assert 'trend' in data['data']
        assert 'days' in data['data']
        assert data['data']['days'] == 7
    
    def test_get_trend_default_days(self, client, auth_headers, sample_statistics):
        """测试默认天数"""
        response = client.get('/api/statistics/trend', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['days'] == 7
    
    def test_get_trend_invalid_days(self, client, auth_headers):
        """测试无效天数"""
        response = client.get('/api/statistics/trend?days=0', headers=auth_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'INVALID_DAYS' in data['error']['code']
    
    def test_get_trend_max_days_limit(self, client, auth_headers, sample_statistics):
        """测试最大天数限制"""
        response = client.get('/api/statistics/trend?days=500', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        # 应该被限制为365天
        assert data['data']['days'] == 365
    
    def test_get_exam_statistics_success(self, client, auth_headers):
        """测试获取考试统计成功"""
        response = client.get('/api/statistics/exams', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
        assert 'total_exams' in data['data']
        assert 'average_score' in data['data']
        assert 'average_accuracy' in data['data']
    
    def test_get_exam_statistics_with_date_range(self, client, auth_headers):
        """测试带日期范围的考试统计"""
        today = date.today()
        start_date = (today - timedelta(days=30)).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
        
        response = client.get(
            f'/api/statistics/exams?start_date={start_date}&end_date={end_date}',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
    
    def test_get_exam_statistics_no_data(self, client, auth_headers):
        """测试无考试数据时的统计"""
        response = client.get('/api/statistics/exams', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['total_exams'] == 0
        assert data['data']['average_score'] == 0.0
