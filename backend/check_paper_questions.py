"""检查试卷题目的脚本"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from app.models.exam import ExamPaper, ExamPaperQuestion
from app.models.question import Question

def check_papers():
    """检查所有试卷的题目情况"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("检查试卷题目情况")
        print("=" * 60)
        
        papers = ExamPaper.query.filter_by(is_published=True).all()
        
        if not papers:
            print("\n❌ 没有找到已发布的试卷")
            return
        
        print(f"\n找到 {len(papers)} 个已发布的试卷\n")
        
        for paper in papers:
            print(f"试卷 ID: {paper.id}")
            print(f"试卷名称: {paper.name}")
            print(f"考试类型: {paper.exam_type}")
            print(f"考试时长: {paper.duration} 分钟")
            print(f"总分: {paper.total_score}")
            
            # 查询题目数量
            paper_questions = ExamPaperQuestion.query.filter_by(
                paper_id=paper.id
            ).all()
            
            question_count = len(paper_questions)
            print(f"题目数量: {question_count}")
            
            if question_count == 0:
                print("⚠️  警告：该试卷没有题目！")
            else:
                print("✓ 该试卷有题目")
                
                # 显示题目详情
                print("\n题目列表:")
                for pq in paper_questions:
                    question = Question.query.get(pq.question_id)
                    if question and not question.is_deleted:
                        print(f"  - 题目 {pq.order}: {question.content[:50]}... (分值: {pq.score})")
                    else:
                        print(f"  - 题目 {pq.order}: [已删除或不存在] (分值: {pq.score})")
            
            print("-" * 60)
            print()

def add_sample_questions_to_paper(paper_id):
    """为指定试卷添加示例题目"""
    app = create_app()
    
    with app.app_context():
        paper = ExamPaper.query.get(paper_id)
        if not paper:
            print(f"❌ 试卷 {paper_id} 不存在")
            return
        
        print(f"为试卷 '{paper.name}' 添加示例题目...")
        
        # 查找可用的题目
        questions = Question.query.filter_by(
            exam_type=paper.exam_type,
            is_deleted=False
        ).limit(10).all()
        
        if not questions:
            print(f"❌ 没有找到类型为 {paper.exam_type} 的题目")
            print("请先在题库中添加题目")
            return
        
        # 添加题目到试卷
        for i, question in enumerate(questions, 1):
            # 检查题目是否已存在
            existing = ExamPaperQuestion.query.filter_by(
                paper_id=paper_id,
                question_id=question.id
            ).first()
            
            if existing:
                print(f"  题目 {question.id} 已存在，跳过")
                continue
            
            # 根据题目类型设置分值
            score_map = {
                'single_choice': 2,
                'multiple_choice': 3,
                'true_false': 1,
                'fill_blank': 2,
                'short_answer': 5
            }
            score = score_map.get(question.question_type, 2)
            
            pq = ExamPaperQuestion(
                paper_id=paper_id,
                question_id=question.id,
                order=i,
                score=score
            )
            db.session.add(pq)
            
            # 更新试卷总分
            paper.total_score += score
            
            print(f"  ✓ 添加题目 {i}: {question.content[:50]}... (分值: {score})")
        
        db.session.commit()
        print(f"\n✓ 成功添加题目到试卷")
        print(f"试卷总分: {paper.total_score}")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='检查和管理试卷题目')
    parser.add_argument('--check', action='store_true', help='检查所有试卷的题目情况')
    parser.add_argument('--add', type=int, metavar='PAPER_ID', help='为指定试卷添加示例题目')
    
    args = parser.parse_args()
    
    if args.check:
        check_papers()
    elif args.add:
        add_sample_questions_to_paper(args.add)
    else:
        parser.print_help()
