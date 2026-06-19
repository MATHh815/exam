"""练习服务属性测试模块

使用 Hypothesis 进行基于属性的测试，验证练习服务的正确性属性
"""
import pytest
from datetime import datetime, date
from hypothesis import given, settings, strategies as st, assume, HealthCheck
from hypothesis.strategies import composite

from app import db
from app.models.user import User
from app.models.question import Question
from app.models.practice import PracticeRecord, WrongQuestion
from app.services.practice_service import PracticeService


# ============================================================================
# 测试数据生成策略
# ============================================================================

@composite
def valid_answer_data(draw):
    """生成有效的答案数据
    
    生成题目类型、正确答案和用户答案
    """
    question_types = ['single_choice', 'multiple_choice', 'true_false', 'fill_blank']
    question_type = draw(st.sampled_from(question_types))
    
    if question_type == 'single_choice':
        # 单选题：A-D
        correct_answer = draw(st.sampled_from(['A', 'B', 'C', 'D']))
        # 用户答案可能正确或错误
        user_answer = draw(st.sampled_from(['A', 'B', 'C', 'D']))
    elif question_type == 'multiple_choice':
        # 多选题：A,B,C,D的组合
        options = ['A', 'B', 'C', 'D']
        correct_count = draw(st.integers(min_value=2, max_value=4))
        correct_options = draw(st.lists(
            st.sampled_from(options),
            min_size=correct_count,
            max_size=correct_count,
            unique=True
        ))
        correct_answer = ','.join(sorted(correct_options))
        
        # 用户答案可能正确或错误
        user_count = draw(st.integers(min_value=1, max_value=4))
        user_options = draw(st.lists(
            st.sampled_from(options),
            min_size=user_count,
            max_size=user_count,
            unique=True
        ))
        user_answer = ','.join(sorted(user_options))
    elif question_type == 'true_false':
        # 判断题：对/错
        correct_answer = draw(st.sampled_from(['对', '错', 'T', 'F']))
        user_answer = draw(st.sampled_from(['对', '错', 'T', 'F']))
    else:  # fill_blank
        # 填空题：任意文本
        correct_answer = draw(st.text(min_size=1, max_size=50))
        user_answer = draw(st.text(min_size=0, max_size=50))
    
    return {
        'question_type': question_type,
        'correct_answer': correct_answer,
        'user_answer': user_answer
    }


@composite
def practice_session_data(draw):
    """生成练习会话数据
    
    生成一组答题记录，包含题目数量和每题的答题信息
    """
    # 生成1到20个题目
    count = draw(st.integers(min_value=1, max_value=20))
    
    records = []
    for _ in range(count):
        answer_data = draw(valid_answer_data())
        time_spent = draw(st.integers(min_value=1, max_value=300))  # 1-300秒
        records.append({
            'question_type': answer_data['question_type'],
            'correct_answer': answer_data['correct_answer'],
            'user_answer': answer_data['user_answer'],
            'time_spent': time_spent
        })
    
    return records


# ============================================================================
# 属性测试类
# ============================================================================

