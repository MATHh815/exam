<template>
  <div class="wrong-book-container">
    <!-- 顶部横幅 -->
    <div class="page-banner">
      <div class="banner-bg"></div>
      <div class="banner-content">
        <div class="banner-icon">
          <el-icon :size="48"><Collection /></el-icon>
        </div>
        <div class="banner-text">
          <h1>我的错题本</h1>
          <p>记录错题，反复练习，攻克薄弱环节</p>
        </div>
        <div class="banner-action">
          <button
            class="btn-practice"
            :disabled="wrongQuestions.length === 0"
            @click="startPracticeFromWrongBook"
          >
            <el-icon><Edit /></el-icon>
            <span>错题重练</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-section">
      <div class="stats-cards">
        <div class="stat-card total">
          <div class="stat-icon">
            <el-icon :size="28"><Document /></el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ wrongQuestions.length }}</span>
            <span class="stat-label">错题总数</span>
          </div>
        </div>
        <div class="stat-card unmastered">
          <div class="stat-icon">
            <el-icon :size="28"><Warning /></el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ unmasteredCount }}</span>
            <span class="stat-label">未掌握</span>
          </div>
        </div>
        <div class="stat-card mastered">
          <div class="stat-icon">
            <el-icon :size="28"><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ masteredCount }}</span>
            <span class="stat-label">已掌握</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 筛选条件 -->
    <div class="filter-section">
      <div class="filter-bar">
        <div class="filter-group">
          <label>掌握状态</label>
          <el-select
            v-model="filters.mastered"
            placeholder="全部"
            clearable
            @change="loadWrongBook"
          >
            <el-option label="未掌握" :value="false" />
            <el-option label="已掌握" :value="true" />
          </el-select>
        </div>

        <div class="filter-group">
          <label>考试类型</label>
          <el-select
            v-model="filters.exam_type"
            placeholder="全部"
            clearable
            @change="loadWrongBook"
          >
            <el-option label="公务员考试" value="civil_service" />
            <el-option label="研究生考试" value="postgraduate" />
            <el-option label="事业编考试" value="public_institution" />
          </el-select>
        </div>

        <div class="filter-group">
          <label>科目</label>
          <el-select
            v-model="filters.subject"
            placeholder="全部"
            clearable
            @change="loadWrongBook"
          >
            <el-option label="行测" value="行测" />
            <el-option label="申论" value="申论" />
            <el-option label="数学" value="数学" />
            <el-option label="英语" value="英语" />
            <el-option label="政治" value="政治" />
            <el-option label="专业课" value="专业课" />
          </el-select>
        </div>

        <button class="btn-reset" @click="resetFilters">
          <el-icon><Refresh /></el-icon>
          重置
        </button>
      </div>
    </div>

    <!-- 错题列表 -->
    <div class="questions-section" v-loading="loading">
      <el-empty
        v-if="!loading && wrongQuestions.length === 0"
        description="暂无错题，继续保持！"
        :image-size="200"
      >
        <template #image>
          <div class="empty-icon">
            <el-icon :size="80" color="#67c23a"><CircleCheck /></el-icon>
          </div>
        </template>
      </el-empty>

      <div class="questions-list">
        <div
          v-for="(item, index) in wrongQuestions"
          :key="item.wrong_question.id"
          class="question-item"
          :style="{ animationDelay: `${index * 0.05}s` }"
        >
          <!-- 错题状态栏 -->
          <div class="question-status-bar">
            <div class="status-left">
              <span 
                class="status-badge"
                :class="item.wrong_question.mastered ? 'mastered' : 'unmastered'"
              >
                {{ item.wrong_question.mastered ? '已掌握' : '未掌握' }}
              </span>
              <span class="wrong-count">
                <el-icon><Warning /></el-icon>
                错误次数: {{ item.wrong_question.wrong_count }}
              </span>
              <span class="last-wrong">
                <el-icon><Clock /></el-icon>
                最近错误: {{ formatDate(item.wrong_question.last_wrong_at) }}
              </span>
            </div>
            <div class="status-right">
              <el-tag v-if="item.question.exam_type" size="small" type="info">
                {{ getExamTypeLabel(item.question.exam_type) }}
              </el-tag>
              <el-tag v-if="item.question.subject" size="small">
                {{ item.question.subject }}
              </el-tag>
            </div>
          </div>

          <!-- 题目内容 -->
          <div class="question-content">
            <div class="question-number">第 {{ index + 1 }} 题</div>
            <QuestionCard
              :question="item.question"
              :show-order="false"
              :show-explanation="expandedQuestions.includes(item.question.id)"
              :show-correct-answer="expandedQuestions.includes(item.question.id)"
              disabled
            />
          </div>

          <!-- 操作按钮 -->
          <div class="question-actions">
            <button
              class="action-btn view"
              @click="toggleExplanation(item.question.id)"
            >
              <el-icon><View /></el-icon>
              {{ expandedQuestions.includes(item.question.id) ? '收起解析' : '查看解析' }}
            </button>
            <button
              class="action-btn practice"
              @click="practiceQuestion(item.question)"
            >
              <el-icon><Edit /></el-icon>
              单题练习
            </button>
            <button
              class="action-btn remove"
              @click="confirmRemove(item.wrong_question.id)"
            >
              <el-icon><Delete /></el-icon>
              移除
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 单题练习对话框 -->
    <el-dialog
      v-model="practiceDialogVisible"
      title="单题练习"
      width="800px"
      :close-on-click-modal="false"
      class="practice-dialog"
    >
      <div v-if="currentPracticeQuestion" class="practice-content">
        <QuestionCard
          :question="currentPracticeQuestion"
          :user-answer="practiceAnswer"
          :show-correct-answer="practiceSubmitted"
          :show-explanation="practiceSubmitted"
          :show-result="practiceSubmitted"
          :disabled="practiceSubmitted"
          @answer-change="handlePracticeAnswerChange"
        />
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="closePracticeDialog">取消</el-button>
          <el-button
            v-if="!practiceSubmitted"
            type="primary"
            :disabled="!practiceAnswer"
            @click="submitPracticeAnswer"
          >
            提交答案
          </el-button>
          <el-button
            v-else
            type="success"
            @click="closePracticeDialog"
          >
            完成
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Edit, Collection, Document, Warning, CircleCheck, 
  Clock, View, Delete, Refresh 
} from '@element-plus/icons-vue'
import QuestionCard from '../components/QuestionCard.vue'
import { getWrongBook, removeFromWrongBook } from '../api/practice'
import { submitPracticeAnswer as submitAnswer } from '../api/practice'

