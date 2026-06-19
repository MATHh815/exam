<template>
  <div class="daily-tasks-page">
    <div class="page-header">
      <h1>
        <CheckSquare class="page-icon" />
        每日任务
      </h1>
      <p class="page-description">完成每日任务，获取积分奖励，保持学习习惯</p>
    </div>

    <DailyTaskList ref="taskListRef" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { CheckSquare } from 'lucide-vue-next'
import DailyTaskList from '@/components/DailyTaskList.vue'

const taskListRef = ref(null)
</script>

<style scoped>
.daily-tasks-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

.page-header {
  margin-bottom: 32px;
  text-align: center;
}

.page-header h1 {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 12px 0;
  color: #fff;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-icon {
  width: 36px;
  height: 36px;
  color: #667eea;
  filter: drop-shadow(0 0 8px rgba(102, 126, 234, 0.5));
}

.page-description {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}

@media (max-width: 768px) {
  .daily-tasks-page {
    padding: 16px;
  }

  .page-header h1 {
    font-size: 24px;
  }
}
</style>
