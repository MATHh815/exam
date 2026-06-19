/**
 * 题库相关 API
 */
import request from '../utils/request'

/**
 * 获取题目列表（支持分页和筛选）
 * @param {Object} params - 查询参数
 * @param {number} [params.page=1] - 页码
 * @param {number} [params.page_size=20] - 每页数量
 * @param {string} [params.exam_type] - 考试类型
 * @param {string} [params.question_type] - 题目类型
 * @param {string} [params.subject] - 科目
 * @param {string} [params.chapter] - 章节
 * @param {number} [params.difficulty] - 难度
 * @param {string} [params.keyword] - 关键词
 * @returns {Promise} 题目列表和分页信息
 */
export function getQuestions(params) {
  return request({
    url: '/questions',
    method: 'get',
    params
  })
}

/**
 * 获取单个题目详情
 * @param {number} id - 题目ID
 * @returns {Promise} 题目详情
 */
export function getQuestion(id) {
  return request({
    url: `/api/questions/${id}`,
    method: 'get'
  })
}

/**
 * 创建题目（管理员）
 * @param {Object} data - 题目数据
 * @param {string} data.exam_type - 考试类型
 * @param {string} data.question_type - 题目类型
 * @param {string} data.subject - 科目
 * @param {string} [data.chapter] - 章节
 * @param {number} data.difficulty - 难度（1-5）
 * @param {string} data.content - 题目内容
 * @param {Array} [data.options] - 选项（选择题）
 * @param {string} data.correct_answer - 正确答案
 * @param {string} [data.explanation] - 解析
 * @param {Array} [data.tags] - 标签
 * @returns {Promise} 创建结果
 */
export function createQuestion(data) {
  return request({
    url: '/questions',
    method: 'post',
    data
  })
}

/**
 * 更新题目（管理员）
 * @param {number} id - 题目ID
 * @param {Object} data - 更新数据
 * @returns {Promise} 更新结果
 */
export function updateQuestion(id, data) {
  return request({
    url: `/api/questions/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除题目（管理员，软删除）
 * @param {number} id - 题目ID
 * @returns {Promise} 删除结果
 */
export function deleteQuestion(id) {
  return request({
    url: `/api/questions/${id}`,
    method: 'delete'
  })
}

/**
 * 批量导入题目（管理员）
 * @param {Object} data - 导入数据
 * @param {Array} data.questions - 题目数组
 * @returns {Promise} 导入结果
 */
export function importQuestions(data) {
  return request({
    url: '/questions/import',
    method: 'post',
    data
  })
}

/**
 * 随机获取题目
 * @param {Object} params - 查询参数
 * @param {number} [params.count=10] - 数量
 * @param {string} [params.exam_type] - 考试类型
 * @param {string} [params.question_type] - 题目类型
 * @param {string} [params.subject] - 科目
 * @param {string} [params.chapter] - 章节
 * @param {number} [params.difficulty] - 难度
 * @returns {Promise} 随机题目列表
 */
export function getRandomQuestions(params) {
  return request({
    url: '/questions/random',
    method: 'get',
    params
  })
}

/**
 * 获取题库统计信息（管理员）
 * @param {Object} params - 查询参数
 * @param {string} [params.exam_type] - 考试类型
 * @returns {Promise} 统计信息
 */
export function getQuestionStatistics(params) {
  return request({
    url: '/questions/statistics',
    method: 'get',
    params
  })
}
