/**
 * 性能监控工具
 */

/**
 * 测量函数执行时间
 */
export function measureTime(fn, label = 'Function') {
  const start = performance.now()
  const result = fn()
  const end = performance.now()
  console.log(`${label} 执行时间: ${(end - start).toFixed(2)}ms`)
  return result
}

/**
 * 测量异步函数执行时间
 */
export async function measureAsyncTime(fn, label = 'Async Function') {
  const start = performance.now()
  const result = await fn()
  const end = performance.now()
  console.log(`${label} 执行时间: ${(end - start).toFixed(2)}ms`)
  return result
}

/**
 * 获取页面性能指标
 */
export function getPerformanceMetrics() {
  if (!window.performance || !window.performance.timing) {
    console.warn('Performance API 不支持')
    return null
  }

  const timing = window.performance.timing
  const metrics = {
    // DNS 查询时间
    dns: timing.domainLookupEnd - timing.domainLookupStart,
    // TCP 连接时间
    tcp: timing.connectEnd - timing.connectStart,
    // 请求时间
    request: timing.responseStart - timing.requestStart,
    // 响应时间
    response: timing.responseEnd - timing.responseStart,
    // DOM 解析时间
    domParse: timing.domInteractive - timing.domLoading,
    // DOM 内容加载完成时间
    domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
    // 页面完全加载时间
    pageLoad: timing.loadEventEnd - timing.navigationStart,
    // 首次渲染时间
    firstPaint: 0,
    // 首次内容渲染时间
    firstContentfulPaint: 0
  }

  // 获取 Paint Timing
  if (window.performance.getEntriesByType) {
    const paintEntries = window.performance.getEntriesByType('paint')
    paintEntries.forEach((entry) => {
      if (entry.name === 'first-paint') {
        metrics.firstPaint = entry.startTime
      } else if (entry.name === 'first-contentful-paint') {
        metrics.firstContentfulPaint = entry.startTime
      }
    })
  }

  return metrics
}

/**
 * 打印性能指标
 */
export function logPerformanceMetrics() {
  const metrics = getPerformanceMetrics()
  if (!metrics) return

  console.group('📊 页面性能指标')
  console.log(`DNS 查询: ${metrics.dns}ms`)
  console.log(`TCP 连接: ${metrics.tcp}ms`)
  console.log(`请求时间: ${metrics.request}ms`)
  console.log(`响应时间: ${metrics.response}ms`)
  console.log(`DOM 解析: ${metrics.domParse}ms`)
  console.log(`DOM 内容加载: ${metrics.domContentLoaded}ms`)
  console.log(`页面完全加载: ${metrics.pageLoad}ms`)
  if (metrics.firstPaint) {
    console.log(`首次渲染: ${metrics.firstPaint.toFixed(2)}ms`)
  }
  if (metrics.firstContentfulPaint) {
    console.log(`首次内容渲染: ${metrics.firstContentfulPaint.toFixed(2)}ms`)
  }
  console.groupEnd()
}

/**
 * 监听页面加载完成
 */
export function onPageLoad(callback) {
  if (document.readyState === 'complete') {
    callback()
  } else {
    window.addEventListener('load', callback)
  }
}

/**
 * 获取资源加载时间
 */
export function getResourceTimings() {
  if (!window.performance || !window.performance.getEntriesByType) {
    return []
  }

  const resources = window.performance.getEntriesByType('resource')
  return resources.map((resource) => ({
    name: resource.name,
    type: resource.initiatorType,
    duration: resource.duration,
    size: resource.transferSize || 0
  }))
}

/**
 * 打印资源加载信息
 */
export function logResourceTimings() {
  const resources = getResourceTimings()
  
  console.group('📦 资源加载信息')
  console.table(resources)
  console.groupEnd()

  // 统计各类型资源
  const stats = resources.reduce((acc, resource) => {
    if (!acc[resource.type]) {
      acc[resource.type] = { count: 0, totalDuration: 0, totalSize: 0 }
    }
    acc[resource.type].count++
    acc[resource.type].totalDuration += resource.duration
    acc[resource.type].totalSize += resource.size
    return acc
  }, {})

  console.group('📊 资源统计')
  Object.entries(stats).forEach(([type, stat]) => {
    console.log(
      `${type}: ${stat.count} 个, 总时间: ${stat.totalDuration.toFixed(2)}ms, 总大小: ${(stat.totalSize / 1024).toFixed(2)}KB`
    )
  })
  console.groupEnd()
}

/**
 * 监控长任务
 */
export function observeLongTasks(callback) {
  if (!window.PerformanceObserver) {
    console.warn('PerformanceObserver 不支持')
    return null
  }

  try {
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.duration > 50) {
          callback({
            name: entry.name,
            duration: entry.duration,
            startTime: entry.startTime
          })
        }
      }
    })

    observer.observe({ entryTypes: ['longtask'] })
    return observer
  } catch (error) {
    console.warn('长任务监控不支持:', error)
    return null
  }
}

/**
 * 内存使用情况
 */
export function getMemoryUsage() {
  if (!window.performance || !window.performance.memory) {
    console.warn('Memory API 不支持')
    return null
  }

  const memory = window.performance.memory
  return {
    // 已使用的 JS 堆大小（字节）
    usedJSHeapSize: memory.usedJSHeapSize,
    // JS 堆大小限制（字节）
    jsHeapSizeLimit: memory.jsHeapSizeLimit,
    // 总的 JS 堆大小（字节）
    totalJSHeapSize: memory.totalJSHeapSize,
    // 使用率
    usagePercent: ((memory.usedJSHeapSize / memory.jsHeapSizeLimit) * 100).toFixed(2)
  }
}

/**
 * 打印内存使用情况
 */
export function logMemoryUsage() {
  const memory = getMemoryUsage()
  if (!memory) return

  console.group('💾 内存使用情况')
  console.log(`已使用: ${(memory.usedJSHeapSize / 1024 / 1024).toFixed(2)}MB`)
  console.log(`总大小: ${(memory.totalJSHeapSize / 1024 / 1024).toFixed(2)}MB`)
  console.log(`限制: ${(memory.jsHeapSizeLimit / 1024 / 1024).toFixed(2)}MB`)
  console.log(`使用率: ${memory.usagePercent}%`)
  console.groupEnd()
}

/**
 * 开启性能监控（开发环境）
 */
export function enablePerformanceMonitoring() {
  if (import.meta.env.MODE !== 'development') {
    return
  }

  // 页面加载完成后打印性能指标
  onPageLoad(() => {
    setTimeout(() => {
      logPerformanceMetrics()
      logResourceTimings()
      logMemoryUsage()
    }, 1000)
  })

  // 监控长任务
  observeLongTasks((task) => {
    console.warn(`⚠️ 检测到长任务: ${task.name}, 耗时: ${task.duration.toFixed(2)}ms`)
  })
}
