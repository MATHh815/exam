"""题库服务模块"""
from datetime import datetime
from sqlalchemy import or_, and_
from app import db
from app.models.question import Question


class QuestionService:
    """题库服务类
    
    提供题目的创建、更新、删除、查询和随机抽题等功能
    """
    
    @staticmethod
    def create_question(data, created_by):
        """创建题目
        
        Args:
            data: 题目数据字典
            created_by: 创建者用户ID
        
        Returns:
            Question: 创建的题目对象
        
        Raises:
            ValueError: 数据验证失败
        """
        # 验证必填字段
        required_fields = ['exam_type', 'question_type', 'content', 'correct_answer']
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValueError(f'缺少必填字段: {field}')
        
        # 创建题目
        question = Question(
            exam_type=data['exam_type'],
            question_type=data['question_type'],
            subject=data.get('subject'),
            chapter=data.get('chapter'),
            difficulty=data.get('difficulty', 3),
            content=data['content'],
            options=data.get('options'),
            correct_answer=data['correct_answer'],
            explanation=data.get('explanation'),
            tags=data.get('tags'),
            created_by=created_by
        )
        
        db.session.add(question)
        db.session.commit()
        
        return question
    
    @staticmethod
    def update_question(question_id, data):
        """更新题目（保持ID不变）
        
        Args:
            question_id: 题目ID
            data: 更新的数据字典
        
        Returns:
            Question: 更新后的题目对象
        
        Raises:
            ValueError: 题目不存在或已删除
        """
        question = Question.query.get(question_id)
        
        if not question:
            raise ValueError('题目不存在')
        
        if question.is_deleted:
            raise ValueError('题目已被删除')
        
        # 更新允许的字段
        allowed_fields = [
            'exam_type', 'question_type', 'subject', 'chapter',
            'difficulty', 'content', 'options', 'correct_answer',
            'explanation', 'tags'
        ]
        
        for field in allowed_fields:
            if field in data:
                setattr(question, field, data[field])
        
        question.updated_at = datetime.utcnow()
        db.session.commit()
        
        return question
    
    @staticmethod
    def delete_question(question_id):
        """软删除题目
        
        Args:
            question_id: 题目ID
        
        Returns:
            bool: 是否成功
        
        Raises:
            ValueError: 题目不存在
        """
        question = Question.query.get(question_id)
        
        if not question:
            raise ValueError('题目不存在')
        
        if question.is_deleted:
            raise ValueError('题目已被删除')
        
        question.soft_delete()
        
        return True
    
    @staticmethod
    def get_question(question_id, include_deleted=False):
        """获取单个题目
        
        Args:
            question_id: 题目ID
            include_deleted: 是否包含已删除的题目
        
        Returns:
            Question: 题目对象
        
        Raises:
            ValueError: 题目不存在
        """
        question = Question.query.get(question_id)
        
        if not question:
            raise ValueError('题目不存在')
        
        if question.is_deleted and not include_deleted:
            raise ValueError('题目已被删除')
        
        return question
    
    @staticmethod
    def list_questions(filters=None, page=1, page_size=20, include_deleted=False):
        """查询题目列表（支持筛选和分页）
        
        Args:
            filters: 筛选条件字典
                - exam_type: 考试类型
                - question_type: 题目类型
                - subject: 科目
                - chapter: 章节
                - difficulty: 难度
                - keyword: 关键词（搜索content）
                - tags: 标签列表
            page: 页码（从1开始）
            page_size: 每页数量
            include_deleted: 是否包含已删除的题目
        
        Returns:
            tuple: (题目列表, 总数)
        """
        query = Question.query
        
        # 默认不包含已删除的题目
        if not include_deleted:
            query = query.filter_by(is_deleted=False)
        
        # 应用筛选条件
        if filters:
            if 'exam_type' in filters and filters['exam_type']:
                query = query.filter_by(exam_type=filters['exam_type'])
            
            if 'question_type' in filters and filters['question_type']:
                query = query.filter_by(question_type=filters['question_type'])
            
            if 'subject' in filters and filters['subject']:
                query = query.filter_by(subject=filters['subject'])
            
            if 'chapter' in filters and filters['chapter']:
                query = query.filter_by(chapter=filters['chapter'])
            
            if 'difficulty' in filters and filters['difficulty']:
                query = query.filter_by(difficulty=filters['difficulty'])
            
            if 'keyword' in filters and filters['keyword']:
                keyword = f"%{filters['keyword']}%"
                query = query.filter(
                    or_(
                        Question.content.like(keyword),
                        Question.explanation.like(keyword)
                    )
                )
            
            if 'tags' in filters and filters['tags']:
                # 标签筛选（包含任一标签）
                for tag in filters['tags']:
                    query = query.filter(Question.tags.contains([tag]))
        
        # 获取总数
        total = query.count()
        
        # 分页
        questions = query.order_by(Question.created_at.desc()) \
                        .offset((page - 1) * page_size) \
                        .limit(page_size) \
                        .all()
        
        return questions, total
    
    @staticmethod
    def random_questions(exam_type=None, count=10, filters=None):
        """随机抽取题目
        
        Args:
            exam_type: 考试类型（可选）
            count: 抽取数量
            filters: 额外的筛选条件
        
        Returns:
            list: 随机题目列表
        """
        query = Question.query.filter_by(is_deleted=False)
        
        # 考试类型筛选
        if exam_type:
            query = query.filter_by(exam_type=exam_type)
        
        # 应用额外筛选条件
        if filters:
            if 'question_type' in filters and filters['question_type']:
                query = query.filter_by(question_type=filters['question_type'])
            
            if 'subject' in filters and filters['subject']:
                query = query.filter_by(subject=filters['subject'])
            
            if 'chapter' in filters and filters['chapter']:
                query = query.filter_by(chapter=filters['chapter'])
            
            if 'difficulty' in filters and filters['difficulty']:
                query = query.filter_by(difficulty=filters['difficulty'])
        
        # 随机排序并限制数量
        questions = query.order_by(db.func.random()).limit(count).all()
        
        return questions
    
    @staticmethod
    def import_questions(questions_data, created_by):
        """批量导入题目
        
        Args:
            questions_data: 题目数据列表
            created_by: 创建者用户ID
        
        Returns:
            dict: 导入结果统计
                - success_count: 成功数量
                - failed_count: 失败数量
                - errors: 错误列表
        
        Raises:
            ValueError: 数据格式错误
        """
        if not isinstance(questions_data, list):
            raise ValueError('题目数据必须是列表格式')
        
        success_count = 0
        failed_count = 0
        errors = []
        
        for index, data in enumerate(questions_data):
            try:
                # 验证必填字段
                required_fields = ['exam_type', 'question_type', 'content', 'correct_answer']
                for field in required_fields:
                    if field not in data or not data[field]:
                        raise ValueError(f'缺少必填字段: {field}')
                
                # 创建题目
                question = Question(
                    exam_type=data['exam_type'],
                    question_type=data['question_type'],
                    subject=data.get('subject'),
                    chapter=data.get('chapter'),
                    difficulty=data.get('difficulty', 3),
                    content=data['content'],
                    options=data.get('options'),
                    correct_answer=data['correct_answer'],
                    explanation=data.get('explanation'),
                    tags=data.get('tags'),
                    created_by=created_by
                )
                
                db.session.add(question)
                success_count += 1
                
            except Exception as e:
                failed_count += 1
                errors.append({
                    'index': index,
                    'error': str(e),
                    'data': data
                })
        
        # 提交所有成功的题目
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ValueError(f'批量导入失败: {str(e)}')
        
        return {
            'success_count': success_count,
            'failed_count': failed_count,
            'errors': errors
        }
    
    @staticmethod
    def get_statistics(filters=None):
        """获取题库统计信息
        
        Args:
            filters: 筛选条件
        
        Returns:
            dict: 统计信息
                - total: 总题数
                - by_exam_type: 按考试类型统计
                - by_question_type: 按题目类型统计
                - by_difficulty: 按难度统计
        """
        query = Question.query.filter_by(is_deleted=False)
        
        # 应用筛选条件
        if filters:
            if 'exam_type' in filters and filters['exam_type']:
                query = query.filter_by(exam_type=filters['exam_type'])
        
        total = query.count()
        
        # 按考试类型统计
        by_exam_type = {}
        for exam_type in ['civil_service', 'postgraduate', 'public_institution']:
            count = query.filter_by(exam_type=exam_type).count()
            by_exam_type[exam_type] = count
        
        # 按题目类型统计
        by_question_type = {}
        for question_type in ['single_choice', 'multiple_choice', 'true_false', 'fill_blank', 'essay']:
            count = query.filter_by(question_type=question_type).count()
            by_question_type[question_type] = count
        
        # 按难度统计
        by_difficulty = {}
        for difficulty in range(1, 6):
            count = query.filter_by(difficulty=difficulty).count()
            by_difficulty[str(difficulty)] = count
        
        return {
            'total': total,
            'by_exam_type': by_exam_type,
            'by_question_type': by_question_type,
            'by_difficulty': by_difficulty
        }
