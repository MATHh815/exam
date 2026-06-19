"""Flask 应用工厂"""
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_marshmallow import Marshmallow

from config import config

# 初始化扩展
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
ma = Marshmallow()


def create_app(config_name=None):
    """应用工厂函数
    
    Args:
        config_name: 配置名称 ('development', 'production', 'testing')
    
    Returns:
        Flask 应用实例
    """
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # CORS 配置 - 支持通配符
    cors_origins = app.config['CORS_ORIGINS']
    if cors_origins == ['*'] or '*' in cors_origins:
        CORS(app, supports_credentials=True)
    else:
        CORS(app, origins=cors_origins, supports_credentials=True)
    
    ma.init_app(app)
    
    # 导入所有模型（确保Flask-Migrate能够检测到）
    with app.app_context():
        from app import models
    
    # 配置日志
    setup_logging(app)
    
    # 注册蓝图
    register_blueprints(app)
    
    # 注册错误处理器
    register_error_handlers(app)
    
    # 注册 JWT 回调
    register_jwt_callbacks(app)
    
    return app


def setup_logging(app):
    """配置日志系统"""
    # 创建日志目录
    log_dir = os.path.dirname(app.config['LOG_FILE'])
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 日志格式
    log_format = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s - %(message)s '
        '[in %(pathname)s:%(lineno)d]'
    )
    
    # 文件日志处理器 - 所有日志
    file_handler = RotatingFileHandler(
        app.config['LOG_FILE'],
        maxBytes=10240000,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(log_format)
    file_handler.setLevel(getattr(logging, app.config['LOG_LEVEL']))
    
    # 错误日志处理器 - 仅错误
    error_log_file = app.config['LOG_FILE'].replace('.log', '_error.log')
    error_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=10240000,  # 10MB
        backupCount=10
    )
    error_handler.setFormatter(log_format)
    error_handler.setLevel(logging.ERROR)
    
    # 控制台日志处理器（开发环境）
    if app.debug:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_format)
        console_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(console_handler)
    
    # 添加处理器
    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_handler)
    
    # 设置日志级别
    app.logger.setLevel(getattr(logging, app.config['LOG_LEVEL']))
    
    # 记录启动信息
    app.logger.info('=' * 50)
    app.logger.info('考试系统启动')
    app.logger.info(f'环境: {app.config.get("ENV", "unknown")}')
    app.logger.info(f'调试模式: {app.debug}')
    app.logger.info(f'数据库: {app.config["SQLALCHEMY_DATABASE_URI"]}')
    app.logger.info('=' * 50)
    
    # 记录请求日志
    @app.before_request
    def log_request():
        """记录请求信息"""
        from flask import request
        app.logger.debug(f'请求: {request.method} {request.path}')
        # 只在有 JSON 数据时记录
        if request.is_json and request.method in ['POST', 'PUT', 'PATCH']:
            try:
                data = request.get_json()
                if data:
                    # 不记录敏感信息
                    data_copy = data.copy()
                    if 'password' in data_copy:
                        data_copy['password'] = '***'
                    if 'old_password' in data_copy:
                        data_copy['old_password'] = '***'
                    if 'new_password' in data_copy:
                        data_copy['new_password'] = '***'
                    app.logger.debug(f'请求数据: {data_copy}')
            except Exception:
                pass  # 忽略 JSON 解析错误
    
    @app.after_request
    def log_response(response):
        """记录响应信息"""
        from flask import request
        app.logger.debug(
            f'响应: {request.method} {request.path} - '
            f'状态码: {response.status_code}'
        )
        return response


