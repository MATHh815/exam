"""
考研院校信息模型
包含全国具有硕士研究生点的学校信息、专业、分数线、考试科目等
"""
from datetime import datetime
from app import db


class GraduateSchool(db.Model):
    """研究生院校表"""
    __tablename__ = 'graduate_schools'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, comment='学校名称')
    code = db.Column(db.String(20), unique=True, comment='学校代码')
    province = db.Column(db.String(20), comment='所在省份')
    city = db.Column(db.String(50), comment='所在城市')
    level = db.Column(db.String(50), comment='学校层次：985/211/双一流/普通')
    type = db.Column(db.String(50), comment='学校类型：综合/理工/师范/财经等')
    is_985 = db.Column(db.Boolean, default=False, comment='是否985')
    is_211 = db.Column(db.Boolean, default=False, comment='是否211')
    is_double_first = db.Column(db.Boolean, default=False, comment='是否双一流')
    website = db.Column(db.String(200), comment='研究生院官网')
    phone = db.Column(db.String(50), comment='招生电话')
    address = db.Column(db.String(200), comment='学校地址')
    description = db.Column(db.Text, comment='学校简介')
    logo_url = db.Column(db.String(300), comment='学校logo')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    majors = db.relationship('GraduateMajor', backref='school', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'province': self.province,
            'city': self.city,
            'level': self.level,
            'type': self.type,
            'is_985': self.is_985,
            'is_211': self.is_211,
            'is_double_first': self.is_double_first,
            'website': self.website,
            'phone': self.phone,
            'address': self.address,
            'description': self.description,
            'logo_url': self.logo_url
        }


class GraduateMajor(db.Model):
    """研究生专业表"""
    __tablename__ = 'graduate_majors'
    
    id = db.Column(db.Integer, primary_key=True)
    school_id = db.Column(db.Integer, db.ForeignKey('graduate_schools.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False, comment='专业名称')
    code = db.Column(db.String(20), comment='专业代码')
    category = db.Column(db.String(50), comment='学科门类：哲学/经济学/法学等')
    degree_type = db.Column(db.String(20), comment='学位类型：学术型/专业型')
    duration = db.Column(db.Integer, default=3, comment='学制（年）')
    department = db.Column(db.String(100), comment='所属学院')
    research_directions = db.Column(db.Text, comment='研究方向，JSON格式')
    description = db.Column(db.Text, comment='专业简介')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联
    score_lines = db.relationship('ScoreLine', backref='major', lazy='dynamic')
    exam_subjects = db.relationship('ExamSubject', backref='major', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'school_id': self.school_id,
            'school_name': self.school.name if self.school else None,
            'name': self.name,
            'code': self.code,
            'category': self.category,
            'degree_type': self.degree_type,
            'duration': self.duration,
            'department': self.department,
            'research_directions': self.research_directions,
            'description': self.description
        }


class ScoreLine(db.Model):
    """分数线表"""
    __tablename__ = 'score_lines'
    
    id = db.Column(db.Integer, primary_key=True)
    major_id = db.Column(db.Integer, db.ForeignKey('graduate_majors.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False, comment='年份')
    total_score = db.Column(db.Integer, comment='总分分数线')
    politics_score = db.Column(db.Integer, comment='政治分数线')
    english_score = db.Column(db.Integer, comment='英语分数线')
    math_score = db.Column(db.Integer, comment='数学分数线')
    professional_score = db.Column(db.Integer, comment='专业课分数线')
    enrollment_num = db.Column(db.Integer, comment='录取人数')
    applicant_num = db.Column(db.Integer, comment='报考人数')
    admission_ratio = db.Column(db.Float, comment='录取比例')
    remark = db.Column(db.String(500), comment='备注')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'major_id': self.major_id,
            'major_name': self.major.name if self.major else None,
            'school_name': self.major.school.name if self.major and self.major.school else None,
            'year': self.year,
            'total_score': self.total_score,
            'politics_score': self.politics_score,
            'english_score': self.english_score,
            'math_score': self.math_score,
            'professional_score': self.professional_score,
            'enrollment_num': self.enrollment_num,
            'applicant_num': self.applicant_num,
            'admission_ratio': self.admission_ratio,
            'remark': self.remark
        }


class ExamSubject(db.Model):
    """考试科目表"""
    __tablename__ = 'exam_subjects'
    
    id = db.Column(db.Integer, primary_key=True)
    major_id = db.Column(db.Integer, db.ForeignKey('graduate_majors.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False, comment='年份')
    subject_code = db.Column(db.String(20), comment='科目代码')
    subject_name = db.Column(db.String(100), nullable=False, comment='科目名称')
    subject_type = db.Column(db.String(20), comment='科目类型：政治/英语/数学/专业课')
    full_score = db.Column(db.Integer, default=150, comment='满分')
    reference_books = db.Column(db.Text, comment='参考书目，JSON格式')
    exam_outline = db.Column(db.Text, comment='考试大纲')
    remark = db.Column(db.String(500), comment='备注')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'major_id': self.major_id,
            'major_name': self.major.name if self.major else None,
            'school_name': self.major.school.name if self.major and self.major.school else None,
            'year': self.year,
            'subject_code': self.subject_code,
            'subject_name': self.subject_name,
            'subject_type': self.subject_type,
            'full_score': self.full_score,
            'reference_books': self.reference_books,
            'exam_outline': self.exam_outline,
            'remark': self.remark
        }
