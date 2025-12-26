/**
 * localStorage 封装
 */

export const storage = {
  /**
   * 设置存储项
   */
  set(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value))
    } catch (error) {
      console.error('存储失败:', error)
    }
  },

  /**
   * 获取存储项
   */
  get(key) {
    try {
      const value = localStorage.getItem(key)
      return value ? JSON.parse(value) : null
    } catch (error) {
      console.error('读取失败:', error)
      return null
    }
  },

  /**
   * 移除存储项
   */
  remove(key) {
    try {
      localStorage.removeItem(key)
    } catch (error) {
      console.error('移除失败:', error)
    }
  },

  /**
   * 清空所有存储
   */
  clear() {
    try {
      localStorage.clear()
    } catch (error) {
      console.error('清空失败:', error)
    }
  }
}

export default storage
