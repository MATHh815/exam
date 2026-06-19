<template>
  <el-card class="today-schedule-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <div class="title-section">
          <el-icon class="header-icon"><Calendar /></el-icon>
          <span class="title">今日日程</span>
        </div>
        <el-button type="primary" size="small" text @click="goToSchedule">
          查看全部
          <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>
    </template>

    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="3" animated />
    </div>

    <div v-else-if="schedules.length === 0" class="empty-state">
      <el-empty description="今天还没有日程安排" :image-size="80">
        <el-button type="primary" size="small" @click="goToSchedule">
          创建日程
        </el-button>
      </el-empty>
    </div>

    <div v-else class="schedule-list">
      <div
        v-for="schedule in displaySchedules"
        :key="schedule.id"
        class="schedule-item"
        :class="{ completed: schedule.is_completed, current: isCurrentSchedule(schedule) }"
      >
        <div class="time-badge" :class="getTimeBadgeClass(schedule)">
          <div class="time">{{ schedule.start_time }}</div>
        </div>

        <div class="schedule-content">
          <div class="schedule-header">
            <el-tag :type="getActivityTagType(schedule.activity_type)" size="small">
              {{ activityTypes[schedule.activity_type] || schedule.activity_type }}
            </el-tag>
            <el-tag v-if="schedule.subject" type="info" size="small">
              {{ subjects[schedule.subject] || schedule.subject }}
            </el-tag>
          </div>

          <div class="schedule-title">{{ schedule.title }}</div>

          <div class="schedule-meta">
            <span class="duration">
              <el-icon><Clock /></el-icon>
              {{ schedule.duration_minutes }}分钟
            </span>
            <span v-if="schedule.location" class="location">
              <el-icon><Location /></el-icon>
              {{ schedule.location }}
            </span>
          </div>
        </div>

        <div class="schedule-actions">
          <el-button
            v-if="!schedule.is_completed"
            type="success"
            size="small"
            circle
            @click="handleComplete(schedule.id)"
          >
            <el-icon><Check /></el-icon>
          </el-button>
          <el-icon v-else class="completed-icon"><CircleCheck /></el-icon>
        </div>
      </div>

      <div v-if="schedules.length > maxDisplay" class="more-indicator">
        还有 {{ schedules.length - maxDisplay }} 个日程
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Calendar, ArrowRight, Clock, Location, Check, CircleCheck
} from '@element-plus/icons-vue'
import { getTodaySchedules, getScheduleOptions, completeSchedule } from '@/api/studySchedules'

const router = useRouter()

// 状态
const loading = ref(true)
const schedules = ref([])
const activityTypes = ref({})
const subjects = ref({})
const maxDisplay = 5 // 最多显示5个

// 计算属性
const displaySchedules = computed(() => {
  return schedules.value.slice(0, maxDisplay)
})

// 方法
const fetchOptions = async () => {
  try {
    const res = await getScheduleOptions()
    if (res.success) {
      activityTypes.value = res.data.activity_types
      subjects.value = res.data.subjects
    }
  } catch (error) {
    console.error('获取选项失败:', error)
  }
}

const fetchSchedules = async () => {
  loading.value = true
  try {
    const res = await getTodaySchedules()
    if (res.success) {
      schedules.value = res.data.schedules
    }
  } catch (error) {
    console.error('获取今日日程失败:', error)
  } finally {
    loading.value = false
  }
}

const handleComplete = async (id) => {
  try {
    const res = await completeSchedule(id)
    if (res.success) {
      ElMessage.success('日程已完成')
      fetchSchedules()
    }
  } catch (error) {
    console.error('完成日程失败:', error)
    ElMessage.error('完成日程失败')
  }
}

const goToSchedule = () => {
  router.push({ name: 'studySchedule' })
}

const isCurrentSchedule = (schedule) => {
  const now = new Date()
  const currentTime = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`
  return currentTime >= schedule.start_time && currentTime < schedule.end_time
}

const getTimeBadgeClass = (schedule) => {
  if (schedule.is_completed) return 'completed'
  if (isCurrentSchedule(schedule)) return 'current'
  return ''
}

const getActivityTagType = (activityType) => {
  const typeMap = {
    memorize: 'warning',
    lecture: 'primary',
    practice: 'success',
    review: 'info',
    mock_exam: 'danger',
    reading: '',
    writing: 'warning',
    rest: 'info'
  }
  return typeMap[activityType] || ''
}

// 初始化
onMounted(() => {
  fetchOptions()
  fetchSchedules()
})
</script>

<style scoped>
.today-schedule-card {
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-section {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-icon {
  font-size: 20px;
  color: #409eff;
}

.title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.loading-container {
  padding: 20px 0;
}

.empty-state {
  padding: 20px 0;
}

.schedule-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.schedule-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
  transition: all 0.3s;
}

.schedule-item:hover {
  background: #e4e7ed;
  transform: translateX(4px);
}

.schedule-item.completed {
  opacity: 0.6;
}

.schedule-item.current {
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  border-left: 4px solid #2196f3;
}

.time-badge {
  flex-shrink: 0;
  width: 60px;
  text-align: center;
  padding: 8px;
  background: #909399;
  color: white;
  border-radius: 6px;
  font-weight: bold;
}

.time-badge.current {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  animation: pulse 2s infinite;
}

.time-badge.completed {
  background: #67c23a;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

.time-badge .time {
  font-size: 14px;
}

.schedule-content {
  flex: 1;
  min-width: 0;
}

.schedule-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 6px;
}

.schedule-title {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.schedule-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  color: #909399;
}

.schedule-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.schedule-actions {
  flex-shrink: 0;
}

.completed-icon {
  font-size: 24px;
  color: #67c23a;
}

.more-indicator {
  text-align: center;
  padding: 8px;
  color: #909399;
  font-size: 12px;
}

@media (max-width: 768px) {
  .schedule-item {
    flex-direction: column;
    align-items: flex-start;
  }

  .time-badge {
    width: 100%;
  }

  .schedule-actions {
    width: 100%;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
