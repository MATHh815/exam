<template>
  <div class="dashboard-container">
    <!-- 欢迎横幅 -->
    <div class="welcome-banner">
      <div class="welcome-content">
        <div class="welcome-text">
          <h1>欢迎回来，{{ userStore.userInfo?.nickname || userStore.userInfo?.username }}！</h1>
          <p>继续你的学习之旅，每一次练习都是进步的阶梯</p>
        </div>
        <div class="welcome-illustration">
          <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 150'%3E%3Crect fill='%23667eea' opacity='0.1' width='200' height='150' rx='10'/%3E%3Ccircle cx='100' cy='60' r='30' fill='%23667eea' opacity='0.3'/%3E%3Crect x='60' y='100' width='80' height='10' rx='5' fill='%23667eea' opacity='0.2'/%3E%3Crect x='70' y='115' width='60' height='8' rx='4' fill='%23667eea' opacity='0.15'/%3E%3C/svg%3E" alt="illustration" />
        </div>
      </div>
      <div class="welcome-stats">
        <div class="welcome-stat-item companion">
          <span class="stat-number">{{ companionDays }}</span>
          <span class="stat-label">陪伴天数</span>
        </div>
        <div class="welcome-stat-item">
          <span class="stat-number">{{ overview.practice_count || 0 }}</span>
          <span class="stat-label">今日练习</span>
        </div>
        <div class="welcome-stat-item">
          <span class="stat-number">{{ overview.accuracy ? overview.accuracy.toFixed(0) + '%' : '0%' }}</span>
          <span class="stat-label">正确率</span>
        </div>
        <div class="welcome-stat-item">
          <span class="stat-number">{{ formatStudyTime(overview.study_duration) }}</span>
          <span class="stat-label">学习时长</span>
        </div>
      </div>
    </div>

    <!-- 快速入口卡片 -->
    <div class="quick-actions">
      <div class="action-card practice" @click="startPractice">
        <div class="action-icon">
          <el-icon :size="32"><EditPen /></el-icon>
        </div>
        <div class="action-info">
          <h3>智能练习</h3>
          <p>随机抽题，巩固知识点</p>
        </div>
        <el-icon class="action-arrow"><ArrowRight /></el-icon>
      </div>

      <div class="action-card exam" @click="goToExams">
        <div class="action-icon">
          <el-icon :size="32"><Document /></el-icon>
        </div>
        <div class="action-info">
          <h3>模拟考试</h3>
          <p>真实考试环境</p>
        </div>
        <el-icon class="action-arrow"><ArrowRight /></el-icon>
      </div>

      <div class="action-card wrong" @click="goToWrongBook">
        <div class="action-icon">
          <el-icon :size="32"><Collection /></el-icon>
          <el-badge v-if="wrongBookCount > 0" :value="wrongBookCount" class="wrong-badge" />
        </div>
        <div class="action-info">
          <h3>错题本</h3>
          <p>攻克薄弱环节</p>
        </div>
        <el-icon class="action-arrow"><ArrowRight /></el-icon>
      </div>

      <div class="action-card stats" @click="goToStatistics">
        <div class="action-icon">
          <el-icon :size="32"><TrendCharts /></el-icon>
        </div>
        <div class="action-info">
          <h3>学习统计</h3>
          <p>查看学习报告</p>
        </div>
        <el-icon class="action-arrow"><ArrowRight /></el-icon>
      </div>

      <div class="action-card ai" @click="goToAIAnalysis">
        <div class="action-icon">
          <el-icon :size="32"><MagicStick /></el-icon>
        </div>
        <div class="action-info">
          <h3>AI智能分析</h3>
          <p>个性化学习建议</p>
        </div>
        <el-icon class="action-arrow"><ArrowRight /></el-icon>
      </div>
    </div>

    <!-- 数据概览和最近活动 -->
    <div class="dashboard-grid">
      <!-- 学习数据卡片 -->
      <el-card class="data-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">学习数据</span>
            <el-button type="primary" link @click="goToStatistics">
              查看详情 <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
        </template>
        
        <div class="data-grid" v-loading="loadingStats">
          <div class="data-item">
            <div class="data-icon blue">
              <el-icon><Tickets /></el-icon>
            </div>
            <div class="data-info">
              <span class="data-value">{{ overview.total_practice || 0 }}</span>
              <span class="data-label">累计练习</span>
            </div>
          </div>
          <div class="data-item">
            <div class="data-icon green">
              <el-icon><CircleCheck /></el-icon>
            </div>
            <div class="data-info">
              <span class="data-value">{{ overview.correct_count || 0 }}</span>
              <span class="data-label">正确题数</span>
            </div>
          </div>
          <div class="data-item">
            <div class="data-icon orange">
              <el-icon><Clock /></el-icon>
            </div>
            <div class="data-info">
              <span class="data-value">{{ overview.exam_count || 0 }}</span>
              <span class="data-label">考试次数</span>
            </div>
          </div>
          <div class="data-item">
            <div class="data-icon purple">
              <el-icon><TrophyBase /></el-icon>
            </div>
            <div class="data-info">
              <span class="data-value">{{ overview.best_score || 0 }}</span>
              <span class="data-label">最高分</span>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 最近活动 -->
      <el-card class="activity-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span class="card-title">最近活动</span>
            <el-radio-group v-model="activeTab" size="small">
              <el-radio-button label="practice">练习</el-radio-button>
              <el-radio-button label="exam">考试</el-radio-button>
            </el-radio-group>
          </div>
        </template>

        <div class="activity-list" v-loading="loadingActivities">
          <!-- 练习记录 -->
          <template v-if="activeTab === 'practice'">
            <el-empty v-if="!recentPractice.length" description="暂无练习记录" :image-size="80" />
            <div v-else class="activity-items">
              <div v-for="record in recentPractice" :key="record.id" class="activity-item">
                <div class="activity-dot" :class="record.is_correct ? 'success' : 'danger'"></div>
                <div class="activity-content">
                  <div class="activity-title">
                    {{ getQuestionTypeLabel(record.question?.question_type) }}
                    <el-tag :type="record.is_correct ? 'success' : 'danger'" size="small">
                      {{ record.is_correct ? '正确' : '错误' }}
                    </el-tag>
                  </div>
                  <div class="activity-meta">
                    <span>{{ record.question?.subject }}</span>
                    <span>用时 {{ record.time_spent }}秒</span>
                  </div>
                </div>
                <div class="activity-time">{{ formatTime(record.created_at) }}</div>
              </div>
            </div>
          </template>

          <!-- 考试记录 -->
          <template v-else>
            <el-empty v-if="!recentExams.length" description="暂无考试记录" :image-size="80" />
            <div v-else class="activity-items">
              <div v-for="exam in recentExams" :key="exam.id" class="activity-item">
                <div class="activity-dot" :class="getScoreClass(exam.score, exam.paper?.pass_score)"></div>
                <div class="activity-content">
                  <div class="activity-title">
                    {{ exam.paper?.name }}
                    <el-tag :type="getScoreType(exam.score, exam.paper?.pass_score)" size="small">
                      {{ exam.score }}分
                    </el-tag>
                  </div>
                  <div class="activity-meta">
                    <span>正确率 {{ (exam.accuracy * 100).toFixed(0) }}%</span>
                    <span>用时 {{ formatSeconds(exam.time_spent) }}</span>
                  </div>
                </div>
                <div class="activity-time">{{ formatTime(exam.created_at) }}</div>
              </div>
            </div>
          </template>
        </div>
      </el-card>
    </div>

    <!-- 开始练习对话框 -->
    <el-dialog v-model="practiceDialogVisible" title="开始练习" width="480px" :close-on-click-modal="false">
      <el-form :model="practiceForm" label-width="80px" label-position="left">
        <el-form-item label="考试类型">
          <el-select v-model="practiceForm.exam_type" placeholder="全部类型" clearable style="width: 100%">
            <el-option label="公务员考试" value="civil_service" />
            <el-option label="研究生考试" value="postgraduate" />
            <el-option label="事业编考试" value="public_institution" />
          </el-select>
        </el-form-item>
        <el-form-item label="题目类型">
          <el-select v-model="practiceForm.question_type" placeholder="全部题型" clearable style="width: 100%">
            <el-option label="单选题" value="single_choice" />
            <el-option label="多选题" value="multiple_choice" />
            <el-option label="判断题" value="true_false" />
            <el-option label="填空题" value="fill_blank" />
            <el-option label="简答题" value="essay" />
          </el-select>
        </el-form-item>
        <el-form-item label="题目数量">
          <el-slider v-model="practiceForm.count" :min="5" :max="50" :step="5" show-stops show-input />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="practiceDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmStartPractice" :loading="startingPractice">
          开始练习
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  EditPen, Document, Collection, TrendCharts, ArrowRight,
  Tickets, CircleCheck, Clock, TrophyBase, MagicStick
} from '@element-plus/icons-vue'
import { useUserStore } from '../stores/user'
import { getOverview } from '../api/statistics'
import { getPracticeHistory, getWrongBook, startPractice as startPracticeApi } from '../api/practice'
import { getExamHistory } from '../api/exams'

