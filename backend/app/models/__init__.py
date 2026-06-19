"""数据模型包"""
# 导入所有模型以便 Flask-Migrate 能够检测到
from .user import User
from .question import Question
from .exam import ExamPaper, ExamPaperQuestion, ExamSession, ExamResult
from .practice import PracticeRecord, WrongQuestion
from .statistics import StudyStatistics
from .graduate_school import GraduateSchool, GraduateMajor, ScoreLine, ExamSubject
from .study_plan import StudyPlan, StudyGoal, StudyReminder
from .note import QuestionNote, QuestionBookmark
from .achievement import Achievement, UserAchievement, UserPoints, PointTransaction, DailyTask

__all__ = [
    'User', 'Question', 
    'ExamPaper', 'ExamPaperQuestion', 'ExamSession', 'ExamResult',
    'PracticeRecord', 'WrongQuestion',
    'StudyStatistics',
    'GraduateSchool', 'GraduateMajor', 'ScoreLine', 'ExamSubject',
    'StudyPlan', 'StudyGoal', 'StudyReminder',
    'QuestionNote', 'QuestionBookmark',
    'Achievement', 'UserAchievement', 'UserPoints', 'PointTransaction', 'DailyTask'
]
