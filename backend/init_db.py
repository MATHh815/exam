"""数据库初始化脚本

创建初始管理员用户和示例数据
"""
from app import create_app, db
from app.models import User, Question

app = create_app()

with app.app_context():
    print("开始初始化数据库...")
    
    # 检查是否已有管理员用户
    admin = User.query.filter_by(username='admin').first()
    
    if not admin:
        print("\n创建管理员用户...")
        admin = User(
            username='admin',
            email='admin@example.com',
            nickname='系统管理员',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print(f"✓ 管理员用户创建成功: {admin.username}")
        print(f"  用户名: admin")
        print(f"  密码: admin123")
    else:
        print(f"\n管理员用户已存在: {admin.username}")
    
    # 创建示例普通用户
    student = User.query.filter_by(username='student').first()
    if not student:
        print("\n创建示例学生用户...")
        student = User(
            username='student',
            email='student@example.com',
            nickname='测试学生',
            role='user'
        )
        student.set_password('student123')
        db.session.add(student)
        db.session.commit()
        print(f"✓ 学生用户创建成功: {student.username}")
        print(f"  用户名: student")
        print(f"  密码: student123")
    else:
        print(f"\n学生用户已存在: {student.username}")
    
    # 创建示例题目
    question_count = Question.query.count()
    if question_count == 0:
        print("\n创建示例题目...")
        
        sample_questions = [
            {
                'exam_type': 'civil_service',
                'question_type': 'single_choice',
                'subject': '行测',
                'chapter': '数量关系',
                'difficulty': 2,
                'content': '某单位有职工100人，其中男职工60人。已知男职工中党员占40%，女职工中党员占50%，那么该单位党员人数是多少？',
                'options': ['A. 44人', 'B. 45人', 'C. 46人', 'D. 47人'],
                'correct_answer': 'A',
                'explanation': '男职工党员：60×40%=24人，女职工党员：(100-60)×50%=20人，总计：24+20=44人',
                'tags': ['数量关系', '百分比计算']
            },
            {
                'exam_type': 'civil_service',
                'question_type': 'single_choice',
                'subject': '行测',
                'chapter': '言语理解',
                'difficulty': 3,
                'content': '下列词语中，加点字的读音全都正确的一组是：',
                'options': ['A. 档(dàng)案  模(mó)样', 'B. 处(chǔ)理  角(jué)色', 'C. 参(cān)与  着(zháo)急', 'D. 勉强(qiǎng)  强(qiáng)大'],
                'correct_answer': 'C',
                'explanation': 'A项"模样"应读mú yàng；B项"角色"应读jué sè；D项"勉强"应读miǎn qiǎng',
                'tags': ['言语理解', '字音']
            },
            {
                'exam_type': 'postgraduate',
                'question_type': 'single_choice',
                'subject': '数学',
                'chapter': '高等数学',
                'difficulty': 4,
                'content': '设函数f(x)在x=0处可导，且f(0)=0，f\'(0)=1，则lim(x→0)[f(x)/x]等于：',
                'options': ['A. 0', 'B. 1', 'C. 2', 'D. 不存在'],
                'correct_answer': 'B',
                'explanation': '根据导数定义，f\'(0)=lim(x→0)[f(x)-f(0)]/x=lim(x→0)[f(x)/x]=1',
                'tags': ['高等数学', '极限', '导数']
            }
        ]
        
        for q_data in sample_questions:
            question = Question.create_from_dict(q_data, created_by=admin.id)
            db.session.add(question)
        
        db.session.commit()
        print(f"✓ 创建了 {len(sample_questions)} 道示例题目")
    else:
        print(f"\n已有 {question_count} 道题目")
    
    print("\n✅ 数据库初始化完成！")
    print("\n可以使用以下账号登录：")
    print("  管理员 - 用户名: admin, 密码: admin123")
    print("  学生   - 用户名: student, 密码: student123")
