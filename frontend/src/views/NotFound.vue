<template>
  <div class="not-found-container">
    <el-result icon="warning" title="404" sub-title="抱歉，您访问的页面不存在">
      <template #extra>
        <el-button type="primary" @click="goHome">返回首页</el-button>
        <el-button @click="goBack">返回上一页</el-button>
      </template>
    </el-result>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

/**
 * 返回首页
 */
function goHome() {
  router.push('/dashboard')
}

/**
 * 返回上一页
 */
function goBack() {
  router.back()
}
</script>

<style scoped>
.not-found-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 20px;
  background-color: #f5f7fa;
}

@media (max-width: 768px) {
  .not-found-container {
    padding: 10px;
  }
  
  .not-found-container :deep(.el-result__title) {
    font-size: 48px;
  }
  
  .not-found-container :deep(.el-result__subtitle) {
    font-size: 14px;
  }
}
</style>
