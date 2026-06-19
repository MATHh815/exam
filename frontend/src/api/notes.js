/**
 * 笔记相关 API
 */
import request from '../utils/request'

/**
 * 创建笔记
 * @param {Object} data - 笔记数据
 * @param {number} data.question_id - 题目ID
 * @param {string} data.content - 笔记内容（Markdown格式）
 * @param {Array} [data.tags] - 标签列表
 * @returns {Promise} 创建的笔记
 */
export function createNote(data) {
  return request({
    url: '/notes',
    method: 'post',
    data
  })
}

/**
 * 获取笔记列表
 * @param {Object} params - 查询参数
 * @param {number} [params.page=1] - 页码
 * @param {number} [params.page_size=20] - 每页数量
 * @param {string} [params.subject] - 科目
 * @param {string} [params.chapter] - 章节
 * @returns {Promise} 笔记列表
 */
export function getNotes(params) {
  return request({
    url: '/notes',
    method: 'get',
    params
  })
}

/**
 * 获取笔记详情
 * @param {number} noteId - 笔记ID
 * @returns {Promise} 笔记详情
 */
export function getNote(noteId) {
  return request({
    url: `/notes/${noteId}`,
    method: 'get'
  })
}

/**
 * 更新笔记
 * @param {number} noteId - 笔记ID
 * @param {Object} data - 更新数据
 * @returns {Promise} 更新后的笔记
 */
export function updateNote(noteId, data) {
  return request({
    url: `/notes/${noteId}`,
    method: 'put',
    data
  })
}

/**
 * 删除笔记
 * @param {number} noteId - 笔记ID
 * @returns {Promise} 删除结果
 */
export function deleteNote(noteId) {
  return request({
    url: `/notes/${noteId}`,
    method: 'delete'
  })
}

/**
 * 搜索笔记
 * @param {Object} params - 搜索参数
 * @param {string} [params.keyword] - 关键词
 * @param {string} [params.subject] - 科目
 * @param {string} [params.chapter] - 章节
 * @param {string} [params.start_date] - 开始日期
 * @param {string} [params.end_date] - 结束日期
 * @param {string} [params.sort_by] - 排序方式
 * @returns {Promise} 搜索结果
 */
export function searchNotes(params) {
  return request({
    url: '/notes/search',
    method: 'get',
    params
  })
}

/**
 * 获取题目的笔记
 * @param {number} questionId - 题目ID
 * @returns {Promise} 笔记列表
 */
export function getQuestionNotes(questionId) {
  return request({
    url: `/notes/question/${questionId}`,
    method: 'get'
  })
}
