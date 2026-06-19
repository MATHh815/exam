<template>
  <el-card class="study-plan-card" :class="{ 'is-active': plan.is_active }">
    <template #header>
      <div class="card-header">
        <div class="header-left">
          <el-tag :type="plan.is_active ? 'success' : 'info'" size="small">
            {{ plan.is_active ? '进行中' : '已完成' }}
          </el-tag>
          <span class="plan-name">{{ plan.name }}</span>
        </div>
        <div class="header-right">
          <el-button link type="primary" @click="$emit('view', plan)">
            <el-icon><View /></el-icon>
          </el-button>
          <el-button link type="primary" @click="$emit('edit', plan)">
            <el-icon><Edit /></el-icon>
          </el-button>
          <el-button link type="danger" @click="$emit('delete', plan)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
      </div>
    </template>

    <div class="plan-info">
      <div class="info-item">
        <el-icon><Calendar /></el-icon>
        <span>{{ formatDate(plan.start_date) }} - {{ formatDate(plan.end_date) }}</span>
      </div>
      <div class="info-item">
        <el-icon><Trophy /></el-icon>
        <span>考试类型：{{ plan.exam_type }}</span>
      </div>
      <div class="info-item" v-if="plan.description">
        <el-icon><Document /></el-icon>
        <span>{{ plan.description }}</span>
      </div>
    </div>

    <div class="goals-section" v-if="plan.goals && plan.goals.length > 0">
      <div class="section-title">学习目标</div>
      <div class="goals-list">
        <div v-for="goal in plan.goals" :key="goal.id" class="goal-item">
          <div class="goal-header">
            <span class="goal-type">{{ getGoalTypeLabel(goal.goal_type) }}</span>
            <span class="goal-progress">{{ goal.current_value }} / {{ goal.target_value }}</span>
          </div>
          <el-progress 
            :percentage="getGoalProgress(goal)" 
            :status="goal.is_completed ? 'success' : ''"
            :stroke-width="8"
          />
        </div>
      </div>
    </div>

    <div class="plan-footer">
      <span class="created-time">创建于 {{ formatDate(plan.created_at) }}</span>
      <el-button type="primary" size="small" @click="$emit('view-report', plan)">
        查看报告
      </el-button>
    </div>
  </el-card>
</template>

<script setup>
import { computed } from 'vue'
import { Calendar, Trophy, Document, View, Edit, Delete } from '@element-plus/icons-vue'

const props = defineProps({
  plan: {
    type: Object,
    required: true
  }
})

defineEmits(['view', 'edit', 'delete', 'view-report'])

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

const getGoalTypeLabel = (type) => {
  const labels = {
    'daily_practice': '每日练习',
    'weekly_practice': '每周练习',
    'daily_duration': '每日学习时长',
    'exam_count': '考试次数'
  }
  return labels[type] || type
}

const getGoalProgress = (goal) => {
  if (goal.target_value === 0) return 0
  return Math.min(100, Math.round((goal.current_value / goal.target_value) * 100))
}
</script>

<style scoped>
.study-plan-card {
  margin-bottom: 16px;
  transition: all 0.3s;
}

.study-plan-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.study-plan-card.is-active {
  border-left: 4px solid var(--el-color-primary);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.plan-name {
  font-size: 16px;
  font-weight: 600;
}

.header-right {
  display: flex;
  gap: 4px;
}

.plan-info {
  margin-bottom: 16px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  color: var(--el-text-color-regular);
  font-size: 14px;
}

.goals-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--el-text-color-primary);
}

.goals-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.goal-item {
  padding: 8px;
  background: var(--el-fill-color-light);
  border-radius: 4px;
}

.goal-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 13px;
}

.goal-type {
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.goal-progress {
  color: var(--el-text-color-secondary);
}

.plan-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.created-time {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}
</style>
