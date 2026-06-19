"""直接测试开始考试 API"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.exam import ExamPaper, ExamSession
from app.models.user import User
from app.services.exam_service import ExamService

app = create_app()

with app.app_context():
    print("=" * 60)
    print("测试开始考试 API")
    print("=" * 60)
    
    # 获取第一个用户和第一个已发布的试卷
    user = User.query.first()
    paper = ExamPaper.query.filter_by(is_published=True, is_deleted=False).first()
    
    if not user:
        print("❌ 没有找到用户")
        sys.exit(1)
    
    if not paper:
        print("❌ 没有找到已发布的试卷")
        sys.exit(1)
    
    print(f"用户: {user.username} (ID={user.id})")
    print(f"试卷: {paper.name} (ID={paper.id})")
    print(f"试卷发布状态: {paper.is_published}")
    
    # 检查题目数量
    from app.models.exam import ExamPaperQuestion
    question_count = ExamPaperQuestion.query.filter_by(paper_id=paper.id).count()
    print(f"试卷题目数量: {question_count}")
    
    # 检查进行中的会话
    existing = ExamSession.query.filter_by(
        user_id=user.id,
        paper_id=paper.id,
        status='in_progress'
    ).first()
    print(f"进行中的会话: {existing}")
    
    print("\n尝试调用 ExamService.start_exam()...")
    
    try:
        session = ExamService.start_exam(
            user_id=user.id,
            paper_id=paper.id
        )
        print(f"\n✅ 成功创建考试会话!")
        print(f"  会话 ID: {session.id}")
        print(f"  开始时间: {session.start_time}")
        print(f"  结束时间: {session.end_time}")
        print(f"  状态: {session.status}")
        
        # 清理测试数据
        db.session.delete(session)
        db.session.commit()
        print("\n已清理测试会话")
        
    except ValueError as e:
        print(f"\n❌ ValueError: {e}")
    except RuntimeError as e:
        print(f"\n❌ RuntimeError: {e}")
    except Exception as e:
        print(f"\n❌ 未知错误: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
