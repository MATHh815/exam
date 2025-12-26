"""清除所有进行中的考试会话"""
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.exam import ExamSession

app = create_app()

with app.app_context():
    print("正在清除所有进行中的考试会话...")
    
    # 查找所有进行中的会话
    sessions = ExamSession.query.filter_by(status='in_progress').all()
    
    print(f"找到 {len(sessions)} 个进行中的会话")
    
    for session in sessions:
        print(f"  - 会话 ID={session.id}, 用户 ID={session.user_id}, 试卷 ID={session.paper_id}")
        # 标记为超时
        session.status = 'timeout'
        session.submit_time = datetime.utcnow()
    
    if sessions:
        db.session.commit()
        print(f"\n✅ 已将 {len(sessions)} 个会话标记为超时")
    else:
        print("\n没有进行中的会话")
    
    # 验证
    remaining = ExamSession.query.filter_by(status='in_progress').count()
    print(f"当前进行中的会话数: {remaining}")
