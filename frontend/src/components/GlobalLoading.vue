<template>
  <transition name="fade">
    <div v-if="visible" class="global-loading-overlay">
      <div class="loading-content">
        <el-icon class="loading-icon" :size="50">
          <Loading />
        </el-icon>
        <p class="loading-text">{{ text }}</p>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref } from 'vue'
import { Loading } from '@element-plus/icons-vue'

const visible = ref(false)
const text = ref('加载中...')

/**
 * 显示加载状态
 */
function show(loadingText = '加载中...') {
  text.value = loadingText
  visible.value = true
}

/**
 * 隐藏加载状态
 */
function hide() {
  visible.value = false
}

// 暴露方法供外部调用
defineExpose({
  show,
  hide
})
</script>

<style scoped>
.global-loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.loading-content {
  text-align: center;
  color: white;
}

.loading-icon {
  animation: rotate 1.5s linear infinite;
  margin-bottom: 15px;
}

.loading-text {
  font-size: 16px;
  margin: 0;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
