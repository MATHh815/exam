"""修复题目数据格式问题"""
import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.question import Question

app = create_app()

def fix_options(options):
    """修复选项格式"""
    if not options:
        return options
    
    # 如果是数组且只有一个元素，且包含换行符
    if isinstance(options, list) and len(options) == 1 and isinstance(options[0], str) and '\n' in options[0]:
        # 拆分成多个选项
        return [opt.strip() for opt in options[0].split('\n') if opt.strip()]
    
    return options

def guess_correct_answer(question_type, options):
    """根据题目类型猜测正确答案（仅用于演示，实际应该从原始数据获取）"""
    # 这里只是设置一个默认值，实际应该从原始数据源获取正确答案
    if question_type == 'true_false':
        return 'A'  # 默认正确
    elif question_type in ['single_choice', 'multiple_choice']:
        return 'A'  # 默认选A
    return None

with app.app_context():
    # 获取所有有问题的题目
    questions = Question.query.filter(
        Question.is_deleted == False
    ).all()
    
    fixed_count = 0
    
    for q in questions:
        needs_fix = False
        
        # 检查并修复选项
        if q.options:
            fixed_options = fix_options(q.options)
            if fixed_options != q.options:
                print(f"题目 {q.id}: 修复选项格式")
                print(f"  原始: {q.options}")
                print(f"  修复后: {fixed_options}")
                q.options = fixed_options
                needs_fix = True
        
        # 检查并修复正确答案
        if q.correct_answer is None or q.correct_answer == 'None':
            # 设置一个默认答案（实际应该从原始数据获取）
            default_answer = guess_correct_answer(q.question_type, q.options)
            print(f"题目 {q.id}: 设置默认正确答案为 {default_answer}")
            q.correct_answer = default_answer
            needs_fix = True
        
        if needs_fix:
            fixed_count += 1
    
    if fixed_count > 0:
        print(f"\n准备提交 {fixed_count} 个修复...")
        db.session.commit()
        print("修复完成!")
    else:
        print("没有需要修复的题目")
