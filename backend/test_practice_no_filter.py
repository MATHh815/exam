"""测试不带筛选条件的练习API"""
import requests
import json

BASE_URL = "http://localhost:5000"

# 先登录获取token
response = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={"username": "admin", "password": "admin123"}
)
token = response.json()['data']['access_token']

# 测试不带筛选条件
print("测试1: 不带任何筛选条件")
headers = {"Authorization": f"Bearer {token}"}
data = {"count": 10}

response = requests.post(
    f"{BASE_URL}/api/practice/start",
    json=data,
    headers=headers
)

result = response.json()
print(f"状态码: {response.status_code}")
print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
print(f"获取题目数: {len(result.get('data', {}).get('questions', []))}")

# 测试带空字符串筛选条件
print("\n测试2: 带空字符串筛选条件（模拟前端）")
data = {
    "count": 10,
    "exam_type": "",
    "question_type": ""
}

response = requests.post(
    f"{BASE_URL}/api/practice/start",
    json=data,
    headers=headers
)

result = response.json()
print(f"状态码: {response.status_code}")
print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
print(f"获取题目数: {len(result.get('data', {}).get('questions', []))}")
