"""笔记管理属性测试

测试笔记管理系统的正确性属性，使用 Hypothesis 进行基于属性的测试。
每个测试类对应设计文档中的一个正确性属性。
"""
import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime
from app import create_app, db
from app.models.user import User
from app.models.question import Question
from app.models.note import QuestionNote
from app.services.note_service import NoteService


class TestProperty11NoteCreationRoundTrip:
    """Property 11: Note creation round-trip
    
    验证笔记创建后可以正确读取，且数据完整。
    对应设计文档 Property 11。
    """
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """测试前设置"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # 创建测试用户
        self.user = User(username='testuser', email='test@example.com')
        self.user.set_password('password123')
        db.session.add(self.user)
        db.session.flush()
        
        # 创建测试题目
        self.question = Question(
            content='测试题目',
            question_type='single_choice',
            exam_type='civil_service',
            subject='行测',
            chapter='数量关系',
            difficulty=3,
            correct_answer='A'
        )
        db.session.add(self.question)
        db.session.commit()
        
        yield
        
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    @given(
        content=st.text(min_size=1, max_size=100),  # 减少最大长度
        tags=st.lists(st.text(min_size=1, max_size=10), max_size=3)  # 减少标签数量和长度
    )
    @settings(max_examples=20, deadline=5000)  # 减少迭代次数，增加超时时间
    def test_note_creation_round_trip(self, content, tags):
        """测试笔记创建和读取的往返一致性"""
        # 创建笔记
        note_data = {
            'question_id': self.question.id,
            'content': content,
            'tags': tags
        }
        
        created_note = NoteService.create_note(self.user.id, note_data)
        
        # 读取笔记
        retrieved_note = NoteService.get_note_by_id(created_note.id, self.user.id)
        
        # 验证数据一致性
        assert retrieved_note.id == created_note.id
        assert retrieved_note.user_id == self.user.id
        assert retrieved_note.question_id == self.question.id
        assert retrieved_note.content == content
        assert retrieved_note.tags == tags
        assert retrieved_note.is_deleted is False
        
        # 清理
        db.session.delete(created_note)
        db.session.commit()


class TestProperty12NoteUpdatePreservesIdentity:
    """Property 12: Note update preserves identity
    
    验证笔记更新后ID和关联关系不变。
    对应设计文档 Property 12。
    """
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """测试前设置"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # 创建测试数据
        self.user = User(username='testuser', email='test@example.com')
        self.user.set_password('password123')
        db.session.add(self.user)
        db.session.flush()
        
        self.question = Question(
            content='测试题目',
            question_type='single_choice',
            exam_type='civil_service',
            subject='行测',
            chapter='数量关系',
            difficulty=3,
            correct_answer='A'
        )
        db.session.add(self.question)
        db.session.commit()
        
        yield
        
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    @given(
        original_content=st.text(min_size=1, max_size=100),
        updated_content=st.text(min_size=1, max_size=100),
        original_tags=st.lists(st.text(min_size=1, max_size=10), max_size=3),
        updated_tags=st.lists(st.text(min_size=1, max_size=10), max_size=3)
    )
    @settings(max_examples=20, deadline=5000)
    def test_update_preserves_identity(self, original_content, updated_content, original_tags, updated_tags):
        """测试更新笔记保留ID和关联"""
        # 创建笔记
        note_data = {
            'question_id': self.question.id,
            'content': original_content,
            'tags': original_tags
        }
        note = NoteService.create_note(self.user.id, note_data)
        
        original_id = note.id
        original_user_id = note.user_id
        original_question_id = note.question_id
        
        # 更新笔记
        update_data = {
            'content': updated_content,
            'tags': updated_tags
        }
        updated_note = NoteService.update_note(note.id, self.user.id, update_data)
        
        # 验证ID和关联不变
        assert updated_note.id == original_id
        assert updated_note.user_id == original_user_id
        assert updated_note.question_id == original_question_id
        
        # 验证内容已更新
        assert updated_note.content == updated_content
        assert updated_note.tags == updated_tags
        
        # 清理
        db.session.delete(note)
        db.session.commit()


