"""修复题目正确答案"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.question import Question

app = create_app()

with app.app_context():
    # 获取所有正确答案为空的题目
    questions = Question.query.filter(
        Question.is_deleted == False,
        (Question.correct_answer == None) | (Question.correct_answer == 'None')
    ).all()
    
    print(f"找到 {len(questions)} 道正确答案为空的题目")
    
    for q in questions:
        # 根据题目类型设置默认答案
        if q.question_type == 'true_false':
            q.correct_answer = 'A'  # 默认正确
        elif q.question_type in ['single_choice', 'multiple_choice']:
            q.correct_answer = 'A'  # 默认选A
        
        print(f"题目 {q.id} ({q.question_type}): 设置正确答案为 {q.correct_answer}")
    
    db.session.commit()
    print("\n修复完成!")
