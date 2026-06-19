"""
笔记导出功能属性测试

使用 Hypothesis 进行基于属性的测试
"""
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from io import BytesIO

from app import create_app, db
from app.models.user import User
from app.models.question import Question
from app.models.note import QuestionNote
from app.services.export_service import ExportService


@pytest.fixture(scope='module')
def app():
    """创建测试应用"""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """创建测试客户端"""
    return app.test_client()


@pytest.fixture(scope='function')
def test_user(app):
    """创建测试用户"""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            role='user'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        yield user
        
        db.session.delete(user)
        db.session.commit()


@pytest.fixture(scope='function')
def test_question(app):
    """创建测试题目"""
    with app.app_context():
        question = Question(
            content='测试题目内容',
            question_type='单选题',
            options='["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"]',
            correct_answer='A',
            explanation='这是解析',
            exam_type='公务员',
            subject='行测',
            chapter='数量关系',
            difficulty=2
        )
        db.session.add(question)
        db.session.commit()
        
        yield question
        
        db.session.delete(question)
        db.session.commit()


@pytest.fixture(scope='function')
def export_service(app):
    """创建导出服务实例"""
    with app.app_context():
        return ExportService()


# Property 28: Export format support
# 验证导出服务支持 PDF 和 Markdown 两种格式
@given(
    export_format=st.sampled_from(['pdf', 'markdown'])
)
@settings(
    max_examples=10, 
    deadline=5000,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
def test_property_28_export_format_support(app, test_user, test_question, export_service, export_format):
    """
    Property 28: Export format support
    
    验证导出服务支持指定的格式
    
    对应设计文档: Property 28
    对应需求: Requirement 8.1, 8.2
    """
    with app.app_context():
        # 创建测试笔记
        note = QuestionNote(
            user_id=test_user.id,
            question_id=test_question.id,
            content='# 测试笔记\n\n这是测试内容'
        )
        db.session.add(note)
        db.session.commit()
        
        try:
            # 尝试导出
            result = export_service.generate_download_link(
                user_id=test_user.id,
                export_format=export_format
            )
            
            # 验证结果
            assert 'filename' in result
            assert 'content' in result
            assert 'content_type' in result
            
            # 验证文件名扩展名
            if export_format == 'pdf':
                assert result['filename'].endswith('.pdf')
                assert result['content_type'] == 'application/pdf'
                assert isinstance(result['content'], BytesIO)
            else:
                assert result['filename'].endswith('.md')
                assert result['content_type'] == 'text/markdown'
                assert isinstance(result['content'], str)
        
        finally:
            db.session.delete(note)
            db.session.commit()


# Property 29: PDF export completeness
# 验证 PDF 导出包含所有笔记内容
@given(
    note_count=st.integers(min_value=1, max_value=5)
)
@settings(
    max_examples=10, 
    deadline=5000,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
def test_property_29_pdf_export_completeness(app, test_user, test_question, export_service, note_count):
    """
    Property 29: PDF export completeness
    
    验证 PDF 导出包含所有笔记
    
    对应设计文档: Property 29
    对应需求: Requirement 8.2
    """
    with app.app_context():
        # 创建多条笔记
        notes = []
        for i in range(note_count):
            note = QuestionNote(
                user_id=test_user.id,
                question_id=test_question.id,
                content=f'# 笔记 {i+1}\n\n这是第 {i+1} 条笔记的内容'
            )
            db.session.add(note)
            notes.append(note)
        
        db.session.commit()
        
        try:
            # 导出为 PDF
            pdf_buffer = export_service.export_notes_to_pdf(
                user_id=test_user.id
            )
            
            # 验证 PDF 生成成功
            assert isinstance(pdf_buffer, BytesIO)
            assert pdf_buffer.getbuffer().nbytes > 0
            
            # PDF 应该包含所有笔记（通过大小判断）
            # 每条笔记至少增加一定的字节数
            min_size = 1000 + (note_count * 100)  # 基础大小 + 每条笔记的最小大小
            assert pdf_buffer.getbuffer().nbytes > min_size
        
        finally:
            for note in notes:
                db.session.delete(note)
            db.session.commit()


# Property 30: Markdown export completeness
# 验证 Markdown 导出包含所有笔记内容
@given(
    note_count=st.integers(min_value=1, max_value=5)
)
@settings(
    max_examples=10, 
    deadline=5000,
    suppress_health_check=[HealthCheck.function_scoped_fixture]
)
def test_property_30_markdown_export_completeness(app, test_user, test_question, export_service, note_count):
    """
    Property 30: Markdown export completeness
    
    验证 Markdown 导出包含所有笔记
    
    对应设计文档: Property 29（扩展）
    对应需求: Requirement 8.1
    """
    with app.app_context():
        # 创建多条笔记
        notes = []
        for i in range(note_count):
            note = QuestionNote(
                user_id=test_user.id,
                question_id=test_question.id,
                content=f'# 笔记 {i+1}\n\n这是第 {i+1} 条笔记的内容'
            )
            db.session.add(note)
            notes.append(note)
        
        db.session.commit()
        
        try:
            # 导出为 Markdown
            markdown_content = export_service.export_notes_to_markdown(
                user_id=test_user.id
            )
            
            # 验证 Markdown 内容
            assert isinstance(markdown_content, str)
            assert len(markdown_content) > 0
            
            # 验证包含所有笔记
            for i in range(note_count):
                assert f'笔记 {i+1}' in markdown_content
                assert f'这是第 {i+1} 条笔记的内容' in markdown_content
            
            # 验证笔记数量
            assert markdown_content.count('## 笔记') == note_count
        
        finally:
            for note in notes:
                db.session.delete(note)
            db.session.commit()


# Property 31: Export filters work correctly
# 验证导出筛选功能正确工作
def test_property_31_export_filters(app, test_user, export_service):
    """
    Property 31: Export filters work correctly
    
    验证导出筛选功能
    
    对应设计文档: Property 27（搜索筛选）
    对应需求: Requirement 7.3, 8.3
    """
    with app.app_context():
        # 创建不同科目的题目和笔记
        questions = []
        notes = []
        
        for subject in ['行测', '申论', '数学']:
            question = Question(
                content=f'{subject}测试题目',
                question_type='单选题',
                options='["A", "B", "C", "D"]',
                correct_answer='A',
                exam_type='公务员',
                subject=subject,
                chapter='测试章节',
                difficulty=2
            )
            db.session.add(question)
            db.session.flush()
            
            note = QuestionNote(
                user_id=test_user.id,
                question_id=question.id,
                content=f'# {subject}笔记\n\n内容'
            )
            db.session.add(note)
            
            questions.append(question)
            notes.append(note)
        
        db.session.commit()
        
        try:
            # 测试每个科目的筛选
            for subject in ['行测', '申论', '数学']:
                # 使用筛选条件导出
                markdown_content = export_service.export_notes_to_markdown(
                    user_id=test_user.id,
                    filters={'subject': subject}
                )
                
                # 验证只包含指定科目的笔记
                assert f'{subject}笔记' in markdown_content
                
                # 验证不包含其他科目的笔记
                other_subjects = [s for s in ['行测', '申论', '数学'] if s != subject]
                for other_subj in other_subjects:
                    assert f'{other_subj}笔记' not in markdown_content
                
                # 验证笔记数量为 1
                assert markdown_content.count('## 笔记') == 1
        
        finally:
            for note in notes:
                db.session.delete(note)
            for question in questions:
                db.session.delete(question)
            db.session.commit()


# Property 32: Empty export handling
# 验证空笔记列表的导出处理
def test_property_32_empty_export_handling(app, test_user, export_service):
    """
    Property 32: Empty export handling
    
    验证没有笔记时的导出处理
    
    对应设计文档: 错误处理
    对应需求: Requirement 18.1
    """
    with app.app_context():
        # 尝试导出（没有笔记）
        with pytest.raises(ValueError, match='没有可导出的笔记'):
            export_service.export_notes_to_pdf(user_id=test_user.id)
        
        with pytest.raises(ValueError, match='没有可导出的笔记'):
            export_service.export_notes_to_markdown(user_id=test_user.id)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
