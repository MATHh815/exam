"""测试错题本功能"""
from app import create_app, db
from app.models.practice import WrongQuestion, PracticeRecord
from app.models.question import Question
from app.services.practice_service import PracticeService

app = create_app()
with app.app_context():
    print("=" * 50)
    print("测试错题本功能")
    print("=" * 50)
    
    # 获取第一个用户和第一道题
    user_id = 1
    question = Question.query.first()
    
    if not question:
        print("❌ 没有题目数据")
        exit(1)
    
    print(f"\n使用题目: ID={question.id}, 正确答案={question.correct_answer}")
    
    # 测试提交错误答案
    print("\n1. 提交错误答案...")
    wrong_answer = "Z"  # 故意答错
    
    try:
        result = PracticeService.submit_answer(
            user_id=user_id,
            question_id=question.id,
            user_answer=wrong_answer,
            time_spent=10
        )
        
        print(f"   判题结果: {'正确' if result['is_correct'] else '错误'}")
        
        # 检查错题本
        wrong_q = WrongQuestion.query.filter_by(
            user_id=user_id,
            question_id=question.id
        ).first()
        
        if wrong_q:
            print(f"   ✅ 错题已添加到错题本")
            print(f"      错误次数: {wrong_q.wrong_count}")
            print(f"      已掌握: {wrong_q.mastered}")
        else:
            print(f"   ❌ 错题未添加到错题本")
            
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    # 检查总数
    print(f"\n2. 错题本总数: {WrongQuestion.query.filter_by(user_id=user_id, mastered=False).count()}")
    print(f"   练习记录总数: {PracticeRecord.query.filter_by(user_id=user_id).count()}")
    
    print("\n" + "=" * 50)
