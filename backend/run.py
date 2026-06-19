"""应用启动脚本"""
import os
from app import create_app, db

# 创建应用实例
app = create_app(os.getenv('FLASK_ENV', 'development'))


@app.shell_context_processor
def make_shell_context():
    """为 Flask shell 提供上下文"""
    from app.models import (
        User, Question, 
        ExamPaper, ExamPaperQuestion, ExamSession, ExamResult,
        PracticeRecord, WrongQuestion,
        StudyStatistics
    )
    
    return {
        'db': db,
        'User': User,
        'Question': Question,
        'ExamPaper': ExamPaper,
        'ExamPaperQuestion': ExamPaperQuestion,
        'ExamSession': ExamSession,
        'ExamResult': ExamResult,
        'PracticeRecord': PracticeRecord,
        'WrongQuestion': WrongQuestion,
        'StudyStatistics': StudyStatistics
    }


@app.cli.command()
def init_db():
    """初始化数据库"""
    db.create_all()
    print('数据库初始化完成')


@app.cli.command()
def test():
    """运行测试"""
    import pytest
    pytest.main(['-v', 'tests/'])


if __name__ == '__main__':
    # 禁用 reloader 以避免 watchdog 版本冲突问题
    # 如果需要自动重载，请升级 watchdog: pip install --upgrade watchdog
    # 监听所有接口，允许局域网访问
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