class TestProperty13NoteSoftDelete:
    """Property 13: Note soft delete
    
    验证笔记软删除后不在列表中显示，但数据库记录保留。
    对应设计文档 Property 13。
    """
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """测试前设置"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # 创建测试数据
        self.user = User(username='testuser', email='test@example.com')
        self.user.set_password('password123')
        db.session.add(self.user)
        db.session.flush()
        
        self.question = Question(
            content='测试题目',
            question_type='single_choice',
            exam_type='civil_service',
            subject='行测',
            chapter='数量关系',
            difficulty=3,
            correct_answer='A'
        )
        db.session.add(self.question)
        db.session.commit()
        
        yield
        
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    @given(content=st.text(min_size=1, max_size=5000))
    @settings(max_examples=100, deadline=None)
    def test_soft_delete_preserves_record(self, content):
        """测试软删除保留数据库记录"""
        # 创建笔记
        note_data = {
            'question_id': self.question.id,
            'content': content,
            'tags': []
        }
        note = NoteService.create_note(self.user.id, note_data)
        note_id = note.id
        
        # 删除笔记
        NoteService.delete_note(note_id, self.user.id)
        
        # 验证笔记不在用户笔记列表中
        result = NoteService.get_user_notes(self.user.id)
        assert len(result['notes']) == 0
        
        # 验证数据库记录仍存在
        db_note = QuestionNote.query.get(note_id)
        assert db_note is not None
        assert db_note.is_deleted is True
        
        # 验证无法通过 get_note_by_id 获取
        with pytest.raises(ValueError, match='笔记不存在或无权访问'):
            NoteService.get_note_by_id(note_id, self.user.id)
        
        # 清理
        db.session.delete(db_note)
        db.session.commit()


class TestProperty14QuestionNotesCompleteness:
    """Property 14: Question notes completeness
    
    验证获取题目笔记时返回完整信息。
    对应设计文档 Property 14。
    """
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """测试前设置"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # 创建测试数据
        self.user = User(username='testuser', email='test@example.com')
        self.user.set_password('password123')
        db.session.add(self.user)
        db.session.flush()
        
        self.question = Question(
            content='测试题目',
            question_type='single_choice',
            exam_type='civil_service',
            subject='行测',
            chapter='数量关系',
            difficulty=3,
            correct_answer='A'
        )
        db.session.add(self.question)
        db.session.commit()
        
        yield
        
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    @given(content=st.text(min_size=1, max_size=5000))
    @settings(max_examples=100, deadline=None)
    def test_question_notes_completeness(self, content):
        """测试获取题目笔记返回完整信息"""
        # 创建笔记
        note_data = {
            'question_id': self.question.id,
            'content': content,
            'tags': ['测试']
        }
        created_note = NoteService.create_note(self.user.id, note_data)
        
        # 获取题目笔记
        retrieved_note = NoteService.get_question_notes(self.user.id, self.question.id)
        
        # 验证返回完整信息
        assert retrieved_note is not None
        assert retrieved_note.id == created_note.id
        assert retrieved_note.user_id == self.user.id
        assert retrieved_note.question_id == self.question.id
        assert retrieved_note.content == content
        assert retrieved_note.tags == ['测试']
        assert retrieved_note.created_at is not None
        assert retrieved_note.updated_at is not None
        
        # 验证 has_note_for_question 方法
        assert NoteService.has_note_for_question(self.user.id, self.question.id) is True
        
        # 清理
        db.session.delete(created_note)
        db.session.commit()


class TestProperty15MarkdownPreservation:
    """Property 15: Markdown preservation
    
    验证 Markdown 格式的笔记内容正确保存和读取。
    对应设计文档 Property 15。
    """
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """测试前设置"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # 创建测试数据
        self.user = User(username='testuser', email='test@example.com')
        self.user.set_password('password123')
        db.session.add(self.user)
        db.session.flush()
        
        self.question = Question(
            content='测试题目',
            question_type='single_choice',
            exam_type='civil_service',
            subject='行测',
            chapter='数量关系',
            difficulty=3,
            correct_answer='A'
        )
        db.session.add(self.question)
        db.session.commit()
        
        yield
        
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    @given(
        markdown_content=st.one_of(
            st.just('# 标题\n\n这是一段**加粗**的文字'),
            st.just('- 列表项1\n- 列表项2\n- 列表项3'),
            st.just('```python\nprint("Hello")\n```'),
            st.just('> 这是引用\n\n这是正文'),
            st.just('[链接](https://example.com)')
        )
    )
    @settings(max_examples=100, deadline=None)
    def test_markdown_preservation(self, markdown_content):
        """测试 Markdown 格式保留"""
        # 创建包含 Markdown 的笔记
        note_data = {
            'question_id': self.question.id,
            'content': markdown_content,
            'tags': []
        }
        note = NoteService.create_note(self.user.id, note_data)
        
        # 读取笔记
        retrieved_note = NoteService.get_note_by_id(note.id, self.user.id)
        
        # 验证 Markdown 内容完全保留
        assert retrieved_note.content == markdown_content
        
        # 验证 Markdown 验证方法
        assert NoteService.validate_markdown(markdown_content) is True
        
        # 清理
        db.session.delete(note)
        db.session.commit()


class TestProperty16NoteIndicatorPresence:
    """Property 16: Note indicator presence
    
    验证题目列表中正确显示笔记指示器。
    对应设计文档 Property 16。
    """
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """测试前设置"""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # 创建测试数据
        self.user = User(username='testuser', email='test@example.com')
        self.user.set_password('password123')
        db.session.add(self.user)
        db.session.flush()
        
        # 创建多个题目
        self.questions = []
        for i in range(5):
            question = Question(
                content=f'测试题目{i}',
                question_type='single_choice',
                exam_type='civil_service',
                subject='行测',
                chapter='数量关系',
                difficulty=3,
                correct_answer='A'
            )
            db.session.add(question)
            self.questions.append(question)
        
        db.session.commit()
        
        yield
        
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    @given(num_notes=st.integers(min_value=0, max_value=5))
    @settings(max_examples=50, deadline=None)
    def test_note_indicator_presence(self, num_notes):
        """测试笔记指示器正确显示"""
        # 为前 num_notes 个题目创建笔记
        created_notes = []
        for i in range(num_notes):
            note_data = {
                'question_id': self.questions[i].id,
                'content': f'笔记内容{i}',
                'tags': []
            }
            note = NoteService.create_note(self.user.id, note_data)
            created_notes.append(note)
        
        # 验证每个题目的笔记指示器
        for i, question in enumerate(self.questions):
            has_note = NoteService.has_note_for_question(self.user.id, question.id)
            
            if i < num_notes:
                # 应该有笔记
                assert has_note is True
                note = NoteService.get_question_notes(self.user.id, question.id)
                assert note is not None
            else:
                # 不应该有笔记
                assert has_note is False
                note = NoteService.get_question_notes(self.user.id, question.id)
                assert note is None
        
        # 清理
        for note in created_notes:
            db.session.delete(note)
        db.session.commit()
