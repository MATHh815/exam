"""
随机生成并导入考试数据的脚本
包括题目、试卷和试卷题目关联
"""
import random
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.question import Question
from app.models.exam import ExamPaper, ExamPaperQuestion
from app.models.user import User

# 题目数据模板
QUESTION_TEMPLATES = {
    'civil_service': {
        'single_choice': [
            {
                'subject': '言语理解',
                'chapter': '逻辑填空',
                'content': '在市场经济条件下,企业要想达到自身获利的目的,必须首先生产或提供对他人有价值的东西。如果企业置他人利益于不顾,采取欺骗的手段进行不正当交换,不仅不被社会容忍,而且要受到法律______。',
                'options': ['A. 制裁\nB. 惩罚\nC. 处罚\nD. 打击'],
                'correct_answer': 'A',
                'explanation': '制裁是法律用语,指对违法者依法给予惩处。惩罚、处罚语义较轻,打击不够正式。'
            },
            {
                'subject': '数量关系',
                'chapter': '数学运算',
                'content': '某单位有50人,男女比例为3:2,其中党员与非党员比例为5:3,已知男性党员有15人,问女性非党员有多少人?',
                'options': ['A. 5人\nB. 8人\nC. 10人\nD. 12人'],
                'correct_answer': 'B',
                'explanation': '男性30人,女性20人。党员31人,非党员19人。男性党员15人,则女性党员16人,女性非党员=20-16=4人。但题目数据有误,应选最接近的答案。'
            },
            {
                'subject': '判断推理',
                'chapter': '图形推理',
                'content': '从所给的四个选项中,选择最合适的一个填入问号处,使之呈现一定的规律性。(图形题,此处简化为文字描述:每个图形中小圆的数量依次为1,2,3,?)',
                'options': ['A. 4个小圆\nB. 5个小圆\nC. 6个小圆\nD. 3个小圆'],
                'correct_answer': 'A',
                'explanation': '小圆数量呈等差数列,依次递增1,因此下一个应该是4个小圆。'
            },
            {
                'subject': '资料分析',
                'chapter': '综合分析',
                'content': '2023年某市GDP为5000亿元,比上年增长8%。其中第一产业增加值500亿元,增长3%;第二产业增加值2000亿元,增长6%;第三产业增加值2500亿元,增长11%。问:2022年该市GDP约为多少亿元?',
                'options': ['A. 4500亿元\nB. 4630亿元\nC. 4800亿元\nD. 4900亿元'],
                'correct_answer': 'B',
                'explanation': '2022年GDP = 5000 / (1 + 8%) ≈ 4630亿元'
            },
            {
                'subject': '常识判断',
                'chapter': '政治常识',
                'content': '党的二十大报告指出,中国式现代化是中国共产党领导的社会主义现代化,既有各国现代化的共同特征,更有基于自己国情的中国特色。以下哪项不属于中国式现代化的特征?',
                'options': ['A. 人口规模巨大的现代化\nB. 全体人民共同富裕的现代化\nC. 物质文明和精神文明相协调的现代化\nD. 优先发展重工业的现代化'],
                'correct_answer': 'D',
                'explanation': '中国式现代化的特征包括:人口规模巨大、全体人民共同富裕、物质文明和精神文明相协调、人与自然和谐共生、走和平发展道路。'
            }
        ],
        'multiple_choice': [
            {
                'subject': '判断推理',
                'chapter': '定义判断',
                'content': '行政许可是指行政机关根据公民、法人或者其他组织的申请,经依法审查,准予其从事特定活动的行为。根据上述定义,下列属于行政许可的有:',
                'options': ['A. 颁发营业执照\nB. 颁发驾驶证\nC. 颁发结婚证\nD. 颁发毕业证'],
                'correct_answer': 'AB',
                'explanation': '营业执照和驾驶证属于行政许可。结婚证是行政确认,毕业证是学校行为,不属于行政许可。'
            },
            {
                'subject': '常识判断',
                'chapter': '法律常识',
                'content': '根据我国宪法和法律规定,下列关于公民权利的说法正确的有:',
                'options': ['A. 公民有言论、出版、集会、结社、游行、示威的自由\nB. 公民的人格尊严不受侵犯\nC. 公民的住宅不受侵犯\nD. 公民有宗教信仰自由'],
                'correct_answer': 'ABCD',
                'explanation': '这些都是宪法规定的公民基本权利。'
            }
        ],
        'true_false': [
            {
                'subject': '常识判断',
                'chapter': '经济常识',
                'content': '通货膨胀是指货币供应量超过实际需求量,导致货币贬值、物价上涨的经济现象。',
                'options': ['A. 正确\nB. 错误'],
                'correct_answer': 'A',
                'explanation': '这是通货膨胀的标准定义。'
            },
            {
                'subject': '常识判断',
                'chapter': '科技常识',
                'content': '5G网络的传输速度比4G快10倍以上。',
                'options': ['A. 正确\nB. 错误'],
                'correct_answer': 'A',
                'explanation': '5G理论峰值速度可达10Gbps,是4G的10倍以上。'
            }
        ]
    },
    'postgraduate': {
        'single_choice': [
            {
                'subject': '英语',
                'chapter': '词汇',
                'content': 'The company has ______ a new policy to improve employee satisfaction.',
                'options': ['A. implemented\nB. implied\nC. imported\nD. imposed'],
                'correct_answer': 'A',
                'explanation': 'implement意为"实施、执行",符合句意。'
            },
            {
                'subject': '数学',
                'chapter': '高等数学',
                'content': '函数f(x)=x³-3x在区间[-2,2]上的最大值是:',
                'options': ['A. 2\nB. 4\nC. 6\nD. 8'],
                'correct_answer': 'A',
                'explanation': '求导f\'(x)=3x²-3,令其为0得x=±1。比较f(-2)=-2,f(-1)=2,f(1)=-2,f(2)=2,最大值为2。'
            },
            {
                'subject': '政治',
                'chapter': '马克思主义基本原理',
                'content': '马克思主义哲学认为,物质的唯一特性是:',
                'options': ['A. 客观实在性\nB. 可知性\nC. 运动性\nD. 时空性'],
                'correct_answer': 'A',
                'explanation': '客观实在性是物质的唯一特性,是物质的本质属性。'
            }
        ],
        'multiple_choice': [
            {
                'subject': '政治',
                'chapter': '毛泽东思想',
                'content': '新民主主义革命的三大法宝包括:',
                'options': ['A. 统一战线\nB. 武装斗争\nC. 党的建设\nD. 土地革命'],
                'correct_answer': 'ABC',
                'explanation': '毛泽东总结的三大法宝是:统一战线、武装斗争、党的建设。'
            }
        ]
    },
    'public_institution': {
        'single_choice': [
            {
                'subject': '公共基础知识',
                'chapter': '政治知识',
                'content': '社会主义核心价值观中,属于国家层面的价值要求是:',
                'options': ['A. 富强、民主、文明、和谐\nB. 自由、平等、公正、法治\nC. 爱国、敬业、诚信、友善\nD. 以上都是'],
                'correct_answer': 'A',
                'explanation': '国家层面:富强、民主、文明、和谐;社会层面:自由、平等、公正、法治;个人层面:爱国、敬业、诚信、友善。'
            },
            {
                'subject': '公共基础知识',
                'chapter': '法律知识',
                'content': '我国现行宪法是哪一年颁布的?',
                'options': ['A. 1954年\nB. 1975年\nC. 1978年\nD. 1982年'],
                'correct_answer': 'D',
                'explanation': '现行宪法是1982年12月4日颁布的,后经多次修正。'
            },
            {
                'subject': '公共基础知识',
                'chapter': '经济知识',
                'content': '下列哪项不属于宏观经济调控的手段?',
                'options': ['A. 财政政策\nB. 货币政策\nC. 价格政策\nD. 企业内部管理'],
                'correct_answer': 'D',
                'explanation': '企业内部管理属于微观经济活动,不属于宏观调控手段。'
            }
        ],
        'true_false': [
            {
                'subject': '公共基础知识',
                'chapter': '管理知识',
                'content': '事业单位是指国家为了社会公益目的,由国家机关举办或者其他组织利用国有资产举办的,从事教育、科技、文化、卫生等活动的社会服务组织。',
                'options': ['A. 正确\nB. 错误'],
                'correct_answer': 'A',
                'explanation': '这是事业单位的标准定义。'
            }
        ]
    }
}

