"""查找特定题目"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.question import Question

app = create_app()

with app.app_context():
    # 查找包含"三大法宝"的题目
    questions = Question.query.filter(
        Question.content.like('%三大法宝%')
    ).all()
    
    print(f"找到 {len(questions)} 道相关题目")
    
    for q in questions:
        print(f"\n题目 ID: {q.id}")
        print(f"题目类型: {q.question_type}")
        print(f"题目内容: {q.content}")
        print(f"选项类型: {type(q.options)}")
        print(f"选项内容: {q.options}")
        print(f"正确答案: {q.correct_answer}")
