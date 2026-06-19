"""检查正确答案字段"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.question import Question

app = create_app()

with app.app_context():
    # 获取几道题目检查正确答案
    questions = Question.query.filter(
        Question.is_deleted == False
    ).limit(10).all()
    
    for q in questions:
        print(f"题目 {q.id}:")
        print(f"  correct_answer 值: {repr(q.correct_answer)}")
        print(f"  correct_answer 类型: {type(q.correct_answer)}")
        print(f"  是否为 None: {q.correct_answer is None}")
        print(f"  是否为 'None': {q.correct_answer == 'None'}")
        print()
