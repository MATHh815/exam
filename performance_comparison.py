#!/usr/bin/env python3
"""
Flask vs FastAPI 性能对比测试工具
"""
import asyncio
import aiohttp
import time
import statistics
import json
from datetime import datetime
import argparse

class PerformanceComparison:
    def __init__(self):
        self.flask_url = "http://localhost:5000/api"
        self.fastapi_url = "http://localhost:8000/api"
        
    async def test_endpoint(self, session, url, method="GET", data=None):
        """测试单个端点"""
        start_time = time.time()
        try:
            if method == "POST":
                async with session.post(url, json=data) as response:
                    result = await response.json()
                    return {
                        "success": response.status == 200,
                        "status": response.status,
                        "response_time": time.time() - start_time,
                        "data": result
                    }
            else:
                async with session.get(url) as response:
                    result = await response.json()
                    return {
                        "success": response.status == 200,
                        "status": response.status,
                        "response_time": time.time() - start_time,
                        "data": result
                    }
        except Exception as e:
            return {
                "success": False,
                "status": 0,
                "response_time": time.time() - start_time,
                "error": str(e)
            }
    
    async def run_concurrent_test(self, base_url, endpoint, num_requests, method="GET", data=None):
        """运行并发测试"""
        connector = aiohttp.TCPConnector(limit=100)
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            tasks = []
            for _ in range(num_requests):
                task = asyncio.create_task(
                    self.test_endpoint(session, f"{base_url}{endpoint}", method, data)
                )
                tasks.append(task)
            
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            total_time = time.time() - start_time
            
            # 处理结果
            successful_requests = 0
            response_times = []
            errors = []
            
            for result in results:
                if isinstance(result, Exception):
                    errors.append(str(result))
                    continue
                
                if result.get("success", False):
                    successful_requests += 1
                    response_times.append(result["response_time"])
                else:
                    errors.append(result.get("error", f"HTTP {result.get('status', 'Unknown')}"))
            
            return {
                "total_requests": num_requests,
                "successful_requests": successful_requests,
                "failed_requests": num_requests - successful_requests,
                "success_rate": successful_requests / num_requests * 100,
                "total_time": total_time,
                "requests_per_second": num_requests / total_time,
                "avg_response_time": statistics.mean(response_times) if response_times else 0,
                "median_response_time": statistics.median(response_times) if response_times else 0,
                "min_response_time": min(response_times) if response_times else 0,
                "max_response_time": max(response_times) if response_times else 0,
                "errors": errors[:5]  # 只显示前5个错误
            }
    
    async def compare_frameworks(self, num_requests=20):
        """对比Flask和FastAPI性能"""
        print("🔥 Flask vs FastAPI 性能对比测试")
        print("=" * 60)
        print(f"📊 测试参数: {num_requests} 并发请求")
        print(f"⏰ 开始时间: {datetime.now().strftime('%H:%M:%S')}")
        print()
        
        # 测试端点列表
        test_cases = [
            {
                "name": "用户登录",
                "endpoint": "/auth/login",
                "method": "POST",
                "data": {"username": "admin", "password": "123456"}
            },
            {
                "name": "获取用户信息",
                "endpoint": "/auth/profile",
                "method": "GET"
            },
            {
                "name": "获取试卷列表",
                "endpoint": "/exams/papers",
                "method": "GET"
            },
            {
                "name": "获取统计信息",
                "endpoint": "/statistics/overview",
                "method": "GET"
            }
        ]
        
        comparison_results = {}
        
        for test_case in test_cases:
            print(f"🧪 测试: {test_case['name']}")
            print("-" * 40)
            
            # 测试Flask
            print("📍 测试 Flask...")
            flask_result = await self.run_concurrent_test(
                self.flask_url,
                test_case["endpoint"],
                num_requests,
                test_case["method"],
                test_case.get("data")
            )
            
            # 等待一秒避免服务器压力
            await asyncio.sleep(1)
            
            # 测试FastAPI
            print("📍 测试 FastAPI...")
            fastapi_result = await self.run_concurrent_test(
                self.fastapi_url,
                test_case["endpoint"],
                num_requests,
                test_case["method"],
                test_case.get("data")
            )
            
            # 保存结果
            comparison_results[test_case["name"]] = {
                "flask": flask_result,
                "fastapi": fastapi_result
            }
            
            # 显示对比结果
            self.print_comparison(test_case["name"], flask_result, fastapi_result)
            print()
        
        # 生成总结报告
        self.generate_summary_report(comparison_results)
    
    def print_comparison(self, test_name, flask_result, fastapi_result):
        """打印单个测试的对比结果"""
        print(f"📊 {test_name} 对比结果:")
        
        # 成功率对比
        flask_success = flask_result["success_rate"]
        fastapi_success = fastapi_result["success_rate"]
        print(f"   成功率:     Flask {flask_success:.1f}% | FastAPI {fastapi_success:.1f}%")
        
        # 响应时间对比
        flask_avg = flask_result["avg_response_time"] * 1000
        fastapi_avg = fastapi_result["avg_response_time"] * 1000
        improvement = (flask_avg - fastapi_avg) / flask_avg * 100 if flask_avg > 0 else 0
        print(f"   平均响应时间: Flask {flask_avg:.0f}ms | FastAPI {fastapi_avg:.0f}ms ({improvement:+.1f}%)")
        
        # 吞吐量对比
        flask_rps = flask_result["requests_per_second"]
        fastapi_rps = fastapi_result["requests_per_second"]
        rps_improvement = (fastapi_rps - flask_rps) / flask_rps * 100 if flask_rps > 0 else 0
        print(f"   吞吐量:     Flask {flask_rps:.1f} req/s | FastAPI {fastapi_rps:.1f} req/s ({rps_improvement:+.1f}%)")
        
        # 错误情况
        if flask_result["errors"] or fastapi_result["errors"]:
            print(f"   错误:")
            if flask_result["errors"]:
                print(f"     Flask: {flask_result['errors'][0]}")
            if fastapi_result["errors"]:
                print(f"     FastAPI: {fastapi_result['errors'][0]}")
    
    def generate_summary_report(self, results):
        """生成总结报告"""
        print("🎯 性能对比总结报告")
        print("=" * 60)
        
        total_flask_rps = 0
        total_fastapi_rps = 0
        total_tests = len(results)
        
        flask_wins = 0
        fastapi_wins = 0
        
        for test_name, result in results.items():
            flask_rps = result["flask"]["requests_per_second"]
            fastapi_rps = result["fastapi"]["requests_per_second"]
            
            total_flask_rps += flask_rps
            total_fastapi_rps += fastapi_rps
            
            if fastapi_rps > flask_rps:
                fastapi_wins += 1
            else:
                flask_wins += 1
        
        avg_flask_rps = total_flask_rps / total_tests
        avg_fastapi_rps = total_fastapi_rps / total_tests
        overall_improvement = (avg_fastapi_rps - avg_flask_rps) / avg_flask_rps * 100
        
        print(f"📈 整体性能提升: {overall_improvement:+.1f}%")
        print(f"🏆 FastAPI获胜: {fastapi_wins}/{total_tests} 项测试")
        print(f"📊 平均吞吐量: Flask {avg_flask_rps:.1f} vs FastAPI {avg_fastapi_rps:.1f} req/s")
        
        # 给出建议
        print("\n💡 迁移建议:")
        if overall_improvement > 50:
            print("🚀 强烈推荐迁移到FastAPI！性能提升显著")
        elif overall_improvement > 20:
            print("✅ 推荐迁移到FastAPI，有明显性能提升")
        elif overall_improvement > 0:
            print("⚖️ 可以考虑迁移，有一定性能提升")
        else:
            print("🤔 性能提升不明显，可根据其他因素决定")
        
        print(f"\n📋 预期并发能力提升:")
        print(f"   当前Flask: 5-10 并发用户")
        print(f"   迁移后FastAPI: {int(10 * (1 + overall_improvement/100))}-{int(50 * (1 + overall_improvement/100))} 并发用户")

async def main():
    parser = argparse.ArgumentParser(description="Flask vs FastAPI 性能对比")
    parser.add_argument("--requests", type=int, default=20, help="并发请求数 (默认: 20)")
    
    args = parser.parse_args()
    
    print("⚠️ 请确保以下服务正在运行:")
    print("   Flask: http://localhost:5000")
    print("   FastAPI: http://localhost:8000 (运行 python fastapi_demo.py)")
    print()
    
    input("按Enter键开始测试...")
    
    tester = PerformanceComparison()
    await tester.compare_frameworks(args.requests)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️ 测试被中断")
    except Exception as e:
        print(f"\n\n❌ 测试失败: {e}")
        print("\n💡 请确保:")
        print("   1. Flask服务运行在 http://localhost:5000")
        print("   2. FastAPI演示运行在 http://localhost:8000")
        print("   3. 安装了必要依赖: pip install aiohttp uvicorn fastapi aiosqlite")