const router = useRouter()
const userStore = useUserStore()

// 计算陪伴天数
const companionDays = computed(() => {
  const createdAt = userStore.userInfo?.created_at
  if (!createdAt) return 1
  
  const registerDate = new Date(createdAt)
  const today = new Date()
  const diffTime = today.getTime() - registerDate.getTime()
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
  
  // 至少显示1天
  return Math.max(1, diffDays + 1)
})

// 数据状态
const loadingStats = ref(false)
const loadingActivities = ref(false)
const overview = ref({})
const wrongBookCount = ref(0)
const recentPractice = ref([])
const recentExams = ref([])
const activeTab = ref('practice')

// 练习对话框
const practiceDialogVisible = ref(false)
const startingPractice = ref(false)
const practiceForm = ref({
  exam_type: '',
  question_type: '',
  count: 10
})

function formatStudyTime(minutes) {
  if (!minutes) return '0分'
  if (minutes < 60) return `${minutes}分`
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return mins > 0 ? `${hours}h${mins}m` : `${hours}h`
}

function formatTime(dateString) {
  if (!dateString) return ''
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  
  return date.toLocaleDateString('zh-CN')
}

function formatSeconds(seconds) {
  if (!seconds) return '0秒'
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return mins > 0 ? `${mins}分${secs}秒` : `${secs}秒`
}

