import { ElMessage, ElNotification } from 'element-plus'

/**
 * 错误类型枚举
 */
export const ErrorType = {
  NETWORK: 'network',
  AUTH: 'auth',
  VALIDATION: 'validation',
  SERVER: 'server',
  UNKNOWN: 'unknown'
}

/**
 * 错误处理器类
 */
class ErrorHandler {
  /**
   * 处理错误
   * @param {Error} error - 错误对象
   * @param {object} options - 处理选项
   */
  handle(error, options = {}) {
    const {
      showMessage = true,
      showNotification = false,
      logToConsole = true,
      customMessage = null
    } = options

    // 记录到控制台
    if (logToConsole) {
      console.error('错误:', error)
    }

    // 确定错误类型和消息
    const { type, message } = this.parseError(error)

    // 显示错误消息
    if (showMessage) {
      ElMessage.error({
        message: customMessage || message,
        duration: 3000,
        showClose: true
      })
    }

    // 显示通知
    if (showNotification) {
      ElNotification.error({
        title: '错误',
        message: customMessage || message,
        duration: 5000
      })
    }

    return { type, message }
  }

  /**
   * 解析错误
   * @param {Error} error - 错误对象
   */
  parseError(error) {
    // 网络错误
    if (!error.response && error.message === 'Network Error') {
      return {
        type: ErrorType.NETWORK,
        message: '网络连接失败，请检查网络设置'
      }
    }

    // HTTP 响应错误
    if (error.response) {
      const { status, data } = error.response

      switch (status) {
        case 400:
          return {
            type: ErrorType.VALIDATION,
            message: data?.error?.message || '请求参数错误'
          }
        case 401:
          return {
            type: ErrorType.AUTH,
            message: '未授权，请重新登录'
          }
        case 403:
          return {
            type: ErrorType.AUTH,
            message: '没有权限访问该资源'
          }
        case 404:
          return {
            type: ErrorType.VALIDATION,
            message: '请求的资源不存在'
          }
        case 409:
          return {
            type: ErrorType.VALIDATION,
            message: data?.error?.message || '数据冲突'
          }
        case 500:
        case 502:
        case 503:
          return {
            type: ErrorType.SERVER,
            message: '服务器错误，请稍后重试'
          }
        default:
          return {
            type: ErrorType.UNKNOWN,
            message: data?.error?.message || '请求失败'
          }
      }
    }

    // 超时错误
    if (error.code === 'ECONNABORTED') {
      return {
        type: ErrorType.NETWORK,
        message: '请求超时，请重试'
      }
    }

    // 其他错误
    return {
      type: ErrorType.UNKNOWN,
      message: error.message || '发生未知错误'
    }
  }

  /**
   * 处理验证错误
   * @param {object} errors - 验证错误对象
   */
  handleValidationErrors(errors) {
    if (!errors || typeof errors !== 'object') {
      return
    }

    const messages = Object.entries(errors)
      .map(([field, message]) => `${field}: ${message}`)
      .join('\n')

    ElNotification.error({
      title: '表单验证失败',
      message: messages,
      duration: 5000
    })
  }

  /**
   * 处理批量错误
   * @param {Array} errors - 错误数组
   */
  handleBatchErrors(errors) {
    if (!Array.isArray(errors) || errors.length === 0) {
      return
    }

    const errorMessages = errors
      .map((err, index) => `${index + 1}. ${err.message || err}`)
      .join('\n')

    ElNotification.error({
      title: `发生 ${errors.length} 个错误`,
      message: errorMessages,
      duration: 8000
    })
  }
}

// 创建单例
const errorHandler = new ErrorHandler()

/**
 * 全局错误处理函数
 */
export function handleError(error, options) {
  return errorHandler.handle(error, options)
}

/**
 * 处理验证错误
 */
export function handleValidationErrors(errors) {
  return errorHandler.handleValidationErrors(errors)
}

/**
 * 处理批量错误
 */
export function handleBatchErrors(errors) {
  return errorHandler.handleBatchErrors(errors)
}

export default errorHandler
