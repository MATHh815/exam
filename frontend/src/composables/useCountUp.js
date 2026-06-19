/**
 * 数字滚动动画 Hook
 * 使用 GSAP 实现平滑的数字增长动画
 */
import { ref, watch, onMounted } from 'vue'
import { gsap } from 'gsap'

export function useCountUp(target, options = {}) {
  const {
    duration = 1.5,
    delay = 0,
    ease = 'power2.out',
    decimals = 0,
    onComplete = null
  } = options

  const displayValue = ref(0)
  const tweenObject = ref({ value: 0 })

  const startAnimation = (endValue) => {
    gsap.to(tweenObject.value, {
      value: endValue,
      duration,
      delay,
      ease,
      onUpdate: () => {
        displayValue.value = tweenObject.value.value.toFixed(decimals)
      },
      onComplete: () => {
        if (onComplete) onComplete()
      }
    })
  }

  watch(() => target.value, (newValue) => {
    if (newValue !== undefined && newValue !== null) {
      startAnimation(newValue)
    }
  }, { immediate: true })

  return {
    displayValue
  }
}
