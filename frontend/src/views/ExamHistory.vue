<template>
  <div class="exam-history-container">
    <!-- 顶部横幅 -->
    <div class="page-banner">
      <div class="banner-bg"></div>
      <div class="banner-content">
        <div class="banner-icon">
          <el-icon :size="48"><Clock /></el-icon>
        </div>
        <div class="banner-text">
          <h1>考试记录</h1>
          <p>查看您的考试历史，继续未完成的考试</p>
        </div>
      </div>
    </div>

    <!-- 未完成的考试提示 -->
    <div class="incomplete-section" v-if="incompleteSessions.length > 0">
      <div class="section-header">
        <el-icon class="warning-icon"><WarningFilled /></el-icon>
        <span>您有 {{ incompleteSessions.length }} 场未完成的考试</span>
      </div>
      <div class="incomplete-cards">
        <div 
          v-for="session in incompleteSessions" 
          :key="session.id" 
          class="incomplete-card"
        >
          <div class="card-info">
            <h4>{{ session.paper?.name || '未知试卷' }}</h4>
            <div class="card-meta">
              <span><el-icon><Clock /></el-icon> 开始于 {{ formatDate(session.start_time) }}</span>
              <span><el-icon><Document /></el-icon> 已答 {{ session.answered_count || 0 }} 题</span>
              <el-tag :type="session.status === 'paused' ? 'warning' : 'primary'" size="small">
                {{ session.status === 'paused' ? '已暂停' : '进行中' }}
              </el-tag>
            </div>
          </div>
          <el-button type="primary" @click="continueExam(session)">
            <el-icon><VideoPlay /></el-icon>
            继续考试
          </el-button>
        </div>
      </div>
    </div>

    <!-- 筛选条件 -->
    <div class="filter-section">
      <div class="filter-tabs">
        <div 
          class="filter-tab" 
          :class="{ active: filters.status === '' }"
          @click="setStatusFilter('')"
        >
          全部记录
        </div>
        <div 
          class="filter-tab" 
          :class="{ active: filters.status === 'submitted' }"
          @click="setStatusFilter('submitted')"
        >
          已完成
        </div>
        <div 
          class="filter-tab" 
          :class="{ active: filters.status === 'in_progress' }"
          @click="setStatusFilter('in_progress')"
        >
          进行中
        </div>
        <div 
          class="filter-tab" 
          :class="{ active: filters.status === 'timeout' }"
          @click="setStatusFilter('timeout')"
        >
          已超时
        </div>
      </div>
    </div>

    <!-- 考试记录列表 -->
    <div class="history-section" v-loading="loading">
      <el-empty v-if="!loading && sessions.length === 0" description="暂无考试记录" />
      
      <div class="history-list">
        <div 
          v-for="session in sessions" 
          :key="session.id" 
          class="history-card"
          :class="getStatusClass(session.status)"
        >
          <div class="card-header">
            <h3>{{ session.paper?.name || '未知试卷' }}</h3>
            <el-tag :type="getStatusTagType(session.status)" size="small">
              {{ getStatusLabel(session.status) }}
            </el-tag>
          </div>
          
          <div class="card-body">
            <div class="info-row">
              <div class="info-item">
                <el-icon><Calendar /></el-icon>
                <span>开始时间：{{ formatDate(session.start_time) }}</span>
              </div>
              <div class="info-item" v-if="session.submit_time">
                <el-icon><CircleCheck /></el-icon>
                <span>提交时间：{{ formatDate(session.submit_time) }}</span>
              </div>
            </div>
            
            <div class="info-row">
              <div class="info-item">
                <el-icon><Document /></el-icon>
                <span>已答题数：{{ session.answered_count || 0 }} / {{ session.paper?.question_count || '?' }}</span>
              </div>
              <div class="info-item" v-if="session.current_question_index !== undefined">
                <el-icon><Position /></el-icon>
                <span>当前进度：第 {{ (session.current_question_index || 0) + 1 }} 题</span>
              </div>
            </div>
          </div>
          
          <div class="card-footer">
            <el-button 
              v-if="canContinue(session)" 
              type="primary" 
              @click="continueExam(session)"
            >
              <el-icon><VideoPlay /></el-icon>
              继续考试
            </el-button>
            <el-button 
              v-if="session.status === 'submitted' || session.status === 'timeout'" 
              @click="viewResult(session)"
            >
              <el-icon><View /></el-icon>
              查看结果
            </el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination-container" v-if="total > 0">
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.page_size"
        :page-sizes="[10, 20, 30, 50]"
        :total="total"
        layout="total, sizes, prev, pager, next"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Clock,
  Document,
  Calendar,
  CircleCheck,
  VideoPlay,
  View,
  WarningFilled,
  Position
} from '@element-plus/icons-vue'
import { getUserSessions, getIncompleteSessions, getExamPaper } from '../api/exams'
import { useExamStore } from '../stores/exam'

