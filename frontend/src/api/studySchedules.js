/**
 * 学习日程 API 客户端
 */
import request from '@/utils/request'

/**
 * 获取活动类型和科目选项
 */
export function getScheduleOptions() {
  return request({
    url: '/study-schedules/options',
    method: 'get'
  })
}

/**
 * 创建学习日程
 * @param {Object} data - 日程数据
 * @param {string} data.title - 标题
 * @param {string} data.activity_type - 活动类型
 * @param {string} data.subject - 科目
 * @param {string} data.schedule_date - 日期 (YYYY-MM-DD)
 * @param {string} data.start_time - 开始时间 (HH:MM)
 * @param {string} data.end_time - 结束时间 (HH:MM)
 * @param {string} data.repeat_type - 重复类型 (once/daily/weekly)
 * @param {string} data.repeat_days - 重复的星期几 (1,2,3,4,5)
 * @param {string} data.repeat_until - 重复截止日期 (YYYY-MM-DD)
 * @param {string} data.description - 描述
 * @param {string} data.location - 地点
 * @param {number} data.reminder_minutes - 提醒时间（分钟）
 */
export function createSchedule(data) {
  return request({
    url: '/study-schedules',
    method: 'post',
    data
  })
}

/**
 * 获取今天的日程
 */
export function getTodaySchedules() {
  return request({
    url: '/study-schedules/today',
    method: 'get'
  })
}

/**
 * 获取日期范围内的日程
 * @param {string} startDate - 开始日期 (YYYY-MM-DD)
 * @param {string} endDate - 结束日期 (YYYY-MM-DD)
 */
export function getSchedulesByRange(startDate, endDate) {
  return request({
    url: '/study-schedules',
    method: 'get',
    params: {
      start_date: startDate,
      end_date: endDate
    }
  })
}

/**
 * 更新日程
 * @param {number} id - 日程ID
 * @param {Object} data - 更新的数据
 */
export function updateSchedule(id, data) {
  return request({
    url: `/study-schedules/${id}`,
    method: 'put',
    data
  })
}

/**
 * 完成日程
 * @param {number} id - 日程ID
 */
export function completeSchedule(id) {
  return request({
    url: `/study-schedules/${id}/complete`,
    method: 'put'
  })
}

/**
 * 删除日程
 * @param {number} id - 日程ID
 */
export function deleteSchedule(id) {
  return request({
    url: `/study-schedules/${id}`,
    method: 'delete'
  })
}

/**
 * 获取统计数据
 * @param {string} startDate - 开始日期 (YYYY-MM-DD)
 * @param {string} endDate - 结束日期 (YYYY-MM-DD)
 */
export function getScheduleStatistics(startDate, endDate) {
  return request({
    url: '/study-schedules/statistics',
    method: 'get',
    params: {
      start_date: startDate,
      end_date: endDate
    }
  })
}
