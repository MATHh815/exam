"""
初始化知识点关系图谱数据
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.knowledge_point import KnowledgePoint
from app.models.knowledge_graph import KnowledgeRelation, UserKnowledgeMastery

def init_knowledge_relations():
    """初始化知识点关系"""
    app = create_app()
    
    with app.app_context():
        print("开始初始化知识点关系...")
        
        try:
            # 获取所有知识点
            knowledge_points = KnowledgePoint.query.all()
            
            if not knowledge_points:
                print("警告: 没有找到知识点数据，请先初始化题库")
                return False
            
            # 创建知识点名称到ID的映射
            kp_dict = {kp.name: kp.id for kp in knowledge_points}
            
            # 定义知识点关系（示例数据）
            relations_data = [
                # Python 基础关系
                ('变量与数据类型', '运算符与表达式', 'prerequisite', 0.9),
                ('运算符与表达式', '控制流程', 'prerequisite', 0.9),
                ('控制流程', '函数定义', 'prerequisite', 0.9),
                ('函数定义', '递归', 'prerequisite', 0.8),
                ('函数定义', '装饰器', 'prerequisite', 0.7),
                ('控制流程', '循环结构', 'prerequisite', 0.9),
                ('运算符与表达式', '字符串操作', 'prerequisite', 0.7),
                ('变量与数据类型', '列表与元组', 'prerequisite', 0.8),
                ('列表与元组', '字典与集合', 'prerequisite', 0.8),
                ('字典与集合', '推导式', 'prerequisite', 0.7),
                ('列表与元组', '迭代器与生成器', 'prerequisite', 0.6),
                
                # 相关关系
                ('循环结构', '迭代器与生成器', 'related', 0.8),
                ('函数定义', '推导式', 'related', 0.6),
                ('字符串操作', '正则表达式', 'related', 0.7),
                
                # 数据结构关系
                ('数组', '链表', 'prerequisite', 0.7),
                ('链表', '栈', 'prerequisite', 0.6),
                ('链表', '队列', 'prerequisite', 0.6),
                ('栈', '递归', 'related', 0.8),
                ('数组', '排序算法', 'prerequisite', 0.8),
                ('排序算法', '查找算法', 'related', 0.7),
                
                # 算法关系
                ('递归', '动态规划', 'prerequisite', 0.7),
                ('递归', '分治算法', 'prerequisite', 0.7),
                ('贪心算法', '动态规划', 'related', 0.6),
            ]
            
            # 创建关系
            created_count = 0
            skipped_count = 0
            
            for source_name, target_name, rel_type, strength in relations_data:
                # 检查知识点是否存在
                if source_name not in kp_dict or target_name not in kp_dict:
                    skipped_count += 1
                    continue
                
                source_id = kp_dict[source_name]
                target_id = kp_dict[target_name]
                
                # 检查关系是否已存在
                existing = KnowledgeRelation.query.filter_by(
                    source_id=source_id,
                    target_id=target_id,
                    relation_type=rel_type
                ).first()
                
                if existing:
                    skipped_count += 1
                    continue
                
                # 创建新关系
                relation = KnowledgeRelation(
                    source_id=source_id,
                    target_id=target_id,
                    relation_type=rel_type,
                    strength=strength
                )
                db.session.add(relation)
                created_count += 1
            
            db.session.commit()
            
            print(f"✓ 知识点关系初始化完成")
            print(f"  - 创建关系: {created_count} 个")
            print(f"  - 跳过关系: {skipped_count} 个")
            
            # 统计信息
            total_relations = KnowledgeRelation.query.count()
            print(f"  - 总关系数: {total_relations} 个")
            
            return True
            
        except Exception as e:
            print(f"✗ 初始化失败: {e}")
            db.session.rollback()
            return False

def init_sample_mastery():
    """初始化示例掌握度数据（用于测试）"""
    app = create_app()
    
    with app.app_context():
        print("\n开始初始化示例掌握度数据...")
        
        try:
            # 获取测试用户
            from app.models.user import User
            user = User.query.filter_by(username='student').first()
            
            if not user:
                print("警告: 未找到测试用户 'student'")
                return False
            
            # 获取所有知识点
            knowledge_points = KnowledgePoint.query.limit(20).all()
            
            import random
            created_count = 0
            
            for kp in knowledge_points:
                # 随机生成掌握度数据
                practice_count = random.randint(5, 50)
                correct_count = random.randint(int(practice_count * 0.3), practice_count)
                
                # 检查是否已存在
                existing = UserKnowledgeMastery.query.filter_by(
                    user_id=user.id,
                    knowledge_point_id=kp.id
                ).first()
                
                if existing:
                    continue
                
                # 创建掌握度记录
                mastery = UserKnowledgeMastery(
                    user_id=user.id,
                    knowledge_point_id=kp.id,
                    practice_count=practice_count,
                    correct_count=correct_count
                )
                
                # 生成最近练习记录
                recent = [random.choice([0, 1]) for _ in range(10)]
                import json
                mastery.recent_practices = json.dumps(recent)
                
                # 计算掌握度
                from app.services.knowledge_graph_service import KnowledgeGraphService
                mastery.mastery_score = KnowledgeGraphService._calculate_mastery_score(mastery, recent)
                
                db.session.add(mastery)
                created_count += 1
            
            db.session.commit()
            
            print(f"✓ 示例掌握度数据初始化完成")
            print(f"  - 创建记录: {created_count} 个")
            
            return True
            
        except Exception as e:
            print(f"✗ 初始化失败: {e}")
            db.session.rollback()
            return False

def main():
    """主函数"""
    print("=" * 60)
    print("知识点关系图谱数据初始化")
    print("=" * 60)
    
    # 初始化关系
    if not init_knowledge_relations():
        print("\n初始化失败")
        sys.exit(1)
    
    # 初始化示例掌握度
    if not init_sample_mastery():
        print("\n初始化失败")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("初始化完成！")
    print("=" * 60)

if __name__ == '__main__':
    main()
