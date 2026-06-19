"""生成测试题目数据"""
from app import create_app, db
from app.models.question import Question
import json

app = create_app()

# 测试题目数据
test_questions = [
    {
        'exam_type': 'civil_service',
        'question_type': 'single_choice',
        'subject': '行测',
        'chapter': '数量关系',
        'difficulty': 3,
        'content': '某单位有职工100人，其中男职工60人。已知男职工中党员占40%，女职工中党员占30%，那么该单位党员人数是多少？',
        'options': json.dumps(['36人', '38人', '40人', '42人'], ensure_ascii=False),
        'correct_answer': 'A',
        'explanation': '男职工党员：60×40%=24人，女职工党员：(100-60)×30%=12人，总计：24+12=36人',
        'tags': json.dumps(['数量关系', '百分比计算'], ensure_ascii=False)
    },
    {
        'exam_type': 'civil_service',
        'question_type': 'single_choice',
        'subject': '行测',
        'chapter': '言语理解',
        'difficulty': 2,
        'content': '下列词语中，加点字的读音全都正确的一组是：',
        'options': json.dumps([
            'A. 档(dàng)案  模(mó)样  处(chǔ)理',
            'B. 角(jiǎo)色  着(zháo)急  勉强(qiǎng)',
            'C. 参(cān)与  供(gòng)给  应(yìng)届',
            'D. 载(zǎi)体  调(tiáo)查  差(chà)别'
        ], ensure_ascii=False),
        'correct_answer': 'C',
        'explanation': 'A项"模样"应读mú；B项"强"应读qiáng；D项"调查"应读diào',
        'tags': json.dumps(['言语理解', '字音'], ensure_ascii=False)
    },
    {
        'exam_type': 'civil_service',
        'question_type': 'single_choice',
        'subject': '行测',
        'chapter': '逻辑判断',
        'difficulty': 4,
        'content': '所有的天鹅都是白色的，这只鸟是黑色的，所以这只鸟不是天鹅。以下哪项与上述推理方式最为相似？',
        'options': json.dumps([
            'A. 所有的金属都导电，铜是金属，所以铜导电',
            'B. 所有的猫都吃鱼，这只动物不吃鱼，所以它不是猫',
            'C. 有些学生会游泳，小明是学生，所以小明会游泳',
            'D. 所有的鸟都会飞，企鹅是鸟，所以企鹅会飞'
        ], ensure_ascii=False),
        'correct_answer': 'B',
        'explanation': '题干推理形式：所有A是B，C不是B，所以C不是A。B选项符合这个推理形式。',
        'tags': json.dumps(['逻辑判断', '演绎推理'], ensure_ascii=False)
    },
    {
        'exam_type': 'civil_service',
        'question_type': 'single_choice',
        'subject': '申论',
        'chapter': '综合分析',
        'difficulty': 3,
        'content': '根据给定资料，概括当前我国城市交通拥堵的主要原因。（不超过200字）',
        'options': json.dumps([], ensure_ascii=False),
        'correct_answer': '1.机动车保有量快速增长；2.城市道路建设滞后；3.公共交通不够完善；4.交通管理水平有待提高；5.市民交通意识淡薄。',
        'explanation': '需要从材料中提炼要点，注意分条列举，语言简洁。',
        'tags': json.dumps(['申论', '概括题'], ensure_ascii=False)
    },
    {
        'exam_type': 'postgraduate',
        'question_type': 'single_choice',
        'subject': '英语',
        'chapter': '阅读理解',
        'difficulty': 4,
        'content': 'According to the passage, which of the following is true about climate change?',
        'options': json.dumps([
            'A. It only affects polar regions',
            'B. It is caused solely by human activities',
            'C. It has multiple contributing factors',
            'D. It can be easily reversed'
        ], ensure_ascii=False),
        'correct_answer': 'C',
        'explanation': '文章指出气候变化有多种促成因素，包括自然因素和人为因素。',
        'tags': json.dumps(['英语', '阅读理解'], ensure_ascii=False)
    },
    {
        'exam_type': 'postgraduate',
        'question_type': 'single_choice',
        'subject': '数学',
        'chapter': '高等数学',
        'difficulty': 5,
        'content': '设函数f(x)在[0,1]上连续，在(0,1)内可导，且f(0)=0，f(1)=1，证明：存在ξ∈(0,1)，使得f\'(ξ)=1。',
        'options': json.dumps([], ensure_ascii=False),
        'correct_answer': '由拉格朗日中值定理，存在ξ∈(0,1)，使得f\'(ξ)=[f(1)-f(0)]/(1-0)=1',
        'explanation': '直接应用拉格朗日中值定理即可证明。',
        'tags': json.dumps(['数学', '微分中值定理'], ensure_ascii=False)
    },
    {
        'exam_type': 'public_institution',
        'question_type': 'true_false',
        'subject': '公共基础知识',
        'chapter': '法律常识',
        'difficulty': 2,
        'content': '我国宪法规定，中华人民共和国的一切权力属于人民。',
        'options': json.dumps(['正确', '错误'], ensure_ascii=False),
        'correct_answer': 'A',
        'explanation': '《宪法》第二条明确规定：中华人民共和国的一切权力属于人民。',
        'tags': json.dumps(['法律', '宪法'], ensure_ascii=False)
    },
    {
        'exam_type': 'public_institution',
        'question_type': 'multiple_choice',
        'subject': '公共基础知识',
        'chapter': '时事政治',
        'difficulty': 3,
        'content': '党的二十大报告指出，中国式现代化的本质要求包括：',
        'options': json.dumps([
            'A. 坚持中国共产党领导',
            'B. 坚持中国特色社会主义',
            'C. 实现高质量发展',
            'D. 发展全过程人民民主',
            'E. 丰富人民精神世界'
        ], ensure_ascii=False),
        'correct_answer': 'ABCDE',
        'explanation': '这些都是中国式现代化的本质要求，需要全面准确把握。',
        'tags': json.dumps(['时事政治', '党的二十大'], ensure_ascii=False)
    },
    {
        'exam_type': 'civil_service',
        'question_type': 'single_choice',
        'subject': '行测',
        'chapter': '资料分析',
        'difficulty': 3,
        'content': '2022年某市GDP为5000亿元，比上年增长8%。问2021年该市GDP约为多少亿元？',
        'options': json.dumps(['4630', '4650', '4680', '4700'], ensure_ascii=False),
        'correct_answer': 'A',
        'explanation': '2021年GDP = 5000÷(1+8%) = 5000÷1.08 ≈ 4630亿元',
        'tags': json.dumps(['资料分析', '增长率计算'], ensure_ascii=False)
    },
    {
        'exam_type': 'civil_service',
        'question_type': 'single_choice',
        'subject': '行测',
        'chapter': '常识判断',
        'difficulty': 2,
        'content': '下列关于我国地理知识的表述，正确的是：',
        'options': json.dumps([
            'A. 我国最大的淡水湖是洞庭湖',
            'B. 我国最长的河流是黄河',
            'C. 我国最高的山峰是珠穆朗玛峰',
            'D. 我国最大的岛屿是海南岛'
        ], ensure_ascii=False),
        'correct_answer': 'C',
        'explanation': 'A项应为鄱阳湖；B项应为长江；D项应为台湾岛；C项正确。',
        'tags': json.dumps(['常识判断', '地理知识'], ensure_ascii=False)
    }
]

with app.app_context():
    print("开始生成测试题目...")
    
    # 检查是否已有题目
    existing_count = Question.query.count()
    if existing_count > 0:
        print(f"数据库中已有 {existing_count} 道题目")
        response = input("是否继续添加测试题目？(y/n): ")
        if response.lower() != 'y':
            print("操作已取消")
            exit(0)
    
    # 添加题目
    added_count = 0
    for q_data in test_questions:
        question = Question(**q_data)
        db.session.add(question)
        added_count += 1
    
    db.session.commit()
    
    print(f"\n✅ 成功添加 {added_count} 道测试题目！")
    
    # 显示添加的题目
    print("\n题目列表:")
    questions = Question.query.all()
    for q in questions:
        print(f"  ID: {q.id}, 类型: {q.exam_type}, 科目: {q.subject}, 难度: {q.difficulty}")
    
    print(f"\n数据库中现在共有 {len(questions)} 道题目")
    print("\n现在可以在试卷管理中添加这些题目了！")
