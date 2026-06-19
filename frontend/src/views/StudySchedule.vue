<template>
  <div class="study-schedule-container">
    <el-card class="header-card">
      <div class="header-content">
        <div class="title-section">
          <h2>📅 学习日程</h2>
          <p class="subtitle">精确到分钟的时间管理</p>
        </div>
        <el-button type="primary" @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          创建日程
        </el-button>
      </div>
    </el-card>

    <!-- 视图切换 -->
    <el-card class="view-tabs-card">
      <el-radio-group v-model="currentView" size="large">
        <el-radio-button label="today">今日日程</el-radio-button>
        <el-radio-button label="week">本周日程</el-radio-button>
        <el-radio-button label="month">本月日程</el-radio-button>
      </el-radio-group>
    </el-card>

    <!-- 今日日程视图 -->
    <div v-if="currentView === 'today'" class="today-view">
      <el-card v-if="todaySchedules.length === 0" class="empty-card">
        <el-empty description="今天还没有安排日程">
          <el-button type="primary" @click="showCreateDialog = true">创建第一个日程</el-button>
        </el-empty>
      </el-card>

      <div v-else class="schedule-timeline">
        <div
          v-for="schedule in todaySchedules"
          :key="schedule.id"
          class="schedule-item"
          :class="{ completed: schedule.is_completed }"
        >
          <div class="time-badge">
            <div class="time">{{ schedule.start_time }}</div>
            <div class="duration">{{ schedule.duration_minutes }}分钟</div>
          </div>
          
          <el-card class="schedule-card" :class="getActivityClass(schedule.activity_type)">
            <div class="schedule-header">
              <div class="title-row">
                <el-tag :type="getActivityTagType(schedule.activity_type)" size="small">
                  {{ activityTypes[schedule.activity_type] }}
                </el-tag>
                <el-tag v-if="schedule.subject" type="info" size="small">
                  {{ subjects[schedule.subject] }}
                </el-tag>
                <h3>{{ schedule.title }}</h3>
              </div>
              <div class="actions">
                <el-button
                  v-if="!schedule.is_completed"
                  type="success"
                  size="small"
                  @click="handleComplete(schedule.id)"
                >
                  <el-icon><Check /></el-icon>
                  完成
                </el-button>
                <el-button
                  type="primary"
                  size="small"
                  plain
                  @click="handleEdit(schedule)"
                >
                  <el-icon><Edit /></el-icon>
                </el-button>
                <el-button
                  type="danger"
                  size="small"
                  plain
                  @click="handleDelete(schedule.id)"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>

            <div class="schedule-details">
              <div class="detail-item">
                <el-icon><Clock /></el-icon>
                <span>{{ schedule.start_time }} - {{ schedule.end_time }}</span>
              </div>
              <div v-if="schedule.location" class="detail-item">
                <el-icon><Location /></el-icon>
                <span>{{ schedule.location }}</span>
              </div>
              <div v-if="schedule.description" class="description">
                {{ schedule.description }}
              </div>
            </div>

            <div v-if="schedule.is_completed" class="completed-badge">
              <el-icon><CircleCheck /></el-icon>
              已完成
            </div>
          </el-card>
        </div>
      </div>
    </div>

    <!-- 本周/本月日程视图 -->
    <div v-else class="list-view">
      <el-card v-if="schedules.length === 0" class="empty-card">
        <el-empty :description="`${currentView === 'week' ? '本周' : '本月'}还没有日程安排`">
          <el-button type="primary" @click="showCreateDialog = true">创建日程</el-button>
        </el-empty>
      </el-card>

      <div v-else class="schedule-list">
        <div v-for="(group, date) in groupedSchedules" :key="date" class="date-group">
          <div class="date-header">
            <h3>{{ formatDate(date) }}</h3>
            <el-tag>{{ group.length }}个日程</el-tag>
          </div>

          <div class="schedule-cards">
            <el-card
              v-for="schedule in group"
              :key="schedule.id"
              class="schedule-card-compact"
              :class="{ completed: schedule.is_completed }"
            >
              <div class="compact-header">
                <div class="time-info">
                  <span class="time">{{ schedule.start_time }} - {{ schedule.end_time }}</span>
                  <span class="duration">{{ schedule.duration_minutes }}分钟</span>
                </div>
                <div class="actions">
                  <el-button
                    v-if="!schedule.is_completed"
                    type="success"
                    size="small"
                    text
                    @click="handleComplete(schedule.id)"
                  >
                    完成
                  </el-button>
                  <el-button type="primary" size="small" text @click="handleEdit(schedule)">
                    编辑
                  </el-button>
                  <el-button type="danger" size="small" text @click="handleDelete(schedule.id)">
                    删除
                  </el-button>
                </div>
              </div>

              <div class="compact-content">
                <div class="title-row">
                  <el-tag :type="getActivityTagType(schedule.activity_type)" size="small">
                    {{ activityTypes[schedule.activity_type] }}
                  </el-tag>
                  <el-tag v-if="schedule.subject" type="info" size="small">
                    {{ subjects[schedule.subject] }}
                  </el-tag>
                  <span class="title">{{ schedule.title }}</span>
                </div>
                <div v-if="schedule.location" class="location">
                  <el-icon><Location /></el-icon>
                  {{ schedule.location }}
                </div>
              </div>
            </el-card>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建/编辑日程对话框 -->
    <ScheduleForm
      v-model="showCreateDialog"
      :schedule="editingSchedule"
      :activity-types="activityTypes"
      :subjects="subjects"
      @success="handleFormSuccess"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Check, Edit, Delete, Clock, Location, CircleCheck
} from '@element-plus/icons-vue'
import {
  getTodaySchedules,
  getSchedulesByRange,
  getScheduleOptions,
  completeSchedule,
  deleteSchedule
} from '@/api/studySchedules'
import ScheduleForm from '@/components/ScheduleForm.vue'

