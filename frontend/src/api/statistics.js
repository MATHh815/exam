/**
 * 统计相关 API
 */
import request from '../utils/request'

/**
 * 获取学习概览统计
 * @param {Object} params - 查询参数
 * @param {string} [params.start_date] - 开始日期（格式：YYYY-MM-DD）
 * @param {string} [params.end_date] - 结束日期（格式：YYYY-MM-DD）
 * @returns {Promise} 学习概览数据
 */
export function getOverview(params) {
  return request({
    url: '/statistics/overview',
    method: 'get',
    params
  })
}

/**
 * 获取知识点分析
 * @param {Object} params - 查询参数
 * @param {string} [params.start_date] - 开始日期（格式：YYYY-MM-DD）
 * @param {string} [params.end_date] - 结束日期（格式：YYYY-MM-DD）
 * @returns {Promise} 知识点分析数据
 */
export function getKnowledgeAnalysis(params) {
  return request({
    url: '/statistics/knowledge',
    method: 'get',
    params
  })
}

/**
 * 获取学习趋势
 * @param {Object} params - 查询参数
 * @param {number} [params.days=7] - 天数（默认7天，最多365天）
 * @returns {Promise} 学习趋势数据
 */
export function getTrend(params) {
  return request({
    url: '/statistics/trend',
    method: 'get',
    params
  })
}

/**
 * 获取考试历史统计
 * @param {Object} params - 查询参数
 * @param {string} [params.start_date] - 开始日期（格式：YYYY-MM-DD）
 * @param {string} [params.end_date] - 结束日期（格式：YYYY-MM-DD）
 * @returns {Promise} 考试统计数据
 */
export function getExamStatistics(params) {
  return request({
    url: '/statistics/exams',
    method: 'get',
    params
  })
}
