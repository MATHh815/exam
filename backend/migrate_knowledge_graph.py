"""
知识点关系图谱数据库迁移脚本
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.knowledge_graph import KnowledgeRelation, UserKnowledgeMastery

def migrate():
    """执行迁移"""
    app = create_app()
    
    with app.app_context():
        print("开始创建知识点关系图谱相关表...")
        
        try:
            # 创建表
            db.create_all()
            print("✓ 数据库表创建成功")
            
            # 验证表是否存在
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            required_tables = ['knowledge_relations', 'user_knowledge_mastery']
            for table in required_tables:
                if table in tables:
                    print(f"✓ 表 {table} 已创建")
                else:
                    print(f"✗ 表 {table} 创建失败")
            
            print("\n知识点关系图谱迁移完成！")
            print("下一步: 运行 python init_knowledge_graph.py 初始化数据")
            
        except Exception as e:
            print(f"✗ 迁移失败: {e}")
            db.session.rollback()
            return False
    
    return True

if __name__ == '__main__':
    success = migrate()
    sys.exit(0 if success else 1)
