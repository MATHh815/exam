<template>
  <div class="daily-task-list">
    <div class="task-header">
      <div class="header-left">
        <CheckSquare class="header-icon" />
        <h2>每日任务</h2>
      </div>
      <div class="header-right">
        <el-tag :type="completionTagType" size="large">
          {{ completedCount }} / {{ tasks.length }} 完成
        </el-tag>
        <div class="total-points">
          <Coins class="coin-icon" />
          <span>今日可获得 {{ totalAvailablePoints }} 积分</span>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="5" animated />
    </div>

    <div v-else-if="tasks.length === 0" class="empty-state">
      <Calendar class="empty-icon" />
      <p>今日任务尚未生成</p>
    </div>

    <div v-else class="task-list">
      <div 
        v-for="task in tasks" 
        :key="task.id"
        class="task-item"
        :class="{ 'completed': task.is_completed }"
      >
        <div class="task-icon">
          <component :is="getTaskIcon(task.task_type)" class="icon" />
        </div>

        <div class="task-content">
          <div class="task-title">{{ task.title }}</div>
          <div class="task-description">{{ task.description }}</div>
          
          <div class="task-progress">
            <el-progress 
              :percentage="getProgressPercentage(task)" 
              :stroke-width="8"
              :color="getProgressColor(task)"
              :status="task.is_completed ? 'success' : undefined"
            />
            <span class="progress-text">
              {{ task.current_progress }} / {{ task.target_value }}
            </span>
          </div>
        </div>

        <div class="task-reward">
          <div class="reward-points">
            <Coins class="coin-icon" />
            <span>+{{ task.points_reward }}</span>
          </div>
          <el-button 
            v-if="task.is_completed"
            type="success"
            size="small"
            disabled
            :icon="CheckCircle"
          >
            已完成
          </el-button>
        </div>
      </div>
    </div>

    <div v-if="stats" class="task-stats">
      <div class="stat-item">
        <TrendingUp class="stat-icon" />
        <div class="stat-content">
          <div class="stat-value">{{ stats.total_completed }}</div>
          <div class="stat-label">累计完成</div>
        </div>
      </div>
      <div class="stat-item">
        <Flame class="stat-icon" />
        <div class="stat-content">
          <div class="stat-value">{{ stats.streak_days }}</div>
          <div class="stat-label">连续天数</div>
        </div>
      </div>
      <div class="stat-item">
        <Award class="stat-icon" />
        <div class="stat-content">
          <div class="stat-value">{{ stats.total_points_earned }}</div>
          <div class="stat-label">累计积分</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { 
  CheckSquare, Coins, Calendar, CheckCircle, TrendingUp, 
  Flame, Award, Target, BookOpen, Clock, RotateCcw 
} from 'lucide-vue-next'
import { getTodayTasks, getTaskStats } from '@/api/dailyTasks'
import { ElMessage } from 'element-plus'

const tasks = ref([])
const stats = ref(null)
const loading = ref(false)

const taskIconMap = {
  'daily_practice': Target,
  'daily_questions': CheckCircle,
  'daily_study_time': Clock,
  'daily_notes': BookOpen,
  'daily_review': RotateCcw
}

const completedCount = computed(() => {
  return tasks.value.filter(t => t.is_completed).length
})

const totalAvailablePoints = computed(() => {
  return tasks.value
    .filter(t => !t.is_completed)
    .reduce((sum, t) => sum + t.points_reward, 0)
})

const completionTagType = computed(() => {
  const rate = completedCount.value / tasks.value.length
  if (rate === 1) return 'success'
  if (rate >= 0.5) return 'warning'
  return 'info'
})

const getTaskIcon = (taskType) => {
  return taskIconMap[taskType] || CheckSquare
}

const getProgressPercentage = (task) => {
  if (task.target_value === 0) return 0
  return Math.min(100, Math.floor((task.current_progress / task.target_value) * 100))
}

const getProgressColor = (task) => {
  if (task.is_completed) return '#67c23a'
  const percentage = getProgressPercentage(task)
  if (percentage >= 80) return '#e6a23c'
  if (percentage >= 50) return '#409eff'
  return '#909399'
}

const loadTasks = async () => {
  loading.value = true
  try {
    const response = await getTodayTasks()
    if (response.data.success) {
      tasks.value = response.data.data
    }
  } catch (error) {
    console.error('加载每日任务失败:', error)
    ElMessage.error('加载每日任务失败')
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const response = await getTaskStats()
    if (response.data.success) {
      stats.value = response.data.data
    }
  } catch (error) {
    console.error('加载任务统计失败:', error)
  }
}

onMounted(() => {
  loadTasks()
  loadStats()
})

defineExpose({
  refresh: () => {
    loadTasks()
    loadStats()
  }
})
</script>

<style scoped>
.daily-task-list {
  width: 100%;
}

.task-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  transition: all 0.3s ease;
}

.task-header:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-icon {
  width: 28px;
  height: 28px;
  color: #409eff;
  filter: drop-shadow(0 0 8px rgba(64, 158, 255, 0.6));
}

