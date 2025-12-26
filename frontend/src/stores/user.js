/**
 * 用户状态管理 Store
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, logout as logoutApi, getProfile, register as registerApi } from '../api/auth'
import storage from '../utils/storage'

export const useUserStore = defineStore('user', () => {
  // 状态
  const user = ref(null)
  const accessToken = ref(localStorage.getItem('access_token') || '')
  const refreshToken = ref(localStorage.getItem('refresh_token') || '')

  // 计算属性
  const isLoggedIn = computed(() => !!accessToken.value)
  const isAdmin = computed(() => user.value?.role === 'admin')
  const userInfo = computed(() => user.value)

  /**
   * 设置令牌
   */
  function setTokens(access, refresh) {
    accessToken.value = access
    refreshToken.value = refresh
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
  }

  /**
   * 清除令牌
   */
  function clearTokens() {
    accessToken.value = ''
    refreshToken.value = ''
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  /**
   * 设置用户信息
   */
  function setUser(userData) {
    user.value = userData
    // 同时保存到 localStorage，使用 'user' 键
    if (userData) {
      localStorage.setItem('user', JSON.stringify(userData))
    }
    storage.set('user', userData)
  }

  /**
   * 清除用户信息
   */
  function clearUser() {
    user.value = null
    localStorage.removeItem('user')
    storage.remove('user')
  }

  /**
   * 用户注册
   */
  async function register(registerData) {
    try {
      const response = await registerApi(registerData)
      if (response.success) {
        // 注册成功后自动登录
        return await login({
          username: registerData.username,
          password: registerData.password
        })
      }
      return response
    } catch (error) {
      console.error('注册失败:', error)
      throw error
    }
  }

  /**
   * 用户登录
   */
  async function login(loginData) {
    try {
      const response = await loginApi(loginData)
      if (response.success && response.data) {
        const { user: userData, access_token, refresh_token } = response.data
        
        // 同步保存所有数据，确保原子性
        accessToken.value = access_token
        refreshToken.value = refresh_token
        user.value = userData
        
        // 批量写入localStorage
        localStorage.setItem('access_token', access_token)
        localStorage.setItem('refresh_token', refresh_token)
        localStorage.setItem('user', JSON.stringify(userData))
        
        console.log('登录成功，token和用户信息已保存')
        
        return response
      }
      return response
    } catch (error) {
      console.error('登录失败:', error)
      throw error
    }
  }

  /**
   * 用户登出
   */
  async function logout() {
    try {
      // 调用登出 API
      await logoutApi()
    } catch (error) {
      console.error('登出 API 调用失败:', error)
    } finally {
      // 无论 API 调用是否成功，都清除本地数据
      clearUser()
      clearTokens()
    }
  }

  /**
   * 获取用户信息
   */
  async function fetchUserInfo() {
    try {
      const response = await getProfile()
      if (response.success && response.data) {
        setUser(response.data.user)
        return response.data.user
      }
      return null
    } catch (error) {
      console.error('获取用户信息失败:', error)
      // 如果获取失败（如令牌过期），清除登录状态
      clearUser()
      clearTokens()
      throw error
    }
  }

  /**
   * 刷新访问令牌
   */
  async function refreshAccessToken() {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/api/auth/refresh`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${refreshToken.value}`,
          'Content-Type': 'application/json'
        }
      })
      
      const data = await response.json()
      
      if (data.success && data.data) {
        const { access_token } = data.data
        accessToken.value = access_token
        localStorage.setItem('access_token', access_token)
        return access_token
      }
      
      // 刷新失败，清除登录状态
      clearUser()
      clearTokens()
      return null
    } catch (error) {
      console.error('刷新令牌失败:', error)
      clearUser()
      clearTokens()
      throw error
    }
  }

  /**
   * 初始化用户状态（从本地存储恢复）
   */
  function initUserState() {
    const storedToken = localStorage.getItem('access_token')
    const storedRefreshToken = localStorage.getItem('refresh_token')
    
    // 同步 token 状态
    if (storedToken) {
      accessToken.value = storedToken
    }
    if (storedRefreshToken) {
      refreshToken.value = storedRefreshToken
    }
    
    // 尝试恢复用户信息
    if (storedToken) {
      // 先尝试从 localStorage 直接读取
      const userStr = localStorage.getItem('user')
      if (userStr) {
        try {
          user.value = JSON.parse(userStr)
        } catch (e) {
          console.error('解析用户信息失败:', e)
        }
      }
      
      // 如果没有，尝试从 storage 工具读取
      if (!user.value) {
        const storedUser = storage.get('user')
        if (storedUser) {
          user.value = storedUser
        }
      }
    } else {
      // 没有 token，清除所有数据
      clearUser()
      clearTokens()
    }
  }

  // 初始化
  initUserState()

  return {
    // 状态
    user,
    accessToken,
    refreshToken,
    
    // 计算属性
    isLoggedIn,
    isAdmin,
    userInfo,
    
    // 方法
    register,
    login,
    logout,
    fetchUserInfo,
    refreshAccessToken,
    setTokens,
    clearTokens,
    setUser,
    clearUser
  }
})
