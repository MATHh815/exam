"""
考研院校信息API路由
"""
from flask import Blueprint, request, jsonify
from app.models.graduate_school import (
    GraduateSchool, GraduateMajor, ScoreLine, ExamSubject
)
from app import db

graduate_bp = Blueprint('graduate', __name__)


@graduate_bp.route('/schools', methods=['GET'])
def get_schools():
    """获取院校列表"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    province = request.args.get('province')
    level = request.args.get('level')  # 985/211/双一流
    school_type = request.args.get('type')
    keyword = request.args.get('keyword')
    
    query = GraduateSchool.query
    
    if province:
        query = query.filter(GraduateSchool.province == province)
    if level:
        if level == '985':
            query = query.filter(GraduateSchool.is_985 == True)
        elif level == '211':
            query = query.filter(GraduateSchool.is_211 == True)
        elif level == '双一流':
            query = query.filter(GraduateSchool.is_double_first == True)
    if school_type:
        query = query.filter(GraduateSchool.type == school_type)
    if keyword:
        query = query.filter(GraduateSchool.name.like(f'%{keyword}%'))
    
    pagination = query.order_by(GraduateSchool.is_985.desc(), 
                                GraduateSchool.is_211.desc(),
                                GraduateSchool.name).paginate(
        page=page, per_page=page_size, error_out=False
    )
    
    return jsonify({
        'success': True,
        'data': {
            'records': [s.to_dict() for s in pagination.items],
            'total': pagination.total,
            'page': page,
            'page_size': page_size,
            'pages': pagination.pages
        }
    })


@graduate_bp.route('/schools/<int:school_id>', methods=['GET'])
def get_school_detail(school_id):
    """获取院校详情"""
    school = GraduateSchool.query.get_or_404(school_id)
    data = school.to_dict()
    data['major_count'] = school.majors.count()
    return jsonify({
        'success': True,
        'data': data
    })


@graduate_bp.route('/schools/<int:school_id>/majors', methods=['GET'])
def get_school_majors(school_id):
    """获取院校的专业列表"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    category = request.args.get('category')
    degree_type = request.args.get('degree_type')
    keyword = request.args.get('keyword')
    
    query = GraduateMajor.query.filter(GraduateMajor.school_id == school_id)
    
    if category:
        query = query.filter(GraduateMajor.category == category)
    if degree_type:
        query = query.filter(GraduateMajor.degree_type == degree_type)
    if keyword:
        query = query.filter(GraduateMajor.name.like(f'%{keyword}%'))
    
    pagination = query.order_by(GraduateMajor.code).paginate(
        page=page, per_page=page_size, error_out=False
    )
    
    return jsonify({
        'success': True,
        'data': {
            'records': [m.to_dict() for m in pagination.items],
            'total': pagination.total,
            'page': page,
            'page_size': page_size
        }
    })


@graduate_bp.route('/majors/<int:major_id>', methods=['GET'])
def get_major_detail(major_id):
    """获取专业详情"""
    major = GraduateMajor.query.get_or_404(major_id)
    return jsonify({
        'success': True,
        'data': major.to_dict()
    })


@graduate_bp.route('/majors/<int:major_id>/score-lines', methods=['GET'])
def get_major_score_lines(major_id):
    """获取专业的历年分数线"""
    score_lines = ScoreLine.query.filter(
        ScoreLine.major_id == major_id
    ).order_by(ScoreLine.year.desc()).all()
    
    return jsonify({
        'success': True,
        'data': [s.to_dict() for s in score_lines]
    })


@graduate_bp.route('/majors/<int:major_id>/exam-subjects', methods=['GET'])
def get_major_exam_subjects(major_id):
    """获取专业的考试科目"""
    year = request.args.get('year', type=int)
    
    query = ExamSubject.query.filter(ExamSubject.major_id == major_id)
    if year:
        query = query.filter(ExamSubject.year == year)
    else:
        # 默认获取最新年份
        latest = ExamSubject.query.filter(
            ExamSubject.major_id == major_id
        ).order_by(ExamSubject.year.desc()).first()
        if latest:
            query = query.filter(ExamSubject.year == latest.year)
    
    subjects = query.order_by(ExamSubject.subject_type).all()
    
    return jsonify({
        'success': True,
        'data': [s.to_dict() for s in subjects]
    })


