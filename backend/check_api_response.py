"""检查 API 返回的题目数据格式"""
import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.question import Question
from app.services.exam_paper_service import ExamPaperService

app = create_app()

with app.app_context():
    # 获取试卷3的题目
    questions = ExamPaperService.get_paper_questions(3)
    
    print(f"试卷3包含 {len(questions)} 道题目")
    print("=" * 60)
    
    if questions:
        q = questions[0]
        print(f"\n第一道题目:")
        print(f"ID: {q.get('id')}")
        print(f"题目类型: {q.get('question_type')}")
        print(f"题目内容: {q.get('content', '')[:50]}...")
        print(f"选项类型: {type(q.get('options'))}")
        print(f"选项内容: {q.get('options')}")
        print(f"正确答案: {q.get('correct_answer')}")
        
        # 模拟 JSON 序列化
        print("\n\nJSON 序列化后:")
        json_str = json.dumps(q, ensure_ascii=False, indent=2)
        print(json_str[:500])
