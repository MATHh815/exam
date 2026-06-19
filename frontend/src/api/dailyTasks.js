import request from '@/utils/request'

/**
 * 获取今日任务
 */
export function getTodayTasks() {
  return request({
    url: '/daily-tasks',
    method: 'get'
  })
}

/**
 * 完成任务
 * @param {number} id - 任务ID
 */
export function completeTask(id) {
  return request({
    url: `/daily-tasks/${id}/complete`,
    method: 'put'
  })
}

/**
 * 获取任务统计
 */
export function getTaskStats() {
  return request({
    url: '/daily-tasks/stats',
    method: 'get'
  })
}

/**
 * 获取任务模板
 */
export function getTaskTemplates() {
  return request({
    url: '/daily-tasks/templates',
    method: 'get'
  })
}
