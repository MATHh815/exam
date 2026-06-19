"""测试试卷模型"""
import pytest
from datetime import datetime
from app.models.exam import ExamPaper, ExamPaperQuestion
from app.models.question import Question
from app.models.user import User


@pytest.fixture
def sample_questions(db_session, admin_user):
    """创建多个示例题目"""
    questions = []
    for i in range(5):
        question = Question(
            exam_type='civil_service',
            question_type='single_choice',
            subject='行测',
            chapter='数量关系',
            difficulty=3,
            content=f'测试题目{i+1}',
            options={'A': '选项A', 'B': '选项B', 'C': '选项C', 'D': '选项D'},
            correct_answer='A',
            explanation='测试解析',
            tags=['测试'],
            created_by=admin_user.id
        )
        db_session.session.add(question)
        questions.append(question)
    
    db_session.session.commit()
    return questions


class TestExamPaperModel:
    """测试 ExamPaper 模型"""
    
    def test_create_exam_paper(self, app, db_session, sample_user):
        """测试创建试卷"""
        paper = ExamPaper(
            name='公务员行测模拟试卷一',
            exam_type='civil_service',
            description='行测综合测试',
            duration=120,
            total_score=100,
            pass_score=60,
            created_by=sample_user.id
        )
        
        db_session.session.add(paper)
        db_session.session.commit()
        
        assert paper.id is not None
        assert paper.name == '公务员行测模拟试卷一'
        assert paper.version == 1
        assert paper.is_published is False
        assert paper.is_deleted is False
    
    def test_soft_delete_paper(self, app, db_session, sample_user):
        """测试软删除试卷"""
        paper = ExamPaper(
            name='测试试卷',
            exam_type='civil_service',
            duration=120,
            total_score=100,
            created_by=sample_user.id
        )
        
        db_session.session.add(paper)
        db_session.session.commit()
        
        # 软删除
        paper.soft_delete()
        db_session.session.commit()
        
        assert paper.is_deleted is True
        assert paper.id is not None  # 数据仍然存在
    
    def test_publish_paper(self, app, db_session, sample_user):
        """测试发布试卷"""
        paper = ExamPaper(
            name='测试试卷',
            exam_type='civil_service',
            duration=120,
            total_score=100,
            created_by=sample_user.id
        )
        
        db_session.session.add(paper)
        db_session.session.commit()
        
        # 发布
        paper.publish()
        db_session.session.commit()
        
        assert paper.is_published is True
    
    def test_create_new_version(self, app, db_session, sample_user, sample_questions):
        """测试创建新版本"""
        # 创建原始试卷
        paper = ExamPaper(
            name='原始试卷',
            exam_type='civil_service',
            duration=120,
            total_score=100,
            pass_score=60,
            created_by=sample_user.id,
            is_published=True
        )
        
        db_session.session.add(paper)
        db_session.session.commit()
        
        # 添加题目
        for i, question in enumerate(sample_questions[:3]):
            pq = ExamPaperQuestion(
                paper_id=paper.id,
                question_id=question.id,
                order=i + 1,
                score=10
            )
            db_session.session.add(pq)
        
        db_session.session.commit()
        
        # 创建新版本
        new_paper = paper.create_new_version()
        db_session.session.add(new_paper)
        db_session.session.commit()
        
        # 验证新版本
        assert new_paper.id != paper.id
        assert new_paper.version == paper.version + 1
        assert new_paper.is_published is False
        assert new_paper.name == paper.name
        assert new_paper.paper_questions.count() == paper.paper_questions.count()
        
        # 验证原试卷未被修改
        assert paper.version == 1
        assert paper.is_published is True


class TestExamPaperQuestionModel:
    """测试 ExamPaperQuestion 模型"""
    
    def test_create_paper_question(self, app, db_session, sample_user, sample_questions):
        """测试创建试卷题目关联"""
        paper = ExamPaper(
            name='测试试卷',
            exam_type='civil_service',
            duration=120,
            total_score=100,
            created_by=sample_user.id
        )
        
        db_session.session.add(paper)
        db_session.session.commit()
        
        # 添加题目
        pq = ExamPaperQuestion(
            paper_id=paper.id,
            question_id=sample_questions[0].id,
            order=1,
            score=10
        )
        
        db_session.session.add(pq)
        db_session.session.commit()
        
        assert pq.id is not None
        assert pq.paper_id == paper.id
        assert pq.question_id == sample_questions[0].id
        assert pq.order == 1
        assert pq.score == 10
    
    def test_unique_constraint_paper_question(self, app, db_session, sample_user, sample_questions):
        """测试同一试卷不能有重复题目"""
        paper = ExamPaper(
            name='测试试卷',
            exam_type='civil_service',
            duration=120,
            total_score=100,
            created_by=sample_user.id
        )
        
        db_session.session.add(paper)
        db_session.session.commit()
        
        # 添加第一个题目
        pq1 = ExamPaperQuestion(
            paper_id=paper.id,
            question_id=sample_questions[0].id,
            order=1,
            score=10
        )
        
        db_session.session.add(pq1)
        db_session.session.commit()
        
        # 尝试添加重复题目
        pq2 = ExamPaperQuestion(
            paper_id=paper.id,
            question_id=sample_questions[0].id,
            order=2,
            score=10
        )
        
        db_session.session.add(pq2)
        
        with pytest.raises(Exception):  # 应该抛出唯一约束异常
            db_session.session.commit()
    
    def test_unique_constraint_paper_order(self, app, db_session, sample_user, sample_questions):
        """测试同一试卷不能有重复顺序"""
        paper = ExamPaper(
            name='测试试卷',
            exam_type='civil_service',
            duration=120,
            total_score=100,
            created_by=sample_user.id
        )
        
        db_session.session.add(paper)
        db_session.session.commit()
        
        # 添加第一个题目
        pq1 = ExamPaperQuestion(
            paper_id=paper.id,
            question_id=sample_questions[0].id,
            order=1,
            score=10
        )
        
        db_session.session.add(pq1)
        db_session.session.commit()
        
        # 尝试添加相同顺序的题目
        pq2 = ExamPaperQuestion(
            paper_id=paper.id,
            question_id=sample_questions[1].id,
            order=1,
            score=10
        )
        
        db_session.session.add(pq2)
        
        with pytest.raises(Exception):  # 应该抛出唯一约束异常
            db_session.session.commit()