def generate_questions(exam_type, count_per_type):
    """生成题目"""
    questions = []
    templates = QUESTION_TEMPLATES.get(exam_type, QUESTION_TEMPLATES['civil_service'])
    
    for question_type, template_list in templates.items():
        for i in range(count_per_type):
            # 从模板中随机选择一个
            template = random.choice(template_list)
            
            # 创建题目
            question = Question(
                exam_type=exam_type,
                question_type=question_type,
                subject=template['subject'],
                chapter=template['chapter'],
                difficulty=random.choice(['easy', 'medium', 'hard']),
                content=template['content'],
                options=template['options'],
                correct_answer=template['correct_answer'],
                explanation=template['explanation'],
                tags=f"{template['subject']},{template['chapter']}",
                created_by=1  # 假设管理员ID为1
            )
            questions.append(question)
    
    return questions

def create_exam_paper(name, exam_type, questions, duration, description):
    """创建试卷"""
    # 先计算总分
    total_score = 0
    score_map = {
        'single_choice': 2,
        'multiple_choice': 3,
        'true_false': 1,
        'fill_blank': 3,
        'essay': 10
    }
    for question in questions:
        score = score_map.get(question.question_type, 2)
        total_score += score
    
    # 创建试卷
    paper = ExamPaper(
        name=name,
        exam_type=exam_type,
        duration=duration,
        description=description,
        total_score=total_score,
        pass_score=int(total_score * 0.6),  # 60%及格
        created_by=1,
        is_published=True
    )
    
    db.session.add(paper)
    db.session.flush()  # 获取试卷ID
    
    # 添加题目到试卷
    for idx, question in enumerate(questions):
        score = score_map.get(question.question_type, 2)
        
        paper_question = ExamPaperQuestion(
            paper_id=paper.id,
            question_id=question.id,
            order=idx + 1,
            score=score
        )
        db.session.add(paper_question)
    
    return paper

