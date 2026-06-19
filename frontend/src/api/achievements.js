import request from '@/utils/request'

/**
 * 获取所有成就定义
 * @param {Object} params - 查询参数
 * @param {string} params.category - 成就类别
 */
export function getAllAchievements(params) {
  return request({
    url: '/achievements',
    method: 'get',
    params
  })
}

/**
 * 获取成就详情
 * @param {number} id - 成就ID
 */
export function getAchievementDetail(id) {
  return request({
    url: `/achievements/${id}`,
    method: 'get'
  })
}

/**
 * 获取用户成就
 * @param {Object} params - 查询参数
 * @param {string} params.status - 成就状态 (earned/in_progress/locked)
 */
export function getUserAchievements(params) {
  return request({
    url: '/achievements/user',
    method: 'get',
    params
  })
}

/**
 * 获取成就统计
 */
export function getAchievementStats() {
  return request({
    url: '/achievements/stats',
    method: 'get'
  })
}

/**
 * 手动检查成就
 */
export function checkAchievements() {
  return request({
    url: '/achievements/check',
    method: 'post'
  })
}