const router = useRouter()
const examStore = useExamStore()

const loading = ref(false)
const sessions = ref([])
const incompleteSessions = ref([])
const total = ref(0)

const filters = ref({
  status: ''
})

const pagination = ref({
  page: 1,
  page_size: 20
})

/**
 * 设置状态筛选
 */
function setStatusFilter(status) {
  filters.value.status = status
  pagination.value.page = 1
  loadSessions()
}

/**
 * 获取状态标签类型
 */
function getStatusTagType(status) {
  const types = {
    'in_progress': 'primary',
    'paused': 'warning',
    'submitted': 'success',
    'timeout': 'danger'
  }
  return types[status] || 'info'
}

/**
 * 获取状态标签文本
 */
function getStatusLabel(status) {
  const labels = {
    'in_progress': '进行中',
    'paused': '已暂停',
    'submitted': '已完成',
    'timeout': '已超时'
  }
  return labels[status] || status
}

/**
 * 获取状态样式类
 */
function getStatusClass(status) {
  return `status-${status}`
}

/**
 * 判断是否可以继续考试
 */
function canContinue(session) {
  return session.status === 'in_progress' || session.status === 'paused'
}

/**
 * 格式化日期
 */
function formatDate(dateString) {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

/**
 * 加载考试会话列表
 */
async function loadSessions() {
  loading.value = true
  try {
    const params = {
      page: pagination.value.page,
      page_size: pagination.value.page_size
    }
    
    if (filters.value.status) {
      params.status = filters.value.status
    }
    
    const response = await getUserSessions(params)
    
    if (response.success && response.data) {
      sessions.value = response.data.sessions || []
      total.value = response.data.total || 0
    }
  } catch (error) {
    console.error('加载考试记录失败:', error)
    ElMessage.error('加载考试记录失败')
  } finally {
    loading.value = false
  }
}

/**
 * 加载未完成的考试
 */
async function loadIncompleteSessions() {
  try {
    const response = await getIncompleteSessions()
    
    if (response.success && response.data) {
      incompleteSessions.value = response.data || []
    }
  } catch (error) {
    console.error('加载未完成考试失败:', error)
  }
}

/**
 * 继续考试
 */
async function continueExam(session) {
  try {
    // 获取试卷详情
    const paperResponse = await getExamPaper(session.paper_id, true)
    
    if (!paperResponse.success) {
      throw new Error('获取试卷信息失败')
    }
    
    // 恢复考试状态
    await examStore.resumeExam(session, paperResponse.data)
    
    // 跳转到考试页面
    router.push({
      name: 'exam',
      params: { paperId: session.paper_id }
    })
  } catch (error) {
    console.error('继续考试失败:', error)
    ElMessage.error(error.message || '继续考试失败')
  }
}

/**
 * 查看考试结果
 */
async function viewResult(session) {
  try {
    // 查找对应的考试结果
    const { getExamHistory } = await import('../api/exams')
    const response = await getExamHistory({ page: 1, page_size: 100 })
    
    if (response.success && response.data) {
      const result = response.data.results.find(r => r.session_id === session.id)
      if (result) {
        router.push(`/exam/result/${result.id}`)
      } else {
        ElMessage.warning('未找到考试结果')
      }
    }
  } catch (error) {
    console.error('查看结果失败:', error)
    ElMessage.error('查看结果失败')
  }
}

/**
 * 处理页码变化
 */
function handlePageChange(page) {
  pagination.value.page = page
  loadSessions()
}

/**
 * 处理每页数量变化
 */
function handleSizeChange(size) {
  pagination.value.page_size = size
  pagination.value.page = 1
  loadSessions()
}

onMounted(() => {
  loadSessions()
  loadIncompleteSessions()
})
</script>


<style scoped>
.exam-history-container {
  min-height: 100vh;
  background: transparent;
}

/* 顶部横幅 */
.page-banner {
  position: relative;
  padding: 40px 24px;
  background: linear-gradient(135deg, #0c1445 0%, #1a0a2e 50%, #16213e 100%);
  overflow: hidden;
}

.banner-bg {
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
    radial-gradient(2px 2px at 90% 40%, rgba(255, 255, 255, 0.9) 50%, transparent 50%);
}

.banner-content {
  position: relative;
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 24px;
}

.banner-icon {
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  backdrop-filter: blur(10px);
}

.banner-text h1 {
  margin: 0 0 8px 0;
  font-size: 32px;
  font-weight: 700;
  color: white;
}

.banner-text p {
  margin: 0;
  font-size: 16px;
  color: rgba(255, 255, 255, 0.9);
}

/* 未完成考试提示 */
.incomplete-section {
  max-width: 1200px;
  margin: -20px auto 0;
  padding: 0 24px;
  position: relative;
  z-index: 10;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px 20px;
  background: linear-gradient(135deg, rgba(230, 162, 60, 0.2), rgba(230, 162, 60, 0.1));
  border: 1px solid rgba(230, 162, 60, 0.3);
  border-radius: 12px 12px 0 0;
  color: #e6a23c;
  font-weight: 600;
}

.warning-icon {
  font-size: 20px;
}

.incomplete-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-top: none;
  border-radius: 0 0 12px 12px;
}

.incomplete-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.incomplete-card:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(102, 126, 234, 0.3);
}

