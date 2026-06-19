/**
 * 题目收藏相关 API
 */
import request from '../utils/request'

/**
 * 收藏题目
 * @param {Object} data - 收藏数据
 * @param {number} data.question_id - 题目ID
 * @param {Array} [data.tags] - 标签列表
 * @param {string} [data.note] - 备注
 * @returns {Promise} 收藏记录
 */
export function bookmarkQuestion(data) {
  return request({
    url: '/bookmarks',
    method: 'post',
    data
  })
}

/**
 * 获取收藏列表
 * @param {Object} params - 查询参数
 * @param {number} [params.page=1] - 页码
 * @param {number} [params.page_size=20] - 每页数量
 * @param {string} [params.exam_type] - 考试类型
 * @param {string} [params.subject] - 科目
 * @param {string} [params.chapter] - 章节
 * @param {number} [params.difficulty] - 难度
 * @param {string} [params.tag] - 标签
 * @param {string} [params.sort_by] - 排序方式
 * @returns {Promise} 收藏列表
 */
export function getBookmarks(params) {
  return request({
    url: '/bookmarks',
    method: 'get',
    params
  })
}

/**
 * 获取收藏详情
 * @param {number} bookmarkId - 收藏ID
 * @returns {Promise} 收藏详情
 */
export function getBookmark(bookmarkId) {
  return request({
    url: `/bookmarks/${bookmarkId}`,
    method: 'get'
  })
}

/**
 * 更新收藏
 * @param {number} bookmarkId - 收藏ID
 * @param {Object} data - 更新数据
 * @returns {Promise} 更新后的收藏
 */
export function updateBookmark(bookmarkId, data) {
  return request({
    url: `/bookmarks/${bookmarkId}`,
    method: 'put',
    data
  })
}

/**
 * 取消收藏
 * @param {number} bookmarkId - 收藏ID
 * @returns {Promise} 删除结果
 */
export function deleteBookmark(bookmarkId) {
  return request({
    url: `/bookmarks/${bookmarkId}`,
    method: 'delete'
  })
}

/**
 * 检查题目是否已收藏
 * @param {number} questionId - 题目ID
 * @returns {Promise} 收藏状态
 */
export function checkBookmark(questionId) {
  return request({
    url: `/bookmarks/question/${questionId}`,
    method: 'get'
  })
}

/**
 * 取消收藏（通过题目ID）
 * @param {number} questionId - 题目ID
 * @returns {Promise} 删除结果
 */
export function unbookmarkQuestion(questionId) {
  return request({
    url: `/bookmarks/question/${questionId}`,
    method: 'delete'
  })
}

/**
 * 获取收藏数量
 * @returns {Promise} 收藏数量
 */
export function getBookmarkCount() {
  return request({
    url: '/bookmarks/count',
    method: 'get'
  })
}
