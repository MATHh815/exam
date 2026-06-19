"""
测试考研院校API
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

app = create_app()

def test_api():
    with app.test_client() as client:
        print("测试考研院校API...")
        
        # 测试获取院校列表
        print("\n1. 测试获取院校列表:")
        response = client.get('/api/graduate/schools')
        data = response.get_json()
        print(f"   状态: {response.status_code}")
        print(f"   成功: {data.get('success')}")
        print(f"   院校数量: {data.get('data', {}).get('total', 0)}")
        if data.get('data', {}).get('records'):
            print(f"   第一个院校: {data['data']['records'][0]['name']}")
        
        # 测试获取省份列表
        print("\n2. 测试获取省份列表:")
        response = client.get('/api/graduate/provinces')
        data = response.get_json()
        print(f"   状态: {response.status_code}")
        print(f"   省份: {data.get('data', [])}")
        
        # 测试按985筛选
        print("\n3. 测试按985筛选:")
        response = client.get('/api/graduate/schools?level=985')
        data = response.get_json()
        print(f"   状态: {response.status_code}")
        print(f"   985院校数量: {data.get('data', {}).get('total', 0)}")
        
        # 测试获取院校专业
        print("\n4. 测试获取院校专业 (北京大学 id=1):")
        response = client.get('/api/graduate/schools/1/majors')
        data = response.get_json()
        print(f"   状态: {response.status_code}")
        print(f"   专业数量: {data.get('data', {}).get('total', 0)}")
        if data.get('data', {}).get('records'):
            for major in data['data']['records'][:3]:
                print(f"   - {major['name']} ({major['code']})")
        
        # 测试获取分数线
        print("\n5. 测试获取专业分数线 (major_id=1):")
        response = client.get('/api/graduate/majors/1/score-lines')
        data = response.get_json()
        print(f"   状态: {response.status_code}")
        if data.get('data'):
            for sl in data['data']:
                print(f"   - {sl['year']}年: 总分{sl['total_score']}")
        
        # 测试获取考试科目
        print("\n6. 测试获取考试科目 (major_id=1):")
        response = client.get('/api/graduate/majors/1/exam-subjects')
        data = response.get_json()
        print(f"   状态: {response.status_code}")
        if data.get('data'):
            for subj in data['data']:
                print(f"   - {subj['subject_name']} ({subj['subject_type']})")
        
        # 测试分数估算
        print("\n7. 测试分数估算:")
        response = client.post('/api/graduate/estimate-score', 
                              json={'total_score': 360, 'politics_score': 60, 'english_score': 60})
        data = response.get_json()
        print(f"   状态: {response.status_code}")
        print(f"   成功: {data.get('success')}")
        if data.get('data'):
            print(f"   冲刺院校数: {len(data['data'].get('reach', []))}")
            print(f"   稳妥院校数: {len(data['data'].get('match', []))}")
            print(f"   保底院校数: {len(data['data'].get('safe', []))}")
        
        print("\n所有API测试完成!")

if __name__ == '__main__':
    test_api()
