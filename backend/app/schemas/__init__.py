"""数据验证模式"""
from app.schemas.user_schema import (
    UserRegistrationSchema,
    UserLoginSchema,
    UserUpdateSchema,
    PasswordChangeSchema,
    PasswordResetSchema
)
from app.schemas.question_schema import (
    QuestionCreateSchema,
    QuestionUpdateSchema,
    QuestionFilterSchema
)
from app.schemas.exam_schema import (
    ExamPaperCreateSchema,
    ExamPaperUpdateSchema,
    ExamPaperQuestionSchema,
    ExamAnswerSubmitSchema,
    PracticeStartSchema,
    PracticeAnswerSubmitSchema
)

__all__ = [
    # User schemas
    'UserRegistrationSchema',
    'UserLoginSchema',
    'UserUpdateSchema',
    'PasswordChangeSchema',
    'PasswordResetSchema',
    # Question schemas
    'QuestionCreateSchema',
    'QuestionUpdateSchema',
    'QuestionFilterSchema',
    # Exam schemas
    'ExamPaperCreateSchema',
    'ExamPaperUpdateSchema',
    'ExamPaperQuestionSchema',
    'ExamAnswerSubmitSchema',
    'PracticeStartSchema',
    'PracticeAnswerSubmitSchema',
]