.card-info h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #fff;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
}

.card-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

/* 筛选区域 */
.filter-section {
  max-width: 1200px;
  margin: 24px auto 0;
  padding: 0 24px;
}

.filter-tabs {
  display: flex;
  gap: 12px;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 8px;
  border-radius: 12px;
}

.filter-tab {
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  background: transparent;
}

.filter-tab:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.filter-tab.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

/* 历史记录区域 */
.history-section {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.history-card {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.history-card:hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(102, 126, 234, 0.3);
}

.history-card.status-in_progress,
.history-card.status-paused {
  border-left: 4px solid #e6a23c;
}

.history-card.status-submitted {
  border-left: 4px solid #67c23a;
}

.history-card.status-timeout {
  border-left: 4px solid #f56c6c;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #fff;
}

.card-body {
  padding: 16px 20px;
}

.info-row {
  display: flex;
  gap: 24px;
  margin-bottom: 12px;
}

.info-row:last-child {
  margin-bottom: 0;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

.info-item .el-icon {
  color: #667eea;
}

.card-footer {
  display: flex;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(0, 0, 0, 0.1);
}

/* 分页 */
.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 24px;
  padding-bottom: 32px;
}

.pagination-container :deep(.el-pagination) {
  --el-pagination-bg-color: rgba(255, 255, 255, 0.08);
  --el-pagination-text-color: rgba(255, 255, 255, 0.7);
}

.pagination-container :deep(.el-pager li) {
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.pagination-container :deep(.el-pager li.is-active) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

/* 响应式 */
@media (max-width: 768px) {
  .banner-content {
    flex-direction: column;
    text-align: center;
  }
  
  .incomplete-card {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }
  
  .card-meta {
    flex-wrap: wrap;
    justify-content: center;
  }
  
  .info-row {
    flex-direction: column;
    gap: 8px;
  }
  
  .card-footer {
    flex-direction: column;
  }
}
</style>
