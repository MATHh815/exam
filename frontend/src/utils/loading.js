import { ElLoading } from 'element-plus'

let loadingInstance = null

/**
 * 显示全局加载状态
 * @param {string} text - 加载文本
 * @param {object} options - 加载选项
 */
export function showLoading(text = '加载中...', options = {}) {
  if (loadingInstance) {
    return loadingInstance
  }

  loadingInstance = ElLoading.service({
    lock: true,
    text,
    background: 'rgba(0, 0, 0, 0.7)',
    ...options
  })

  return loadingInstance
}

/**
 * 隐藏全局加载状态
 */
export function hideLoading() {
  if (loadingInstance) {
    loadingInstance.close()
    loadingInstance = null
  }
}

/**
 * 包装异步函数，自动显示/隐藏加载状态
 * @param {Function} asyncFn - 异步函数
 * @param {string} loadingText - 加载文本
 */
export async function withLoading(asyncFn, loadingText = '加载中...') {
  showLoading(loadingText)
  try {
    const result = await asyncFn()
    return result
  } finally {
    hideLoading()
  }
}