function getQuestionTypeLabel(type) {
  const labels = {
    single_choice: '单选题',
    multiple_choice: '多选题',
    true_false: '判断题',
    fill_blank: '填空题',
    essay: '简答题'
  }
  return labels[type] || type
}

function getScoreType(score, passScore) {
  if (!passScore) return 'info'
  return score >= passScore ? 'success' : 'danger'
}

function getScoreClass(score, passScore) {
  if (!passScore) return 'info'
  return score >= passScore ? 'success' : 'danger'
}

async function loadOverview() {
  loadingStats.value = true
  try {
    const response = await getOverview({ days: 30 })
    if (response.data) {
      overview.value = response.data
    }
  } catch (error) {
    console.error('加载学习概览失败:', error)
  } finally {
    loadingStats.value = false
  }
}

async function loadWrongBookCount() {
  try {
    const response = await getWrongBook({ mastered: false })
    if (response.data) {
      wrongBookCount.value = response.data.length
    }
  } catch (error) {
    console.error('加载错题本数量失败:', error)
  }
}

async function loadRecentActivities() {
  loadingActivities.value = true
  try {
    const practiceResponse = await getPracticeHistory({ page: 1, page_size: 5 })
    if (practiceResponse.data?.records) {
      recentPractice.value = practiceResponse.data.records
    }

    const examResponse = await getExamHistory({ page: 1, page_size: 5 })
    if (examResponse.data?.records) {
      recentExams.value = examResponse.data.records
    }
  } catch (error) {
    console.error('加载最近活动失败:', error)
  } finally {
    loadingActivities.value = false
  }
}

function startPractice() {
  practiceDialogVisible.value = true
}

