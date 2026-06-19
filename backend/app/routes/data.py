"""数据导入导出 API 路由"""
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required
from io import BytesIO
from datetime import datetime

from app.services import DataService
from app.utils.decorators import admin_required

data_bp = Blueprint('data', __name__)


@data_bp.route('/export/json', methods=['GET'])
@jwt_required()
@admin_required
def export_json():
    """导出数据为 JSON 格式
    
    Returns:
        JSON 文件下载
    """
    try:
        json_data = DataService.export_to_json()

        # 创建文件对象
        buffer = BytesIO()
        buffer.write(json_data.encode('utf-8'))
        buffer.seek(0)

        filename = f'exam_data_export_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.json'

        return send_file(
            buffer,
            mimetype='application/json',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'EXPORT_FAILED',
                'message': '数据导出失败',
                'details': str(e)
            }
        }), 500


@data_bp.route('/export/sql', methods=['GET'])
@jwt_required()
@admin_required
def export_sql():
    """导出数据为 SQL 格式
    
    Returns:
        SQL 文件下载
    """
    try:
        sql_data = DataService.export_to_sql()

        # 创建文件对象
        buffer = BytesIO()
        buffer.write(sql_data.encode('utf-8'))
        buffer.seek(0)

        filename = f'exam_data_export_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.sql'

        return send_file(
            buffer,
            mimetype='text/plain',
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'EXPORT_FAILED',
                'message': '数据导出失败',
                'details': str(e)
            }
        }), 500


@data_bp.route('/import/json', methods=['POST'])
@jwt_required()
@admin_required
def import_json():
    """从 JSON 格式导入数据
    
    Request Body:
        - file: JSON 文件
        - clear_existing: 是否清空现有数据（可选，默认 false）
    
    Returns:
        导入统计信息
    """
    try:
        # 检查文件
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_FILE',
                    'message': '缺少文件',
                    'details': '请上传 JSON 文件'
                }
            }), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({
                'success': False,
                'error': {
                    'code': 'EMPTY_FILENAME',
                    'message': '文件名为空',
                    'details': '请选择有效的文件'
                }
            }), 400

        # 读取文件内容
        json_data = file.read().decode('utf-8')

        # 获取参数
        clear_existing = request.form.get('clear_existing', 'false').lower() == 'true'

        # 导入数据
        import_stats = DataService.import_from_json(json_data, clear_existing)

        return jsonify({
            'success': True,
            'message': '数据导入成功',
            'data': {
                'import_stats': import_stats,
                'clear_existing': clear_existing
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'IMPORT_FAILED',
                'message': '数据导入失败',
                'details': str(e)
            }
        }), 500


@data_bp.route('/import/sql', methods=['POST'])
@jwt_required()
@admin_required
def import_sql():
    """从 SQL 格式导入数据
    
    Request Body:
        - file: SQL 文件
    
    Returns:
        导入统计信息
    """
    try:
        # 检查文件
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_FILE',
                    'message': '缺少文件',
                    'details': '请上传 SQL 文件'
                }
            }), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({
                'success': False,
                'error': {
                    'code': 'EMPTY_FILENAME',
                    'message': '文件名为空',
                    'details': '请选择有效的文件'
                }
            }), 400

        # 读取文件内容
        sql_data = file.read().decode('utf-8')

        # 导入数据
        import_stats = DataService.import_from_sql(sql_data)

        return jsonify({
            'success': True,
            'message': '数据导入成功',
            'data': {
                'import_stats': import_stats
            }
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'IMPORT_FAILED',
                'message': '数据导入失败',
                'details': str(e)
            }
        }), 500