// 状态
const currentView = ref('today')
const todaySchedules = ref([])
const schedules = ref([])
const activityTypes = ref({})
const subjects = ref({})
const showCreateDialog = ref(false)
const editingSchedule = ref(null)

// 计算属性
const groupedSchedules = computed(() => {
  const groups = {}
  schedules.value.forEach(schedule => {
    const date = schedule.schedule_date
    if (!groups[date]) {
      groups[date] = []
    }
    groups[date].push(schedule)
  })
  
  // 按时间排序每组内的日程
  Object.keys(groups).forEach(date => {
    groups[date].sort((a, b) => a.start_time.localeCompare(b.start_time))
  })
  
  return groups
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

const fetchTodaySchedules = async () => {
  try {
    const res = await getTodaySchedules()
    if (res.success) {
      todaySchedules.value = res.data.schedules
    }
  } catch (error) {
    console.error('获取今日日程失败:', error)
    ElMessage.error('获取今日日程失败')
  }
}

const fetchSchedulesByView = async () => {
  const today = new Date()
  let startDate, endDate

  if (currentView.value === 'week') {
    // 本周一到周日
    const dayOfWeek = today.getDay() || 7 // 周日为0，转换为7
    startDate = new Date(today)
    startDate.setDate(today.getDate() - dayOfWeek + 1)
    endDate = new Date(startDate)
    endDate.setDate(startDate.getDate() + 6)
  } else if (currentView.value === 'month') {
    // 本月第一天到最后一天
    startDate = new Date(today.getFullYear(), today.getMonth(), 1)
    endDate = new Date(today.getFullYear(), today.getMonth() + 1, 0)
  }

  try {
    const res = await getSchedulesByRange(
      formatDateString(startDate),
      formatDateString(endDate)
    )
    if (res.success) {
      schedules.value = res.data.schedules
    }
  } catch (error) {
    console.error('获取日程失败:', error)
    ElMessage.error('获取日程失败')
  }
}

const handleComplete = async (id) => {
  try {
    const res = await completeSchedule(id)
    if (res.success) {
      ElMessage.success('日程已完成')
      refreshCurrentView()
    }
  } catch (error) {
    console.error('完成日程失败:', error)
    ElMessage.error('完成日程失败')
  }
}

const handleEdit = (schedule) => {
  editingSchedule.value = schedule
  showCreateDialog.value = true
}

const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这个日程吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const res = await deleteSchedule(id)
    if (res.success) {
      ElMessage.success('删除成功')
      refreshCurrentView()
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除日程失败:', error)
      ElMessage.error('删除日程失败')
    }
  }
}

