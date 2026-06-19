"""
知识点关系图谱路由
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.knowledge_graph_service import KnowledgeGraphService

knowledge_graph_bp = Blueprint('knowledge_graph', __name__, url_prefix='/api/knowledge-graph')

@knowledge_graph_bp.route('/data', methods=['GET'])
@jwt_required()
def get_graph_data():
    """获取知识点关系图谱数据"""
    try:
        current_user_id = get_jwt_identity()
        subject = request.args.get('subject')
        chapter = request.args.get('chapter')
        min_mastery = request.args.get('min_mastery', type=float)
        max_mastery = request.args.get('max_mastery', type=float)
        
        data = KnowledgeGraphService.get_graph_data(
            user_id=current_user_id,
            subject=subject,
            chapter=chapter,
            min_mastery=min_mastery,
            max_mastery=max_mastery
        )
        
        return jsonify({
            'success': True,
            'data': data
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取图谱数据失败: {str(e)}'
        }), 500

@knowledge_graph_bp.route('/detail/<int:knowledge_point_id>', methods=['GET'])
@jwt_required()
def get_knowledge_detail(knowledge_point_id):
    """获取知识点详情"""
    try:
        current_user_id = get_jwt_identity()
        detail = KnowledgeGraphService.get_knowledge_detail(
            user_id=current_user_id,
            knowledge_point_id=knowledge_point_id
        )
        
        if not detail:
            return jsonify({
                'success': False,
                'message': '知识点不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'data': detail
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取知识点详情失败: {str(e)}'
        }), 500

@knowledge_graph_bp.route('/path', methods=['GET'])
@jwt_required()
def get_learning_path():
    """获取推荐学习路径"""
    try:
        current_user_id = get_jwt_identity()
        subject = request.args.get('subject')
        
        path = KnowledgeGraphService.get_learning_path(
            user_id=current_user_id,
            subject=subject
        )
        
        return jsonify({
            'success': True,
            'data': path
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取学习路径失败: {str(e)}'
        }), 500

@knowledge_graph_bp.route('/mastery/update', methods=['POST'])
@jwt_required()
def update_mastery():
    """更新知识点掌握度"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        knowledge_point_id = data.get('knowledge_point_id')
        is_correct = data.get('is_correct', False)
        
        if not knowledge_point_id:
            return jsonify({
                'success': False,
                'message': '缺少知识点ID'
            }), 400
        
        KnowledgeGraphService.update_mastery(
            user_id=current_user_id,
            knowledge_point_id=knowledge_point_id,
            is_correct=is_correct
        )
        
        return jsonify({
            'success': True,
            'message': '掌握度更新成功'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'更新掌握度失败: {str(e)}'
        }), 500
