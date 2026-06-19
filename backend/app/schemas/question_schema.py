"""题目相关的数据验证模式"""
from marshmallow import Schema, fields, validates, ValidationError, validate


class QuestionCreateSchema(Schema):
    """题目创建验证模式"""
    
    exam_type = fields.Str(
        required=True,
        validate=validate.OneOf(['civil_service', 'postgraduate', 'public_institution'])
    )
    question_type = fields.Str(
        required=True,
        validate=validate.OneOf(['single_choice', 'multiple_choice', 'true_false', 'fill_blank', 'essay'])
    )
    subject = fields.Str(validate=validate.Length(max=50))
    chapter = fields.Str(validate=validate.Length(max=100))
    difficulty = fields.Int(validate=validate.Range(min=1, max=5))
    content = fields.Str(required=True, validate=validate.Length(min=1))
    options = fields.Dict()
    correct_answer = fields.Str(required=True)
    explanation = fields.Str()
    tags = fields.List(fields.Str())


class QuestionUpdateSchema(Schema):
    """题目更新验证模式"""
    
    exam_type = fields.Str(
        validate=validate.OneOf(['civil_service', 'postgraduate', 'public_institution'])
    )
    question_type = fields.Str(
        validate=validate.OneOf(['single_choice', 'multiple_choice', 'true_false', 'fill_blank', 'essay'])
    )
    subject = fields.Str(validate=validate.Length(max=50))
    chapter = fields.Str(validate=validate.Length(max=100))
    difficulty = fields.Int(validate=validate.Range(min=1, max=5))
    content = fields.Str(validate=validate.Length(min=1))
    options = fields.Dict()
    correct_answer = fields.Str()
    explanation = fields.Str()
    tags = fields.List(fields.Str())


class QuestionFilterSchema(Schema):
    """题目筛选验证模式"""
    
    exam_type = fields.Str(
        validate=validate.OneOf(['civil_service', 'postgraduate', 'public_institution'])
    )
    question_type = fields.Str(
        validate=validate.OneOf(['single_choice', 'multiple_choice', 'true_false', 'fill_blank', 'essay'])
    )
    subject = fields.Str()
    chapter = fields.Str()
    difficulty = fields.Int(validate=validate.Range(min=1, max=5))
    tags = fields.List(fields.Str())
    page = fields.Int(validate=validate.Range(min=1))
    page_size = fields.Int(validate=validate.Range(min=1, max=100))
