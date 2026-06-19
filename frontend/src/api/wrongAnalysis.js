/**
 * 错题分析 API
 */
import request from '../utils/request'

/**
 * 获取错题概览
 * @param {Object} params - 查询参数
 * @param {number} params.days - 统计天数（默认30天）
 * @returns {Promise}
 */
export function getWrongOverview(params) {
  return request({
    url: '/api/statistics/wrong-questions/overview',
    method: 'get',
    params
  })
}

/**
 * 获取错题分布
 * @param {Object} params - 查询参数
 * @param {string} params.dimension - 统计维度 (subject/type/knowledge)
 * @param {number} params.days - 统计天数（默认30天）
 * @returns {Promise}
 */
export function getWrongDistribution(params) {
  return request({
    url: '/api/statistics/wrong-questions/distribution',
    method: 'get',
    params
  })
}

/**
 * 获取高频错题
 * @param {Object} params - 查询参数
 * @param {number} params.limit - 返回数量（默认10）
 * @returns {Promise}
 */
export function getFrequentWrong(params) {
  return request({
    url: '/api/statistics/wrong-questions/frequent',
    method: 'get',
    params
  })
}

/**
 * 获取错题趋势
 * @param {Object} params - 查询参数
 * @param {number} params.days - 统计天数（默认30天）
 * @returns {Promise}
 */
export function getWrongTrend(params) {
  return request({
    url: '/api/statistics/wrong-questions/trend',
    method: 'get',
    params
  })
}

/**
 * 获取薄弱知识点
 * @param {Object} params - 查询参数
 * @param {number} params.limit - 返回数量（默认10）
 * @returns {Promise}
 */
export function getWeakPoints(params) {
  return request({
    url: '/api/statistics/wrong-questions/weak-points',
    method: 'get',
    params
  })
}

/**
 * 获取学习建议
 * @returns {Promise}
 */
export function getLearningSuggestions() {
  return request({
    url: '/api/statistics/wrong-questions/suggestions',
    method: 'get'
  })
}
