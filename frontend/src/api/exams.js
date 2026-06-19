/**
 * 考试相关 API
 * 
 * 包含以下功能：
 * - 试卷查询（列表、详情）
 * - 试卷管理（创建、编辑、删除、发布）- 管理员
 * - 考试流程（开始考试、提交答案、提交试卷）
 * - 考试结果（查询结果、考试历史）
 */

import request from '../utils/request'

/**
 * 获取试卷列表
 * @param {Object} params - 查询参数
 * @param {string} params.exam_type - 考试类型筛选
 * @param {boolean} params.is_published - 发布状态筛选
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @returns {Promise}
 */
export function getExamPapers(params = {}) {
  return request({
    url: '/exams',
    method: 'get',
    params
  })
}

/**
 * 获取试卷详情
 * @param {number} paperId - 试卷ID
 * @param {boolean} includeQuestions - 是否包含题目列表
 * @returns {Promise}
 */
export function getExamPaper(paperId, includeQuestions = false) {
  return request({
    url: `/exams/${paperId}`,
    method: 'get',
    params: {
      include_questions: includeQuestions
    }
  })
}

/**
 * 创建试卷（管理员）
 * @param {Object} data - 试卷数据
 * @param {string} data.name - 试卷名称
 * @param {string} data.exam_type - 考试类型
 * @param {number} data.duration - 考试时长（分钟）
 * @param {string} data.description - 试卷描述
 * @param {number} data.total_score - 总分
 * @param {number} data.pass_score - 及格分
 * @returns {Promise}
 */
export function createExamPaper(data) {
  return request({
    url: '/exams',
    method: 'post',
    data
  })
}

/**
 * 更新试卷（管理员）
 * @param {number} paperId - 试卷ID
 * @param {Object} data - 更新数据
 * @returns {Promise}
 */
export function updateExamPaper(paperId, data) {
  return request({
    url: `/exams/${paperId}`,
    method: 'put',
    data
  })
}

/**
 * 删除试卷（管理员）
 * @param {number} paperId - 试卷ID
 * @returns {Promise}
 */
export function deleteExamPaper(paperId) {
  return request({
    url: `/exams/${paperId}`,
    method: 'delete'
  })
}

/**
 * 添加题目到试卷（管理员）
 * @param {number} paperId - 试卷ID
 * @param {Object} data - 题目数据
 * @param {number} data.question_id - 题目ID
 * @param {number} data.order - 题目顺序
 * @param {number} data.score - 题目分值
 * @returns {Promise}
 */
export function addQuestionToPaper(paperId, data) {
  return request({
    url: `/exams/${paperId}/questions`,
    method: 'post',
    data
  })
}

/**
 * 发布试卷（管理员）
 * @param {number} paperId - 试卷ID
 * @returns {Promise}
 */
export function publishExamPaper(paperId) {
  return request({
    url: `/exams/${paperId}/publish`,
    method: 'post'
  })
}

/**
 * 获取当前进行中的考试会话
 * @param {number} paperId - 试卷ID
 * @returns {Promise}
 */
export function getCurrentSession(paperId) {
  return request({
    url: `/exams/${paperId}/current-session`,
    method: 'get'
  })
}

/**
 * 开始考试
 * @param {number} paperId - 试卷ID
 * @returns {Promise}
 */
export function startExam(paperId) {
  return request({
    url: `/exams/${paperId}/start`,
    method: 'post'
  })
}

/**
 * 提交单题答案
 * @param {number} sessionId - 考试会话ID
 * @param {Object} data - 答案数据
 * @param {number} data.question_id - 题目ID
 * @param {string} data.answer - 用户答案
 * @param {number} data.question_index - 当前题目索引（可选）
 * @returns {Promise}
 */
export function submitAnswer(sessionId, data) {
  return request({
    url: `/exams/sessions/${sessionId}/answer`,
    method: 'post',
    data
  })
}

/**
 * 保存考试进度
 * @param {number} sessionId - 考试会话ID
 * @param {number} questionIndex - 当前题目索引
 * @returns {Promise}
 */
export function saveProgress(sessionId, questionIndex) {
  return request({
    url: `/exams/sessions/${sessionId}/progress`,
    method: 'post',
    data: { question_index: questionIndex }
  })
}

/**
 * 暂停考试
 * @param {number} sessionId - 考试会话ID
 * @returns {Promise}
 */
export function pauseExam(sessionId) {
  return request({
    url: `/exams/sessions/${sessionId}/pause`,
    method: 'post'
  })
}

/**
 * 恢复暂停的考试
 * @param {number} sessionId - 考试会话ID
 * @returns {Promise}
 */
export function resumeExam(sessionId) {
  return request({
    url: `/exams/sessions/${sessionId}/resume`,
    method: 'post'
  })
}

/**
 * 获取考试会话详情
 * @param {number} sessionId - 考试会话ID
 * @returns {Promise}
 */
export function getSessionDetail(sessionId) {
  return request({
    url: `/exams/sessions/${sessionId}`,
    method: 'get'
  })
}

/**
 * 获取用户所有考试会话
 * @param {Object} params - 查询参数
 * @param {string} params.status - 状态筛选
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @returns {Promise}
 */
export function getUserSessions(params = {}) {
  return request({
    url: '/exams/sessions',
    method: 'get',
    params
  })
}

/**
 * 获取用户未完成的考试会话
 * @returns {Promise}
 */
export function getIncompleteSessions() {
  return request({
    url: '/exams/sessions/incomplete',
    method: 'get'
  })
}

/**
 * 提交整份试卷
 * @param {number} sessionId - 考试会话ID
 * @returns {Promise}
 */
export function submitExam(sessionId) {
  return request({
    url: `/exams/sessions/${sessionId}/submit`,
    method: 'post'
  })
}

/**
 * 获取考试结果
 * @param {number} resultId - 结果ID
 * @param {boolean} includeDetails - 是否包含详细结果
 * @returns {Promise}
 */
export function getExamResult(resultId, includeDetails = true) {
  return request({
    url: `/exams/results/${resultId}`,
    method: 'get',
    params: {
      include_details: includeDetails
    }
  })
}

/**
 * 获取用户考试历史
 * @param {Object} params - 查询参数
 * @param {number} params.paper_id - 试卷ID筛选
 * @param {number} params.page - 页码
 * @param {number} params.page_size - 每页数量
 * @returns {Promise}
 */
export function getExamHistory(params = {}) {
  return request({
    url: '/exams/results',
    method: 'get',
    params
  })
}