def register_blueprints(app):
    """注册蓝图"""
    from flask import jsonify
    
    # 健康检查端点
    @app.route('/health')
    def health_check():
        return jsonify({
            'success': True,
            'message': '考试系统运行正常',
            'version': '1.0.0'
        })
    
    @app.route('/api')
    def api_info():
        return jsonify({
            'success': True,
            'message': 'API 服务运行正常',
            'endpoints': {
                'auth': '/api/auth',
                'questions': '/api/questions',
                'practice': '/api/practice',
                'exams': '/api/exams',
                'statistics': '/api/statistics',
                'data': '/api/data',
                'graduate': '/api/graduate',
                'study_plans': '/api/study-plans',
                'reminders': '/api/reminders'
            }
        })
    
    # 导入并注册蓝图
    from app.routes.auth import auth_bp
    from app.routes.questions import questions_bp
    from app.routes.practice import practice_bp
    from app.routes.exams import exams_bp
    from app.routes.statistics import statistics_bp
    from app.routes.data import data_bp
    from app.routes.graduate import graduate_bp
    from app.routes.study_plans import study_plans_bp
    from app.routes.reminders import reminders_bp
    from app.routes.notes import notes_bp
    from app.routes.bookmarks import bookmarks_bp
    from app.routes.export import export_bp
    from app.routes.points import points_bp
    from app.routes.achievements import achievements_bp
    from app.routes.daily_tasks import daily_tasks_bp
    # from app.routes.wrong_analysis import wrong_analysis_bp  # 暂时注释，修复导入问题
    from app.routes.pomodoro import pomodoro_bp
    # from app.routes.knowledge_graph import knowledge_graph_bp  # 暂时注释，缺少 KnowledgePoint 模型
    from app.routes.study_schedules import study_schedules_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(questions_bp, url_prefix='/api/questions')
    app.register_blueprint(practice_bp, url_prefix='/api/practice')
    app.register_blueprint(exams_bp, url_prefix='/api/exams')
    app.register_blueprint(statistics_bp, url_prefix='/api/statistics')
    app.register_blueprint(data_bp, url_prefix='/api/data')
    app.register_blueprint(graduate_bp, url_prefix='/api/graduate')
    app.register_blueprint(study_plans_bp, url_prefix='/api/study-plans')
    app.register_blueprint(reminders_bp)
    app.register_blueprint(notes_bp, url_prefix='/api/notes')
    app.register_blueprint(bookmarks_bp, url_prefix='/api/bookmarks')
    app.register_blueprint(export_bp)  # export_bp 已经包含 url_prefix
    app.register_blueprint(points_bp)  # points_bp 已经包含 url_prefix
    app.register_blueprint(achievements_bp)  # achievements_bp 已经包含 url_prefix
    app.register_blueprint(daily_tasks_bp)  # daily_tasks_bp 已经包含 url_prefix
    # app.register_blueprint(wrong_analysis_bp)  # 暂时注释，修复导入问题
    app.register_blueprint(pomodoro_bp)  # pomodoro_bp 已经包含 url_prefix
    # app.register_blueprint(knowledge_graph_bp)  # 暂时注释，缺少 KnowledgePoint 模型
    app.register_blueprint(study_schedules_bp, url_prefix='/api/study-schedules')


def register_error_handlers(app):
    """注册错误处理器"""
    from flask import jsonify
    from datetime import datetime
    from sqlalchemy.exc import SQLAlchemyError
    from app.utils.exceptions import APIException
    
    @app.errorhandler(APIException)
    def handle_api_exception(error):
        """处理自定义 API 异常"""
        app.logger.warning(f'API 异常: {error.code} - {error.message}')
        response = {
            'success': False,
            'error': {
                'code': error.code,
                'message': error.message
            },
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        if error.details:
            response['error']['details'] = error.details
        return jsonify(response), error.status_code
    
    @app.errorhandler(SQLAlchemyError)
    def handle_database_error(error):
        """处理数据库错误"""
        db.session.rollback()
        app.logger.error(f'数据库错误: {error}')
        return jsonify({
            'success': False,
            'error': {
                'code': 'DATABASE_ERROR',
                'message': '数据库操作失败',
                'details': '请稍后重试'
            },
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        """处理 400 错误"""
        app.logger.warning(f'请求错误: {error}')
        return jsonify({
            'success': False,
            'error': {
                'code': 'BAD_REQUEST',
                'message': '请求参数错误',
                'details': str(error)
            },
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        """处理 401 错误"""
        return jsonify({
            'success': False,
            'error': {
                'code': 'UNAUTHORIZED',
                'message': '未授权访问',
                'details': str(error)
            },
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        """处理 403 错误"""
        return jsonify({
            'success': False,
            'error': {
                'code': 'FORBIDDEN',
                'message': '禁止访问',
                'details': str(error)
            },
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 403
    
    @app.errorhandler(404)
    def not_found(error):
        """处理 404 错误"""
        return jsonify({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': '资源不存在',
                'details': str(error)
            },
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        """处理 405 错误"""
        return jsonify({
            'success': False,
            'error': {
                'code': 'METHOD_NOT_ALLOWED',
                'message': '请求方法不允许',
                'details': str(error)
            },
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 405
    
    @app.errorhandler(409)
    def conflict(error):
        """处理 409 错误"""
        return jsonify({
            'success': False,
            'error': {
                'code': 'CONFLICT',
                'message': '资源冲突',
                'details': str(error)
            },
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 409
    
    @app.errorhandler(500)
    def internal_error(error):
        """处理 500 错误"""
        db.session.rollback()
        app.logger.error(f'服务器错误: {error}', exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '服务器内部错误',
                'details': '请联系管理员'
            },
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        """处理未预期的异常"""
        db.session.rollback()
        app.logger.error(f'未预期的错误: {error}', exc_info=True)
        return jsonify({
            'success': False,
            'error': {
                'code': 'UNEXPECTED_ERROR',
                'message': '发生未预期的错误',
                'details': '请联系管理员'
            },
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 500


def register_jwt_callbacks(app):
    """注册 JWT 回调函数"""
    from flask import jsonify
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'success': False,
            'error': {
                'code': 'TOKEN_EXPIRED',
                'message': '令牌已过期',
                'details': '请刷新令牌'
            }
        }), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_TOKEN',
                'message': '无效的令牌',
                'details': str(error)
            }
        }), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'success': False,
            'error': {
                'code': 'MISSING_TOKEN',
                'message': '缺少令牌',
                'details': '请提供有效的访问令牌'
            }
        }), 401
