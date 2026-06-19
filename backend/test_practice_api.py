"""测试练习API的诊断脚本"""
import requests
import json

# 测试配置
BASE_URL = "http://localhost:5000"
# 如果localhost不行，尝试127.0.0.1
# BASE_URL = "http://127.0.0.1:5000"

def test_health():
    """测试健康检查"""
    print("=" * 50)
    print("1. 测试健康检查")
    print("=" * 50)
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return True
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

def test_login():
    """测试登录获取token"""
    print("\n" + "=" * 50)
    print("2. 测试登录")
    print("=" * 50)
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": "admin", "password": "admin123"},
            timeout=5
        )
        print(f"状态码: {response.status_code}")
        data = response.json()
        print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        if data.get('success') and data.get('data', {}).get('access_token'):
            return data['data']['access_token']
        return None
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None

def test_start_practice(token):
    """测试开始练习"""
    print("\n" + "=" * 50)
    print("3. 测试开始练习")
    print("=" * 50)
    
    if not token:
        print("❌ 没有token，跳过测试")
        return
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "count": 10,
            "exam_type": "公务员考试",
            "question_type": "单选题"
        }
        
        print(f"请求数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        
        response = requests.post(
            f"{BASE_URL}/api/practice/start",
            json=data,
            headers=headers,
            timeout=5
        )
        
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if result.get('success'):
            print(f"✅ 成功获取 {len(result.get('data', {}).get('questions', []))} 道题目")
        else:
            print(f"❌ 失败: {result.get('error', {}).get('message')}")
            
    except Exception as e:
        print(f"❌ 错误: {e}")

def test_questions_count():
    """测试题目数量"""
    print("\n" + "=" * 50)
    print("4. 检查数据库题目数量")
    print("=" * 50)
    try:
        from app import create_app, db
        from app.models.question import Question
        
        app = create_app()
        with app.app_context():
            total = Question.query.filter_by(is_deleted=False).count()
            print(f"数据库中有 {total} 道题目")
            
            if total > 0:
                # 显示题目类型分布
                questions = Question.query.filter_by(is_deleted=False).all()
                exam_types = {}
                for q in questions:
                    exam_types[q.exam_type] = exam_types.get(q.exam_type, 0) + 1
                
                print("\n题目类型分布:")
                for exam_type, count in exam_types.items():
                    print(f"  - {exam_type}: {count} 道")
            else:
                print("⚠️  数据库中没有题目！")
                
    except Exception as e:
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    print("开始诊断练习API...")
    print(f"目标服务器: {BASE_URL}")
    
    # 1. 测试健康检查
    if not test_health():
        print("\n❌ 后端服务未运行或无法访问！")
        print("请确保:")
        print("1. 后端服务已启动 (python run.py)")
        print("2. 端口5000没有被占用")
        print("3. 防火墙没有阻止连接")
        exit(1)
    
    # 2. 测试登录
    token = test_login()
    
    # 3. 测试开始练习
    test_start_practice(token)
    
    # 4. 检查题目数量
    test_questions_count()
    
    print("\n" + "=" * 50)
    print("诊断完成")
    print("=" * 50)
