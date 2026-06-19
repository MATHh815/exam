<template>
  <div class="lazy-image" :class="{ loaded: isLoaded, error: hasError }">
    <img
      v-if="!hasError"
      :src="currentSrc"
      :alt="alt"
      :class="imageClass"
      @load="handleLoad"
      @error="handleError"
    />
    <div v-if="!isLoaded && !hasError" class="image-placeholder">
      <el-icon class="loading-icon" :size="40">
        <Loading />
      </el-icon>
    </div>
    <div v-if="hasError" class="image-error">
      <el-icon class="error-icon" :size="40">
        <Picture />
      </el-icon>
      <p>图片加载失败</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Loading, Picture } from '@element-plus/icons-vue'

const props = defineProps({
  src: {
    type: String,
    required: true
  },
  alt: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: ''
  },
  imageClass: {
    type: String,
    default: ''
  },
  lazy: {
    type: Boolean,
    default: true
  }
})

const currentSrc = ref(props.placeholder || '')
const isLoaded = ref(false)
const hasError = ref(false)
let observer = null

/**
 * 加载图片
 */
function loadImage() {
  currentSrc.value = props.src
}

/**
 * 处理图片加载完成
 */
function handleLoad() {
  isLoaded.value = true
}

/**
 * 处理图片加载错误
 */
function handleError() {
  hasError.value = true
}

onMounted(() => {
  if (!props.lazy) {
    // 不使用懒加载，直接加载图片
    loadImage()
    return
  }

  // 使用 Intersection Observer 实现懒加载
  if ('IntersectionObserver' in window) {
    observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            loadImage()
            observer.disconnect()
          }
        })
      },
      {
        rootMargin: '50px'
      }
    )

    const element = document.querySelector('.lazy-image')
    if (element) {
      observer.observe(element)
    }
  } else {
    // 不支持 Intersection Observer，直接加载
    loadImage()
  }
})

onUnmounted(() => {
  if (observer) {
    observer.disconnect()
  }
})
</script>

<style scoped>
.lazy-image {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background-color: #f5f7fa;
}

.lazy-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.lazy-image.loaded img {
  opacity: 1;
}

.image-placeholder,
.image-error {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: #f5f7fa;
}

.loading-icon {
  color: #909399;
  animation: rotate 1.5s linear infinite;
}

.error-icon {
  color: #f56c6c;
  margin-bottom: 10px;
}

.image-error p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
