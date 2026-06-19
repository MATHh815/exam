import { ref, onMounted, onUnmounted } from 'vue'

/**
 * 响应式断点
 */
export const Breakpoints = {
  XS: 480,
  SM: 768,
  MD: 1024,
  LG: 1280,
  XL: 1920
}

/**
 * 获取当前屏幕尺寸类型
 */
export function getScreenSize() {
  const width = window.innerWidth

  if (width < Breakpoints.XS) {
    return 'xs'
  } else if (width < Breakpoints.SM) {
    return 'sm'
  } else if (width < Breakpoints.MD) {
    return 'md'
  } else if (width < Breakpoints.LG) {
    return 'lg'
  } else {
    return 'xl'
  }
}

/**
 * 检查是否为移动设备
 */
export function isMobile() {
  return window.innerWidth < Breakpoints.SM
}

/**
 * 检查是否为平板设备
 */
export function isTablet() {
  const width = window.innerWidth
  return width >= Breakpoints.SM && width < Breakpoints.MD
}

/**
 * 检查是否为桌面设备
 */
export function isDesktop() {
  return window.innerWidth >= Breakpoints.MD
}

/**
 * 响应式 Hook - 监听屏幕尺寸变化
 */
export function useResponsive() {
  const screenSize = ref(getScreenSize())
  const width = ref(window.innerWidth)
  const height = ref(window.innerHeight)

  function handleResize() {
    screenSize.value = getScreenSize()
    width.value = window.innerWidth
    height.value = window.innerHeight
  }

  onMounted(() => {
    window.addEventListener('resize', handleResize)
  })

  onUnmounted(() => {
    window.removeEventListener('resize', handleResize)
  })

  return {
    screenSize,
    width,
    height,
    isMobile: () => screenSize.value === 'xs' || screenSize.value === 'sm',
    isTablet: () => screenSize.value === 'md',
    isDesktop: () => screenSize.value === 'lg' || screenSize.value === 'xl'
  }
}

/**
 * 媒体查询 Hook
 */
export function useMediaQuery(query) {
  const matches = ref(false)
  let mediaQuery = null

  function handleChange(e) {
    matches.value = e.matches
  }

  onMounted(() => {
    mediaQuery = window.matchMedia(query)
    matches.value = mediaQuery.matches
    mediaQuery.addEventListener('change', handleChange)
  })

  onUnmounted(() => {
    if (mediaQuery) {
      mediaQuery.removeEventListener('change', handleChange)
    }
  })

  return matches
}

/**
 * 防抖函数
 */
export function debounce(fn, delay = 300) {
  let timer = null
  return function (...args) {
    if (timer) {
      clearTimeout(timer)
    }
    timer = setTimeout(() => {
      fn.apply(this, args)
    }, delay)
  }
}

/**
 * 节流函数
 */
export function throttle(fn, delay = 300) {
  let lastTime = 0
  return function (...args) {
    const now = Date.now()
    if (now - lastTime >= delay) {
      fn.apply(this, args)
      lastTime = now
    }
  }
}