const handleFormSuccess = () => {
  showCreateDialog.value = false
  editingSchedule.value = null
  refreshCurrentView()
}

const refreshCurrentView = () => {
  if (currentView.value === 'today') {
    fetchTodaySchedules()
  } else {
    fetchSchedulesByView()
  }
}

const getActivityClass = (activityType) => {
  const classMap = {
    memorize: 'activity-memorize',
    lecture: 'activity-lecture',
    practice: 'activity-practice',
    review: 'activity-review',
    mock_exam: 'activity-exam',
    reading: 'activity-reading',
    writing: 'activity-writing',
    rest: 'activity-rest'
  }
  return classMap[activityType] || ''
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

const formatDate = (dateString) => {
  const date = new Date(dateString)
  const today = new Date()
  const tomorrow = new Date(today)
  tomorrow.setDate(today.getDate() + 1)

  if (dateString === formatDateString(today)) {
    return '今天'
  } else if (dateString === formatDateString(tomorrow)) {
    return '明天'
  }

  const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  const month = date.getMonth() + 1
  const day = date.getDate()
  const weekday = weekdays[date.getDay()]

  return `${month}月${day}日 ${weekday}`
}

const formatDateString = (date) => {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

// 监听视图切换
watch(currentView, (newView) => {
  if (newView === 'today') {
    fetchTodaySchedules()
  } else {
    fetchSchedulesByView()
  }
})

// 初始化
onMounted(() => {
  fetchOptions()
  fetchTodaySchedules()
})
</script>

<style scoped>
.study-schedule-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.header-card {
  margin-bottom: 20px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title-section h2 {
  margin: 0 0 5px 0;
  font-size: 24px;
  color: #303133;
}

.subtitle {
  margin: 0;
  color: #909399;
  font-size: 14px;
}

.view-tabs-card {
  margin-bottom: 20px;
  text-align: center;
}

/* 今日日程视图 */
.schedule-timeline {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.schedule-item {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.schedule-item.completed {
  opacity: 0.7;
}

.time-badge {
  flex-shrink: 0;
  width: 100px;
  text-align: center;
  padding: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px;
}

.time-badge .time {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 5px;
}

.time-badge .duration {
  font-size: 12px;
  opacity: 0.9;
}

.schedule-card {
  flex: 1;
  position: relative;
  transition: all 0.3s;
}

.schedule-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.schedule-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.title-row h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.actions {
  display: flex;
  gap: 8px;
}

.schedule-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #606266;
  font-size: 14px;
}

.description {
  margin-top: 8px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
  color: #606266;
  font-size: 14px;
}

.completed-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 12px;
  background: #67c23a;
  color: white;
  border-radius: 12px;
  font-size: 12px;
}

/* 活动类型样式 */
.activity-memorize { border-left: 4px solid #e6a23c; }
.activity-lecture { border-left: 4px solid #409eff; }
.activity-practice { border-left: 4px solid #67c23a; }
.activity-review { border-left: 4px solid #909399; }
.activity-exam { border-left: 4px solid #f56c6c; }
.activity-reading { border-left: 4px solid #5470c6; }
.activity-writing { border-left: 4px solid #fac858; }
.activity-rest { border-left: 4px solid #91cc75; }

/* 列表视图 */
.schedule-list {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.date-group {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.date-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-bottom: 10px;
  border-bottom: 2px solid #e4e7ed;
}

.date-header h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.schedule-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 15px;
}

.schedule-card-compact {
  transition: all 0.3s;
}

.schedule-card-compact:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.schedule-card-compact.completed {
  opacity: 0.6;
  background: #f5f7fa;
}

.compact-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e4e7ed;
}

.time-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.time-info .time {
  font-size: 16px;
  font-weight: bold;
  color: #303133;
}

.time-info .duration {
  font-size: 12px;
  color: #909399;
}

.compact-content .title-row {
  margin-bottom: 8px;
}

.compact-content .title {
  font-size: 16px;
  color: #303133;
  font-weight: 500;
}

.compact-content .location {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #606266;
  font-size: 14px;
}

.empty-card {
  margin-top: 40px;
}

@media (max-width: 768px) {
  .schedule-item {
    flex-direction: column;
  }

  .time-badge {
    width: 100%;
  }

  .schedule-cards {
    grid-template-columns: 1fr;
  }

  .compact-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
