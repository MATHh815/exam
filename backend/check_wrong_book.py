"""检查错题本数据"""
from app import create_app, db
from app.models.practice import WrongQuestion, PracticeRecord

app = create_app()
with app.app_context():
    # 检查错题本
    wrong_count = WrongQuestion.query.count()
    print(f'错题本记录数: {wrong_count}')
    
    if wrong_count > 0:
        print('\n错题详情:')
        for wq in WrongQuestion.query.all():
            print(f'  - 用户{wq.user_id}, 题目{wq.question_id}, 错误次数{wq.wrong_count}, 已掌握{wq.mastered}')
    
    # 检查练习记录
    practice_count = PracticeRecord.query.count()
    print(f'\n练习记录数: {practice_count}')
    
    if practice_count > 0:
        print('\n练习记录详情:')
        for pr in PracticeRecord.query.all():
            print(f'  - 用户{pr.user_id}, 题目{pr.question_id}, 答案{pr.user_answer}, 正确{pr.is_correct}')
