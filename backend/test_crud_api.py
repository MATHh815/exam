"""测试CRUD API"""
import requests

BASE_URL = "http://localhost:5000/api"

def test_create_school():
    """测试添加院校"""
    data = {
        "name": "测试大学",
        "code": "99999",
        "province": "测试省",
        "type": "综合类"
    }
    response = requests.post(f"{BASE_URL}/graduate/schools", json=data)
    print(f"POST /graduate/schools: {response.status_code}")
    print(response.json())
    return response.json()

def test_get_schools():
    """测试获取院校列表"""
    response = requests.get(f"{BASE_URL}/graduate/schools")
    print(f"GET /graduate/schools: {response.status_code}")
    data = response.json()
    print(f"Total schools: {data['data']['total']}")
    return data

def test_create_major():
    """测试添加专业"""
    data = {
        "school_id": 1,
        "name": "测试专业",
        "code": "999999",
        "category": "工学",
        "degree_type": "学术型"
    }
    response = requests.post(f"{BASE_URL}/graduate/majors", json=data)
    print(f"POST /graduate/majors: {response.status_code}")
    print(response.json())
    return response.json()

def test_create_score_line():
    """测试添加分数线"""
    data = {
        "major_id": 1,
        "year": 2024,
        "total_score": 350,
        "politics_score": 60,
        "english_score": 60
    }
    response = requests.post(f"{BASE_URL}/graduate/score-lines", json=data)
    print(f"POST /graduate/score-lines: {response.status_code}")
    print(response.json())
    return response.json()

if __name__ == "__main__":
    print("=" * 50)
    print("测试院校CRUD API")
    print("=" * 50)
    
    # 测试获取列表
    test_get_schools()
    print()
    
    # 测试创建院校
    result = test_create_school()
    print()
    
    # 测试创建专业
    test_create_major()
    print()
    
    # 测试创建分数线
    test_create_score_line()