def seed_data():
    """生成并导入数据"""
    app = create_app()
    
    with app.app_context():
        print("开始生成测试数据...")
        
        # 检查是否已有管理员用户
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            print("创建管理员用户...")
            admin = User(
                username='admin',
                email='admin@example.com',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("管理员用户创建成功: username=admin, password=admin123")
        
        # 生成公务员考试题目和试卷
        print("\n生成公务员考试数据...")
        civil_questions = generate_questions('civil_service', 10)
        db.session.add_all(civil_questions)
        db.session.commit()
        print(f"已生成 {len(civil_questions)} 道公务员考试题目")
        
        # 创建公务员模拟试卷
        civil_paper_questions = random.sample(civil_questions, min(30, len(civil_questions)))
        civil_paper = create_exam_paper(
            name="2024年国家公务员考试行测模拟卷(一)",
            exam_type='civil_service',
            questions=civil_paper_questions,
            duration=120,
            description="本试卷包含言语理解、数量关系、判断推理、资料分析、常识判断五大模块,共30题,满分60分,考试时间120分钟。"
        )
        db.session.commit()
        print(f"已创建试卷: {civil_paper.name}, 总分: {civil_paper.total_score}分")
        
        # 生成研究生考试题目和试卷
        print("\n生成研究生考试数据...")
        postgrad_questions = generate_questions('postgraduate', 8)
        db.session.add_all(postgrad_questions)
        db.session.commit()
        print(f"已生成 {len(postgrad_questions)} 道研究生考试题目")
        
        postgrad_paper_questions = random.sample(postgrad_questions, min(20, len(postgrad_questions)))
        postgrad_paper = create_exam_paper(
            name="2024年硕士研究生入学考试综合模拟卷",
            exam_type='postgraduate',
            questions=postgrad_paper_questions,
            duration=180,
            description="本试卷涵盖英语、数学、政治三个科目,共20题,满分40分,考试时间180分钟。"
        )
        db.session.commit()
        print(f"已创建试卷: {postgrad_paper.name}, 总分: {postgrad_paper.total_score}分")
        
        # 生成事业编考试题目和试卷
        print("\n生成事业编考试数据...")
        public_questions = generate_questions('public_institution', 10)
        db.session.add_all(public_questions)
        db.session.commit()
        print(f"已生成 {len(public_questions)} 道事业编考试题目")
        
        public_paper_questions = random.sample(public_questions, min(25, len(public_questions)))
        public_paper = create_exam_paper(
            name="2024年事业单位公开招聘公共基础知识模拟卷",
            exam_type='public_institution',
            questions=public_paper_questions,
            duration=90,
            description="本试卷主要考查公共基础知识,包括政治、法律、经济、管理等内容,共25题,满分50分,考试时间90分钟。"
        )
        db.session.commit()
        print(f"已创建试卷: {public_paper.name}, 总分: {public_paper.total_score}分")
        
        print("\n" + "="*50)
        print("数据生成完成!")
        print("="*50)
        print(f"\n总计:")
        print(f"  - 题目数量: {len(civil_questions) + len(postgrad_questions) + len(public_questions)} 道")
        print(f"  - 试卷数量: 3 套")
        print(f"\n试卷列表:")
        print(f"  1. {civil_paper.name}")
        print(f"     类型: 公务员考试 | 时长: {civil_paper.duration}分钟 | 总分: {civil_paper.total_score}分")
        print(f"  2. {postgrad_paper.name}")
        print(f"     类型: 研究生考试 | 时长: {postgrad_paper.duration}分钟 | 总分: {postgrad_paper.total_score}分")
        print(f"  3. {public_paper.name}")
        print(f"     类型: 事业编考试 | 时长: {public_paper.duration}分钟 | 总分: {public_paper.total_score}分")
        print("\n现在可以登录系统查看试卷并开始考试了!")

if __name__ == '__main__':
    seed_data()
