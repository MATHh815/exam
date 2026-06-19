/**
 * 知识点关系图谱 API
 */
import request from '@/utils/request'

/**
 * 获取知识点关系图谱数据
 */
export function getGraphData(params) {
  return request({
    url: '/api/knowledge-graph/data',
    method: 'get',
    params
  })
}

/**
 * 获取知识点详情
 */
export function getKnowledgeDetail(knowledgePointId) {
  return request({
    url: `/api/knowledge-graph/detail/${knowledgePointId}`,
    method: 'get'
  })
}

/**
 * 获取推荐学习路径
 */
export function getLearningPath(params) {
  return request({
    url: '/api/knowledge-graph/path',
    method: 'get',
    params
  })
}

/**
 * 更新知识点掌握度
 */
export function updateMastery(data) {
  return request({
    url: '/api/knowledge-graph/mastery/update',
    method: 'post',
    data
  })
}
