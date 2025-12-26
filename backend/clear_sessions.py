"""
清理进行中的考试会话
用于测试和调试
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.exam import ExamSession

def clear_in_progress_sessions(user_id=None):
    """清理进行中的考试会话
    
    Args:
        user_id: 用户ID，如果指定则只清理该用户的会话
    """
    app = create_app()
    
    with app.app_context():
        query = ExamSession.query.filter_by(status='in_progress')
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        sessions = query.all()
        
        if not sessions:
            print("没有找到进行中的考试会话")
            return
        
        print(f"找到 {len(sessions)} 个进行中的考试会话:")
        for session in sessions:
            print(f"  - 会话ID: {session.id}, 用户ID: {session.user_id}, 试卷ID: {session.paper_id}, 开始时间: {session.start_time}")
        
        confirm = input("\n确定要清理这些会话吗? (yes/no): ")
        
        if confirm.lower() == 'yes':
            for session in sessions:
                db.session.delete(session)
            
            db.session.commit()
            print(f"\n已清理 {len(sessions)} 个会话")
        else:
            print("\n已取消")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='清理进行中的考试会话')
    parser.add_argument('--user-id', type=int, help='指定用户ID')
    
    args = parser.parse_args()
    
    clear_in_progress_sessions(args.user_id)
