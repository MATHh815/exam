"""修复过期的考试会话"""
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.exam import ExamSession

app = create_app()

with app.app_context():
    print("正在检查过期的考试会话...")
    
    # 查找所有进行中但已超时的会话
    now = datetime.utcnow()
    expired_sessions = ExamSession.query.filter(
        ExamSession.status == 'in_progress',
        ExamSession.end_time < now
    ).all()
    
    print(f"找到 {len(expired_sessions)} 个过期会话")
    
    for session in expired_sessions:
        print(f"  - 会话 ID={session.id}, 试卷 ID={session.paper_id}, 结束时间={session.end_time}")
        # 标记为超时
        session.status = 'timeout'
        session.submit_time = now
    
    if expired_sessions:
        db.session.commit()
        print(f"\n✅ 已将 {len(expired_sessions)} 个过期会话标记为超时")
    else:
        print("\n没有需要处理的过期会话")
    
    # 显示当前状态
    remaining = ExamSession.query.filter_by(status='in_progress').count()
    print(f"\n当前进行中的会话数: {remaining}")
