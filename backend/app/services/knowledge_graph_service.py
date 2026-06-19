"""
知识点关系图谱服务
"""
import json
from datetime import datetime
from sqlalchemy import func, and_, or_
from app import db
from app.models.knowledge_point import KnowledgePoint
from app.models.knowledge_graph import KnowledgeRelation, UserKnowledgeMastery
from app.models.practice import PracticeRecord

class KnowledgeGraphService:
    """知识点关系图谱服务类"""
    
    @staticmethod
    def get_graph_data(user_id, subject=None, chapter=None, min_mastery=None, max_mastery=None):
        """
        获取知识点关系图谱数据
        
        Args:
            user_id: 用户ID
            subject: 科目筛选
            chapter: 章节筛选
            min_mastery: 最小掌握度
            max_mastery: 最大掌握度
            
        Returns:
            dict: 图谱数据（nodes, edges, categories）
        """
        # 构建查询条件
        query = KnowledgePoint.query
        
        if subject:
            query = query.filter(KnowledgePoint.subject == subject)
        if chapter:
            query = query.filter(KnowledgePoint.chapter == chapter)
        
        knowledge_points = query.all()
        
        # 获取用户掌握度数据
        mastery_dict = KnowledgeGraphService._get_user_mastery_dict(user_id)
        
        # 构建节点数据
        nodes = []
        for kp in knowledge_points:
            mastery = mastery_dict.get(kp.id, {})
            mastery_score = mastery.get('mastery_score', 0)
            
            # 掌握度筛选
            if min_mastery is not None and mastery_score < min_mastery:
                continue
            if max_mastery is not None and mastery_score > max_mastery:
                continue
            
            # 获取题目数量
            question_count = len(kp.questions) if hasattr(kp, 'questions') else 0
            
            nodes.append({
                'id': f'kp_{kp.id}',
                'name': kp.name,
                'category': KnowledgeGraphService._get_category(mastery_score),
                'mastery': round(mastery_score, 2),
                'importance': KnowledgeGraphService._calculate_importance(kp),
                'subject': kp.subject,
                'chapter': kp.chapter,
                'difficulty': kp.difficulty,
                'questionCount': question_count,
                'practiceCount': mastery.get('practice_count', 0),
                'correctRate': mastery.get('correct_rate', 0),
                'value': mastery_score  # 用于节点大小
            })
        
        # 获取知识点ID集合
        kp_ids = [kp.id for kp in knowledge_points]
        
        # 构建边数据
        edges = []
        relations = KnowledgeRelation.query.filter(
            and_(
                KnowledgeRelation.source_id.in_(kp_ids),
                KnowledgeRelation.target_id.in_(kp_ids)
            )
        ).all()
        
        for rel in relations:
            edges.append({
                'source': f'kp_{rel.source_id}',
                'target': f'kp_{rel.target_id}',
                'type': rel.relation_type,
                'strength': rel.strength,
                'lineStyle': {
                    'width': rel.strength * 3,
                    'curveness': 0.2
                }
            })
        
        # 分类定义
        categories = [
            {'name': '未掌握', 'color': '#f56c6c'},
            {'name': '部分掌握', 'color': '#e6a23c'},
            {'name': '已掌握', 'color': '#67c23a'}
        ]
        
        return {
            'nodes': nodes,
            'edges': edges,
            'categories': categories
        }
    
    @staticmethod
    def get_knowledge_detail(user_id, knowledge_point_id):
        """
        获取知识点详情
        
        Args:
            user_id: 用户ID
            knowledge_point_id: 知识点ID
            
        Returns:
            dict: 知识点详情
        """
        kp = KnowledgePoint.query.get(knowledge_point_id)
        if not kp:
            return None
        
        # 获取掌握度
        mastery = UserKnowledgeMastery.query.filter_by(
            user_id=user_id,
            knowledge_point_id=knowledge_point_id
        ).first()
        
        # 获取相关题目
        questions = kp.questions if hasattr(kp, 'questions') else []
        
        # 获取前置知识点
        prerequisites = []
        for rel in kp.incoming_relations:
            if rel.relation_type == 'prerequisite':
                prerequisites.append({
                    'id': rel.source_id,
                    'name': rel.source.name,
                    'mastery': KnowledgeGraphService._get_mastery_score(user_id, rel.source_id)
                })
        
        # 获取后续知识点
        next_points = []
        for rel in kp.outgoing_relations:
            if rel.relation_type == 'prerequisite':
                next_points.append({
                    'id': rel.target_id,
                    'name': rel.target.name,
                    'mastery': KnowledgeGraphService._get_mastery_score(user_id, rel.target_id)
                })
        
        # 获取相关知识点
        related_points = []
        for rel in kp.outgoing_relations:
            if rel.relation_type == 'related':
                related_points.append({
                    'id': rel.target_id,
                    'name': rel.target.name,
                    'mastery': KnowledgeGraphService._get_mastery_score(user_id, rel.target_id)
                })
        
        return {
            'id': kp.id,
            'name': kp.name,
            'subject': kp.subject,
            'chapter': kp.chapter,
            'difficulty': kp.difficulty,
            'description': kp.description,
            'mastery': mastery.to_dict() if mastery else {
                'mastery_score': 0,
                'practice_count': 0,
                'correct_count': 0,
                'correct_rate': 0
            },
            'questionCount': len(questions),
            'prerequisites': prerequisites,
            'nextPoints': next_points,
            'relatedPoints': related_points
        }
    
    @staticmethod
    def get_learning_path(user_id, subject=None):
        """
        获取推荐学习路径
        
        Args:
            user_id: 用户ID
            subject: 科目筛选
            
        Returns:
            list: 推荐学习路径
        """
        # 获取所有知识点
        query = KnowledgePoint.query
        if subject:
            query = query.filter(KnowledgePoint.subject == subject)
        
        knowledge_points = query.all()
        
        # 获取用户掌握度
        mastery_dict = KnowledgeGraphService._get_user_mastery_dict(user_id)
        
        # 构建知识点评分
        kp_scores = []
        for kp in knowledge_points:
            mastery_score = mastery_dict.get(kp.id, {}).get('mastery_score', 0)
            
            # 计算推荐分数
            score = KnowledgeGraphService._calculate_recommendation_score(
                kp, mastery_score, mastery_dict
            )
            
            kp_scores.append({
                'id': kp.id,
                'name': kp.name,
                'subject': kp.subject,
                'chapter': kp.chapter,
                'difficulty': kp.difficulty,
                'mastery': round(mastery_score, 2),
                'score': score,
                'reason': KnowledgeGraphService._get_recommendation_reason(kp, mastery_score, mastery_dict)
            })
        
        # 按推荐分数排序
        kp_scores.sort(key=lambda x: x['score'], reverse=True)
        
        return kp_scores[:20]  # 返回前20个推荐
    
    @staticmethod
    def update_mastery(user_id, knowledge_point_id, is_correct):
        """
        更新知识点掌握度
        
        Args:
            user_id: 用户ID
            knowledge_point_id: 知识点ID
            is_correct: 是否正确
        """
        mastery = UserKnowledgeMastery.query.filter_by(
            user_id=user_id,
            knowledge_point_id=knowledge_point_id
        ).first()
        
        if not mastery:
            mastery = UserKnowledgeMastery(
                user_id=user_id,
                knowledge_point_id=knowledge_point_id
            )
            db.session.add(mastery)
        
        # 更新统计
        mastery.practice_count += 1
        if is_correct:
            mastery.correct_count += 1
        mastery.last_practice_date = datetime.utcnow()
        
        # 更新最近练习记录
        recent = json.loads(mastery.recent_practices) if mastery.recent_practices else []
        recent.append(1 if is_correct else 0)
        if len(recent) > 10:
            recent = recent[-10:]  # 只保留最近10次
        mastery.recent_practices = json.dumps(recent)
        
        # 重新计算掌握度
        mastery.mastery_score = KnowledgeGraphService._calculate_mastery_score(mastery, recent)
        
        db.session.commit()
    
    @staticmethod
    def _get_user_mastery_dict(user_id):
        """获取用户掌握度字典"""
        masteries = UserKnowledgeMastery.query.filter_by(user_id=user_id).all()
        return {
            m.knowledge_point_id: {
                'mastery_score': m.mastery_score,
                'practice_count': m.practice_count,
                'correct_count': m.correct_count,
                'correct_rate': round(m.correct_count / m.practice_count * 100, 2) if m.practice_count > 0 else 0
            }
            for m in masteries
        }
    
    @staticmethod
    def _get_mastery_score(user_id, knowledge_point_id):
        """获取单个知识点掌握度"""
        mastery = UserKnowledgeMastery.query.filter_by(
            user_id=user_id,
            knowledge_point_id=knowledge_point_id
        ).first()
        return round(mastery.mastery_score, 2) if mastery else 0
    
    @staticmethod
    def _calculate_mastery_score(mastery, recent_practices):
        """
        计算掌握度分数
        
        公式: mastery_score = correct_rate * 0.5 + practice_factor * 0.3 + recent_performance * 0.2
        """
        # 正确率
        correct_rate = mastery.correct_count / mastery.practice_count if mastery.practice_count > 0 else 0
        
        # 练习次数因子（0-1）
        practice_factor = min(mastery.practice_count / 20, 1.0)
        
        # 最近表现
        recent_performance = sum(recent_practices) / len(recent_practices) if recent_practices else 0
        
        # 综合评分
        score = (
            correct_rate * 0.5 +
            practice_factor * 0.3 +
            recent_performance * 0.2
        ) * 100
        
        return round(score, 2)
    
    @staticmethod
    def _calculate_importance(kp):
        """计算知识点重要程度"""
        # 基于出度（被多少知识点依赖）
        outgoing_count = len(kp.outgoing_relations) if hasattr(kp, 'outgoing_relations') else 0
        # 基于题目数量
        question_count = len(kp.questions) if hasattr(kp, 'questions') else 0
        
        return min(outgoing_count * 2 + question_count / 10, 10)
    
    @staticmethod
    def _get_category(mastery_score):
        """根据掌握度获取分类"""
        if mastery_score < 40:
            return '未掌握'
        elif mastery_score < 70:
            return '部分掌握'
        else:
            return '已掌握'
    
    @staticmethod
    def _calculate_recommendation_score(kp, mastery_score, mastery_dict):
        """
        计算推荐分数
        
        优先级:
        1. 前置知识点已掌握
        2. 当前知识点未掌握
        3. 重要程度高
        4. 难度适中
        """
        score = 0
        
        # 未掌握的知识点优先（0-40分）
        if mastery_score < 40:
            score += 40
        elif mastery_score < 70:
            score += 20
        else:
            score += 5  # 已掌握的也可以复习
        
        # 检查前置知识点（0-30分）
        prerequisites_mastered = 0
        prerequisites_total = 0
        for rel in kp.incoming_relations:
            if rel.relation_type == 'prerequisite':
                prerequisites_total += 1
                prereq_mastery = mastery_dict.get(rel.source_id, {}).get('mastery_score', 0)
                if prereq_mastery >= 70:
                    prerequisites_mastered += 1
        
        if prerequisites_total > 0:
            score += (prerequisites_mastered / prerequisites_total) * 30
        else:
            score += 30  # 没有前置要求，可以直接学习
        
        # 重要程度（0-20分）
        importance = KnowledgeGraphService._calculate_importance(kp)
        score += importance * 2
        
        # 难度适中（0-10分）
        if kp.difficulty == 'medium':
            score += 10
        elif kp.difficulty == 'easy':
            score += 8
        else:
            score += 5
        
        return round(score, 2)
    
    @staticmethod
    def _get_recommendation_reason(kp, mastery_score, mastery_dict):
        """获取推荐理由"""
        reasons = []
        
        if mastery_score < 40:
            reasons.append('尚未掌握')
        elif mastery_score < 70:
            reasons.append('需要加强')
        
        # 检查前置知识点
        all_prerequisites_met = True
        for rel in kp.incoming_relations:
            if rel.relation_type == 'prerequisite':
                prereq_mastery = mastery_dict.get(rel.source_id, {}).get('mastery_score', 0)
                if prereq_mastery < 70:
                    all_prerequisites_met = False
                    break
        
        if all_prerequisites_met:
            reasons.append('前置知识已掌握')
        else:
            reasons.append('建议先学习前置知识')
        
        if KnowledgeGraphService._calculate_importance(kp) >= 5:
            reasons.append('重要知识点')
        
        return '、'.join(reasons) if reasons else '推荐学习'
