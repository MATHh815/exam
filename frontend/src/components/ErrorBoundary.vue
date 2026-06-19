<template>
  <div class="error-boundary">
    <slot v-if="!hasError" />
    <div v-else class="error-container">
      <el-result icon="error" title="出错了" :sub-title="errorMessage">
        <template #extra>
          <el-button type="primary" @click="handleReset">重新加载</el-button>
          <el-button @click="handleGoHome">返回首页</el-button>
        </template>
      </el-result>
    </div>
  </div>
</template>

<script setup>
import { ref, onErrorCaptured } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const router = useRouter()
const hasError = ref(false)
const errorMessage = ref('')

/**
 * 捕获子组件错误
 */
onErrorCaptured((err, instance, info) => {
  console.error('捕获到错误:', err, info)
  hasError.value = true
  errorMessage.value = err.message || '发生了未知错误'
  
  // 显示错误提示
  ElMessage.error({
    message: '页面加载失败，请重试',
    duration: 3000
  })
  
  // 返回 false 阻止错误继续传播
  return false
})

/**
 * 重置错误状态
 */
function handleReset() {
  hasError.value = false
  errorMessage.value = ''
  // 刷新当前路由
  router.go(0)
}

/**
 * 返回首页
 */
function handleGoHome() {
  hasError.value = false
  errorMessage.value = ''
  router.push('/dashboard')
}
</script>

<style scoped>
.error-boundary {
  min-height: 100vh;
}

.error-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 20px;
}

@media (max-width: 768px) {
  .error-container {
    padding: 10px;
  }
  
  .error-container :deep(.el-result__title) {
    font-size: 18px;
  }
  
  .error-container :deep(.el-result__subtitle) {
    font-size: 14px;
  }
}
</style>