const router = useRouter()

// 数据状态
const loading = ref(false)
const wrongQuestions = ref([])
const expandedQuestions = ref([])

// 筛选条件
const filters = ref({
  mastered: null,
  exam_type: '',
  subject: ''
})

// 单题练习相关
const practiceDialogVisible = ref(false)
const currentPracticeQuestion = ref(null)
const practiceAnswer = ref(null)
const practiceSubmitted = ref(false)

// 统计信息
const unmasteredCount = computed(() => {
  return wrongQuestions.value.filter(item => !item.wrong_question.mastered).length
})

const masteredCount = computed(() => {
  return wrongQuestions.value.filter(item => item.wrong_question.mastered).length
})

/**
 * 获取考试类型标签
 */
function getExamTypeLabel(type) {
  const labels = {
    civil_service: '公务员',
    postgraduate: '研究生',
    public_institution: '事业编'
  }
  return labels[type] || type
}

/**
 * 加载错题本
 */
async function loadWrongBook() {
  loading.value = true
  try {
    const params = {}
    if (filters.value.mastered !== null) {
      params.mastered = filters.value.mastered
    }
    if (filters.value.exam_type) {
      params.exam_type = filters.value.exam_type
    }
    if (filters.value.subject) {
      params.subject = filters.value.subject
    }

    const response = await getWrongBook(params)
    if (response.success && response.data) {
      wrongQuestions.value = response.data.wrong_questions || []
    } else {
      wrongQuestions.value = []
    }
  } catch (error) {
    console.error('加载错题本失败:', error)
    ElMessage.error('加载错题本失败')
    wrongQuestions.value = []
  } finally {
    loading.value = false
  }
}

