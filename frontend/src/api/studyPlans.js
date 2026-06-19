/**
 * 学习计划相关 API
 */
import request from '../utils/request'

/**
 * 创建学习计划
 * @param {Object} data - 学习计划数据
 * @param {string} data.name - 计划名称
 * @param {string} data.exam_type - 考试类型
 * @param {string} data.target_date - 目标日期
 * @param {string} [data.description] - 计划描述
 * @param {Array} [data.goals] - 学习目标列表
 * @returns {Promise} 创建的学习计划
 */
export function createStudyPlan(data) {
  return request({
    url: '/study-plans',
    method: 'post',
    data
  })
}

/**
 * 获取学习计划列表
 * @param {Object} params - 查询参数
 * @param {boolean} [params.active_only] - 仅显示活跃计划
 * @returns {Promise} 学习计划列表
 */
export function getStudyPlans(params) {
  return request({
    url: '/study-plans',
    method: 'get',
    params
  })
}

/**
 * 获取学习计划详情
 * @param {number} planId - 计划ID
 * @returns {Promise} 学习计划详情
 */
export function getStudyPlan(planId) {
  return request({
    url: `/study-plans/${planId}`,
    method: 'get'
  })
}

/**
 * 更新学习计划
 * @param {number} planId - 计划ID
 * @param {Object} data - 更新数据
 * @returns {Promise} 更新后的学习计划
 */
export function updateStudyPlan(planId, data) {
  return request({
    url: `/study-plans/${planId}`,
    method: 'put',
    data
  })
}

/**
 * 删除学习计划
 * @param {number} planId - 计划ID
 * @returns {Promise} 删除结果
 */
export function deleteStudyPlan(planId) {
  return request({
    url: `/study-plans/${planId}`,
    method: 'delete'
  })
}

/**
 * 更新学习进度
 * @param {number} planId - 计划ID
 * @param {Object} data - 进度数据
 * @returns {Promise} 更新结果
 */
export function updateProgress(planId, data) {
  return request({
    url: `/study-plans/${planId}/progress`,
    method: 'put',
    data
  })
}

/**
 * 获取学习报告
 * @param {number} planId - 计划ID
 * @returns {Promise} 学习报告
 */
export function getStudyReport(planId) {
  return request({
    url: `/study-plans/${planId}/report`,
    method: 'get'
  })
}
