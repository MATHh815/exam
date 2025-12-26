"""检查所有题目的选项格式"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.question import Question
from app.services.exam_paper_service import ExamPaperService

app = create_app()

with app.app_context():
    # 获取试卷3的所有题目
    questions = ExamPaperService.get_paper_questions(3)
    
    print(f"试卷3包含 {len(questions)} 道题目")
    print("=" * 60)
    
    problem_count = 0
    for i, q in enumerate(questions[:10]):  # 只检查前10道
        options = q.get('options')
        correct = q.get('correct_answer')
        qtype = q.get('question_type')
        
        has_problem = False
        problems = []
        
        # 检查选项格式
        if options:
            if isinstance(options, list) and len(options) == 1 and '\n' in str(options[0]):
                has_problem = True
                problems.append("选项被合并成一个字符串")
        
        # 检查正确答案
        if correct is None:
            has_problem = True
            problems.append("正确答案为空")
        
        if has_problem:
            problem_count += 1
            print(f"\n题目 {i+1} (ID: {q.get('id')}) - 有问题!")
            print(f"  类型: {qtype}")
            print(f"  选项: {options}")
            print(f"  正确答案: {correct}")
            print(f"  问题: {', '.join(problems)}")
    
    print(f"\n\n总结: 前10道题中有 {problem_count} 道题有格式问题")