/**
 * 重置筛选条件
 */
function resetFilters() {
  filters.value = {
    mastered: null,
    exam_type: '',
    subject: ''
  }
  loadWrongBook()
}

/**
 * 切换题目解析显示
 */
function toggleExplanation(questionId) {
  const index = expandedQuestions.value.indexOf(questionId)
  if (index > -1) {
    expandedQuestions.value.splice(index, 1)
  } else {
    expandedQuestions.value.push(questionId)
  }
}

/**
 * 单题练习
 */
function practiceQuestion(question) {
  currentPracticeQuestion.value = question
  practiceAnswer.value = null
  practiceSubmitted.value = false
  practiceDialogVisible.value = true
}

/**
 * 处理练习答案变化
 */
function handlePracticeAnswerChange(answer) {
  practiceAnswer.value = answer
}

/**
 * 提交练习答案
 */
async function submitPracticeAnswer() {
  if (!practiceAnswer.value) {
    ElMessage.warning('请先选择答案')
    return
  }

  try {
    const response = await submitAnswer({
      question_id: currentPracticeQuestion.value.id,
      user_answer: practiceAnswer.value,
      time_spent: 0
    })

    if (response.data.success) {
      practiceSubmitted.value = true
      const result = response.data.data
      
      if (result.is_correct) {
        ElMessage.success('回答正确！')
        setTimeout(() => {
          loadWrongBook()
        }, 1000)
      } else {
        ElMessage.error('回答错误，请查看解析')
      }
    } else {
      ElMessage.error(response.data.error?.message || '提交失败')
    }
  } catch (error) {
    console.error('提交答案失败:', error)
    ElMessage.error('提交答案失败')
  }
}

/**
 * 关闭练习对话框
 */
function closePracticeDialog() {
  practiceDialogVisible.value = false
  currentPracticeQuestion.value = null
  practiceAnswer.value = null
  practiceSubmitted.value = false
}

/**
 * 确认移除错题
 */
