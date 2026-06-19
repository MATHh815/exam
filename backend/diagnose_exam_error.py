"""诊断考试开始失败的问题"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.exam import ExamPaper, ExamPaperQuestion, ExamSession
from app.models.user import User

app = create_app()

with app.app_context():
    print("=" * 60)
    print("考试系统诊断报告")
    print("=" * 60)
    
    # 1. 检查试卷
    print("\n【1. 试卷状态检查】")
    papers = ExamPaper.query.filter_by(is_deleted=False).all()
    print(f"总试卷数: {len(papers)}")
    
    for paper in papers:
        question_count = ExamPaperQuestion.query.filter_by(paper_id=paper.id).count()
        print(f"\n  试卷 ID={paper.id}: {paper.name}")
        print(f"    - 发布状态: {'已发布' if paper.is_published else '未发布'}")
        print(f"    - 题目数量: {question_count}")
        print(f"    - 考试时长: {paper.duration} 分钟")
        print(f"    - 总分: {paper.total_score}")
        
        # 检查问题
        issues = []
        if not paper.is_published:
            issues.append("❌ 试卷未发布")
        if question_count == 0:
            issues.append("❌ 试卷没有题目")
        
        if issues:
            print(f"    - 问题: {', '.join(issues)}")
        else:
            print(f"    - 状态: ✅ 可以开始考试")
    
    # 2. 检查进行中的考试会话
    print("\n【2. 进行中的考试会话】")
    in_progress_sessions = ExamSession.query.filter_by(status='in_progress').all()
    print(f"进行中的会话数: {len(in_progress_sessions)}")
    
    for session in in_progress_sessions:
        user = User.query.get(session.user_id)
        paper = ExamPaper.query.get(session.paper_id)
        print(f"\n  会话 ID={session.id}:")
        print(f"    - 用户: {user.username if user else 'Unknown'} (ID={session.user_id})")
        print(f"    - 试卷: {paper.name if paper else 'Unknown'} (ID={session.paper_id})")
        print(f"    - 开始时间: {session.start_time}")
        print(f"    - 结束时间: {session.end_time}")
    
    # 3. 检查用户
    print("\n【3. 用户检查】")
    users = User.query.filter_by(is_active=True).all()
    print(f"活跃用户数: {len(users)}")
    for user in users[:5]:  # 只显示前5个
        print(f"  - {user.username} (ID={user.id}, 角色={user.role})")
    
    # 4. 建议
    print("\n【4. 解决建议】")
    
    # 检查是否有可用的试卷
    available_papers = [p for p in papers if p.is_published and ExamPaperQuestion.query.filter_by(paper_id=p.id).count() > 0]
    
    if not available_papers:
        print("  ❌ 没有可用的试卷！请确保：")
        print("     1. 至少有一个试卷已发布 (is_published=True)")
        print("     2. 试卷中至少有一道题目")
    else:
        print(f"  ✅ 有 {len(available_papers)} 个可用试卷")
    
    if in_progress_sessions:
        print(f"\n  ⚠️ 有 {len(in_progress_sessions)} 个进行中的会话")
        print("     如果需要清除，可以运行: python clear_sessions.py")
    
    print("\n" + "=" * 60)
