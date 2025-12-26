<template>
  <div class="exam-list-container">
    <!-- 顶部横幅 -->
    <div class="page-banner">
      <div class="banner-bg"></div>
      <div class="banner-content">
        <div class="banner-icon">
          <el-icon :size="48"><Reading /></el-icon>
        </div>
        <div class="banner-text">
          <h1>模拟考试</h1>
          <p>真实考试环境，检验学习成果，助你金榜题名</p>
        </div>
        <div class="banner-stats">
          <div class="stat-item">
            <span class="stat-number">{{ total }}</span>
            <span class="stat-label">套试卷</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <span class="stat-number">{{ totalQuestions }}</span>
            <span class="stat-label">道题目</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 筛选条件 -->
    <div class="filter-section">
      <div class="filter-tabs">
        <div 
          class="filter-tab" 
          :class="{ active: filters.exam_type === '' }"
          @click="setExamType('')"
        >
          <el-icon><Grid /></el-icon>
          <span>全部</span>
        </div>
        <div 
          class="filter-tab" 
          :class="{ active: filters.exam_type === 'civil_service' }"
          @click="setExamType('civil_service')"
        >
          <el-icon><OfficeBuilding /></el-icon>
          <span>公务员考试</span>
        </div>
        <div 
          class="filter-tab" 
          :class="{ active: filters.exam_type === 'postgraduate' }"
          @click="setExamType('postgraduate')"
        >
          <el-icon><School /></el-icon>
          <span>研究生考试</span>
        </div>
        <div 
          class="filter-tab" 
          :class="{ active: filters.exam_type === 'public_institution' }"
          @click="setExamType('public_institution')"
        >
          <el-icon><Briefcase /></el-icon>
          <span>事业编考试</span>
        </div>
      </div>
    </div>

    <!-- 试卷列表 -->
    <div class="papers-section" v-loading="loading">
      <el-empty v-if="!loading && papers.length === 0" description="暂无可用试卷" :image-size="200">
        <template #image>
          <div class="empty-icon">
            <el-icon :size="80" color="#c0c4cc"><Document /></el-icon>
          </div>
        </template>
      </el-empty>
      
      <div class="papers-grid">
        <div 
          v-for="(paper, index) in papers" 
          :key="paper.id" 
          class="paper-card"
          :class="getExamTypeClass(paper.exam_type)"
          :style="{ animationDelay: `${index * 0.1}s` }"
        >
          <!-- 卡片装饰 -->
          <div class="card-decoration">
            <div class="decoration-circle"></div>
            <div class="decoration-circle small"></div>
          </div>
          
          <!-- 类型标签 -->
          <div class="type-badge" :class="paper.exam_type">
            {{ getExamTypeLabel(paper.exam_type) }}
          </div>

          <!-- 卡片内容 -->
          <div class="card-body">
            <h3 class="paper-title">{{ paper.name }}</h3>
            
            <p class="paper-description" v-if="paper.description">
              {{ paper.description }}
            </p>
            <p class="paper-description placeholder" v-else>
              本试卷包含多种题型，全面考察知识掌握程度。
            </p>

            <!-- 信息网格 -->
            <div class="info-grid">
              <div class="info-box">
                <el-icon class="info-icon"><Clock /></el-icon>
                <div class="info-content">
                  <span class="info-value">{{ paper.duration }}</span>
                  <span class="info-label">分钟</span>
                </div>
              </div>
              <div class="info-box">
                <el-icon class="info-icon"><Document /></el-icon>
                <div class="info-content">
                  <span class="info-value">{{ paper.question_count || 0 }}</span>
                  <span class="info-label">题</span>
                </div>
              </div>
              <div class="info-box">
                <el-icon class="info-icon"><Star /></el-icon>
                <div class="info-content">
                  <span class="info-value">{{ paper.total_score }}</span>
                  <span class="info-label">总分</span>
                </div>
              </div>
              <div class="info-box">
                <el-icon class="info-icon"><TrophyBase /></el-icon>
                <div class="info-content">
                  <span class="info-value">{{ paper.pass_score }}</span>
                  <span class="info-label">及格</span>
                </div>
              </div>
            </div>

            <!-- 考试记录 -->
            <div class="exam-record" v-if="paper.attempt_count > 0">
              <div class="record-item">
                <span class="record-label">已考</span>
                <span class="record-value">{{ paper.attempt_count }}次</span>
              </div>
              <div class="record-item" v-if="paper.best_score !== null">
                <span class="record-label">最高</span>
                <span class="record-value highlight">{{ paper.best_score }}分</span>
              </div>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="card-footer">
            <button 
              class="btn-start" 
              @click="handleStartExam(paper)" 
              :disabled="startingExam === paper.id"
            >
              <el-icon v-if="startingExam !== paper.id"><VideoPlay /></el-icon>
              <el-icon v-else class="is-loading"><Loading /></el-icon>
              <span>开始考试</span>
            </button>
            <button class="btn-detail" @click="viewPaperDetail(paper)">
              <el-icon><View /></el-icon>
              <span>查看详情</span>
            </button>
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
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>

    <!-- 试卷详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      :title="selectedPaper?.name"
      width="700px"
      @close="selectedPaper = null"
    >
      <div v-if="selectedPaper" class="paper-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="考试类型">
            <el-tag :type="getExamTypeColor(selectedPaper.exam_type)">
              {{ getExamTypeLabel(selectedPaper.exam_type) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="考试时长">
            {{ selectedPaper.duration }}分钟
          </el-descriptions-item>
          <el-descriptions-item label="题目数量">
            {{ selectedPaper.question_count || 0 }}题
          </el-descriptions-item>
          <el-descriptions-item label="总分">
            {{ selectedPaper.total_score }}分
          </el-descriptions-item>
          <el-descriptions-item label="及格分">
            {{ selectedPaper.pass_score }}分
          </el-descriptions-item>
          <el-descriptions-item label="发布状态">
            <el-tag :type="selectedPaper.is_published ? 'success' : 'info'">
              {{ selectedPaper.is_published ? '已发布' : '未发布' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间" :span="2">
            {{ formatDate(selectedPaper.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="试卷说明" :span="2">
            {{ selectedPaper.description || '暂无说明' }}
          </el-descriptions-item>
        </el-descriptions>

        <div class="detail-actions">
          <el-button type="primary" @click="handleStartExam(selectedPaper)" :loading="startingExam === selectedPaper.id">
            开始考试
          </el-button>
          <el-button @click="detailDialogVisible = false">
            关闭
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Search,
  Refresh,
  Clock,
  Document,
  Star,
  TrophyBase,
  VideoPlay,
  View,
  Reading,
  Grid,
  OfficeBuilding,
  School,
  Briefcase,
  Loading
} from '@element-plus/icons-vue'
import { getExamPapers, startExam } from '../api/exams'

const router = useRouter()

// 数据状态
const loading = ref(false)
const papers = ref([])
const total = ref(0)
const startingExam = ref(null)

// 筛选条件
const filters = ref({
  exam_type: ''
})

// 分页
const pagination = ref({
  page: 1,
  page_size: 12
})

// 详情对话框
const detailDialogVisible = ref(false)
const selectedPaper = ref(null)

// 计算总题目数
const totalQuestions = computed(() => {
  return papers.value.reduce((sum, paper) => sum + (paper.question_count || 0), 0)
})

/**
 * 设置考试类型筛选
 */
function setExamType(type) {
  filters.value.exam_type = type
  pagination.value.page = 1
  loadExamPapers()
}

/**
 * 获取考试类型标签
 */
function getExamTypeLabel(type) {
  const labels = {
    civil_service: '公务员考试',
    postgraduate: '研究生考试',
    public_institution: '事业编考试'
  }
  return labels[type] || type
}

/**
 * 获取考试类型样式类
 */
function getExamTypeClass(type) {
  return `type-${type || 'default'}`
}

/**
 * 获取考试类型颜色
 */
function getExamTypeColor(type) {
  const colors = {
    civil_service: 'primary',
    postgraduate: 'success',
    public_institution: 'warning'
  }
  return colors[type] || 'info'
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
 * 加载试卷列表
 */
async function loadExamPapers() {
  loading.value = true
  try {
    const params = {
      is_published: true, // 只显示已发布的试卷
      page: pagination.value.page,
      page_size: pagination.value.page_size
    }

    // 添加筛选条件
    if (filters.value.exam_type) {
      params.exam_type = filters.value.exam_type
    }

    const response = await getExamPapers(params)
    
    if (response.success && response.data) {
      papers.value = response.data.papers || []
      total.value = response.data.total || 0
    }
  } catch (error) {
    console.error('加载试卷列表失败:', error)
    ElMessage.error(error.response?.data?.error?.message || '加载试卷列表失败')
  } finally {
    loading.value = false
  }
}

/**
 * 重置筛选条件
 */
function resetFilters() {
  filters.value = {
    exam_type: ''
  }
  pagination.value.page = 1
  loadExamPapers()
}

/**
 * 处理页码变化
 */
function handlePageChange(page) {
  pagination.value.page = page
  loadExamPapers()
}

/**
 * 处理每页数量变化
 */
function handleSizeChange(size) {
  pagination.value.page_size = size
  pagination.value.page = 1
  loadExamPapers()
}

/**
 * 查看试卷详情
 */
function viewPaperDetail(paper) {
  selectedPaper.value = paper
  detailDialogVisible.value = true
}

/**
 * 开始考试
 */
async function handleStartExam(paper) {
  try {
    // 确认对话框
    await ElMessageBox.confirm(
      `确定要开始《${paper.name}》考试吗？考试时长为 ${paper.duration} 分钟。`,
      '开始考试',
      {
        confirmButtonText: '开始',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    startingExam.value = paper.id

    // 调用开始考试 API
    const response = await startExam(paper.id)

    if (response.success && response.data) {
      ElMessage.success('考试已开始，祝你取得好成绩！')
      
      // 关闭详情对话框
      detailDialogVisible.value = false
      
      // 跳转到考试页面
      router.push({
        name: 'exam',
        params: { paperId: paper.id },
        query: { sessionId: response.data.id }
      })
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('开始考试失败:', error)
      
      // 检查是否是"已有进行中的考试"错误
      const errorMessage = error.response?.data?.error?.message || ''
      if (errorMessage.includes('已有进行中的考试') || errorMessage.includes('进行中')) {
        // 提示用户有进行中的考试
        try {
          await ElMessageBox.confirm(
            '检测到您有一个进行中的考试。您可以继续之前的考试，或者放弃后重新开始。',
            '提示',
            {
              confirmButtonText: '继续考试',
              cancelButtonText: '取消',
              distinguishCancelAndClose: true,
              type: 'warning'
            }
          )
          
          // 用户选择继续考试，直接跳转到考试页面
          router.push({
            name: 'exam',
            params: { paperId: paper.id }
          })
        } catch (confirmError) {
          // 用户取消
          if (confirmError === 'cancel' || confirmError === 'close') {
            ElMessage.info('已取消')
          }
        }
      } else {
        ElMessage.error(errorMessage || '开始考试失败')
      }
    }
  } finally {
    startingExam.value = null
  }
}

/**
 * 检查进行中的考试
 */
async function checkInProgressExams() {
  // 暂时禁用此功能，因为会导致500错误
  // TODO: 修复后端API后再启用
  return
}

/**
 * 初始化
 */
onMounted(() => {
  loadExamPapers()
  checkInProgressExams()
})
</script>

<style scoped>
.exam-list-container {
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
  animation: banner-stars 5s ease-in-out infinite;
}

@keyframes banner-stars {
  0%, 100% { opacity: 0.7; }
  50% { opacity: 1; }
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

.banner-text {
  flex: 1;
}

.banner-text h1 {
  margin: 0 0 8px 0;
  font-size: 32px;
  font-weight: 700;
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.banner-text p {
  margin: 0;
  font-size: 16px;
  color: rgba(255, 255, 255, 0.9);
}

.banner-stats {
  display: flex;
  align-items: center;
  gap: 24px;
  background: rgba(255, 255, 255, 0.15);
  padding: 16px 28px;
  border-radius: 16px;
  backdrop-filter: blur(10px);
}

.stat-item {
  text-align: center;
}

.stat-number {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: white;
}

.stat-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: rgba(255, 255, 255, 0.3);
}

/* 筛选区域 */
.filter-section {
  max-width: 1200px;
  margin: -20px auto 0;
  padding: 0 24px;
  position: relative;
  z-index: 10;
}

.filter-tabs {
  display: flex;
  gap: 12px;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 8px;
  border-radius: 16px;
}

.filter-tab {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border-radius: 12px;
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
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.filter-tab .el-icon {
  font-size: 18px;
}

/* 试卷区域 */
.papers-section {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px;
}

.papers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 24px;
}

/* 试卷卡片 */
.paper-card {
  position: relative;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  overflow: hidden;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  animation: fadeInUp 0.6s ease forwards;
  opacity: 0;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.paper-card:hover {
  transform: translateY(-8px);
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(102, 126, 234, 0.3);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

/* 卡片装饰 */
.card-decoration {
  position: absolute;
  top: -30px;
  right: -30px;
  pointer-events: none;
}

.decoration-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  opacity: 0.1;
}

.decoration-circle.small {
  width: 60px;
  height: 60px;
  position: absolute;
  top: 80px;
  right: 20px;
}

.type-civil_service .decoration-circle { background: #409eff; }
.type-postgraduate .decoration-circle { background: #67c23a; }
.type-public_institution .decoration-circle { background: #e6a23c; }

/* 类型标签 */
.type-badge {
  position: absolute;
  top: 16px;
  right: 16px;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  z-index: 2;
}

.type-badge.civil_service {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  color: white;
}

.type-badge.postgraduate {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
  color: white;
}

.type-badge.public_institution {
  background: linear-gradient(135deg, #e6a23c 0%, #ebb563 100%);
  color: white;
}

/* 卡片内容 */
.card-body {
  padding: 24px 24px 16px;
}

.paper-title {
  margin: 0 0 12px 0;
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  line-height: 1.4;
  padding-right: 100px;
}

.paper-description {
  margin: 0 0 20px 0;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 44px;
}

.paper-description.placeholder {
  color: rgba(255, 255, 255, 0.5);
}

/* 信息网格 */
.info-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 16px;
}

.info-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 8px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.info-box:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: scale(1.05);
}

.info-icon {
  font-size: 20px;
  color: #667eea;
  margin-bottom: 6px;
}

.info-content {
  text-align: center;
}

.info-value {
  display: block;
  font-size: 18px;
  font-weight: 700;
  color: #fff;
}

.info-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
}

/* 考试记录 */
.exam-record {
  display: flex;
  gap: 16px;
  padding: 12px 16px;
  background: rgba(230, 162, 60, 0.15);
  border: 1px solid rgba(230, 162, 60, 0.2);
  border-radius: 12px;
  margin-bottom: 8px;
}

.record-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.record-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

.record-value {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
}

.record-value.highlight {
  color: #e6a23c;
}

/* 卡片底部 */
.card-footer {
  display: flex;
  gap: 12px;
  padding: 16px 24px 24px;
}

.btn-start,
.btn-detail {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-start {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.35);
}

.btn-start:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.45);
}

.btn-start:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-detail {
  background: #f5f7fa;
  color: #606266;
  border: 1px solid #e4e7ed;
}

.btn-detail:hover {
  background: #eef2ff;
  color: #667eea;
  border-color: #667eea;
}

/* 分页 */
.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 32px;
  padding-bottom: 32px;
}

.pagination-container :deep(.el-pagination) {
  --el-pagination-bg-color: rgba(255, 255, 255, 0.08);
  --el-pagination-text-color: rgba(255, 255, 255, 0.7);
  --el-pagination-button-disabled-bg-color: rgba(255, 255, 255, 0.05);
}

.pagination-container :deep(.el-pager li) {
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.pagination-container :deep(.el-pager li:hover) {
  color: #667eea;
}

.pagination-container :deep(.el-pager li.is-active) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

/* 空状态 */
.empty-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 160px;
  height: 160px;
  background: #f5f7fa;
  border-radius: 50%;
  margin: 0 auto;
}

/* 详情对话框 */
.paper-detail {
  padding: 10px 0;
}

.detail-actions {
  margin-top: 24px;
  text-align: right;
}

/* 加载动画 */
.is-loading {
  animation: rotating 1s linear infinite;
}

@keyframes rotating {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-banner {
    padding: 24px 16px;
  }

  .banner-content {
    flex-direction: column;
    text-align: center;
  }

  .banner-text h1 {
    font-size: 24px;
  }

  .banner-stats {
    width: 100%;
    justify-content: center;
  }

  .filter-section {
    padding: 0 16px;
  }

  .filter-tabs {
    flex-wrap: wrap;
    justify-content: center;
  }

  .filter-tab {
    padding: 10px 16px;
    font-size: 13px;
  }

  .papers-section {
    padding: 24px 16px;
  }

  .papers-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .info-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .card-footer {
    flex-direction: column;
  }
}
</style>
