"""测试收藏功能的调试脚本"""
from app import create_app, db
from app.models.note import QuestionBookmark
from app.models.question import Question

app = create_app()

with app.app_context():
    # 检查表是否存在
    print("=" * 50)
    print("数据库表检查")
    print("=" * 50)
    
    try:
        bookmark_count = QuestionBookmark.query.count()
        print(f"✓ QuestionBookmark 表存在")
        print(f"  收藏总数: {bookmark_count}")
    except Exception as e:
        print(f"✗ QuestionBookmark 表错误: {e}")
    
    try:
        question_count = Question.query.count()
        print(f"✓ Question 表存在")
        print(f"  题目总数: {question_count}")
    except Exception as e:
        print(f"✗ Question 表错误: {e}")
    
    # 检查收藏数据
    print("\n" + "=" * 50)
    print("收藏数据检查")
    print("=" * 50)
    
    bookmarks = QuestionBookmark.query.limit(5).all()
    if bookmarks:
        print(f"找到 {len(bookmarks)} 条收藏记录（显示前5条）:")
        for bm in bookmarks:
            print(f"\n收藏ID: {bm.id}")
            print(f"  用户ID: {bm.user_id}")
            print(f"  题目ID: {bm.question_id}")
            print(f"  标签: {bm.tags}")
            print(f"  备注: {bm.notes[:50] if bm.notes else '无'}")
            print(f"  创建时间: {bm.created_at}")
            
            # 检查关联的题目
            if bm.question:
                print(f"  关联题目: {bm.question.content[:50]}...")
            else:
                print(f"  ✗ 警告: 题目ID {bm.question_id} 不存在")
    else:
        print("没有找到收藏记录")
    
    # 检查 API 路由
    print("\n" + "=" * 50)
    print("API 路由检查")
    print("=" * 50)
    
    bookmark_routes = [rule for rule in app.url_map.iter_rules() if 'bookmark' in rule.rule.lower()]
    if bookmark_routes:
        print(f"找到 {len(bookmark_routes)} 个收藏相关路由:")
        for route in bookmark_routes:
            print(f"  {route.methods} {route.rule}")
    else:
        print("✗ 警告: 没有找到收藏相关路由")
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)
