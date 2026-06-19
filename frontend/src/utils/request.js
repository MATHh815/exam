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
  async error => {
    console.error('响应错误:', error)
    console.error('错误详情:', {
      url: error.config?.url,
      status: error.response?.status,
      message: error.response?.data?.error?.message
    })
    
    // 特殊处理认证错误
    if (error.response?.status === 401) {
      console.warn('收到401错误，尝试刷新token')
      
      // 检查是否是刷新token的请求，如果是则直接清除认证数据
      if (error.config?.url?.includes('/auth/refresh')) {
        console.warn('刷新token请求失败，清除认证数据')
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
        
        // 跳转到登录页
        const currentPath = window.location.pathname
        if (!currentPath.includes('/login') && !currentPath.includes('/register')) {
          handleError(error, { showMessage: true })
          setTimeout(() => {
            window.location.href = '/login'
          }, 1000)
        }
        return Promise.reject(error)
      }
      
      // 尝试刷新token
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          console.log('尝试刷新access token')
          const refreshResponse = await fetch('/api/auth/refresh', {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${refreshToken}`,
              'Content-Type': 'application/json'
            }
          })
          
          if (refreshResponse.ok) {
            const refreshData = await refreshResponse.json()
            if (refreshData.success && refreshData.data) {
              const newAccessToken = refreshData.data.access_token
              localStorage.setItem('access_token', newAccessToken)
              console.log('token刷新成功，重试原请求')
              
              // 更新原请求的token并重试
              error.config.headers.Authorization = `Bearer ${newAccessToken}`
              return request(error.config)
            }
          }
          
          console.warn('token刷新失败')
        } catch (refreshError) {
          console.error('token刷新异常:', refreshError)
        }
      }
      
      // 刷新失败或没有refresh token，清除认证数据
      console.warn('清除认证数据并跳转到登录页')
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
      
      // 防止重定向循环
      const currentPath = window.location.pathname
      const isAuthPage = currentPath.includes('/login') || currentPath.includes('/register')
      
      if (!isAuthPage) {
        handleError(error, { showMessage: true })
        console.log('即将跳转到登录页')
        setTimeout(() => {
          if (window.location.pathname !== '/login') {
            window.location.href = '/login'
          }
        }, 1000)
      } else {
        console.log('已在认证页面，不跳转')
        handleError(error, { showMessage: true })
      }
      
      return Promise.reject(error)
    }
    
    // 其他错误使用统一错误处理
    handleError(error, { showMessage: true })
    
    return Promise.reject(error)
  }
)

export default request
