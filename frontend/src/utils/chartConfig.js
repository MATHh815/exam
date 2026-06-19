/**
 * ECharts 通用配置
 */

/**
 * 获取响应式字体大小
 */
export function getResponsiveFontSize(baseSize = 12) {
  const width = window.innerWidth
  if (width < 768) return baseSize * 0.85
  if (width < 1200) return baseSize * 0.92
  return baseSize
}

/**
 * 通用 tooltip 配置
 */
export function getTooltipConfig(formatter) {
  return {
    trigger: 'axis',
    backgroundColor: 'rgba(0, 0, 0, 0.85)',
    borderColor: 'rgba(255, 255, 255, 0.2)',
    borderWidth: 1,
    padding: [8, 12],
    textStyle: {
      color: '#fff',
      fontSize: getResponsiveFontSize(13)
    },
    formatter: formatter || undefined,
    axisPointer: {
      type: 'cross',
      crossStyle: {
        color: 'rgba(255, 255, 255, 0.3)'
      },
      lineStyle: {
        color: 'rgba(255, 255, 255, 0.2)'
      }
    }
  }
}

/**
 * 通用 grid 配置
 */
export function getGridConfig(options = {}) {
  const {
    top = 40,
    right = 20,
    bottom = 30,
    left = 50
  } = options

  return {
    top,
    right,
    bottom,
    left,
    containLabel: true
  }
}

/**
 * 通用动画配置
 */
export function getAnimationConfig() {
  return {
    animation: true,
    animationDuration: 1000,
    animationEasing: 'cubicOut',
    animationDelay: (idx) => idx * 50
  }
}

/**
 * 格式化数字
 */
export function formatNumber(num) {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + 'w'
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'k'
  }
  return num
}

/**
 * 格式化百分比
 */
export function formatPercent(value) {
  return (value * 100).toFixed(1) + '%'
}

/**
 * 格式化时间
 */
export function formatDuration(minutes) {
  if (minutes < 60) return minutes + '分钟'
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return mins > 0 ? `${hours}小时${mins}分钟` : `${hours}小时`
}
