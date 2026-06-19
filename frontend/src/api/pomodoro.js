/**
 * 番茄钟 API
 */
import request from '@/utils/request'

/**
 * 完成番茄钟会话
 */
export function completeSession(data) {
  return request({
    url: '/api/pomodoro/complete',
    method: 'post',
    data
  })
}

/**
 * 中断番茄钟会话
 */
export function interruptSession(data) {
  return request({
    url: '/api/pomodoro/interrupt',
    method: 'post',
    data
  })
}

/**
 * 获取番茄钟统计
 */
export function getStats() {
  return request({
    url: '/api/pomodoro/stats',
    method: 'get'
  })
}

/**
 * 获取最近的会话
 */
export function getRecentSessions(days = 7) {
  return request({
    url: '/api/pomodoro/sessions/recent',
    method: 'get',
    params: { days }
  })
}

/**
 * 获取每日趋势
 */
export function getDailyTrend(days = 30) {
  return request({
    url: '/api/pomodoro/trend',
    method: 'get',
    params: { days }
  })
}