async function confirmRemove(wrongQuestionId) {
  try {
    await ElMessageBox.confirm(
      '确定要从错题本中移除这道题吗？',
      '确认移除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await removeQuestion(wrongQuestionId)
  } catch (error) {
    if (error !== 'cancel') {
      console.error('移除错题失败:', error)
    }
  }
}

/**
 * 移除错题
 */
async function removeQuestion(wrongQuestionId) {
  try {
    const response = await removeFromWrongBook(wrongQuestionId)
    
    if (response.data.success) {
      ElMessage.success('移除成功')
      wrongQuestions.value = wrongQuestions.value.filter(
        item => item.wrong_question.id !== wrongQuestionId
      )
    } else {
      ElMessage.error(response.data.error?.message || '移除失败')
    }
  } catch (error) {
    console.error('移除错题失败:', error)
    ElMessage.error('移除失败')
  }
}

/**
 * 从错题本开始练习
 */
function startPracticeFromWrongBook() {
  router.push({
    path: '/practice',
    query: {
      from_wrong_book: 'true'
    }
  })
}

/**
 * 格式化日期
 */
function formatDate(dateString) {
  if (!dateString) return '-'
  
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`
  
  return date.toLocaleDateString('zh-CN')
}

onMounted(() => {
  loadWrongBook()
})
</script>


<style scoped>
.wrong-book-container {
  min-height: 100vh;
  background: transparent;
}

/* 顶部横幅 */
.page-banner {
  position: relative;
  padding: 40px 24px;
  background: linear-gradient(135deg, #1a0a2e 0%, #2d1b3d 50%, #0f0c29 100%);
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
    radial-gradient(ellipse at 20% 80%, rgba(245, 108, 108, 0.3) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 30%, rgba(230, 162, 60, 0.25) 0%, transparent 50%);
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
}

.banner-text p {
  margin: 0;
  font-size: 16px;
  color: rgba(255, 255, 255, 0.9);
}

.btn-practice {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 28px;
  background: white;
  color: #f56c6c;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.btn-practice:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.btn-practice:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 统计卡片 */
.stats-section {
  max-width: 1200px;
  margin: -30px auto 0;
  padding: 0 24px;
  position: relative;
  z-index: 10;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  background: rgba(255, 255, 255, 0.15);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.25);
}

.stat-value {
  color: white !important;
}

.stat-label {
  color: rgba(255, 255, 255, 0.8) !important;
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-card.total .stat-icon {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
}

.stat-card.unmastered .stat-icon {
  background: linear-gradient(135deg, #f56c6c 0%, #f89898 100%);
}

.stat-card.mastered .stat-icon {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

/* 筛选区域 */
.filter-section {
  max-width: 1200px;
  margin: 24px auto;
  padding: 0 24px;
}

.filter-bar {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  padding: 20px 24px;
  display: flex;
  align-items: flex-end;
  gap: 24px;
  flex-wrap: wrap;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.filter-group label {
  color: rgba(255, 255, 255, 0.9) !important;
}

/* el-select 玻璃效果 */
.filter-group :deep(.el-select .el-input__wrapper) {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: none;
}

.filter-group :deep(.el-select .el-input__inner) {
  color: white;
}

.filter-group :deep(.el-select .el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.5);
}

.filter-group :deep(.el-select .el-input__suffix) {
  color: rgba(255, 255, 255, 0.6);
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-group label {
  font-size: 13px;
  color: #606266;
  font-weight: 500;
}

.filter-group .el-select {
  width: 160px;
}

.btn-reset {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-reset:hover {
  background: rgba(64, 158, 255, 0.2);
  color: #60a5fa;
  border-color: rgba(64, 158, 255, 0.5);
}

/* 错题列表 */
.questions-section {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px 40px;
}

.questions-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.question-item {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  animation: fadeInUp 0.5s ease forwards;
  opacity: 0;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.question-status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.last-wrong {
  color: rgba(255, 255, 255, 0.7) !important;
}

.status-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge.unmastered {
  background: linear-gradient(135deg, #fef0f0 0%, #fde2e2 100%);
  color: #f56c6c;
}

.status-badge.mastered {
  background: linear-gradient(135deg, #f0f9eb 0%, #e1f3d8 100%);
  color: #67c23a;
}

.wrong-count,
.last-wrong {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #909399;
}

.wrong-count {
  color: #f56c6c;
  font-weight: 500;
}

.status-right {
  display: flex;
  gap: 8px;
}

.question-content {
  padding: 24px;
}

.question-number {
  font-size: 14px;
  font-weight: 600;
  color: #60a5fa;
  margin-bottom: 12px;
}

.question-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  background: rgba(255, 255, 255, 0.05);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-btn.view {
  background: #ecf5ff;
  color: #409eff;
}

.action-btn.view:hover {
  background: #409eff;
  color: white;
}

.action-btn.practice {
  background: #f0f9eb;
  color: #67c23a;
}

.action-btn.practice:hover {
  background: #67c23a;
  color: white;
}

.action-btn.remove {
  background: #fef0f0;
  color: #f56c6c;
}

.action-btn.remove:hover {
  background: #f56c6c;
  color: white;
}

/* 空状态 */
.empty-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 160px;
  height: 160px;
  background: linear-gradient(135deg, #f0f9eb 0%, #e1f3d8 100%);
  border-radius: 50%;
  margin: 0 auto;
}

/* 对话框 */
.practice-dialog .practice-content {
  padding: 20px 0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 响应式 */
@media (max-width: 768px) {
  .page-banner {
    padding: 24px 16px;
  }

  .banner-content {
    flex-direction: column;
    text-align: center;
  }

  .stats-section {
    padding: 0 16px;
  }

  .stats-cards {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .filter-section {
    padding: 0 16px;
  }

  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-group .el-select {
    width: 100%;
  }

  .questions-section {
    padding: 0 16px 24px;
  }

  .question-status-bar {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .question-actions {
    flex-wrap: wrap;
    justify-content: center;
  }
}
</style>
