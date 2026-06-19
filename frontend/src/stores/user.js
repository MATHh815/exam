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
   * 设置令牌 - 原子性操作
   */
  function setTokens(access, refresh) {
    try {
      // 原子性更新：先更新内存，再更新存储
      accessToken.value = access
      refreshToken.value = refresh
      localStorage.setItem('access_token', access)
      localStorage.setItem('refresh_token', refresh)
    } catch (error) {
      console.error('设置令牌失败:', error)
      // 如果存储失败，回滚内存状态
      accessToken.value = ''
      refreshToken.value = ''
      throw error
    }
  }

  /**
   * 清除令牌 - 确保完全清理
   */
  function clearTokens() {
    // 清除内存状态
    accessToken.value = ''
    refreshToken.value = ''
    
    // 清除存储状态
    try {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    } catch (error) {
      console.error('清除令牌存储失败:', error)
      // 即使存储清除失败，内存状态已清除，继续执行
    }
  }

  /**
   * 设置用户信息 - 原子性操作
   */
  function setUser(userData) {
    try {
      // 更新内存状态
      user.value = userData
      
      // 同步更新存储
      if (userData) {
        localStorage.setItem('user', JSON.stringify(userData))
        storage.set('user', userData)
      } else {
        localStorage.removeItem('user')
        storage.remove('user')
      }
    } catch (error) {
      console.error('设置用户信息失败:', error)
      // 如果存储失败，回滚内存状态
      user.value = null
      throw error
    }
  }

  /**
   * 清除用户信息 - 确保完全清理
   */
  function clearUser() {
    // 清除内存状态
    user.value = null
    
    // 清除存储状态
    try {
      localStorage.removeItem('user')
      storage.remove('user')
    } catch (error) {
      console.error('清除用户信息存储失败:', error)
      // 即使存储清除失败，内存状态已清除，继续执行
    }
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
   * 用户登录 - 原子性操作确保状态一致性
   */
  async function login(loginData) {
    try {
      const response = await loginApi(loginData)
      if (response.success && response.data) {
        const { user: userData, access_token, refresh_token } = response.data
        
        // 原子性操作：使用事务性方法确保所有状态同步更新
        const atomicUpdate = () => {
          // 1. 首先更新内存状态
          accessToken.value = access_token
          refreshToken.value = refresh_token
          user.value = userData
          
          // 2. 然后原子性写入localStorage
          const storageOperations = [
            () => localStorage.setItem('access_token', access_token),
            () => localStorage.setItem('refresh_token', refresh_token),
            () => localStorage.setItem('user', JSON.stringify(userData))
          ]
          
          // 执行所有存储操作，如果任何一个失败则回滚
          try {
            storageOperations.forEach(operation => operation())
            console.log('登录成功，token和用户信息已原子性保存')
            return true
          } catch (storageError) {
            console.error('存储写入失败，回滚状态:', storageError)
            // 回滚内存状态
            accessToken.value = ''
            refreshToken.value = ''
            user.value = null
            throw new Error('登录状态保存失败')
          }
        }
        
        // 执行原子性更新
        atomicUpdate()
        
        return response
      }
      return response
    } catch (error) {
      console.error('登录失败:', error)
      // 确保失败时清理所有状态
      clearTokens()
      clearUser()
      throw error
    }
  }

  /**
   * 用户登出 - 完全清理认证数据
   */
  async function logout() {
    try {
      // 调用登出 API
      await logoutApi()
    } catch (error) {
      console.error('登出 API 调用失败:', error)
    } finally {
      // 无论 API 调用是否成功，都执行完全清理
      console.log('执行完全认证数据清理')
      
      // 原子性清理所有认证数据
      try {
        clearUser()
        clearTokens()
        console.log('认证数据清理完成')
      } catch (cleanupError) {
        console.error('清理认证数据时发生错误:', cleanupError)
        // 强制清理，确保状态一致
        accessToken.value = ''
        refreshToken.value = ''
        user.value = null
      }
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
   * 刷新访问令牌 - 原子性更新
   */
  async function refreshAccessToken() {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${refreshToken.value}`,
          'Content-Type': 'application/json'
        }
      })
      
      const data = await response.json()
      
      if (data.success && data.data) {
        const { access_token } = data.data
        
        // 原子性更新token - 确保内存和存储同步
        const atomicTokenUpdate = () => {
          accessToken.value = access_token
          localStorage.setItem('access_token', access_token)
        }
        
        try {
          atomicTokenUpdate()
          console.log('token刷新成功')
          return access_token
        } catch (updateError) {
          console.error('token更新失败:', updateError)
          // 刷新失败，清除登录状态
          clearUser()
          clearTokens()
          throw updateError
        }
      }
      
      // 刷新失败，清除登录状态
      console.warn('token刷新失败，清除认证状态')
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
   * 初始化用户状态（从本地存储恢复）- 增强版本
   */
  function initUserState() {
    try {
      const storedToken = localStorage.getItem('access_token')
      const storedRefreshToken = localStorage.getItem('refresh_token')
      const storedUserStr = localStorage.getItem('user')
      
      console.log('初始化用户状态 - token存在:', !!storedToken, 'user存在:', !!storedUserStr)
      
      // 优先检查token存在性（符合Requirements 1.3 - 优先验证token而非用户对象）
      if (storedToken) {
        // 原子性恢复状态
        accessToken.value = storedToken
        refreshToken.value = storedRefreshToken || ''
        
        // 尝试恢复用户信息
        if (storedUserStr) {
          try {
            const userData = JSON.parse(storedUserStr)
            user.value = userData
            console.log('用户状态完整恢复成功:', userData.username)
            return
          } catch (parseError) {
            console.error('解析用户信息失败，清除损坏的用户数据:', parseError)
            // 解析失败但有token，清除用户信息但保留token
            localStorage.removeItem('user')
            user.value = null
          }
        }
        
        console.log('Token已恢复，用户信息将在需要时获取')
        return
      }
      
      // 没有token，确保清除所有认证数据
      console.log('没有token，清除所有认证数据')
      clearTokens()
      clearUser()
      
    } catch (error) {
      console.error('初始化用户状态失败:', error)
      // 发生任何错误都清除状态，确保系统处于干净状态
      clearTokens()
      clearUser()
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
