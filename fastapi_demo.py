#!/usr/bin/env python3
"""
FastAPI性能演示 - 与Flask对比
运行: uvicorn fastapi_demo:app --host 0.0.0.0 --port 8000
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import asyncio
import time
import hashlib
import jwt
from datetime import datetime, timedelta
import sqlite3
import aiosqlite
import os

# 创建FastAPI应用
app = FastAPI(
    title="考试系统 FastAPI 演示",
    description="与Flask版本的性能对比演示",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置
SECRET_KEY = "fastapi-demo-secret-key"
DATABASE_PATH = "fastapi_demo.db"

# Pydantic模型
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    error: Optional[dict] = None

class UserProfile(BaseModel):
    id: int
    username: str
    email: str
    nickname: str
    role: str
    created_at: str

class ExamPaper(BaseModel):
    id: int
    title: str
    description: str
    question_count: int
    time_limit: int
    created_at: str

class StatisticsOverview(BaseModel):
    total_users: int
    total_exams: int
    total_questions: int
    active_sessions: int

# 数据库初始化
async def init_database():
    """初始化演示数据库"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # 创建用户表
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                nickname TEXT,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建试卷表
        await db.execute("""
            CREATE TABLE IF NOT EXISTS exam_papers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                question_count INTEGER DEFAULT 0,
                time_limit INTEGER DEFAULT 60,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 插入演示数据
        await db.execute("""
            INSERT OR IGNORE INTO users (username, password_hash, email, nickname, role)
            VALUES (?, ?, ?, ?, ?)
        """, ("admin", hashlib.md5("123456".encode()).hexdigest(), "admin@example.com", "管理员", "admin"))
        
        await db.execute("""
            INSERT OR IGNORE INTO users (username, password_hash, email, nickname, role)
            VALUES (?, ?, ?, ?, ?)
        """, ("testuser", hashlib.md5("123456".encode()).hexdigest(), "test@example.com", "测试用户", "user"))
        
        # 插入演示试卷
        for i in range(1, 11):
            await db.execute("""
                INSERT OR IGNORE INTO exam_papers (id, title, description, question_count, time_limit)
                VALUES (?, ?, ?, ?, ?)
            """, (i, f"模拟考试{i}", f"这是第{i}套模拟试卷", 50 + i*5, 90 + i*10))
        
        await db.commit()

# 工具函数
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=1)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def verify_token(token: str):
    """验证JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        return int(user_id)
    except jwt.PyJWTError:
        return None

async def get_current_user(token: str = Depends(lambda: None)):
    """获取当前用户 (简化版，实际应该从Header获取)"""
    if not token:
        return None
    user_id = verify_token(token)
    if not user_id:
        return None
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute("SELECT * FROM users WHERE id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "username": row[1],
                    "email": row[3],
                    "nickname": row[4],
                    "role": row[5],
                    "created_at": row[6]
                }
    return None

# API路由
@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "FastAPI 考试系统演示",
        "version": "1.0.0",
        "docs": "/docs",
        "performance_test": "python create_performance_test.py --url http://localhost:8000/api"
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "success": True,
        "message": "FastAPI 服务运行正常",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.post("/api/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """用户登录 - 异步版本"""
    start_time = time.time()
    
    # 模拟数据库查询延迟 (异步非阻塞)
    await asyncio.sleep(0.05)  # 50ms数据库延迟
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(
            "SELECT id, username, password_hash, email, nickname, role FROM users WHERE username = ?",
            (request.username,)
        ) as cursor:
            row = await cursor.fetchone()
            
            if row and row[2] == hashlib.md5(request.password.encode()).hexdigest():
                # 创建token
                access_token = create_access_token(data={"sub": str(row[0])})
                
                response_time = time.time() - start_time
                
                return LoginResponse(
                    success=True,
                    data={
                        "user": {
                            "id": row[0],
                            "username": row[1],
                            "email": row[3],
                            "nickname": row[4],
                            "role": row[5]
                        },
                        "access_token": access_token,
                        "refresh_token": access_token,  # 简化演示
                        "response_time": f"{response_time:.3f}s"
                    }
                )
    
    # 登录失败
    await asyncio.sleep(0.02)  # 防止时序攻击
    raise HTTPException(
        status_code=401,
        detail={"success": False, "error": {"code": "LOGIN_FAILED", "message": "用户名或密码错误"}}
    )

@app.get("/api/auth/profile")
async def get_profile():
    """获取用户信息 - 模拟认证"""
    start_time = time.time()
    
    # 模拟token验证和数据库查询
    await asyncio.sleep(0.03)  # 30ms延迟
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute("SELECT * FROM users WHERE username = 'admin'") as cursor:
            row = await cursor.fetchone()
            if row:
                response_time = time.time() - start_time
                return {
                    "success": True,
                    "data": {
                        "user": {
                            "id": row[0],
                            "username": row[1],
                            "email": row[3],
                            "nickname": row[4],
                            "role": row[5],
                            "created_at": row[6]
                        },
                        "response_time": f"{response_time:.3f}s"
                    }
                }
    
    raise HTTPException(status_code=401, detail="未授权")

@app.get("/api/exams/papers")
async def get_exam_papers():
    """获取试卷列表 - 异步版本"""
    start_time = time.time()
    
    # 模拟数据库查询
    await asyncio.sleep(0.08)  # 80ms延迟
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        papers = []
        async with db.execute("SELECT * FROM exam_papers ORDER BY created_at DESC") as cursor:
            async for row in cursor:
                papers.append({
                    "id": row[0],
                    "title": row[1],
                    "description": row[2],
                    "question_count": row[3],
                    "time_limit": row[4],
                    "created_at": row[5]
                })
        
        response_time = time.time() - start_time
        return {
            "success": True,
            "data": {
                "papers": papers,
                "total": len(papers),
                "response_time": f"{response_time:.3f}s"
            }
        }

@app.get("/api/statistics/overview")
async def get_statistics_overview():
    """获取统计概览 - 异步版本"""
    start_time = time.time()
    
    # 模拟复杂的统计查询
    await asyncio.sleep(0.12)  # 120ms延迟
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # 并发执行多个查询
        tasks = [
            db.execute("SELECT COUNT(*) FROM users"),
            db.execute("SELECT COUNT(*) FROM exam_papers"),
        ]
        
        results = await asyncio.gather(*[task.__aenter__() for task in tasks])
        
        user_count = await results[0].fetchone()
        paper_count = await results[1].fetchone()
        
        # 清理游标
        for result in results:
            await result.__aexit__(None, None, None)
        
        response_time = time.time() - start_time
        return {
            "success": True,
            "data": {
                "total_users": user_count[0] if user_count else 0,
                "total_exams": paper_count[0] if paper_count else 0,
                "total_questions": 500,  # 模拟数据
                "active_sessions": 0,
                "response_time": f"{response_time:.3f}s"
            }
        }

@app.get("/api/performance/stress-test")
async def stress_test():
    """压力测试端点 - 模拟高负载操作"""
    start_time = time.time()
    
    # 模拟多个并发数据库操作
    tasks = []
    for i in range(5):
        tasks.append(asyncio.sleep(0.1))  # 模拟100ms的I/O操作
    
    # 并发执行所有任务
    await asyncio.gather(*tasks)
    
    response_time = time.time() - start_time
    return {
        "success": True,
        "message": "压力测试完成",
        "operations": 5,
        "total_time": f"{response_time:.3f}s",
        "avg_time_per_operation": f"{response_time/5:.3f}s"
    }

# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    await init_database()
    print("🚀 FastAPI 演示服务启动完成")
    print("📊 性能测试命令:")
    print("   python create_performance_test.py --url http://localhost:8000/api --users 10")
    print("📖 API文档: http://localhost:8000/docs")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理"""
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)
    print("🛑 FastAPI 演示服务已关闭")

if __name__ == "__main__":
    import uvicorn
    print("🚀 启动 FastAPI 演示服务...")
    print("📊 与Flask对比测试:")
    print("   Flask: python create_performance_test.py --url http://localhost:5000/api --users 20")
    print("   FastAPI: python create_performance_test.py --url http://localhost:8000/api --users 20")
    
    uvicorn.run(
        "fastapi_demo:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        workers=1
    )