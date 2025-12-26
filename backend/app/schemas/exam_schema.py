"""考试相关的数据验证模式"""
from marshmallow import Schema, fields, validates, ValidationError, validate


class ExamPaperCreateSchema(Schema):
    """试卷创建验证模式"""
    
    name = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    exam_type = fields.Str(
        required=True,
        validate=validate.OneOf(['civil_service', 'postgraduate', 'public_institution'])
    )
    description = fields.Str()
    duration = fields.Int(required=True, validate=validate.Range(min=1))
    total_score = fields.Int(required=True, validate=validate.Range(min=1))
    pass_score = fields.Int(validate=validate.Range(min=0))


class ExamPaperUpdateSchema(Schema):
    """试卷更新验证模式"""
    
    name = fields.Str(validate=validate.Length(min=1, max=200))
    exam_type = fields.Str(
        validate=validate.OneOf(['civil_service', 'postgraduate', 'public_institution'])
    )
    description = fields.Str()
    duration = fields.Int(validate=validate.Range(min=1))
    total_score = fields.Int(validate=validate.Range(min=1))
    pass_score = fields.Int(validate=validate.Range(min=0))


class ExamPaperQuestionSchema(Schema):
    """试卷题目验证模式"""
    
    question_id = fields.Int(required=True)
    order = fields.Int(required=True, validate=validate.Range(min=1))
    score = fields.Int(required=True, validate=validate.Range(min=1))


class ExamAnswerSubmitSchema(Schema):
    """考试答案提交验证模式"""
    
    question_id = fields.Int(required=True)
    answer = fields.Str(required=True)


class PracticeStartSchema(Schema):
    """练习开始验证模式"""
    
    exam_type = fields.Str(
        validate=validate.OneOf(['civil_service', 'postgraduate', 'public_institution'])
    )
    question_type = fields.Str(
        validate=validate.OneOf(['single_choice', 'multiple_choice', 'true_false', 'fill_blank', 'essay'])
    )
    subject = fields.Str()
    chapter = fields.Str()
    difficulty = fields.Int(validate=validate.Range(min=1, max=5))
    count = fields.Int(validate=validate.Range(min=1, max=100))


class PracticeAnswerSubmitSchema(Schema):
    """练习答案提交验证模式"""
    
    question_id = fields.Int(required=True)
    answer = fields.Str(required=True)
