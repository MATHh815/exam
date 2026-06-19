"""测试开始考试流程"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from app.models.user import User
from app.models.exam import ExamPaper, ExamSession
from app.services.exam_service import ExamService

def test_start_exam():
    """测试开始考试"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("测试开始考试流程")
        print("=" * 60)
        
        # 查找一个测试用户
        user = User.query.filter_by(username='student').first()
        if not user:
            print("❌ 找不到测试用户 'student'")
            print("请先运行 seed_exam_data.py 创建测试数据")
            return
        
        print(f"\n✓ 找到测试用户: {user.username} (ID: {user.id})")
        
        # 查找一个已发布的试卷
        paper = ExamPaper.query.filter_by(is_published=True).first()
        if not paper:
            print("❌ 找不到已发布的试卷")
            return
        
        print(f"✓ 找到试卷: {paper.name} (ID: {paper.id})")
        
        # 检查是否有进行中的考试
        existing_session = ExamSession.query.filter_by(
            user_id=user.id,
            paper_id=paper.id,
            status='in_progress'
        ).first()
        
        if existing_session:
            print(f"\n⚠️  用户已有进行中的考试会话 (ID: {existing_session.id})")
            print("正在删除旧会话...")
            db.session.delete(existing_session)
            db.session.commit()
            print("✓ 旧会话已删除")
        
        # 尝试开始考试
        print(f"\n正在开始考试...")
        try:
            session = ExamService.start_exam(
                user_id=user.id,
                paper_id=paper.id
            )
            
            print(f"✓ 考试开始成功!")
            print(f"  会话 ID: {session.id}")
            print(f"  开始时间: {session.start_time}")
            print(f"  结束时间: {session.end_time}")
            print(f"  状态: {session.status}")
            
            # 清理测试数据
            print(f"\n正在清理测试数据...")
            db.session.delete(session)
            db.session.commit()
            print("✓ 测试数据已清理")
            
        except Exception as e:
            print(f"❌ 开始考试失败: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_start_exam()