async function confirmStartPractice() {
  startingPractice.value = true
  try {
    const response = await startPracticeApi(practiceForm.value)
    if (response.data?.questions && response.data.questions.length > 0) {
      ElMessage.success('已为您准备好练习题目')
      practiceDialogVisible.value = false
      sessionStorage.setItem('practiceQuestions', JSON.stringify(response.data.questions))
      router.push({ name: 'practice' })
    } else {
      ElMessage.warning('没有找到符合条件的题目')
    }
  } catch (error) {
    console.error('开始练习失败:', error)
    ElMessage.error(error.response?.data?.error?.message || '开始练习失败')
  } finally {
    startingPractice.value = false
  }
}

function goToExams() {
  router.push('/exams')
}

function goToWrongBook() {
  router.push('/wrong-book')
}

function goToStatistics() {
  router.push('/statistics')
}

onMounted(async () => {
  if (userStore.isLoggedIn && !userStore.userInfo) {
    try {
      await userStore.fetchUserInfo()
    } catch (error) {
      console.error('获取用户信息失败:', error)
      router.push('/login')
      return
    }
  } else if (!userStore.isLoggedIn) {
    router.push('/login')
    return
  }

  const shouldRefresh = sessionStorage.getItem('refreshDashboard')
  if (shouldRefresh) {
    sessionStorage.removeItem('refreshDashboard')
    ElMessage.success('练习数据已更新')
  }

  loadOverview()
  loadWrongBookCount()
  loadRecentActivities()
})
</script>

<style scoped>
.dashboard-container {
  max-width: 1400px;
  margin: 0 auto;
}

/* 欢迎横幅 */
.welcome-banner {
  background: linear-gradient(135deg, #0c1445 0%, #1a0a2e 50%, #16213e 100%);
  border-radius: 16px;
  padding: 32px;
  color: #fff;
  margin-bottom: 24px;
  position: relative;
  overflow: hidden;
}

.welcome-banner::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    radial-gradient(2px 2px at 10% 20%, rgba(255, 255, 255, 0.9) 50%, transparent 50%),
    radial-gradient(2px 2px at 30% 60%, rgba(255, 255, 255, 0.7) 50%, transparent 50%),
    radial-gradient(2px 2px at 50% 30%, rgba(255, 255, 255, 0.8) 50%, transparent 50%),
    radial-gradient(2px 2px at 70% 80%, rgba(255, 255, 255, 0.6) 50%, transparent 50%),
    radial-gradient(2px 2px at 90% 40%, rgba(255, 255, 255, 0.9) 50%, transparent 50%),
    radial-gradient(1px 1px at 15% 45%, rgba(255, 255, 255, 0.6) 50%, transparent 50%),
    radial-gradient(1px 1px at 35% 85%, rgba(255, 255, 255, 0.5) 50%, transparent 50%),
    radial-gradient(1px 1px at 55% 15%, rgba(255, 255, 255, 0.7) 50%, transparent 50%),
    radial-gradient(1px 1px at 75% 55%, rgba(255, 255, 255, 0.6) 50%, transparent 50%),
    radial-gradient(1px 1px at 85% 25%, rgba(255, 255, 255, 0.8) 50%, transparent 50%),
    radial-gradient(3px 3px at 25% 50%, rgba(255, 255, 255, 1) 50%, transparent 50%),
    radial-gradient(3px 3px at 65% 20%, rgba(255, 255, 255, 0.9) 50%, transparent 50%),
    radial-gradient(ellipse at 20% 80%, rgba(102, 126, 234, 0.3) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 30%, rgba(118, 75, 162, 0.25) 0%, transparent 50%);
  animation: banner-twinkle 5s ease-in-out infinite;
  pointer-events: none;
}

@keyframes banner-twinkle {
  0%, 100% { opacity: 0.7; }
  50% { opacity: 1; }
}

.welcome-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  position: relative;
  z-index: 1;
}

.welcome-text h1 {
  font-size: 28px;
  font-weight: 600;
  margin: 0 0 8px 0;
}

.welcome-text p {
  font-size: 16px;
  opacity: 0.9;
  margin: 0;
}

.welcome-illustration img {
  width: 120px;
  height: auto;
  opacity: 0.8;
}

