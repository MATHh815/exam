"""考试相关模型"""
from datetime import datetime
from app import db


class ExamPaper(db.Model):
    """试卷模型
    
    存储试卷的基本信息和配置
    """
    __tablename__ = 'exam_papers'
    
    # 主键
    id = db.Column(db.Integer, primary_key=True)
    
    # 试卷信息
    name = db.Column(db.String(200), nullable=False)
    exam_type = db.Column(db.String(50), nullable=False, index=True)
    description = db.Column(db.Text)
    
    # 考试配置
    duration = db.Column(db.Integer, nullable=False)  # 考试时长（分钟）
    total_score = db.Column(db.Integer, nullable=False)  # 总分
    pass_score = db.Column(db.Integer)  # 及格分
    
    # 状态和版本
    is_published = db.Column(db.Boolean, default=False, nullable=False, index=True)
    version = db.Column(db.Integer, default=1, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False, index=True)
    
    # 创建信息
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    creator = db.relationship('User', backref='created_papers', foreign_keys=[created_by])
    paper_questions = db.relationship('ExamPaperQuestion', backref='paper', lazy='dynamic', 
                                     cascade='all, delete-orphan', order_by='ExamPaperQuestion.order')
    
    def __repr__(self):
        return f'<ExamPaper {self.id}: {self.name}>'
    
    def soft_delete(self):
        """软删除试卷"""
        self.is_deleted = True
        self.updated_at = datetime.utcnow()
    
    def restore(self):
        """恢复已删除的试卷"""
        self.is_deleted = False
        self.updated_at = datetime.utcnow()
    
    def publish(self):
        """发布试卷"""
        self.is_published = True
        self.updated_at = datetime.utcnow()
    
    def unpublish(self):
        """取消发布试卷"""
        self.is_published = False
        self.updated_at = datetime.utcnow()
    
    def create_new_version(self):
        """创建新版本
        
        当编辑已发布的试卷时，创建新版本而不是修改原试卷
        
        Returns:
            ExamPaper: 新版本的试卷
        """
        new_paper = ExamPaper(
            name=self.name,
            exam_type=self.exam_type,
            description=self.description,
            duration=self.duration,
            total_score=self.total_score,
            pass_score=self.pass_score,
            is_published=False,
            version=self.version + 1,
            created_by=self.created_by
        )
        
        # 复制题目关联
        for pq in self.paper_questions:
            new_pq = ExamPaperQuestion(
                question_id=pq.question_id,
                order=pq.order,
                score=pq.score
            )
            new_paper.paper_questions.append(new_pq)
        
        return new_paper
    
    def get_questions(self):
        """获取试卷的所有题目（按顺序）
        
        Returns:
            list: 题目列表，每个元素包含题目和分值
        """
        from app.models.question import Question
        
        questions = []
        for pq in self.paper_questions.order_by(ExamPaperQuestion.order):
            question = Question.query.get(pq.question_id)
            if question and not question.is_deleted:
                questions.append({
                    'question': question,
                    'order': pq.order,
                    'score': pq.score
                })
        
        return questions
    
    def calculate_actual_total_score(self):
        """计算实际总分（所有题目分值之和）
        
        Returns:
            int: 实际总分
        """
        return sum(pq.score for pq in self.paper_questions)
    
    def to_dict(self, include_questions=False):
        """转换为字典
        
        Args:
            include_questions: 是否包含题目列表
            
        Returns:
            dict: 试卷信息字典
        """
        data = {
            'id': self.id,
            'name': self.name,
            'exam_type': self.exam_type,
            'description': self.description,
            'duration': self.duration,
            'total_score': self.total_score,
            'pass_score': self.pass_score,
            'is_published': self.is_published,
            'version': self.version,
            'question_count': self.paper_questions.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_questions:
            data['questions'] = [
                {
                    'question_id': pq.question_id,
                    'order': pq.order,
                    'score': pq.score
                }
                for pq in self.paper_questions.order_by(ExamPaperQuestion.order)
            ]
        
        return data


class ExamPaperQuestion(db.Model):
    """试卷题目关联模型
    
    存储试卷和题目的多对多关系，以及题目在试卷中的顺序和分值
    """
    __tablename__ = 'exam_paper_questions'
    
    # 主键
    id = db.Column(db.Integer, primary_key=True)
    
    # 外键
    paper_id = db.Column(db.Integer, db.ForeignKey('exam_papers.id'), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False, index=True)
    
    # 题目配置
    order = db.Column(db.Integer, nullable=False)  # 题目顺序
    score = db.Column(db.Integer, nullable=False)  # 该题分值
    
    # 关系
    question = db.relationship('Question', backref='paper_questions')
    
    # 唯一约束：同一试卷中不能有重复的题目
    __table_args__ = (
        db.UniqueConstraint('paper_id', 'question_id', name='uq_paper_question'),
        db.UniqueConstraint('paper_id', 'order', name='uq_paper_order'),
    )
    
    def __repr__(self):
        return f'<ExamPaperQuestion paper={self.paper_id} question={self.question_id} order={self.order}>'
    
    def to_dict(self):
        """转换为字典
        
        Returns:
            dict: 关联信息字典
        """
        return {
            'id': self.id,
            'paper_id': self.paper_id,
            'question_id': self.question_id,
            'order': self.order,
            'score': self.score
        }


class ExamSession(db.Model):
    """考试会话模型
    
    存储用户的考试会话信息
    """
    __tablename__ = 'exam_sessions'
    
    # 主键
    id = db.Column(db.Integer, primary_key=True)
    
    # 外键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    paper_id = db.Column(db.Integer, db.ForeignKey('exam_papers.id'), nullable=False, index=True)
    
    # 时间信息
    start_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    end_time = db.Column(db.DateTime)  # 计划结束时间
    submit_time = db.Column(db.DateTime)  # 实际提交时间
    last_active_time = db.Column(db.DateTime, default=datetime.utcnow)  # 最后活动时间
    
    # 状态
    status = db.Column(db.String(20), default='in_progress', nullable=False, index=True)  # in_progress, submitted, timeout, paused
    
    # 答案（JSON格式：{question_id: answer}）
    answers = db.Column(db.JSON, default=dict)
    
    # 进度信息
    current_question_index = db.Column(db.Integer, default=0)  # 当前做到第几题（索引）
    
    # 关系
    user = db.relationship('User', backref='exam_sessions')
    paper = db.relationship('ExamPaper', backref='exam_sessions')
    
    def __repr__(self):
        return f'<ExamSession {self.id}: user={self.user_id} paper={self.paper_id} status={self.status}>'
    
    def submit(self):
        """提交考试"""
        self.status = 'submitted'
        self.submit_time = datetime.utcnow()
    
    def timeout(self):
        """考试超时"""
        self.status = 'timeout'
        self.submit_time = datetime.utcnow()
    
    def save_answer(self, question_id, answer):
        """保存单题答案
        
        Args:
            question_id: 题目ID
            answer: 用户答案
        """
        if self.answers is None:
            self.answers = {}
        
        # 创建新字典以触发SQLAlchemy的变更检测
        new_answers = dict(self.answers)
        new_answers[str(question_id)] = answer
        self.answers = new_answers
        
        # 更新最后活动时间
        self.last_active_time = datetime.utcnow()
        
        # 标记为已修改
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(self, 'answers')
    
    def update_progress(self, question_index):
        """更新当前题目进度
        
        Args:
            question_index: 当前题目索引
        """
        self.current_question_index = question_index
        self.last_active_time = datetime.utcnow()
    
    def pause(self):
        """暂停考试（用于断点续考）"""
        self.status = 'paused'
        self.last_active_time = datetime.utcnow()
    
    def get_answer(self, question_id):
        """获取单题答案
        
        Args:
            question_id: 题目ID
            
        Returns:
            str: 用户答案，如果未作答返回None
        """
        if self.answers is None:
            return None
        
        return self.answers.get(str(question_id))
    
    def to_dict(self):
        """转换为字典
        
        Returns:
            dict: 会话信息字典
        """
        # 添加 'Z' 后缀表示 UTC 时间，确保前端正确解析
        return {
            'id': self.id,
            'user_id': self.user_id,
            'paper_id': self.paper_id,
            'start_time': (self.start_time.isoformat() + 'Z') if self.start_time else None,
            'end_time': (self.end_time.isoformat() + 'Z') if self.end_time else None,
            'submit_time': (self.submit_time.isoformat() + 'Z') if self.submit_time else None,
            'last_active_time': (self.last_active_time.isoformat() + 'Z') if self.last_active_time else None,
            'status': self.status,
            'answers': self.answers,
            'current_question_index': self.current_question_index or 0,
            'answered_count': len(self.answers) if self.answers else 0
        }


class ExamResult(db.Model):
    """考试结果模型
    
    存储考试的批改结果和统计信息
    """
    __tablename__ = 'exam_results'
    
    # 主键
    id = db.Column(db.Integer, primary_key=True)
    
    # 外键
    session_id = db.Column(db.Integer, db.ForeignKey('exam_sessions.id'), nullable=False, unique=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    paper_id = db.Column(db.Integer, db.ForeignKey('exam_papers.id'), nullable=False, index=True)
    
    # 成绩信息
    total_score = db.Column(db.Integer, nullable=False)  # 试卷总分
    score = db.Column(db.Float, nullable=False)  # 得分
    correct_count = db.Column(db.Integer, nullable=False)  # 正确题数
    wrong_count = db.Column(db.Integer, nullable=False)  # 错误题数
    accuracy = db.Column(db.Float, nullable=False)  # 正确率
    time_spent = db.Column(db.Integer)  # 答题时长（秒）
    
    # 详细结果（JSON格式：{question_id: {correct: bool, score: int, user_answer: str, correct_answer: str}}）
    details = db.Column(db.JSON)
    
    # 创建时间
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # 关系
    session = db.relationship('ExamSession', backref='result')
    user = db.relationship('User', backref='exam_results')
    paper = db.relationship('ExamPaper', backref='exam_results')
    
    def __repr__(self):
        return f'<ExamResult {self.id}: user={self.user_id} score={self.score}/{self.total_score}>'
    
    @staticmethod
    def calculate_score(session):
        """计算考试成绩
        
        Args:
            session: 考试会话
            
        Returns:
            dict: 成绩信息
        """
        from app.models.question import Question
        
        paper = session.paper
        questions = paper.get_questions()
        
        total_score = paper.total_score
        score = 0
        correct_count = 0
        wrong_count = 0
        details = {}
        
        for item in questions:
            question = item['question']
            question_score = item['score']
            user_answer = session.get_answer(question.id)
            
            # 判断答案是否正确
            is_correct = False
            if user_answer:
                # 简单的字符串比较（实际应用中可能需要更复杂的比较逻辑）
                is_correct = str(user_answer).strip().upper() == str(question.correct_answer).strip().upper()
            
            if is_correct:
                score += question_score
                correct_count += 1
            else:
                wrong_count += 1
            
            details[str(question.id)] = {
                'correct': is_correct,
                'score': question_score if is_correct else 0,
                'user_answer': user_answer,
                'correct_answer': question.correct_answer,
                'explanation': question.explanation
            }
        
        # 计算正确率
        total_questions = correct_count + wrong_count
        accuracy = (correct_count / total_questions * 100) if total_questions > 0 else 0
        
        # 计算答题时长
        time_spent = None
        if session.submit_time and session.start_time:
            time_spent = int((session.submit_time - session.start_time).total_seconds())
        
        return {
            'total_score': total_score,
            'score': score,
            'correct_count': correct_count,
            'wrong_count': wrong_count,
            'accuracy': round(accuracy, 2),
            'time_spent': time_spent,
            'details': details
        }
    
    def to_dict(self, include_details=False):
        """转换为字典
        
        Args:
            include_details: 是否包含详细结果
            
        Returns:
            dict: 结果信息字典
        """
        data = {
            'id': self.id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'paper_id': self.paper_id,
            'total_score': self.total_score,
            'score': self.score,
            'correct_count': self.correct_count,
            'wrong_count': self.wrong_count,
            'accuracy': self.accuracy,
            'time_spent': self.time_spent,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_details:
            # 将 details 转换为包含完整题目信息的列表
            from app.models.question import Question
            
            details_list = []
            if self.details:
                for question_id, detail_info in self.details.items():
                    question = Question.query.get(int(question_id))
                    detail_item = {
                        'question_id': int(question_id),
                        'is_correct': detail_info.get('correct', False),
                        'score': detail_info.get('score', 0),
                        'user_answer': detail_info.get('user_answer'),
                        'correct_answer': detail_info.get('correct_answer'),
                        'explanation': detail_info.get('explanation'),
                        # 包含完整题目信息，包括答案和解析
                        'question': question.to_dict(include_answer=True, include_explanation=True) if question else None
                    }
                    details_list.append(detail_item)
            
            # 按题目ID排序
            details_list.sort(key=lambda x: x['question_id'])
            data['details'] = details_list
        
        return data