.task-header h2 {
  margin: 0;
  font-size: 24px;
  color: white;
  font-weight: 600;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.total-points {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: linear-gradient(135deg, rgba(255, 215, 0, 0.2) 0%, rgba(255, 237, 78, 0.2) 100%);
  border: 1px solid rgba(255, 215, 0, 0.3);
  border-radius: 20px;
  font-weight: 600;
  color: #ffd700;
  backdrop-filter: blur(10px);
}

.coin-icon {
  width: 18px;
  height: 18px;
  filter: drop-shadow(0 0 6px rgba(255, 215, 0, 0.6));
}

.loading-container {
  padding: 20px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: rgba(255, 255, 255, 0.5);
}

.empty-icon {
  width: 64px;
  height: 64px;
  margin-bottom: 16px;
  opacity: 0.3;
  color: rgba(255, 255, 255, 0.5);
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  transition: all 0.3s ease;
}

.task-item:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(64, 158, 255, 0.5);
  box-shadow: 0 8px 32px rgba(64, 158, 255, 0.2);
  transform: translateY(-2px);
}

.task-item.completed {
  background: linear-gradient(135deg, rgba(103, 194, 58, 0.1) 0%, rgba(133, 206, 97, 0.1) 100%);
  border-color: rgba(103, 194, 58, 0.5);
  box-shadow: 0 4px 16px rgba(103, 194, 58, 0.2);
}

.task-item.completed:hover {
  background: linear-gradient(135deg, rgba(103, 194, 58, 0.15) 0%, rgba(133, 206, 97, 0.15) 100%);
  box-shadow: 0 8px 32px rgba(103, 194, 58, 0.3);
}

.task-icon {
  width: 48px;
  height: 48px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
}

.task-item.completed .task-icon {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
  box-shadow: 0 4px 12px rgba(103, 194, 58, 0.4);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 4px 12px rgba(103, 194, 58, 0.4);
  }
  50% {
    box-shadow: 0 4px 20px rgba(103, 194, 58, 0.6);
  }
}

.icon {
  width: 24px;
  height: 24px;
  color: white;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

.task-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.task-title {
  font-size: 16px;
  font-weight: 600;
  color: white;
}

.task-description {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

.task-progress {
  display: flex;
  align-items: center;
  gap: 12px;
}

.task-progress :deep(.el-progress) {
  flex: 1;
}

.task-progress :deep(.el-progress__text) {
  color: white !important;
}

.progress-text {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
  white-space: nowrap;
}

.task-reward {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.reward-points {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 12px;
  background: linear-gradient(135deg, rgba(255, 215, 0, 0.2) 0%, rgba(255, 237, 78, 0.2) 100%);
  border: 1px solid rgba(255, 215, 0, 0.3);
  border-radius: 16px;
  font-weight: 600;
  font-size: 14px;
  color: #ffd700;
  backdrop-filter: blur(10px);
}

.reward-points .coin-icon {
  filter: drop-shadow(0 0 6px rgba(255, 215, 0, 0.6));
}

.task-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  padding: 24px;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  color: white;
  position: relative;
  overflow: hidden;
}

.task-stats::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  z-index: -1;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.stat-item:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

.stat-icon {
  width: 32px;
  height: 32px;
  opacity: 0.9;
  filter: drop-shadow(0 2px 8px rgba(255, 255, 255, 0.3));
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  line-height: 1;
  margin-bottom: 4px;
  background: linear-gradient(135deg, #fff 0%, rgba(255, 255, 255, 0.8) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-label {
  font-size: 12px;
  opacity: 0.7;
  color: rgba(255, 255, 255, 0.8);
}

/* Element Plus dark theme overrides */
:deep(.el-tag) {
  background: rgba(255, 255, 255, 0.1) !important;
  border-color: rgba(255, 255, 255, 0.2) !important;
  color: white !important;
}

:deep(.el-tag.el-tag--success) {
  background: rgba(103, 194, 58, 0.2) !important;
  border-color: rgba(103, 194, 58, 0.5) !important;
  color: #67c23a !important;
}

:deep(.el-tag.el-tag--warning) {
  background: rgba(230, 162, 60, 0.2) !important;
  border-color: rgba(230, 162, 60, 0.5) !important;
  color: #e6a23c !important;
}

:deep(.el-tag.el-tag--info) {
  background: rgba(144, 147, 153, 0.2) !important;
  border-color: rgba(144, 147, 153, 0.5) !important;
  color: #909399 !important;
}

:deep(.el-button) {
  background: rgba(255, 255, 255, 0.1) !important;
  border-color: rgba(255, 255, 255, 0.2) !important;
  color: white !important;
}

:deep(.el-button.is-disabled) {
  background: rgba(103, 194, 58, 0.2) !important;
  border-color: rgba(103, 194, 58, 0.5) !important;
  color: #67c23a !important;
}

:deep(.el-skeleton) {
  background: rgba(255, 255, 255, 0.05) !important;
}

:deep(.el-skeleton__item) {
  background: rgba(255, 255, 255, 0.1) !important;
}

@media (max-width: 768px) {
  .task-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .header-right {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
  }

  .task-item {
    flex-direction: column;
    text-align: center;
  }

  .task-stats {
    grid-template-columns: 1fr;
  }
}
</style>
