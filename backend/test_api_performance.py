"""API 性能测试

测试所有 Phase 1 API 的响应时间，确保符合性能要求
"""
import time
import requests
from app import create_app, db
from app.models.user import User
from app.models.study_plan import StudyPlan, StudyGoal
from app.models.note import QuestionNote, QuestionBookmark
from app.models.achievement import Achievement, UserAchievement, UserPoints, DailyTask
from app.models.question import Question
from datetime import datetime, date, timedelta

# 性能要求
PERFORMANCE_REQUIREMENTS = {
    'standard': 200,  # 标准 API 响应时间 < 200ms
    'search': 500,    # 搜索 API 响应时间 < 500ms
    'export': 2000,   # 导出 API 响应时间 < 2s
}

class APIPerformanceTester:
    """API 性能测试器"""
    
    def __init__(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.results = []
        self.user_id = None
        self.token = None
        
    def setup(self):
        """设置测试环境"""
        with self.app.app_context():
            # 创建测试用户
            user = User.query.filter_by(username='perftest').first()
            if not user:
                user = User(username='perftest', email='perftest@example.com')
                user.set_password('password123')
                db.session.add(user)
                db.session.commit()
            
            self.user_id = user.id
            
            # 登录获取 token
            response = self.client.post('/api/auth/login', json={
                'username': 'perftest',
                'password': 'password123'
            })
            
            if response.status_code == 200:
                self.token = response.json.get('token')
            
            # 创建测试数据
            self._create_test_data()
    
    def _create_test_data(self):
        """创建测试数据"""
        with self.app.app_context():
            # 创建学习计划
            plan = StudyPlan.query.filter_by(user_id=self.user_id).first()
            if not plan:
                plan = StudyPlan(
                    user_id=self.user_id,
                    name='测试计划',
                    exam_type='civil_service',
                    start_date=date.today(),
                    end_date=date.today() + timedelta(days=30)
                )
                db.session.add(plan)
                db.session.commit()
            
            # 创建题目（如果不存在）
            question = Question.query.first()
            if not question:
                question = Question(
                    exam_type='civil_service',
                    question_type='single_choice',
                    subject='行测',
                    content='测试题目',
                    correct_answer='A',
                    created_by=self.user_id
                )
                db.session.add(question)
                db.session.commit()
            
            # 创建笔记
            note = QuestionNote.query.filter_by(user_id=self.user_id).first()
            if not note:
                note = QuestionNote(
                    user_id=self.user_id,
                    question_id=question.id,
                    content='测试笔记内容'
                )
                db.session.add(note)
                db.session.commit()
            
            # 初始化用户积分
            points = UserPoints.query.filter_by(user_id=self.user_id).first()
            if not points:
                points = UserPoints(user_id=self.user_id)
                db.session.add(points)
                db.session.commit()
    
    def _get_headers(self):
        """获取请求头"""
        if self.token:
            return {'Authorization': f'Bearer {self.token}'}
        return {}
    
    def test_api(self, name, method, url, expected_time, **kwargs):
        """测试单个 API
        
        Args:
            name: API 名称
            method: HTTP 方法
            url: API 路径
            expected_time: 期望响应时间（毫秒）
            **kwargs: 其他请求参数
        """
        headers = self._get_headers()
        headers.update(kwargs.get('headers', {}))
        
        start_time = time.time()
        
        try:
            if method == 'GET':
                response = self.client.get(url, headers=headers)
            elif method == 'POST':
                response = self.client.post(url, headers=headers, json=kwargs.get('json'))
            elif method == 'PUT':
                response = self.client.put(url, headers=headers, json=kwargs.get('json'))
            elif method == 'DELETE':
                response = self.client.delete(url, headers=headers)
            else:
                raise ValueError(f'不支持的 HTTP 方法: {method}')
            
            elapsed_time = (time.time() - start_time) * 1000  # 转换为毫秒
            
            result = {
                'name': name,
                'method': method,
                'url': url,
                'status': response.status_code,
                'time': round(elapsed_time, 2),
                'expected': expected_time,
                'passed': elapsed_time < expected_time and 200 <= response.status_code < 300
            }
            
            self.results.append(result)
            
            # 打印结果
            status_icon = '✓' if result['passed'] else '✗'
            status_msg = f"{result['time']}ms (期望 < {expected_time}ms) - HTTP {response.status_code}"
            print(f"{status_icon} {name}: {status_msg}")
            
            return result
            
        except Exception as e:
            print(f"✗ {name}: 测试失败 - {str(e)}")
            self.results.append({
                'name': name,
                'method': method,
                'url': url,
                'status': 'ERROR',
                'time': 0,
                'expected': expected_time,
                'passed': False,
                'error': str(e)
            })
            return None
    
    def run_tests(self):
        """运行所有性能测试"""
        print("=" * 80)
        print("API 性能测试")
        print("=" * 80)
        print()
        
        # 学习计划 API
        print("学习计划 API:")
        print("-" * 80)
        self.test_api('获取学习计划列表', 'GET', '/api/study-plans', PERFORMANCE_REQUIREMENTS['standard'])
        self.test_api('创建学习计划', 'POST', '/api/study-plans', PERFORMANCE_REQUIREMENTS['standard'], json={
            'name': '性能测试计划',
            'exam_type': 'civil_service',
            'start_date': date.today().isoformat(),
            'end_date': (date.today() + timedelta(days=30)).isoformat(),
            'goals': []
        })
        print()
        
        # 笔记 API
        print("笔记 API:")
        print("-" * 80)
        self.test_api('获取笔记列表', 'GET', '/api/notes', PERFORMANCE_REQUIREMENTS['standard'])
        self.test_api('搜索笔记', 'GET', '/api/notes/search?keyword=测试', PERFORMANCE_REQUIREMENTS['search'])
        print()
        
        # 收藏 API
        print("收藏 API:")
        print("-" * 80)
        self.test_api('获取收藏列表', 'GET', '/api/bookmarks', PERFORMANCE_REQUIREMENTS['standard'])
        print()
        
        # 积分 API
        print("积分 API:")
        print("-" * 80)
        self.test_api('获取用户积分', 'GET', '/api/points', PERFORMANCE_REQUIREMENTS['standard'])
        self.test_api('获取积分历史', 'GET', '/api/points/history', PERFORMANCE_REQUIREMENTS['standard'])
        self.test_api('获取积分排行榜', 'GET', '/api/points/leaderboard', PERFORMANCE_REQUIREMENTS['standard'])
        print()
        
        # 成就 API
        print("成就 API:")
        print("-" * 80)
        self.test_api('获取所有成就', 'GET', '/api/achievements', PERFORMANCE_REQUIREMENTS['standard'])
        self.test_api('获取用户成就', 'GET', '/api/achievements/user', PERFORMANCE_REQUIREMENTS['standard'])
        self.test_api('获取成就统计', 'GET', '/api/achievements/stats', PERFORMANCE_REQUIREMENTS['standard'])
        print()
        
        # 每日任务 API
        print("每日任务 API:")
        print("-" * 80)
        self.test_api('获取今日任务', 'GET', '/api/daily-tasks', PERFORMANCE_REQUIREMENTS['standard'])
        self.test_api('获取任务统计', 'GET', '/api/daily-tasks/stats', PERFORMANCE_REQUIREMENTS['standard'])
        print()
        
        # 统计结果
        self.print_summary()
    
    def print_summary(self):
        """打印测试总结"""
        print("=" * 80)
        print("测试总结")
        print("=" * 80)
        print()
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r['passed'])
        failed = total - passed
        
        print(f"总测试数: {total}")
        print(f"通过: {passed}")
        print(f"失败: {failed}")
        print(f"通过率: {round(passed / total * 100, 2)}%")
        print()
        
        # 性能统计
        times = [r['time'] for r in self.results if r['time'] > 0]
        if times:
            print(f"平均响应时间: {round(sum(times) / len(times), 2)}ms")
            print(f"最快响应: {round(min(times), 2)}ms")
            print(f"最慢响应: {round(max(times), 2)}ms")
        print()
        
        # 失败的测试
        if failed > 0:
            print("失败的测试:")
            print("-" * 80)
            for result in self.results:
                if not result['passed']:
                    if result['status'] == 401:
                        reason = "未授权 (401) - 需要登录"
                    elif result['status'] >= 400:
                        reason = f"HTTP错误 {result['status']}"
                    elif result['time'] > result['expected']:
                        reason = f"响应时间 {result['time']}ms > {result['expected']}ms"
                    else:
                        reason = result.get('error', '未知错误')
                    print(f"  ✗ {result['name']}: {reason}")
            print()
        
        print("=" * 80)
        if failed == 0:
            print("✓ 所有 API 性能测试通过！")
        else:
            print(f"⚠️  有 {failed} 个 API 性能测试失败，需要优化")
        print("=" * 80)

def main():
    """主函数"""
    tester = APIPerformanceTester()
    tester.setup()
    tester.run_tests()

if __name__ == '__main__':
    main()
