"""测试 API 返回的数据格式"""
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
    
    # 找到"三大法宝"的题目
    for q in questions:
        if '三大法宝' in q.get('content', ''):
            print("找到题目:")
            print(json.dumps(q, ensure_ascii=False, indent=2))
            break
