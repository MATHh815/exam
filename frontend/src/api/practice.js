/**
 * 练习和错题本相关 API
 */
import request from '../utils/request'

/**
 * 开始练习
 * @param {Object} data - 练习参数
 * @param {number} [data.count=10] - 题目数量
 * @param {string} [data.exam_type] - 考试类型
 * @param {string} [data.question_type] - 题目类型
 * @param {string} [data.subject] - 科目
 * @param {string} [data.chapter] - 章节
 * @param {number} [data.difficulty] - 难度
 * @param {boolean} [data.from_wrong_book] - 是否从错题本练习
 * @returns {Promise} 题目列表
 */
export function startPractice(data) {
  return request({
    url: '/practice/start',
    method: 'post',
    data
  })
}

/**
 * 提交练习答案
 * @param {Object} data - 答案数据
 * @param {number} data.question_id - 题目ID
 * @param {string} data.user_answer - 用户答案
 * @param {number} [data.time_spent] - 答题时长（秒）
 * @returns {Promise} 判题结果
 */
export function submitPracticeAnswer(data) {
  return request({
    url: '/practice/submit',
    method: 'post',
    data
  })
}

/**
 * 获取练习历史
 * @param {Object} params - 查询参数
 * @param {number} [params.page=1] - 页码
 * @param {number} [params.page_size=20] - 每页数量
 * @param {boolean} [params.is_correct] - 是否正确
 * @param {string} [params.start_date] - 开始日期
 * @param {string} [params.end_date] - 结束日期
 * @returns {Promise} 练习历史记录
 */
export function getPracticeHistory(params) {
  return request({
    url: '/practice/history',
    method: 'get',
    params
  })
}

/**
 * 获取错题本
 * @param {Object} params - 查询参数
 * @param {boolean} [params.mastered] - 是否已掌握
 * @param {string} [params.exam_type] - 考试类型
 * @param {string} [params.subject] - 科目
 * @returns {Promise} 错题列表
 */
export function getWrongBook(params) {
  return request({
    url: '/practice/wrong-book',
    method: 'get',
    params
  })
}

/**
 * 从错题本移除题目
 * @param {number} wrongQuestionId - 错题记录ID
 * @returns {Promise} 移除结果
 */
export function removeFromWrongBook(wrongQuestionId) {
  return request({
    url: `/practice/wrong-book/${wrongQuestionId}`,
    method: 'delete'
  })
}

/**
 * 获取练习概览统计
 * @param {Object} params - 查询参数
 * @param {number} [params.days=7] - 统计天数
 * @returns {Promise} 统计信息
 */
export function getPracticeSummary(params) {
  return request({
    url: '/practice/summary',
    method: 'get',
    params
  })
}
