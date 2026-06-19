"""检查数据库中的题目数据"""
from app import create_app, db
from app.models.question import Question

app = create_app()

with app.app_context():
    # 查询所有题目
    questions = Question.query.filter_by(is_deleted=False).all()
    
    print(f"数据库中共有 {len(questions)} 道未删除的题目")
    
    if len(questions) > 0:
        print("\n前10道题目:")
        for q in questions[:10]:
            print(f"  ID: {q.id}, 类型: {q.question_type}, 内容: {q.content[:50]}...")
    else:
        print("\n⚠️  数据库中没有题目数据！")
        print("   请先导入题目数据或生成测试题目")
        
    # 检查是否有已删除的题目
    deleted_questions = Question.query.filter_by(is_deleted=True).count()
    print(f"\n已删除的题目数量: {deleted_questions}")
