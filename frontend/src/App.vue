<template>
  <div id="app">
    <ErrorBoundary>
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </ErrorBoundary>
    
    <!-- AI 智能助手（全局悬浮） -->
    <AIChat v-if="showAIChat" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onErrorCaptured } from 'vue'
import { useRoute } from 'vue-router'
import ErrorBoundary from './components/ErrorBoundary.vue'
import AIChat from './components/AIChat.vue'
import { handleError } from './utils/errorHandler'

const route = useRoute()

// 在某些页面不显示 AI 助手（如登录、注册页、考试页、练习页 - 这些页面有自己的 AI 助手）
const showAIChat = computed(() => {
  const hiddenRoutes = ['login', 'register', 'notFound', 'exam', 'practice']
  return !hiddenRoutes.includes(route.name)
})

/**
 * 全局错误捕获
 */
onErrorCaptured((err, instance, info) => {
  console.error('全局错误捕获:', err, info)
  handleError(err, {
    showMessage: true,
    logToConsole: true
  })
  return false
})

/**
 * 监听未捕获的 Promise 错误
 */
onMounted(() => {
  window.addEventListener('unhandledrejection', event => {
    console.error('未处理的 Promise 错误:', event.reason)
    handleError(event.reason, {
      showMessage: true,
      customMessage: '发生了未处理的错误'
    })
  })
})
</script>

<style>
/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  font-size: 16px;
}

body {
  margin: 0;
  padding: 0;
  overflow-x: hidden;
  background: linear-gradient(135deg, #0a0a1a 0%, #1a0a2e 50%, #0c1445 100%);
  min-height: 100vh;
}

#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    'Noto Sans', sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol',
    'Noto Color Emoji';
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  min-height: 100vh;
  background: transparent;
}

/* 页面过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 响应式字体大小 */
@media (max-width: 1200px) {
  html {
    font-size: 15px;
  }
}

@media (max-width: 768px) {
  html {
    font-size: 14px;
  }
}

@media (max-width: 480px) {
  html {
    font-size: 13px;
  }
}

/* 滚动条样式 - 深色主题 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
}

::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* 全局工具类 */
.text-center {
  text-align: center;
}

.text-left {
  text-align: left;
}

.text-right {
  text-align: right;
}

.mt-10 {
  margin-top: 10px;
}

.mt-20 {
  margin-top: 20px;
}

.mb-10 {
  margin-bottom: 10px;
}

.mb-20 {
  margin-bottom: 20px;
}

.p-10 {
  padding: 10px;
}

.p-20 {
  padding: 20px;
}

/* 响应式容器 */
.container {
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
}

@media (max-width: 768px) {
  .container {
    padding: 0 15px;
  }
}

@media (max-width: 480px) {
  .container {
    padding: 0 10px;
  }
}

/* 隐藏类 */
.hidden-xs {
  display: block;
}

@media (max-width: 768px) {
  .hidden-xs {
    display: none !important;
  }
}

.visible-xs {
  display: none;
}

@media (max-width: 768px) {
  .visible-xs {
    display: block !important;
  }
}

/* Element Plus 响应式覆盖 */
@media (max-width: 768px) {
  .el-dialog {
    width: 90% !important;
    margin-top: 5vh !important;
  }
  
  .el-message-box {
    width: 90% !important;
  }
  
  .el-drawer {
    width: 80% !important;
  }
}
</style>
