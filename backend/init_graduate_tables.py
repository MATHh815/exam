"""
初始化考研院校数据库表并导入数据
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.graduate_school import (
    GraduateSchool, GraduateMajor, ScoreLine, ExamSubject
)
import json

app = create_app()

# 示例院校数据
SCHOOLS_DATA = [
    {
        'name': '北京大学', 'code': '10001', 'province': '北京', 'city': '北京',
        'level': '985/211/双一流', 'type': '综合', 'is_985': True, 'is_211': True, 'is_double_first': True,
        'website': 'https://grs.pku.edu.cn', 'phone': '010-62751354',
        'description': '北京大学创办于1898年，是中国第一所国立综合性大学。'
    },
    {
        'name': '清华大学', 'code': '10003', 'province': '北京', 'city': '北京',
        'level': '985/211/双一流', 'type': '理工', 'is_985': True, 'is_211': True, 'is_double_first': True,
        'website': 'https://yz.tsinghua.edu.cn', 'phone': '010-62782192',
        'description': '清华大学是中国著名高等学府，坐落于北京西北郊风景秀丽的清华园。'
    },
    {
        'name': '复旦大学', 'code': '10246', 'province': '上海', 'city': '上海',
        'level': '985/211/双一流', 'type': '综合', 'is_985': True, 'is_211': True, 'is_double_first': True,
        'website': 'https://gsao.fudan.edu.cn', 'phone': '021-65642673',
        'description': '复旦大学是中国人自主创办的第一所高等院校。'
    },
    {
        'name': '上海交通大学', 'code': '10248', 'province': '上海', 'city': '上海',
        'level': '985/211/双一流', 'type': '理工', 'is_985': True, 'is_211': True, 'is_double_first': True,
        'website': 'https://yzb.sjtu.edu.cn', 'phone': '021-62821069',
        'description': '上海交通大学是我国历史最悠久、享誉海内外的著名高等学府之一。'
    },
    {
        'name': '浙江大学', 'code': '10335', 'province': '浙江', 'city': '杭州',
        'level': '985/211/双一流', 'type': '综合', 'is_985': True, 'is_211': True, 'is_double_first': True,
        'website': 'https://grs.zju.edu.cn', 'phone': '0571-87951349',
        'description': '浙江大学是一所历史悠久、声誉卓著的高等学府。'
    },
    {
        'name': '南京大学', 'code': '10284', 'province': '江苏', 'city': '南京',
        'level': '985/211/双一流', 'type': '综合', 'is_985': True, 'is_211': True, 'is_double_first': True,
        'website': 'https://grawww.nju.edu.cn', 'phone': '025-89683251',
        'description': '南京大学是一所历史悠久、声誉卓著的百年名校。'
    },
    {
        'name': '中国人民大学', 'code': '10002', 'province': '北京', 'city': '北京',
        'level': '985/211/双一流', 'type': '综合', 'is_985': True, 'is_211': True, 'is_double_first': True,
        'website': 'https://pgs.ruc.edu.cn', 'phone': '010-62515340',
        'description': '中国人民大学是中国共产党创办的第一所新型正规大学。'
    },
    {
        'name': '武汉大学', 'code': '10486', 'province': '湖北', 'city': '武汉',
        'level': '985/211/双一流', 'type': '综合', 'is_985': True, 'is_211': True, 'is_double_first': True,
        'website': 'https://gs.whu.edu.cn', 'phone': '027-68754125',
        'description': '武汉大学是国家教育部直属重点综合性大学。'
    },
    {
        'name': '华中科技大学', 'code': '10487', 'province': '湖北', 'city': '武汉',
        'level': '985/211/双一流', 'type': '理工', 'is_985': True, 'is_211': True, 'is_double_first': True,
        'website': 'http://gszs.hust.edu.cn', 'phone': '027-87542552',
        'description': '华中科技大学是国家教育部直属重点综合性大学。'
    },
    {
        'name': '中山大学', 'code': '10558', 'province': '广东', 'city': '广州',
        'level': '985/211/双一流', 'type': '综合', 'is_985': True, 'is_211': True, 'is_double_first': True,
        'website': 'https://graduate.sysu.edu.cn', 'phone': '020-84111686',
        'description': '中山大学由孙中山先生创办，有着一百多年办学传统。'
    },
    {
        'name': '四川大学', 'code': '10610', 'province': '四川', 'city': '成都',
        'level': '985/211/双一流', 'type': '综合', 'is_985': True, 'is_211': True, 'is_double_first': True,
        'website': 'https://gs.scu.edu.cn', 'phone': '028-85403337',
        'description': '四川大学是教育部直属全国重点大学。'
    },
    {
        'name': '西安交通大学', 'code': '10698', 'province': '陕西', 'city': '西安',
        'level': '985/211/双一流', 'type': '理工', 'is_985': True, 'is_211': True, 'is_double_first': True,
        'website': 'http://gs.xjtu.edu.cn', 'phone': '029-82668329',
        'description': '西安交通大学是我国最早兴办、享誉海内外的著名高等学府。'
    },
    # 211院校
    {
        'name': '北京邮电大学', 'code': '10013', 'province': '北京', 'city': '北京',
        'level': '211/双一流', 'type': '理工', 'is_985': False, 'is_211': True, 'is_double_first': True,
        'website': 'https://yzb.bupt.edu.cn', 'phone': '010-62282045',
        'description': '北京邮电大学是教育部直属、工业和信息化部共建的全国重点大学。'
    },
    {
        'name': '对外经济贸易大学', 'code': '10036', 'province': '北京', 'city': '北京',
        'level': '211/双一流', 'type': '财经', 'is_985': False, 'is_211': True, 'is_double_first': True,
        'website': 'http://yjsy.uibe.edu.cn', 'phone': '010-64492151',
        'description': '对外经济贸易大学是教育部直属的全国重点大学。'
    },
    {
        'name': '中央财经大学', 'code': '10034', 'province': '北京', 'city': '北京',
        'level': '211/双一流', 'type': '财经', 'is_985': False, 'is_211': True, 'is_double_first': True,
        'website': 'http://gs.cufe.edu.cn', 'phone': '010-62288344',
        'description': '中央财经大学是教育部直属的国家"211工程"重点建设高校。'
    },
    # 普通院校
    {
        'name': '首都经济贸易大学', 'code': '10038', 'province': '北京', 'city': '北京',
        'level': '普通', 'type': '财经', 'is_985': False, 'is_211': False, 'is_double_first': False,
        'website': 'https://yjs.cueb.edu.cn', 'phone': '010-83952090',
        'description': '首都经济贸易大学是北京市属重点大学。'
    },
    {
        'name': '上海对外经贸大学', 'code': '10273', 'province': '上海', 'city': '上海',
        'level': '普通', 'type': '财经', 'is_985': False, 'is_211': False, 'is_double_first': False,
        'website': 'https://gs.suibe.edu.cn', 'phone': '021-67703622',
        'description': '上海对外经贸大学是一所以经济学、管理学为主的多科性财经外语类大学。'
    },
]

# 专业数据
MAJORS_DATA = {
    '北京大学': [
        {'name': '计算机科学与技术', 'code': '081200', 'category': '工学', 'degree_type': '学术型', 'department': '信息科学技术学院'},
        {'name': '软件工程', 'code': '083500', 'category': '工学', 'degree_type': '学术型', 'department': '软件与微电子学院'},
        {'name': '金融学', 'code': '020204', 'category': '经济学', 'degree_type': '学术型', 'department': '经济学院'},
        {'name': '法律（非法学）', 'code': '035101', 'category': '法学', 'degree_type': '专业型', 'department': '法学院'},
        {'name': '工商管理', 'code': '125100', 'category': '管理学', 'degree_type': '专业型', 'department': '光华管理学院'},
    ],
    '清华大学': [
        {'name': '计算机科学与技术', 'code': '081200', 'category': '工学', 'degree_type': '学术型', 'department': '计算机科学与技术系'},
        {'name': '电子信息', 'code': '085400', 'category': '工学', 'degree_type': '专业型', 'department': '电子工程系'},
        {'name': '金融', 'code': '025100', 'category': '经济学', 'degree_type': '专业型', 'department': '五道口金融学院'},
        {'name': '工商管理', 'code': '125100', 'category': '管理学', 'degree_type': '专业型', 'department': '经济管理学院'},
    ],
    '复旦大学': [
        {'name': '计算机科学与技术', 'code': '081200', 'category': '工学', 'degree_type': '学术型', 'department': '计算机科学技术学院'},
        {'name': '金融学', 'code': '020204', 'category': '经济学', 'degree_type': '学术型', 'department': '经济学院'},
        {'name': '新闻与传播', 'code': '055200', 'category': '文学', 'degree_type': '专业型', 'department': '新闻学院'},
        {'name': '法律（非法学）', 'code': '035101', 'category': '法学', 'degree_type': '专业型', 'department': '法学院'},
    ],
}

# 分数线数据
SCORE_LINES_DATA = {
    ('北京大学', '计算机科学与技术'): [
        {'year': 2024, 'total_score': 360, 'politics_score': 55, 'english_score': 55, 'math_score': 90, 'professional_score': 90, 'enrollment_num': 30},
        {'year': 2023, 'total_score': 355, 'politics_score': 55, 'english_score': 55, 'math_score': 90, 'professional_score': 90, 'enrollment_num': 28},
        {'year': 2022, 'total_score': 350, 'politics_score': 50, 'english_score': 50, 'math_score': 85, 'professional_score': 85, 'enrollment_num': 25},
    ],
    ('北京大学', '金融学'): [
        {'year': 2024, 'total_score': 380, 'politics_score': 60, 'english_score': 60, 'math_score': 100, 'professional_score': 100, 'enrollment_num': 20},
        {'year': 2023, 'total_score': 375, 'politics_score': 55, 'english_score': 55, 'math_score': 95, 'professional_score': 95, 'enrollment_num': 18},
    ],
    ('清华大学', '计算机科学与技术'): [
        {'year': 2024, 'total_score': 370, 'politics_score': 55, 'english_score': 55, 'math_score': 95, 'professional_score': 95, 'enrollment_num': 25},
        {'year': 2023, 'total_score': 365, 'politics_score': 55, 'english_score': 55, 'math_score': 90, 'professional_score': 90, 'enrollment_num': 22},
    ],
    ('复旦大学', '计算机科学与技术'): [
        {'year': 2024, 'total_score': 350, 'politics_score': 55, 'english_score': 55, 'math_score': 85, 'professional_score': 85, 'enrollment_num': 35},
        {'year': 2023, 'total_score': 345, 'politics_score': 50, 'english_score': 50, 'math_score': 80, 'professional_score': 80, 'enrollment_num': 32},
    ],
}

# 考试科目数据
EXAM_SUBJECTS_DATA = {
    ('北京大学', '计算机科学与技术'): [
        {'year': 2024, 'subject_code': '101', 'subject_name': '思想政治理论', 'subject_type': '政治', 'full_score': 100},
        {'year': 2024, 'subject_code': '201', 'subject_name': '英语一', 'subject_type': '英语', 'full_score': 100},
        {'year': 2024, 'subject_code': '301', 'subject_name': '数学一', 'subject_type': '数学', 'full_score': 150},
        {'year': 2024, 'subject_code': '408', 'subject_name': '计算机学科专业基础', 'subject_type': '专业课', 'full_score': 150,
         'reference_books': json.dumps(['《数据结构》严蔚敏', '《计算机组成原理》唐朔飞', '《操作系统》汤小丹', '《计算机网络》谢希仁'], ensure_ascii=False)},
    ],
    ('清华大学', '计算机科学与技术'): [
        {'year': 2024, 'subject_code': '101', 'subject_name': '思想政治理论', 'subject_type': '政治', 'full_score': 100},
        {'year': 2024, 'subject_code': '201', 'subject_name': '英语一', 'subject_type': '英语', 'full_score': 100},
        {'year': 2024, 'subject_code': '301', 'subject_name': '数学一', 'subject_type': '数学', 'full_score': 150},
        {'year': 2024, 'subject_code': '912', 'subject_name': '计算机专业基础综合', 'subject_type': '专业课', 'full_score': 150,
         'reference_books': json.dumps(['《数据结构》邓俊辉', '《计算机组成原理》唐朔飞', '《操作系统概念》'], ensure_ascii=False)},
    ],
}


def init_tables_and_data():
    with app.app_context():
        # 创建表
        print("创建数据库表...")
        db.create_all()
        print("数据库表创建成功！")
        
        # 检查是否已有数据
        existing_count = GraduateSchool.query.count()
        if existing_count > 0:
            print(f"已存在 {existing_count} 条院校数据，跳过导入")
            return
        
        print("\n开始导入院校数据...")
        
        # 导入院校
        school_map = {}
        for school_data in SCHOOLS_DATA:
            school = GraduateSchool(**school_data)
            db.session.add(school)
            db.session.flush()
            school_map[school.name] = school
            print(f"  导入院校: {school.name}")
        
        db.session.commit()
        
        # 导入专业
        print("\n开始导入专业数据...")
        major_map = {}
        for school_name, majors in MAJORS_DATA.items():
            if school_name in school_map:
                school = school_map[school_name]
                for major_data in majors:
                    major = GraduateMajor(school_id=school.id, **major_data)
                    db.session.add(major)
                    db.session.flush()
                    major_map[(school_name, major.name)] = major
                    print(f"  导入专业: {school_name} - {major.name}")
        
        db.session.commit()
        
        # 导入分数线
        print("\n开始导入分数线数据...")
        for (school_name, major_name), score_lines in SCORE_LINES_DATA.items():
            key = (school_name, major_name)
            if key in major_map:
                major = major_map[key]
                for sl_data in score_lines:
                    sl = ScoreLine(major_id=major.id, **sl_data)
                    db.session.add(sl)
                    print(f"  导入分数线: {school_name} - {major_name} ({sl_data['year']})")
        
        db.session.commit()
        
        # 导入考试科目
        print("\n开始导入考试科目数据...")
        for (school_name, major_name), subjects in EXAM_SUBJECTS_DATA.items():
            key = (school_name, major_name)
            if key in major_map:
                major = major_map[key]
                for subj_data in subjects:
                    subj = ExamSubject(major_id=major.id, **subj_data)
                    db.session.add(subj)
                    print(f"  导入科目: {school_name} - {major_name} - {subj_data['subject_name']}")
        
        db.session.commit()
        
        print("\n数据导入完成！")
        print(f"  院校数量: {GraduateSchool.query.count()}")
        print(f"  专业数量: {GraduateMajor.query.count()}")
        print(f"  分数线数量: {ScoreLine.query.count()}")
        print(f"  考试科目数量: {ExamSubject.query.count()}")


if __name__ == '__main__':
    init_tables_and_data()
