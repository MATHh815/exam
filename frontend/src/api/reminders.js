/**
 * 学习提醒相关 API
 */
import request from '../utils/request'

/**
 * 创建提醒
 * @param {Object} data - 提醒数据
 * @param {number} data.study_plan_id - 学习计划ID
 * @param {string} data.reminder_type - 提醒类型（daily/weekly）
 * @param {string} data.reminder_time - 提醒时间（HH:MM格式）
 * @param {Array} [data.weekdays] - 星期几（weekly类型必填）
 * @param {string} [data.message] - 自定义消息
 * @returns {Promise} 创建的提醒
 */
export function createReminder(data) {
  return request({
    url: '/reminders',
    method: 'post',
    data
  })
}

/**
 * 获取提醒列表
 * @param {Object} params - 查询参数
 * @param {number} [params.study_plan_id] - 学习计划ID
 * @param {boolean} [params.active_only] - 仅显示活跃提醒
 * @returns {Promise} 提醒列表
 */
export function getReminders(params) {
  return request({
    url: '/reminders',
    method: 'get',
    params
  })
}

/**
 * 获取提醒详情
 * @param {number} reminderId - 提醒ID
 * @returns {Promise} 提醒详情
 */
export function getReminder(reminderId) {
  return request({
    url: `/reminders/${reminderId}`,
    method: 'get'
  })
}

/**
 * 更新提醒
 * @param {number} reminderId - 提醒ID
 * @param {Object} data - 更新数据
 * @returns {Promise} 更新后的提醒
 */
export function updateReminder(reminderId, data) {
  return request({
    url: `/reminders/${reminderId}`,
    method: 'put',
    data
  })
}

/**
 * 删除提醒
 * @param {number} reminderId - 提醒ID
 * @returns {Promise} 删除结果
 */
export function deleteReminder(reminderId) {
  return request({
    url: `/reminders/${reminderId}`,
    method: 'delete'
  })
}
