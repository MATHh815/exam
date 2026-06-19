"""
快速清理所有进行中的考试会话
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.exam import ExamSession

app = create_app()

with app.app_context():
    # 查找所有进行中的会话
    sessions = ExamSession.query.filter_by(status='in_progress').all()
    
    print(f"找到 {len(sessions)} 个进行中的考试会话")
    
    if sessions:
        for session in sessions:
            print(f"删除会话: ID={session.id}, 用户={session.user_id}, 试卷={session.paper_id}")
            db.session.delete(session)
        
        db.session.commit()
        print(f"\n✅ 已清理 {len(sessions)} 个会话")
    else:
        print("✅ 没有需要清理的会话")