@graduate_bp.route('/score-lines/search', methods=['GET'])
def search_score_lines():
    """搜索分数线"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('page_size', 20, type=int)
    school_name = request.args.get('school_name')
    major_name = request.args.get('major_name')
    year = request.args.get('year', type=int)
    province = request.args.get('province')
    min_score = request.args.get('min_score', type=int)
    max_score = request.args.get('max_score', type=int)
    
    query = ScoreLine.query.join(GraduateMajor).join(GraduateSchool)
    
    if school_name:
        query = query.filter(GraduateSchool.name.like(f'%{school_name}%'))
    if major_name:
        query = query.filter(GraduateMajor.name.like(f'%{major_name}%'))
    if year:
        query = query.filter(ScoreLine.year == year)
    if province:
        query = query.filter(GraduateSchool.province == province)
    if min_score:
        query = query.filter(ScoreLine.total_score >= min_score)
    if max_score:
        query = query.filter(ScoreLine.total_score <= max_score)
    
    pagination = query.order_by(ScoreLine.year.desc(), 
                                ScoreLine.total_score.desc()).paginate(
        page=page, per_page=page_size, error_out=False
    )
    
    return jsonify({
        'success': True,
        'data': {
            'records': [s.to_dict() for s in pagination.items],
            'total': pagination.total,
            'page': page,
            'page_size': page_size
        }
    })


@graduate_bp.route('/provinces', methods=['GET'])
def get_provinces():
    """获取所有省份列表"""
    provinces = db.session.query(GraduateSchool.province).distinct().all()
    return jsonify({
        'success': True,
        'data': [p[0] for p in provinces if p[0]]
    })


@graduate_bp.route('/categories', methods=['GET'])
def get_categories():
    """获取所有学科门类"""
    categories = db.session.query(GraduateMajor.category).distinct().all()
    return jsonify({
        'success': True,
        'data': [c[0] for c in categories if c[0]]
    })


@graduate_bp.route('/estimate-score', methods=['POST'])
def estimate_score():
    """分数估算 - 根据用户成绩估算可报考的学校"""
    data = request.get_json()
    total_score = data.get('total_score')
    politics_score = data.get('politics_score')
    english_score = data.get('english_score')
    math_score = data.get('math_score')
    professional_score = data.get('professional_score')
    category = data.get('category')  # 学科门类
    province = data.get('province')  # 目标省份
    
    if not total_score:
        return jsonify({'success': False, 'message': '请输入总分'}), 400
    
    # 查询符合条件的分数线（最近3年）
    query = ScoreLine.query.join(GraduateMajor).join(GraduateSchool)
    query = query.filter(ScoreLine.year >= 2022)
    query = query.filter(ScoreLine.total_score <= total_score)
    
    if politics_score:
        query = query.filter(ScoreLine.politics_score <= politics_score)
    if english_score:
        query = query.filter(ScoreLine.english_score <= english_score)
    if category:
        query = query.filter(GraduateMajor.category == category)
    if province:
        query = query.filter(GraduateSchool.province == province)
    
    # 按分数线从高到低排序，取前50个
    results = query.order_by(ScoreLine.total_score.desc()).limit(50).all()
    
    # 分类：冲刺/稳妥/保底
    score_diff = 20  # 分数差阈值
    categorized = {
        'reach': [],    # 冲刺（分数线接近用户分数）
        'match': [],    # 稳妥（分数线低于用户分数10-30分）
        'safe': []      # 保底（分数线低于用户分数30分以上）
    }
    
    for sl in results:
        diff = total_score - sl.total_score
        item = sl.to_dict()
        if diff <= 10:
            categorized['reach'].append(item)
        elif diff <= 30:
            categorized['match'].append(item)
        else:
            categorized['safe'].append(item)
    
    return jsonify({
        'success': True,
        'data': {
            'user_score': total_score,
            'reach': categorized['reach'][:10],
            'match': categorized['match'][:15],
            'safe': categorized['safe'][:10]
        }
    })


# ============ 院校管理接口 ============

@graduate_bp.route('/schools', methods=['POST'])
def create_school():
    """添加院校"""
    data = request.get_json()
    
    # 验证必填字段
    if not data.get('name'):
        return jsonify({'success': False, 'message': '院校名称不能为空'}), 400
    if not data.get('code'):
        return jsonify({'success': False, 'message': '院校代码不能为空'}), 400
    
    # 检查是否已存在
    existing = GraduateSchool.query.filter_by(code=data['code']).first()
    if existing:
        return jsonify({'success': False, 'message': '该院校代码已存在'}), 400
    
    school = GraduateSchool(
        name=data['name'],
        code=data['code'],
        province=data.get('province'),
        city=data.get('city'),
        type=data.get('type'),
        level=data.get('level'),
        is_985=data.get('is_985', False),
        is_211=data.get('is_211', False),
        is_double_first=data.get('is_double_first', False),
        website=data.get('website'),
        phone=data.get('phone'),
        address=data.get('address'),
        description=data.get('description')
    )
    
    db.session.add(school)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '添加成功',
        'data': school.to_dict()
    })


@graduate_bp.route('/schools/<int:school_id>', methods=['PUT'])
def update_school(school_id):
    """更新院校信息"""
    school = GraduateSchool.query.get_or_404(school_id)
    data = request.get_json()
    
    # 更新字段
    if 'name' in data:
        school.name = data['name']
    if 'code' in data:
        school.code = data['code']
    if 'province' in data:
        school.province = data['province']
    if 'city' in data:
        school.city = data['city']
    if 'type' in data:
        school.type = data['type']
    if 'level' in data:
        school.level = data['level']
    if 'is_985' in data:
        school.is_985 = data['is_985']
    if 'is_211' in data:
        school.is_211 = data['is_211']
    if 'is_double_first' in data:
        school.is_double_first = data['is_double_first']
    if 'website' in data:
        school.website = data['website']
    if 'phone' in data:
        school.phone = data['phone']
    if 'address' in data:
        school.address = data['address']
    if 'description' in data:
        school.description = data['description']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '更新成功',
        'data': school.to_dict()
    })


@graduate_bp.route('/schools/<int:school_id>', methods=['DELETE'])
def delete_school(school_id):
    """删除院校"""
    school = GraduateSchool.query.get_or_404(school_id)
    
    # 删除关联的专业、分数线、考试科目
    for major in school.majors:
        ScoreLine.query.filter_by(major_id=major.id).delete()
        ExamSubject.query.filter_by(major_id=major.id).delete()
    GraduateMajor.query.filter_by(school_id=school_id).delete()
    
    db.session.delete(school)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '删除成功'
    })


# ============ 专业管理接口 ============

@graduate_bp.route('/majors', methods=['POST'])
def create_major():
    """添加专业"""
    data = request.get_json()
    
    if not data.get('school_id'):
        return jsonify({'success': False, 'message': '请选择所属院校'}), 400
    if not data.get('name'):
        return jsonify({'success': False, 'message': '专业名称不能为空'}), 400
    if not data.get('code'):
        return jsonify({'success': False, 'message': '专业代码不能为空'}), 400
    
    major = GraduateMajor(
        school_id=data['school_id'],
        name=data['name'],
        code=data['code'],
        category=data.get('category'),
        degree_type=data.get('degree_type', '学术型'),
        duration=data.get('duration', 3),
        department=data.get('department'),
        research_directions=data.get('research_directions'),
        description=data.get('description')
    )
    
    db.session.add(major)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '添加成功',
        'data': major.to_dict()
    })


@graduate_bp.route('/majors/<int:major_id>', methods=['PUT'])
def update_major(major_id):
    """更新专业信息"""
    major = GraduateMajor.query.get_or_404(major_id)
    data = request.get_json()
    
    if 'name' in data:
        major.name = data['name']
    if 'code' in data:
        major.code = data['code']
    if 'category' in data:
        major.category = data['category']
    if 'degree_type' in data:
        major.degree_type = data['degree_type']
    if 'duration' in data:
        major.duration = data['duration']
    if 'department' in data:
        major.department = data['department']
    if 'research_directions' in data:
        major.research_directions = data['research_directions']
    if 'description' in data:
        major.description = data['description']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '更新成功',
        'data': major.to_dict()
    })


@graduate_bp.route('/majors/<int:major_id>', methods=['DELETE'])
def delete_major(major_id):
    """删除专业"""
    major = GraduateMajor.query.get_or_404(major_id)
    
    # 删除关联的分数线和考试科目
    ScoreLine.query.filter_by(major_id=major_id).delete()
    ExamSubject.query.filter_by(major_id=major_id).delete()
    
    db.session.delete(major)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '删除成功'
    })


# ============ 分数线管理接口 ============

@graduate_bp.route('/score-lines', methods=['POST'])
def create_score_line():
    """添加分数线"""
    data = request.get_json()
    
    if not data.get('major_id'):
        return jsonify({'success': False, 'message': '请选择专业'}), 400
    if not data.get('year'):
        return jsonify({'success': False, 'message': '请选择年份'}), 400
    if not data.get('total_score'):
        return jsonify({'success': False, 'message': '请输入总分线'}), 400
    
    score_line = ScoreLine(
        major_id=data['major_id'],
        year=data['year'],
        total_score=data['total_score'],
        politics_score=data.get('politics_score'),
        english_score=data.get('english_score'),
        math_score=data.get('math_score'),
        professional_score=data.get('professional_score'),
        enrollment_num=data.get('enrollment_num'),
        applicant_num=data.get('applicant_num'),
        admission_ratio=data.get('admission_ratio'),
        remark=data.get('remark')
    )
    
    db.session.add(score_line)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '添加成功',
        'data': score_line.to_dict()
    })


@graduate_bp.route('/score-lines/<int:score_line_id>', methods=['PUT'])
def update_score_line(score_line_id):
    """更新分数线"""
    score_line = ScoreLine.query.get_or_404(score_line_id)
    data = request.get_json()
    
    if 'year' in data:
        score_line.year = data['year']
    if 'total_score' in data:
        score_line.total_score = data['total_score']
    if 'politics_score' in data:
        score_line.politics_score = data['politics_score']
    if 'english_score' in data:
        score_line.english_score = data['english_score']
    if 'math_score' in data:
        score_line.math_score = data['math_score']
    if 'professional_score' in data:
        score_line.professional_score = data['professional_score']
    if 'enrollment_num' in data:
        score_line.enrollment_num = data['enrollment_num']
    if 'applicant_num' in data:
        score_line.applicant_num = data['applicant_num']
    if 'admission_ratio' in data:
        score_line.admission_ratio = data['admission_ratio']
    if 'remark' in data:
        score_line.remark = data['remark']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '更新成功',
        'data': score_line.to_dict()
    })


@graduate_bp.route('/score-lines/<int:score_line_id>', methods=['DELETE'])
def delete_score_line(score_line_id):
    """删除分数线"""
    score_line = ScoreLine.query.get_or_404(score_line_id)
    db.session.delete(score_line)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '删除成功'
    })


# ============ 考试科目管理接口 ============

@graduate_bp.route('/exam-subjects', methods=['POST'])
def create_exam_subject():
    """添加考试科目"""
    data = request.get_json()
    
    if not data.get('major_id'):
        return jsonify({'success': False, 'message': '请选择专业'}), 400
    if not data.get('subject_name'):
        return jsonify({'success': False, 'message': '请输入科目名称'}), 400
    
    subject = ExamSubject(
        major_id=data['major_id'],
        year=data.get('year', 2024),
        subject_code=data.get('subject_code'),
        subject_name=data['subject_name'],
        subject_type=data.get('subject_type', '专业课'),
        full_score=data.get('full_score', 150),
        reference_books=data.get('reference_books'),
        remark=data.get('remark')
    )
    
    db.session.add(subject)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '添加成功',
        'data': subject.to_dict()
    })


@graduate_bp.route('/exam-subjects/<int:subject_id>', methods=['PUT'])
def update_exam_subject(subject_id):
    """更新考试科目"""
    subject = ExamSubject.query.get_or_404(subject_id)
    data = request.get_json()
    
    if 'year' in data:
        subject.year = data['year']
    if 'subject_code' in data:
        subject.subject_code = data['subject_code']
    if 'subject_name' in data:
        subject.subject_name = data['subject_name']
    if 'subject_type' in data:
        subject.subject_type = data['subject_type']
    if 'full_score' in data:
        subject.full_score = data['full_score']
    if 'reference_books' in data:
        subject.reference_books = data['reference_books']
    if 'remark' in data:
        subject.remark = data['remark']
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '更新成功',
        'data': subject.to_dict()
    })


@graduate_bp.route('/exam-subjects/<int:subject_id>', methods=['DELETE'])
def delete_exam_subject(subject_id):
    """删除考试科目"""
    subject = ExamSubject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': '删除成功'
    })