@pytest.mark.property
class TestPracticeServiceProperties:
    """练习服务属性测试类"""
    
    @given(answer_data=valid_answer_data())
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None
    )
    def test_property_answer_checking_correctness(self, app, answer_data):
        """
        Feature: exam-system, Property 6: 答案判断正确性
        
        属性：对于任意题目和用户答案，系统判断结果应该与正确答案比对结果一致
        
        Validates: Requirements 3.2
        """
        with app.app_context():
            # 使用内部的答案检查方法
            is_correct = PracticeService._check_answer(
                answer_data['user_answer'],
                answer_data['correct_answer'],
                answer_data['question_type']
            )
            
            # 手动验证答案是否正确
            user_ans = str(answer_data['user_answer']).strip().upper()
            correct_ans = str(answer_data['correct_answer']).strip().upper()
            
            if answer_data['question_type'] == 'multiple_choice':
                # 多选题需要排序后比较
                user_parts = sorted([p.strip() for p in user_ans.replace('，', ',').split(',')])
                correct_parts = sorted([p.strip() for p in correct_ans.replace('，', ',').split(',')])
                expected_correct = user_parts == correct_parts
            else:
                # 其他题型直接比较
                expected_correct = user_ans == correct_ans
            
            # 属性：系统判断结果应该与手动验证结果一致
            assert is_correct == expected_correct, \
                f"答案判断不一致：系统判断={is_correct}, 预期={expected_correct}, " \
                f"用户答案={answer_data['user_answer']}, 正确答案={answer_data['correct_answer']}, " \
                f"题目类型={answer_data['question_type']}"
    
    @given(session_data=practice_session_data())
    @settings(
        max_examples=20,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None
    )
    def test_property_practice_record_completeness(self, app, session_data):
        """
        Feature: exam-system, Property 7: 答题记录完整性
        
        属性：对于任意答题行为，系统应该记录答题时间、用户答案和正确性三个必要信息
        
        Validates: Requirements 3.3
        """
        with app.app_context():
            # 创建测试用户
            import uuid
            unique_id = str(uuid.uuid4())[:8]
            user = User(
                username=f'proptest_{unique_id}',
                email=f'proptest_{unique_id}@example.com',
                nickname='Property Test User'
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.flush()
            
            # 为每个答题记录创建题目并提交答案
            for record_data in session_data:
                # 创建题目
                question = Question(
                    exam_type='civil_service',
                    question_type=record_data['question_type'],
                    subject='测试科目',
                    chapter='测试章节',
                    difficulty=3,
                    content='测试题目内容',
                    options={'A': '选项A', 'B': '选项B', 'C': '选项C', 'D': '选项D'},
                    correct_answer=record_data['correct_answer'],
                    explanation='测试解析',
                    created_by=user.id
                )
                db.session.add(question)
                db.session.flush()
                
                # 提交答案
                result = PracticeService.submit_answer(
                    user_id=user.id,
                    question_id=question.id,
                    user_answer=record_data['user_answer'],
                    time_spent=record_data['time_spent']
                )
                
                # 查询创建的练习记录
                practice_record = PracticeRecord.query.filter_by(
                    user_id=user.id,
                    question_id=question.id
                ).order_by(PracticeRecord.created_at.desc()).first()
                
                # 属性1：记录必须存在
                assert practice_record is not None, "练习记录应该被创建"
                
                # 属性2：必须记录答题时间
                assert practice_record.created_at is not None, \
                    "练习记录必须包含答题时间"
                assert isinstance(practice_record.created_at, datetime), \
                    "答题时间必须是datetime类型"
                
                # 属性3：必须记录用户答案
                assert practice_record.user_answer is not None, \
                    "练习记录必须包含用户答案"
                assert practice_record.user_answer == record_data['user_answer'], \
                    f"记录的用户答案 {practice_record.user_answer} 应该等于提交的答案 {record_data['user_answer']}"
                
                # 属性4：必须记录正确性
                assert practice_record.is_correct is not None, \
                    "练习记录必须包含正确性标记"
                assert isinstance(practice_record.is_correct, bool), \
                    "正确性标记必须是布尔类型"
                
                # 属性5：记录的正确性应该与返回结果一致
                assert practice_record.is_correct == result['is_correct'], \
                    f"记录的正确性 {practice_record.is_correct} 应该与返回结果 {result['is_correct']} 一致"
                
                # 属性6：必须记录答题时长
                assert practice_record.time_spent is not None, \
                    "练习记录必须包含答题时长"
                assert practice_record.time_spent == record_data['time_spent'], \
                    f"记录的答题时长 {practice_record.time_spent} 应该等于提交的时长 {record_data['time_spent']}"
            
            # 清理测试数据
            db.session.rollback()
    
    @given(session_data=practice_session_data())
    @settings(
        max_examples=20,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None
    )
    def test_property_wrong_question_auto_collection(self, app, session_data):
        """
        Feature: exam-system, Property 10: 错题自动收集
        
        属性：对于任意答错的题目，该题目应该自动出现在用户的错题本中
        
        Validates: Requirements 5.1
        """
        with app.app_context():
            # 创建测试用户
            import uuid
            unique_id = str(uuid.uuid4())[:8]
            user = User(
                username=f'proptest_{unique_id}',
                email=f'proptest_{unique_id}@example.com',
                nickname='Property Test User'
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.flush()
            
            wrong_question_ids = []
            
            # 为每个答题记录创建题目并提交答案
            for record_data in session_data:
                # 创建题目
                question = Question(
                    exam_type='civil_service',
                    question_type=record_data['question_type'],
                    subject='测试科目',
                    chapter='测试章节',
                    difficulty=3,
                    content='测试题目内容',
                    options={'A': '选项A', 'B': '选项B', 'C': '选项C', 'D': '选项D'},
                    correct_answer=record_data['correct_answer'],
                    explanation='测试解析',
                    created_by=user.id
                )
                db.session.add(question)
                db.session.flush()
                
                # 提交答案
                result = PracticeService.submit_answer(
                    user_id=user.id,
                    question_id=question.id,
                    user_answer=record_data['user_answer'],
                    time_spent=record_data['time_spent']
                )
                
                # 如果答错了，记录题目ID
                if not result['is_correct']:
                    wrong_question_ids.append(question.id)
            
            # 获取用户的错题本
            wrong_book = PracticeService.get_wrong_book(user.id)
            wrong_book_question_ids = [item['question']['id'] for item in wrong_book]
            
            # 属性：所有答错的题目都应该在错题本中
            for question_id in wrong_question_ids:
                assert question_id in wrong_book_question_ids, \
                    f"答错的题目 {question_id} 应该自动添加到错题本中"
            
            # 属性：错题本中的题目数量应该等于答错的题目数量（去重）
            unique_wrong_ids = list(set(wrong_question_ids))
            assert len(wrong_book) == len(unique_wrong_ids), \
                f"错题本中的题目数量 {len(wrong_book)} 应该等于答错的题目数量 {len(unique_wrong_ids)}"
            
            # 清理测试数据
            db.session.rollback()
    
    @given(
        initial_wrong_count=st.integers(min_value=1, max_value=5),
        correct_attempts=st.integers(min_value=1, max_value=3)
    )
    @settings(
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None
    )
    def test_property_wrong_book_mastery_update(self, app, initial_wrong_count, correct_attempts):
        """
        Feature: exam-system, Property 11: 错题本答对更新掌握状态
        
        属性：对于任意错题本中的题目，当用户答对时掌握状态应该更新为已掌握
        
        Validates: Requirements 5.3
        """
        with app.app_context():
            # 创建测试用户
            import uuid
            unique_id = str(uuid.uuid4())[:8]
            user = User(
                username=f'proptest_{unique_id}',
                email=f'proptest_{unique_id}@example.com',
                nickname='Property Test User'
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.flush()
            
            # 创建题目
            question = Question(
                exam_type='civil_service',
                question_type='single_choice',
                subject='测试科目',
                chapter='测试章节',
                difficulty=3,
                content='测试题目内容',
                options={'A': '选项A', 'B': '选项B', 'C': '选项C', 'D': '选项D'},
                correct_answer='A',
                explanation='测试解析',
                created_by=user.id
            )
            db.session.add(question)
            db.session.flush()
            
            # 先答错几次，确保题目进入错题本
            for _ in range(initial_wrong_count):
                PracticeService.submit_answer(
                    user_id=user.id,
                    question_id=question.id,
                    user_answer='B',  # 错误答案
                    time_spent=10
                )
            
            # 验证题目在错题本中且未掌握
            wrong_question = WrongQuestion.query.filter_by(
                user_id=user.id,
                question_id=question.id
            ).first()
            
            assert wrong_question is not None, "题目应该在错题本中"
            assert wrong_question.mastered == False, "初始状态应该是未掌握"
            assert wrong_question.wrong_count == initial_wrong_count, \
                f"错误次数应该是 {initial_wrong_count}"
            
            # 现在答对题目
            for attempt in range(correct_attempts):
                result = PracticeService.submit_answer(
                    user_id=user.id,
                    question_id=question.id,
                    user_answer='A',  # 正确答案
                    time_spent=10
                )
                
                assert result['is_correct'] == True, "答案应该是正确的"
                
                # 重新查询错题记录
                wrong_question = WrongQuestion.query.filter_by(
                    user_id=user.id,
                    question_id=question.id
                ).first()
                
                # 属性：答对后，掌握状态应该更新为True
                assert wrong_question.mastered == True, \
                    f"第 {attempt + 1} 次答对后，掌握状态应该更新为已掌握"
            
            # 清理测试数据
            db.session.rollback()
