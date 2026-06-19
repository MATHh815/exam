#!/usr/bin/env python3
"""
考试系统并发性能测试工具
"""
import asyncio
import aiohttp
import time
import json
import statistics
from datetime import datetime
import argparse

class PerformanceTest:
    def __init__(self, base_url="http://localhost:5000/api", max_concurrent=10):
        self.base_url = base_url
        self.max_concurrent = max_concurrent
        self.results = []
        
    async def login_user(self, session, username, password):
        """用户登录测试"""
        start_time = time.time()
        try:
            async with session.post(f"{self.base_url}/auth/login", 
                                  json={"username": username, "password": password}) as response:
                data = await response.json()
                end_time = time.time()
                
                return {
                    "operation": "login",
                    "status": response.status,
                    "success": data.get("success", False),
                    "response_time": end_time - start_time,
                    "token": data.get("data", {}).get("access_token") if data.get("success") else None
                }
        except Exception as e:
            return {
                "operation": "login",
                "status": 0,
                "success": False,
                "response_time": time.time() - start_time,
                "error": str(e)
            }
    
    async def get_profile(self, session, token):
        """获取用户信息测试"""
        start_time = time.time()
        try:
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            async with session.get(f"{self.base_url}/auth/profile", headers=headers) as response:
                data = await response.json()
                end_time = time.time()
                
                return {
                    "operation": "profile",
                    "status": response.status,
                    "success": data.get("success", False),
                    "response_time": end_time - start_time
                }
        except Exception as e:
            return {
                "operation": "profile",
                "status": 0,
                "success": False,
                "response_time": time.time() - start_time,
                "error": str(e)
            }
    
    async def simulate_exam_operations(self, session, token):
        """模拟考试操作"""
        operations = []
        
        # 模拟获取试卷列表
        start_time = time.time()
        try:
            headers = {"Authorization": f"Bearer {token}"} if token else {}
            async with session.get(f"{self.base_url}/exams/papers", headers=headers) as response:
                data = await response.json()
                operations.append({
                    "operation": "get_papers",
                    "status": response.status,
                    "success": data.get("success", False),
                    "response_time": time.time() - start_time
                })
        except Exception as e:
            operations.append({
                "operation": "get_papers",
                "status": 0,
                "success": False,
                "response_time": time.time() - start_time,
                "error": str(e)
            })
        
        # 模拟获取统计信息
        start_time = time.time()
        try:
            async with session.get(f"{self.base_url}/statistics/overview", headers=headers) as response:
                data = await response.json()
                operations.append({
                    "operation": "get_stats",
                    "status": response.status,
                    "success": data.get("success", False),
                    "response_time": time.time() - start_time
                })
        except Exception as e:
            operations.append({
                "operation": "get_stats",
                "status": 0,
                "success": False,
                "response_time": time.time() - start_time,
                "error": str(e)
            })
        
        return operations
    
    async def run_user_simulation(self, session, user_id):
        """模拟单个用户的完整操作流程"""
        username = f"testuser{user_id}" if user_id > 0 else "admin"
        password = "123456"
        
        # 登录
        login_result = await self.login_user(session, username, password)
        results = [login_result]
        
        if login_result["success"] and login_result.get("token"):
            token = login_result["token"]
            
            # 获取用户信息
            profile_result = await self.get_profile(session, token)
            results.append(profile_result)
            
            # 模拟考试相关操作
            exam_operations = await self.simulate_exam_operations(session, token)
            results.extend(exam_operations)
        
        return results
    
    async def run_concurrent_test(self, num_users):
        """运行并发测试"""
        print(f"🚀 开始并发测试: {num_users} 个用户")
        print(f"📡 目标服务器: {self.base_url}")
        print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 50)
        
        connector = aiohttp.TCPConnector(limit=self.max_concurrent)
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # 创建并发任务
            tasks = []
            for i in range(num_users):
                task = asyncio.create_task(self.run_user_simulation(session, i))
                tasks.append(task)
            
            # 等待所有任务完成
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            total_time = time.time() - start_time
            
            # 处理结果
            all_operations = []
            successful_users = 0
            
            for i, user_results in enumerate(results):
                if isinstance(user_results, Exception):
                    print(f"❌ 用户 {i} 测试异常: {user_results}")
                    continue
                
                user_success = True
                for operation in user_results:
                    all_operations.append(operation)
                    if not operation.get("success", False):
                        user_success = False
                
                if user_success:
                    successful_users += 1
            
            # 生成报告
            self.generate_report(all_operations, num_users, successful_users, total_time)
    
    def generate_report(self, operations, total_users, successful_users, total_time):
        """生成测试报告"""
        print("\n" + "=" * 60)
        print("📊 并发测试报告")
        print("=" * 60)
        
        # 基本统计
        print(f"👥 总用户数: {total_users}")
        print(f"✅ 成功用户数: {successful_users}")
        print(f"❌ 失败用户数: {total_users - successful_users}")
        print(f"📈 成功率: {successful_users/total_users*100:.1f}%")
        print(f"⏱️  总测试时间: {total_time:.2f}秒")
        print(f"🔄 平均并发: {total_users/total_time:.1f} 用户/秒")
        
        # 按操作类型统计
        operation_stats = {}
        for op in operations:
            op_type = op["operation"]
            if op_type not in operation_stats:
                operation_stats[op_type] = {
                    "count": 0,
                    "success": 0,
                    "response_times": [],
                    "errors": []
                }
            
            stats = operation_stats[op_type]
            stats["count"] += 1
            if op.get("success", False):
                stats["success"] += 1
            stats["response_times"].append(op["response_time"])
            if "error" in op:
                stats["errors"].append(op["error"])
        
        print("\n📋 操作详细统计:")
        print("-" * 60)
        
        for op_type, stats in operation_stats.items():
            success_rate = stats["success"] / stats["count"] * 100
            avg_time = statistics.mean(stats["response_times"])
            median_time = statistics.median(stats["response_times"])
            max_time = max(stats["response_times"])
            min_time = min(stats["response_times"])
            
            print(f"\n🔸 {op_type.upper()}:")
            print(f"   请求数: {stats['count']}")
            print(f"   成功率: {success_rate:.1f}%")
            print(f"   平均响应时间: {avg_time:.3f}秒")
            print(f"   中位响应时间: {median_time:.3f}秒")
            print(f"   最快响应: {min_time:.3f}秒")
            print(f"   最慢响应: {max_time:.3f}秒")
            
            if stats["errors"]:
                print(f"   错误数: {len(stats['errors'])}")
                # 显示前3个错误
                for i, error in enumerate(stats["errors"][:3]):
                    print(f"     - {error}")
                if len(stats["errors"]) > 3:
                    print(f"     ... 还有 {len(stats['errors']) - 3} 个错误")
        
        # 性能评级
        print("\n🎯 性能评级:")
        print("-" * 30)
        
        if successful_users == total_users:
            if total_users >= 50:
                grade = "A+ 优秀"
            elif total_users >= 20:
                grade = "A 良好"
            else:
                grade = "B+ 正常"
        elif successful_users >= total_users * 0.8:
            grade = "B 一般"
        elif successful_users >= total_users * 0.5:
            grade = "C 较差"
        else:
            grade = "D 很差"
        
        print(f"📊 系统评级: {grade}")
        
        # 建议
        print("\n💡 优化建议:")
        print("-" * 30)
        
        if successful_users < total_users:
            print("❗ 系统存在并发问题，建议:")
            print("   1. 升级到Gunicorn多进程服务器")
            print("   2. 使用PostgreSQL替代SQLite")
            print("   3. 添加Redis缓存")
            print("   4. 实施数据库连接池")
        
        avg_response = statistics.mean([op["response_time"] for op in operations if op.get("success")])
        if avg_response > 1.0:
            print("⚠️  响应时间较慢，建议:")
            print("   1. 优化数据库查询")
            print("   2. 添加缓存机制")
            print("   3. 使用CDN加速静态资源")
        
        if total_users < 10:
            print("📈 可以尝试更高并发测试:")
            print(f"   python {__file__} --users 20 --concurrent 10")

async def main():
    parser = argparse.ArgumentParser(description="考试系统并发性能测试")
    parser.add_argument("--users", type=int, default=5, help="并发用户数 (默认: 5)")
    parser.add_argument("--concurrent", type=int, default=10, help="最大并发连接数 (默认: 10)")
    parser.add_argument("--url", type=str, default="http://localhost:5000/api", help="API基础URL")
    
    args = parser.parse_args()
    
    # 创建测试实例
    test = PerformanceTest(base_url=args.url, max_concurrent=args.concurrent)
    
    # 运行测试
    await test.run_concurrent_test(args.users)

if __name__ == "__main__":
    print("🧪 考试系统并发性能测试工具")
    print("=" * 40)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  测试被用户中断")
    except Exception as e:
        print(f"\n\n❌ 测试异常: {e}")
        print("\n💡 请确保:")
        print("   1. 后端服务正在运行")
        print("   2. 数据库已初始化")
        print("   3. 测试用户已创建")
        print("\n🔧 创建测试用户:")
        print("   python init_database.py")