.welcome-stats {
  display: flex;
  gap: 48px;
  padding-top: 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  position: relative;
  z-index: 1;
}

.welcome-stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.welcome-stat-item .stat-number {
  font-size: 32px;
  font-weight: 700;
}

.welcome-stat-item .stat-label {
  font-size: 14px;
  opacity: 0.8;
}

/* 陪伴天数特殊样式 */
.welcome-stat-item.companion {
  padding: 8px 20px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 12px;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.welcome-stat-item.companion .stat-number {
  font-size: 42px;
  background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
  background-size: 200% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: gradient-shine 3s linear infinite;
}

.welcome-stat-item.companion .stat-label {
  color: #a78bfa;
  font-size: 13px;
}

@keyframes gradient-shine {
  0% { background-position: 0% center; }
  100% { background-position: 200% center; }
}

/* 快速入口 */
.quick-actions {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.action-card {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.action-card:hover {
  transform: translateY(-4px);
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(102, 126, 234, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.action-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.action-card.practice .action-icon {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  color: #fff;
}

.action-card.exam .action-icon {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
  color: #fff;
}

.action-card.wrong .action-icon {
  background: linear-gradient(135deg, #e6a23c 0%, #ebb563 100%);
  color: #fff;
}

.action-card.stats .action-icon {
  background: linear-gradient(135deg, #909399 0%, #a6a9ad 100%);
  color: #fff;
}

.wrong-badge {
  position: absolute;
  top: -8px;
  right: -8px;
}

.action-info {
  flex: 1;
}

.action-info h3 {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  margin: 0 0 4px 0;
}

.action-info p {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}

.action-arrow {
  color: rgba(255, 255, 255, 0.5);
  transition: transform 0.3s;
}

.action-card:hover .action-arrow {
  transform: translateX(4px);
  color: #667eea;
}

/* 数据网格 */
.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
}

/* 数据卡片 */
.data-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.data-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
}

.data-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.data-icon.blue {
  background: rgba(64, 158, 255, 0.1);
  color: #409eff;
}

.data-icon.green {
  background: rgba(103, 194, 58, 0.1);
  color: #67c23a;
}

.data-icon.orange {
  background: rgba(230, 162, 60, 0.1);
  color: #e6a23c;
}

.data-icon.purple {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
}

.data-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.data-value {
  font-size: 22px;
  font-weight: 700;
  color: #fff;
}

.data-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

/* 活动列表 */
.activity-list {
  min-height: 280px;
}

.activity-items {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.activity-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
}

.activity-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-top: 6px;
  flex-shrink: 0;
}

.activity-dot.success {
  background: #67c23a;
}

.activity-dot.danger {
  background: #f56c6c;
}

.activity-dot.info {
  background: #909399;
}

.activity-content {
  flex: 1;
  min-width: 0;
}

.activity-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #fff;
  margin-bottom: 4px;
}

.activity-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.activity-time {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
  white-space: nowrap;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .quick-actions {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 992px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .welcome-banner {
    padding: 24px;
  }

  .welcome-text h1 {
    font-size: 22px;
  }

  .welcome-illustration {
    display: none;
  }

  .welcome-stats {
    gap: 24px;
  }

  .welcome-stat-item .stat-number {
    font-size: 24px;
  }

  .quick-actions {
    grid-template-columns: 1fr;
  }

  .action-card {
    padding: 16px;
  }
}

/* el-card 玻璃效果覆盖 */
:deep(.el-card) {
  background: rgba(255, 255, 255, 0.08) !important;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  border-radius: 16px !important;
}

:deep(.el-card__header) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
  padding: 16px 20px !important;
}

:deep(.el-card__body) {
  padding: 20px !important;
}

:deep(.el-button--text) {
  color: rgba(255, 255, 255, 0.7) !important;
}

:deep(.el-button--text:hover) {
  color: #667eea !important;
}

:deep(.el-radio-button__inner) {
  background: rgba(255, 255, 255, 0.05) !important;
  border-color: rgba(255, 255, 255, 0.1) !important;
  color: rgba(255, 255, 255, 0.7) !important;
}

:deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  border-color: transparent !important;
  color: #fff !important;
}
</style>
