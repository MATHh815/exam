<template>
  <div class="daily-goals">
    <div class="goals-header">
      <h3>今日目标</h3>
      <span class="goals-date">{{ currentDate }}</span>
    </div>

    <div class="goals-list">
      <div 
        v-for="(goal, index) in goals" 
        :key="index"
        class="goal-item"
        :class="{ completed: goal.completed }"
      >
        <div class="goal-info">
          <div class="goal-icon" :style="{ background: goal.color }">
            <component :is="goal.icon" />
          </div>
          <div class="goal-content">
            <div class="goal-title">{{ goal.title }}</div>
            <div class="goal-progress-text">
              {{ goal.current }} / {{ goal.target }} {{ goal.unit }}
            </div>
          </div>
        </div>

        <div class="goal-progress-bar">
          <div 
            class="progress-fill" 
            :style="{ 
              width: getProgressPercent(goal) + '%',
              background: goal.color
            }"
          >
            <span class="progress-percent">{{ getProgressPercent(goal) }}%</span>
          </div>
        </div>

        <div v-if="goal.completed" class="goal-badge">
          <el-icon><CircleCheck /></el-icon>
          <span>已完成</span>
        </div>
      </div>
    </div>

    <div class="goals-summary">
      <div class="summary-item">
        <span class="summary-label">总进度</span>
        <span class="summary-value">{{ overallProgress }}%</span>
      </div>
      <div class="summary-item">
        <span class="summary-label">已完成</span>
        <span class="summary-value">{{ completedCount }}/{{ goals.length }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { CircleCheck, EditPen, Clock, TrendCharts } from '@element-plus/icons-vue'
import dayjs from 'dayjs'

const props = defineProps({
  goals: {
    type: Array,
    default: () => [
      {
        title: '练习题目',
        current: 35,
        target: 50,
        unit: '题',
        icon: EditPen,
        color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        completed: false
      },
      {
        title: '学习时长',
        current: 80,
        target: 120,
        unit: '分钟',
        icon: Clock,
        color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
        completed: false
      },
      {
        title: '正确率',
        current: 88,
        target: 85,
        unit: '%',
        icon: TrendCharts,
        color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
        completed: true
      }
    ]
  }
})

const currentDate = computed(() => {
  return dayjs().format('YYYY年MM月DD日')
})

const completedCount = computed(() => {
  return props.goals.filter(g => g.completed).length
})

const overallProgress = computed(() => {
  if (props.goals.length === 0) return 0
  const total = props.goals.reduce((sum, goal) => {
    return sum + getProgressPercent(goal)
  }, 0)
  return Math.round(total / props.goals.length)
})

function getProgressPercent(goal) {
  if (goal.target === 0) return 0
  const percent = (goal.current / goal.target) * 100
  return Math.min(Math.round(percent), 100)
}
</script>

<style scoped>
.daily-goals {
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
}

.goals-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.goals-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  margin: 0;
}

.goals-date {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

.goals-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 20px;
}

.goal-item {
  position: relative;
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  transition: all 0.3s;
}

.goal-item:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(102, 126, 234, 0.3);
  transform: translateX(4px);
}

.goal-item.completed {
  border-color: rgba(16, 185, 129, 0.3);
}

.goal-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.goal-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 18px;
  flex-shrink: 0;
}

.goal-content {
  flex: 1;
  min-width: 0;
}

.goal-title {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 4px;
}

.goal-progress-text {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.goal-progress-bar {
  position: relative;
  height: 8px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  position: relative;
  height: 100%;
  border-radius: 4px;
  transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 8px;
}

.progress-percent {
  font-size: 10px;
  font-weight: 600;
  color: #fff;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.goal-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: rgba(16, 185, 129, 0.2);
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: 6px;
  font-size: 11px;
  color: #10b981;
  font-weight: 600;
}

.goals-summary {
  display: flex;
  gap: 20px;
  padding-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.summary-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
  text-align: center;
}

.summary-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.summary-value {
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(90deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

@media (max-width: 768px) {
  .daily-goals {
    padding: 16px;
  }

  .goal-item {
    padding: 12px;
  }

  .goal-icon {
    width: 36px;
    height: 36px;
    font-size: 16px;
  }

  .goal-badge {
    position: static;
    margin-top: 8px;
    align-self: flex-start;
  }
}
</style>
