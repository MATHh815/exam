"""检查题目选项格式"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.question import Question

app = create_app()

with app.app_context():
    # 获取几道题目检查选项格式
    questions = Question.query.filter(
        Question.is_deleted == False,
        Question.question_type.in_(['single_choice', 'multiple_choice'])
    ).limit(5).all()
    
    print(f"找到 {len(questions)} 道选择题")
    print("=" * 60)
    
    for q in questions:
        print(f"\n题目 ID: {q.id}")
        print(f"题目类型: {q.question_type}")
        print(f"题目内容: {q.content[:50]}...")
        print(f"选项类型: {type(q.options)}")
        print(f"选项内容: {q.options}")
        print(f"正确答案: {q.correct_answer}")
        print("-" * 40)
