"""
测试笔记增强功能
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.note import QuestionNote
from app.services.note_service import NoteService

def test_extract_linked_questions():
    """测试题目链接提取"""
    print("\n=== 测试题目链接提取 ===")
    
    # 测试用例1：单个链接
    content1 = "这道题很重要 [[Q:123]] 需要重点复习"
    links1 = NoteService.extract_linked_questions(content1)
    print(f"测试1: {content1}")
    print(f"提取结果: {links1}")
    assert links1 == [123], f"期望 [123]，实际 {links1}"
    print("✓ 测试1通过")
    
    # 测试用例2：多个链接
    content2 = "参考 [[Q:123]] 和 [[Q:456]] 以及 [[Q:789]]"
    links2 = NoteService.extract_linked_questions(content2)
    print(f"\n测试2: {content2}")
    print(f"提取结果: {links2}")
    assert links2 == [123, 456, 789], f"期望 [123, 456, 789]，实际 {links2}"
    print("✓ 测试2通过")
    
    # 测试用例3：无链接
    content3 = "这是普通笔记，没有题目链接"
    links3 = NoteService.extract_linked_questions(content3)
    print(f"\n测试3: {content3}")
    print(f"提取结果: {links3}")
    assert links3 == [], f"期望 []，实际 {links3}"
    print("✓ 测试3通过")
    
    # 测试用例4：混合内容
    content4 = """
    # 数学笔记
    
    这道题 [[Q:100]] 考察了二次函数的性质。
    
    ## 解题思路
    1. 先看 [[Q:101]] 的基础知识
    2. 然后参考 [[Q:102]] 的解法
    
    > 重点：配方法
    
    相关题目：[[Q:103]]、[[Q:104]]
    """
    links4 = NoteService.extract_linked_questions(content4)
    print(f"\n测试4: Markdown 格式笔记")
    print(f"提取结果: {links4}")
    assert links4 == [100, 101, 102, 103, 104], f"期望 [100, 101, 102, 103, 104]，实际 {links4}"
    print("✓ 测试4通过")
    
    print("\n✓ 所有题目链接提取测试通过！")

def test_note_model():
    """测试笔记模型"""
    print("\n=== 测试笔记模型 ===")
    
    app = create_app()
    
    with app.app_context():
        # 创建测试笔记
        note = QuestionNote(
            user_id=1,
            question_id=1,
            content="测试笔记 [[Q:123]] 和 [[Q:456]]",
            tags=["重点", "易错"],
            linked_questions=[123, 456]
        )
        
        # 测试 to_dict 方法
        note_dict = note.to_dict()
        print(f"笔记字典: {note_dict}")
        
        assert 'tags' in note_dict, "缺少 tags 字段"
        assert 'linked_questions' in note_dict, "缺少 linked_questions 字段"
        assert note_dict['tags'] == ["重点", "易错"], "tags 字段不正确"
        assert note_dict['linked_questions'] == [123, 456], "linked_questions 字段不正确"
        
        print("✓ 笔记模型测试通过！")

def test_integration():
    """集成测试"""
    print("\n=== 集成测试 ===")
    
    app = create_app()
    
    with app.app_context():
        # 查询现有笔记
        notes = QuestionNote.query.limit(5).all()
        
        if notes:
            print(f"\n找到 {len(notes)} 条笔记")
            for note in notes:
                print(f"\n笔记 #{note.id}:")
                print(f"  内容长度: {len(note.content)} 字符")
                print(f"  标签: {note.tags}")
                print(f"  链接题目: {note.linked_questions}")
                
                # 提取链接
                extracted_links = NoteService.extract_linked_questions(note.content)
                print(f"  提取的链接: {extracted_links}")
        else:
            print("数据库中暂无笔记")
        
        print("\n✓ 集成测试完成！")

def main():
    """运行所有测试"""
    print("=" * 60)
    print("笔记增强功能测试")
    print("=" * 60)
    
    try:
        # 测试1：题目链接提取
        test_extract_linked_questions()
        
        # 测试2：笔记模型
        test_note_model()
        
        # 测试3：集成测试
        test_integration()
        
        print("\n" + "=" * 60)
        print("✓ 所有测试通过！")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"\n✗ 测试失败: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
