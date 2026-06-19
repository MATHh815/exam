import request from '@/utils/request'

/**
 * 获取用户积分信息
 */
export function getUserPoints() {
  return request({
    url: '/points',
    method: 'get'
  })
}

/**
 * 获取积分历史
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.per_page - 每页数量
 */
export function getPointsHistory(params) {
  return request({
    url: '/points/history',
    method: 'get',
    params
  })
}

/**
 * 获取积分排行榜
 * @param {Object} params - 查询参数
 * @param {number} params.page - 页码
 * @param {number} params.per_page - 每页数量
 */
export function getLeaderboard(params) {
  return request({
    url: '/points/leaderboard',
    method: 'get',
    params
  })
}
