"""测试学习计划 API 路由"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from flask_jwt_extended import create_access_token


def test_study_plan_routes():
    """测试学习计划路由"""
    print("=" * 60)
    print("测试学习计划 API 路由")
    print("=" * 60)
    
    # 创建应用
    app = create_app('development')
    
    with app.app_context():
        # 创建测试客户端
        client = app.test_client()
        
        # 获取或创建测试用户
        test_user = User.query.filter_by(username='test_user').first()
        if not test_user:
            test_user = User(
                username='test_user',
                email='test@example.com',
                nickname='测试用户'
            )
            test_user.set_password('password123')
            db.session.add(test_user)
            db.session.commit()
            print(f"✓ 创建测试用户: {test_user.username}")
        else:
            print(f"✓ 使用现有测试用户: {test_user.username}")
        
        # 生成访问令牌
        access_token = create_access_token(identity=test_user.id)
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        print("\n" + "=" * 60)
        print("测试 1: 创建学习计划")
        print("=" * 60)
        
        response = client.post('/api/study-plans', 
            headers=headers,
            json={
                "name": "2024国考冲刺计划",
                "description": "最后30天冲刺",
                "exam_type": "civil_service",
                "start_date": "2024-01-01",
                "end_date": "2024-01-31",
                "goals": [
                    {
                        "goal_type": "daily_practice",
                        "target_value": 50,
                        "period_start": "2024-01-01",
                        "period_end": "2024-01-01"
                    },
                    {
                        "goal_type": "weekly_practice",
                        "target_value": 400,
                        "period_start": "2024-01-01",
                        "period_end": "2024-01-07"
                    }
                ]
            }
        )
        
        print(f"状态码: {response.status_code}")
        data = response.get_json()
        print(f"响应: {data}")
        
        if response.status_code == 201:
            print("✓ 创建学习计划成功")
            plan_id = data['data']['plan']['id']
            print(f"  计划ID: {plan_id}")
            print(f"  计划名称: {data['data']['plan']['name']}")
            print(f"  目标数量: {len(data['data']['plan']['goals'])}")
        else:
            print("✗ 创建学习计划失败")
            return
        
        print("\n" + "=" * 60)
        print("测试 2: 获取学习计划列表")
        print("=" * 60)
        
        response = client.get('/api/study-plans', headers=headers)
        print(f"状态码: {response.status_code}")
        data = response.get_json()
        
        if response.status_code == 200:
            print("✓ 获取学习计划列表成功")
            print(f"  计划数量: {data['data']['count']}")
            for plan in data['data']['plans']:
                print(f"  - {plan['name']} (状态: {plan['status']})")
        else:
            print("✗ 获取学习计划列表失败")
        
        print("\n" + "=" * 60)
        print("测试 3: 获取学习计划详情")
        print("=" * 60)
        
        response = client.get(f'/api/study-plans/{plan_id}', headers=headers)
        print(f"状态码: {response.status_code}")
        data = response.get_json()
        
        if response.status_code == 200:
            print("✓ 获取学习计划详情成功")
            plan = data['data']['plan']
            print(f"  计划名称: {plan['name']}")
            print(f"  考试类型: {plan['exam_type']}")
            print(f"  开始日期: {plan['start_date']}")
            print(f"  结束日期: {plan['end_date']}")
            print(f"  目标数量: {len(plan['goals'])}")
        else:
            print("✗ 获取学习计划详情失败")
        
        print("\n" + "=" * 60)
        print("测试 4: 更新学习计划")
        print("=" * 60)
        
        response = client.put(f'/api/study-plans/{plan_id}',
            headers=headers,
            json={
                "name": "2024国考冲刺计划（已更新）",
                "description": "更新后的描述"
            }
        )
        print(f"状态码: {response.status_code}")
        data = response.get_json()
        
        if response.status_code == 200:
            print("✓ 更新学习计划成功")
            print(f"  新名称: {data['data']['plan']['name']}")
            print(f"  新描述: {data['data']['plan']['description']}")
        else:
            print("✗ 更新学习计划失败")
        
        print("\n" + "=" * 60)
        print("测试 5: 更新学习进度")
        print("=" * 60)
        
        response = client.put(f'/api/study-plans/{plan_id}/progress',
            headers=headers,
            json={
                "goal_type": "daily_practice",
                "increment": 10
            }
        )
        print(f"状态码: {response.status_code}")
        data = response.get_json()
        
        if response.status_code == 200:
            print("✓ 更新学习进度成功")
            if data['data']['updated_goals']:
                for goal in data['data']['updated_goals']:
                    print(f"  目标类型: {goal['goal_type']}")
                    print(f"  当前进度: {goal['current_value']}/{goal['target_value']}")
                    print(f"  是否完成: {goal['is_completed']}")
            else:
                print("  没有匹配的目标被更新")
        else:
            print("✗ 更新学习进度失败")
        
        print("\n" + "=" * 60)
        print("测试 6: 获取学习报告")
        print("=" * 60)
        
        response = client.get(f'/api/study-plans/{plan_id}/report', headers=headers)
        print(f"状态码: {response.status_code}")
        data = response.get_json()
        
        if response.status_code == 200:
            print("✓ 获取学习报告成功")
            report = data['data']['report']
            print(f"  计划名称: {report['plan']['name']}")
            print(f"  目标数量: {len(report.get('goals', []))}")
            print(f"  总体进度: {report.get('overall_progress', 0):.1f}%")
            print(f"  练习统计: {report.get('practice_stats', {})}")
            print(f"  考试统计: {report.get('exam_stats', {})}")
        else:
            print("✗ 获取学习报告失败")
        
        print("\n" + "=" * 60)
        print("测试 7: 删除学习计划")
        print("=" * 60)
        
        response = client.delete(f'/api/study-plans/{plan_id}', headers=headers)
        print(f"状态码: {response.status_code}")
        data = response.get_json()
        
        if response.status_code == 200:
            print("✓ 删除学习计划成功")
            print(f"  消息: {data['data']['message']}")
        else:
            print("✗ 删除学习计划失败")
        
        # 验证软删除
        print("\n验证软删除...")
        response = client.get('/api/study-plans', headers=headers)
        data = response.get_json()
        active_plans = [p for p in data['data']['plans'] if p['id'] == plan_id]
        
        if not active_plans:
            print("✓ 软删除验证成功：计划不再出现在列表中")
        else:
            print("✗ 软删除验证失败：计划仍然出现在列表中")
        
        print("\n" + "=" * 60)
        print("测试 8: 测试错误处理")
        print("=" * 60)
        
        # 测试缺少必填字段
        print("\n8.1 测试缺少必填字段...")
        response = client.post('/api/study-plans',
            headers=headers,
            json={"name": "测试计划"}  # 缺少 exam_type, start_date, end_date
        )
        print(f"状态码: {response.status_code}")
        if response.status_code == 400:
            print("✓ 正确返回 400 错误")
        else:
            print("✗ 错误处理不正确")
        
        # 测试无效的状态值
        print("\n8.2 测试无效的状态值...")
        response = client.get('/api/study-plans?status=invalid', headers=headers)
        print(f"状态码: {response.status_code}")
        if response.status_code == 400:
            print("✓ 正确返回 400 错误")
        else:
            print("✗ 错误处理不正确")
        
        # 测试访问不存在的计划
        print("\n8.3 测试访问不存在的计划...")
        response = client.get('/api/study-plans/99999', headers=headers)
        print(f"状态码: {response.status_code}")
        if response.status_code == 404:
            print("✓ 正确返回 404 错误")
        else:
            print("✗ 错误处理不正确")
        
        print("\n" + "=" * 60)
        print("所有测试完成！")
        print("=" * 60)


if __name__ == '__main__':
    test_study_plan_routes()
