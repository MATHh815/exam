import axios from 'axios'
import { handleError } from './errorHandler'

// 创建 axios 实例
const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
request.interceptors.request.use(
  config => {
    // 从 localStorage 获取 token
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
      console.log('请求携带token:', config.url)
    } else {
      console.warn('请求未携带token:', config.url)
    }
    return config
  },
  error => {
    console.error('请求错误:', error)
    handleError(error, { showMessage: true })
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  response => {
    const res = response.data
    
    // 如果响应成功
    if (res.success !== false) {
      return res
    }
    
    // 如果响应失败
    const error = new Error(res.error?.message || '请求失败')
    error.response = { data: res }
    handleError(error, { showMessage: true })
    return Promise.reject(error)
  },
  error => {
    console.error('响应错误:', error)
    console.error('错误详情:', {
      url: error.config?.url,
      status: error.response?.status,
      message: error.response?.data?.error?.message
    })
    
    // 特殊处理认证错误 - 在显示消息之前检查
    if (error.response?.status === 401) {
      console.warn('收到401错误，清除登录状态')
      
      // 清除 token
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      
      // 避免在登录页重复跳转
      const currentPath = window.location.pathname
      if (!currentPath.includes('/login') && !currentPath.includes('/register')) {
        // 使用统一错误处理显示消息
        handleError(error, { showMessage: true })
        
        console.log('即将跳转到登录页')
        setTimeout(() => {
          window.location.href = '/login'
        }, 1000)
      } else {
        console.log('已在登录页，不跳转')
      }
      
      return Promise.reject(error)
    }
    
    // 其他错误使用统一错误处理
    handleError(error, { showMessage: true })
    
    return Promise.reject(error)
  }
)

export default request
