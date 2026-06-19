"""
笔记导出路由
"""
from flask import Blueprint, request, jsonify, send_file
from io import BytesIO

from app.services.export_service import ExportService
from app.utils.decorators import jwt_required_with_user

export_bp = Blueprint('export', __name__, url_prefix='/api/notes')

export_service = ExportService()


@export_bp.route('/export', methods=['POST'])
@jwt_required_with_user
def export_notes(current_user):
    """
    导出笔记
    
    请求体:
    {
        "format": "pdf" | "markdown",
        "note_ids": [1, 2, 3],  // 可选
        "filters": {            // 可选
            "subject": "行测",
            "chapter": "数量关系",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        }
    }
    
    返回: 文件下载
    """
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data or 'format' not in data:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'MISSING_REQUIRED_FIELD',
                    'message': '缺少必填字段: format'
                }
            }), 400
        
        export_format = data['format']
        note_ids = data.get('note_ids')
        filters = data.get('filters')
        
        # 验证导出格式
        if export_format not in ['pdf', 'markdown']:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'INVALID_FORMAT',
                    'message': '不支持的导出格式，支持: pdf, markdown'
                }
            }), 400
        
        # 生成导出文件
        result = export_service.generate_download_link(
            user_id=current_user.id,
            export_format=export_format,
            note_ids=note_ids,
            filters=filters
        )
        
        # 返回文件
        if export_format == 'pdf':
            return send_file(
                result['content'],
                mimetype=result['content_type'],
                as_attachment=True,
                download_name=result['filename']
            )
        else:
            # Markdown 返回文本
            content = result['content']
            buffer = BytesIO(content.encode('utf-8'))
            return send_file(
                buffer,
                mimetype=result['content_type'],
                as_attachment=True,
                download_name=result['filename']
            )
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'EXPORT_ERROR',
                'message': str(e)
            }
        }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': f'导出失败: {str(e)}'
            }
        }), 500


@export_bp.route('/export/preview', methods=['POST'])
@jwt_required_with_user
def preview_export(current_user):
    """
    预览导出内容（仅 Markdown）
    
    请求体: 同 export_notes
    
    返回:
    {
        "success": true,
        "content": "markdown 内容",
        "note_count": 10
    }
    """
    try:
        data = request.get_json()
        
        note_ids = data.get('note_ids')
        filters = data.get('filters')
        
        # 导出为 Markdown
        content = export_service.export_notes_to_markdown(
            user_id=current_user.id,
            note_ids=note_ids,
            filters=filters
        )
        
        # 统计笔记数量
        note_count = content.count('## 笔记')
        
        return jsonify({
            'success': True,
            'content': content,
            'note_count': note_count
        })
    
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'EXPORT_ERROR',
                'message': str(e)
            }
        }), 400
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': f'预览失败: {str(e)}'
            }
        }), 500
