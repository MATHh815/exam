"""列出试卷3的所有题目"""
import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.services.exam_paper_service import ExamPaperService

app = create_app()

with app.app_context():
    # 获取试卷3的题目
    questions = ExamPaperService.get_paper_questions(3)
    
    print(f"试卷3包含 {len(questions)} 道题目:")
    for i, q in enumerate(questions):
        print(f"\n{i+1}. ID={q.get('id')}, 类型={q.get('question_type')}")
        print(f"   内容: {q.get('content', '')[:50]}...")
        print(f"   选项: {q.get('options')}")
