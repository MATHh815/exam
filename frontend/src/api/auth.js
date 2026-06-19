/**
 * 认证相关 API
 */
import request from '../utils/request'

/**
 * 用户注册
 * @param {Object} data - 注册数据
 * @param {string} data.username - 用户�?
 * @param {string} data.password - 密码
 * @param {string} data.email - 邮箱
 * @param {string} [data.nickname] - 昵称（可选）
 * @returns {Promise} 注册结果
 */
export function register(data) {
  return request({
    url: '/auth/register',
    method: 'post',
    data
  })
}

/**
 * 用户登录
 * @param {Object} data - 登录数据
 * @param {string} data.username - 用户�?
 * @param {string} data.password - 密码
 * @returns {Promise} 登录结果（包含用户信息和令牌�?
 */
export function login(data) {
  return request({
    url: '/auth/login',
    method: 'post',
    data
  })
}

/**
 * 用户登出
 * @returns {Promise} 登出结果
 */
export function logout() {
  return request({
    url: '/auth/logout',
    method: 'post'
  })
}

/**
 * 刷新访问令牌
 * @returns {Promise} 新的访问令牌
 */
export function refreshToken() {
  return request({
    url: '/auth/refresh',
    method: 'post',
    headers: {
      Authorization: `Bearer ${localStorage.getItem('refresh_token')}`
    }
  })
}

/**
 * 获取当前用户信息
 * @returns {Promise} 用户信息
 */
export function getProfile() {
  return request({
    url: '/auth/profile',
    method: 'get'
  })
}

/**
 * 更新用户信息
 * @param {Object} data - 更新数据
 * @param {string} [data.nickname] - 昵称
 * @param {string} [data.email] - 邮箱
 * @param {string} [data.avatar] - 头像 URL
 * @returns {Promise} 更新结果
 */
export function updateProfile(data) {
  return request({
    url: '/auth/profile',
    method: 'put',
    data
  })
}

/**
 * 修改密码
 * @param {Object} data - 密码数据
 * @param {string} data.old_password - 旧密�?
 * @param {string} data.new_password - 新密�?
 * @returns {Promise} 修改结果
 */
export function changePassword(data) {
  return request({
    url: '/auth/change-password',
    method: 'post',
    data
  })
}

/**
 * 重置密码
 * @param {Object} data - 重置数据
 * @param {string} data.email - 邮箱
 * @param {string} data.new_password - 新密�?
 * @returns {Promise} 重置结果
 */
export function resetPassword(data) {
  return request({
    url: '/auth/reset-password',
    method: 'post',
    data
  })
}
