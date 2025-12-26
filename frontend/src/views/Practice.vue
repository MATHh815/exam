<template>
  <div class="practice-container">
    <!-- 练习设置界面 -->
    <div v-if="!hasPracticeStarted" class="practice-setup">
      <!-- 顶部横幅 -->
      <div class="setup-banner">
        <div class="banner-bg"></div>
        <div class="banner-content">
          <div class="banner-icon">
            <el-icon :size="56"><Aim /></el-icon>
          </div>
          <div class="banner-text">
            <h1>智能练习</h1>
            <p>根据你的学习情况，智能推荐练习题目</p>
          </div>
        </div>
      </div>

      <!-- 练习模式选择 -->
      <div class="mode-section">
        <div class="section-title">选择练习模式</div>
        <div class="mode-cards">
          <div 
            class="mode-card" 
            :class="{ active: practiceMode === 'random' }" 
            @click="practiceMode = 'random'"
          >
            <div class="mode-glow"></div>
            <div class="mode-icon random">
              <el-icon :size="36"><Refresh /></el-icon>
            </div>
            <div class="mode-info">
              <h3>随机练习</h3>
              <p>从题库中随机抽取题目</p>
            </div>
            <div class="mode-check" v-if="practiceMode === 'random'">
              <el-icon><Check /></el-icon>
            </div>
          </div>
          
          <div 
            class="mode-card" 
            :class="{ active: practiceMode === 'wrong' }" 
            @click="practiceMode = 'wrong'"
          >
            <div class="mode-glow"></div>
            <div class="mode-icon wrong">
              <el-icon :size="36"><Collection /></el-icon>
            </div>
            <div class="mode-info">
              <h3>错题练习</h3>
              <p>针对错题进行强化训练</p>
            </div>
            <el-badge v-if="wrongBookCount > 0" :value="wrongBookCount" class="wrong-badge" />
            <div class="mode-check" v-if="practiceMode === 'wrong'">
              <el-icon><Check /></el-icon>
            </div>
          </div>
          
          <div 
            class="mode-card" 
            :class="{ active: practiceMode === 'weak' }" 
            @click="practiceMode = 'weak'"
          >
            <div class="mode-glow"></div>
            <div class="mode-icon weak">
              <el-icon :size="36"><TrendCharts /></el-icon>
            </div>
            <div class="mode-info">
              <h3>薄弱点练习</h3>
              <p>针对薄弱知识点强化</p>
            </div>
            <div class="mode-check" v-if="practiceMode === 'weak'">
              <el-icon><Check /></el-icon>
            </div>
          </div>
        </div>
      </div>

      <!-- 练习参数设置 -->
      <div class="settings-section">
        <div class="section-title">练习设置</div>
        <div class="settings-card">
          <div class="settings-grid">
            <div class="setting-item">
              <label>考试类型</label>
              <el-select 
                v-model="practiceForm.exam_type" 
                placeholder="全部类型" 
                clearable
              >
                <el-option label="公务员考试" value="civil_service" />
                <el-option label="研究生考试" value="postgraduate" />
                <el-option label="事业编考试" value="public_institution" />
              </el-select>
            </div>
            <div class="setting-item">
              <label>题目类型</label>
              <el-select 
                v-model="practiceForm.question_type" 
                placeholder="全部题型" 
                clearable
              >
                <el-option label="单选题" value="single_choice" />
                <el-option label="多选题" value="multiple_choice" />
                <el-option label="判断题" value="true_false" />
              </el-select>
            </div>
          </div>
          
          <div class="count-setting">
            <label>题目数量</label>
            <div class="count-control">
              <div class="count-buttons">
                <button 
                  v-for="count in [5, 10, 20, 30, 50]" 
                  :key="count"
                  class="count-btn"
                  :class="{ active: practiceForm.count === count }"
                  @click="practiceForm.count = count"
                >
                  {{ count }} 题
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 开始按钮 -->
      <div class="start-section">
        <button 
          class="btn-start" 
          @click="handleStartPractice" 
          :disabled="startingPractice"
        >
          <el-icon v-if="!startingPractice"><VideoPlay /></el-icon>
          <el-icon v-else class="is-loading"><Loading /></el-icon>
          <span>开始练习</span>
        </button>
      </div>
    </div>

    <!-- 练习进行中界面 -->
    <div v-else class="practice-content">
      <!-- 顶部工具栏 -->
      <div class="practice-header">
        <div class="header-left">
          <button class="btn-back" @click="handleExit">
            <el-icon><ArrowLeft /></el-icon>
            返回
          </button>
          <div class="progress-info">
            <span class="current-num">{{ currentQuestionIndex + 1 }}</span>
            <span class="separator">/</span>
            <span class="total-num">{{ questions.length }}</span>
          </div>
        </div>
        
        <div class="header-center">
          <div class="progress-bar">
            <div 
              class="progress-fill" 
              :style="{ width: progressPercentage + '%' }"
            ></div>
          </div>
        </div>
        
        <div class="header-right">
          <div class="stats-mini">
            <div class="stat-item correct">
              <el-icon><CircleCheck /></el-icon>
              <span>{{ correctCount }}</span>
            </div>
            <div class="stat-item wrong">
              <el-icon><CircleClose /></el-icon>
              <span>{{ wrongCount }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 主体内容 -->
      <div class="practice-body">
        <!-- 题目区域 -->
        <div class="question-area">
          <div class="question-wrapper">
            <QuestionCard
              v-if="currentQuestion"
              :question="currentQuestion"
              :show-answer="showAnswer"
              :show-explanation="showAnswer"
              :user-answer="userAnswer"
              @answer-change="handleAnswerChange"
            />
          </div>
          
          <!-- 答题结果提示 -->
          <transition name="slide-fade">
            <div v-if="showAnswer" class="answer-feedback" :class="isCorrect ? 'correct' : 'wrong'">
              <div class="feedback-icon">
                <el-icon :size="32">
                  <CircleCheck v-if="isCorrect" />
                  <CircleClose v-else />
                </el-icon>
              </div>
              <div class="feedback-text">
                <span class="feedback-title">{{ isCorrect ? '回答正确！' : '回答错误' }}</span>
                <span v-if="!isCorrect" class="correct-answer">
                  正确答案：{{ currentQuestion.correct_answer }}
                </span>
              </div>
            </div>
          </transition>
          
          <!-- 操作按钮 -->
          <div class="action-buttons">
            <button 
              class="btn-nav prev" 
              @click="handlePrevQuestion" 
              :disabled="currentQuestionIndex === 0"
            >
              <el-icon><ArrowLeft /></el-icon>
              上一题
            </button>
            
            <button 
              v-if="!showAnswer"
              class="btn-submit"
              @click="handleSubmitAnswer"
              :disabled="!userAnswer || submitting"
            >
              <el-icon v-if="!submitting"><Select /></el-icon>
              <el-icon v-else class="is-loading"><Loading /></el-icon>
              确认答案
            </button>
            
            <button 
              v-else
              class="btn-next"
              @click="handleNextQuestion"
            >
              {{ currentQuestionIndex < questions.length - 1 ? '下一题' : '完成练习' }}
              <el-icon><ArrowRight /></el-icon>
            </button>
          </div>
        </div>

        <!-- 右侧题号导航 -->
        <div class="question-nav">
          <div class="nav-header">
            <span class="nav-title">题目导航</span>
            <span class="nav-progress">{{ answeredCount }}/{{ questions.length }}</span>
          </div>
          <div class="nav-grid">
            <div
              v-for="(q, index) in questions"
              :key="q.id"
              class="nav-item"
              :class="getNavItemClass(index)"
              @click="navigateToQuestion(index)"
            >
              {{ index + 1 }}
            </div>
          </div>
          <div class="nav-legend">
            <div class="legend-item">
              <span class="dot current"></span>
              <span>当前</span>
            </div>
            <div class="legend-item">
              <span class="dot correct"></span>
              <span>正确</span>
            </div>
            <div class="legend-item">
              <span class="dot wrong"></span>
              <span>错误</span>
            </div>
            <div class="legend-item">
              <span class="dot unanswered"></span>
              <span>未答</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 练习完成弹窗 -->
    <el-dialog 
      v-model="showSummary" 
      title="" 
      width="420px" 
      :close-on-click-modal="false"
      class="summary-dialog"
    >
      <div class="summary-content">
        <div class="summary-header">
          <el-icon :size="48" :class="getScoreClass()"><Trophy /></el-icon>
          <h2>练习完成</h2>
        </div>
        
        <div class="score-display">
          <div class="score-circle" :class="getScoreClass()">
            <span class="score-value">{{ accuracyRate }}</span>
            <span class="score-unit">%</span>
          </div>
          <div class="score-label">正确率</div>
        </div>
        
        <div class="summary-stats">
          <div class="summary-stat">
            <span class="stat-value">{{ questions.length }}</span>
            <span class="stat-label">总题数</span>
          </div>
          <div class="summary-stat correct">
            <span class="stat-value">{{ correctCount }}</span>
            <span class="stat-label">正确</span>
          </div>
          <div class="summary-stat wrong">
            <span class="stat-value">{{ wrongCount }}</span>
            <span class="stat-label">错误</span>
          </div>
        </div>
      </div>
      
      <template #footer>
        <div class="summary-actions">
          <button class="btn-secondary" @click="handleReviewWrong" v-if="wrongCount > 0">
            <el-icon><Collection /></el-icon>
            查看错题
          </button>
          <button class="btn-primary" @click="handleFinish">
            <el-icon><House /></el-icon>
            返回首页
          </button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 练习专用 AI 助手（带题目上下文） -->
    <AIChat 
      ref="aiChatRef"
      v-if="hasPracticeStarted"
      :question-context="currentQuestionContext"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh, Collection, Aim, VideoPlay, ArrowLeft, ArrowRight,
  CircleCheck, CircleClose, Check, TrendCharts, Loading, Select,
  Trophy, House
} from '@element-plus/icons-vue'
import QuestionCard from '../components/QuestionCard.vue'
import AIChat from '../components/AIChat.vue'
import { startPractice, submitPracticeAnswer, getWrongBook } from '../api/practice'

const router = useRouter()

// 练习状态
const hasPracticeStarted = ref(false)
const startingPractice = ref(false)
const practiceMode = ref('random')
const wrongBookCount = ref(0)

// 练习参数
const practiceForm = ref({
  exam_type: '',
  question_type: '',
  count: 10
})

// 题目状态
const questions = ref([])
const currentQuestionIndex = ref(0)
const userAnswer = ref('')
const showAnswer = ref(false)
const isCorrect = ref(false)
const submitting = ref(false)
const showSummary = ref(false)

// 答题记录
const answeredQuestions = ref(new Map())

// AI 助手 ref
const aiChatRef = ref(null)

// 计算属性
const currentQuestion = computed(() => questions.value[currentQuestionIndex.value])
const answeredCount = computed(() => answeredQuestions.value.size)
const correctCount = computed(() => {
  let count = 0
  answeredQuestions.value.forEach(record => { if (record.isCorrect) count++ })
  return count
})
const wrongCount = computed(() => answeredCount.value - correctCount.value)
const accuracyRate = computed(() => {
  if (answeredCount.value === 0) return 0
  return Math.round((correctCount.value / answeredCount.value) * 100)
})
const progressPercentage = computed(() => {
  if (questions.value.length === 0) return 0
  return Math.round((answeredCount.value / questions.value.length) * 100)
})

// 当前题目上下文（传递给 AI 助手）
const currentQuestionContext = computed(() => {
  if (!currentQuestion.value) return null
  
  return {
    question: {
      id: currentQuestion.value.id,
      content: currentQuestion.value.content,
      type: currentQuestion.value.type,
      options: currentQuestion.value.options,
      category: currentQuestion.value.category,
      difficulty: currentQuestion.value.difficulty
    },
    questionNumber: currentQuestionIndex.value + 1,
    totalQuestions: questions.value.length,
    mode: practiceMode.value === 'wrong' ? '错题练习' : practiceMode.value === 'weak' ? '薄弱点练习' : '随机练习'
  }
})

function getNavItemClass(index) {
  const classes = []
  if (index === currentQuestionIndex.value) classes.push('current')
  const question = questions.value[index]
  const record = answeredQuestions.value.get(question.id)
  if (record) {
    classes.push(record.isCorrect ? 'correct' : 'wrong')
  }
  return classes.join(' ')
}

function getScoreClass() {
  if (accuracyRate.value >= 80) return 'excellent'
  if (accuracyRate.value >= 60) return 'good'
  return 'poor'
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

async function handleStartPractice() {
  startingPractice.value = true
  try {
    const params = { ...practiceForm.value }
    if (practiceMode.value === 'wrong') {
      params.from_wrong_book = true
    }
    
    const response = await startPractice(params)
    if (response.data?.questions && response.data.questions.length > 0) {
      questions.value = response.data.questions
      hasPracticeStarted.value = true
      ElMessage.success(`已加载 ${questions.value.length} 道题目`)
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

function handleAnswerChange(answer) {
  userAnswer.value = answer
}

async function handleSubmitAnswer() {
  if (!userAnswer.value) {
    ElMessage.warning('请先选择答案')
    return
  }
  
  submitting.value = true
  try {
    const response = await submitPracticeAnswer({
      question_id: currentQuestion.value.id,
      user_answer: userAnswer.value,
      time_spent: 0
    })
    
    if (response.success) {
      isCorrect.value = response.data.is_correct
      showAnswer.value = true
      answeredQuestions.value.set(currentQuestion.value.id, {
        answer: userAnswer.value,
        isCorrect: isCorrect.value
      })
    }
  } catch (error) {
    console.error('提交答案失败:', error)
    ElMessage.error('提交答案失败')
  } finally {
    submitting.value = false
  }
}

function handlePrevQuestion() {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--
    resetQuestionState()
  }
}

function handleNextQuestion() {
  if (currentQuestionIndex.value < questions.value.length - 1) {
    currentQuestionIndex.value++
    resetQuestionState()
  } else {
    showSummary.value = true
  }
}

function navigateToQuestion(index) {
  currentQuestionIndex.value = index
  resetQuestionState()
}

function resetQuestionState() {
  const record = answeredQuestions.value.get(currentQuestion.value.id)
  if (record) {
    userAnswer.value = record.answer
    showAnswer.value = true
    isCorrect.value = record.isCorrect
  } else {
    userAnswer.value = ''
    showAnswer.value = false
    isCorrect.value = false
  }
}

function handleExit() {
  if (answeredCount.value > 0) {
    ElMessageBox.confirm('确定要退出练习吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      hasPracticeStarted.value = false
      questions.value = []
      answeredQuestions.value.clear()
    }).catch(() => {})
  } else {
    hasPracticeStarted.value = false
  }
}

function handleReviewWrong() {
  showSummary.value = false
  router.push('/wrong-book')
}

function handleFinish() {
  showSummary.value = false
  sessionStorage.setItem('refreshDashboard', 'true')
  router.push('/dashboard')
}

onMounted(() => {
  const questionsData = sessionStorage.getItem('practiceQuestions')
  if (questionsData) {
    try {
      questions.value = JSON.parse(questionsData)
      sessionStorage.removeItem('practiceQuestions')
      hasPracticeStarted.value = true
    } catch (error) {
      console.error('解析题目数据失败:', error)
    }
  }
  loadWrongBookCount()
})
</script>


<style scoped>
.practice-container {
  min-height: 100vh;
  background: transparent;
}

/* 练习设置界面 */
.practice-setup {
  max-width: 900px;
  margin: 0 auto;
  padding-bottom: 40px;
}

/* 顶部横幅 */
.setup-banner {
  position: relative;
  padding: 48px 24px;
  background: linear-gradient(135deg, #0c1445 0%, #1a0a2e 50%, #16213e 100%);
  overflow: hidden;
  margin-bottom: 32px;
}

.setup-banner .banner-bg {
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

.setup-banner .banner-content {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 24px;
}

.setup-banner .banner-icon {
  width: 100px;
  height: 100px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  backdrop-filter: blur(10px);
}

.setup-banner .banner-text {
  text-align: left;
}

.setup-banner .banner-text h1 {
  margin: 0 0 8px 0;
  font-size: 36px;
  font-weight: 700;
  color: white;
}

.setup-banner .banner-text p {
  margin: 0;
  font-size: 16px;
  color: rgba(255, 255, 255, 0.9);
}

/* 区块标题 */
.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 20px;
  padding-left: 24px;
}

/* 模式选择卡片 */
.mode-section {
  margin-bottom: 32px;
}

.mode-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  padding: 0 24px;
}

.mode-card {
  position: relative;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 28px 24px;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  border: 2px solid transparent;
  overflow: hidden;
}

.mode-glow {
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(102, 126, 234, 0.1) 0%, transparent 70%);
  opacity: 0;
  transition: opacity 0.4s ease;
}

.mode-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.mode-card:hover .mode-glow {
  opacity: 1;
}

.mode-card.active {
  border-color: #667eea;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%);
}

.mode-icon {
  width: 72px;
  height: 72px;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  transition: transform 0.3s ease;
}

.mode-card:hover .mode-icon {
  transform: scale(1.1);
}

.mode-icon.random {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  color: white;
  box-shadow: 0 8px 20px rgba(64, 158, 255, 0.3);
}

.mode-icon.wrong {
  background: linear-gradient(135deg, #f56c6c 0%, #f89898 100%);
  color: white;
  box-shadow: 0 8px 20px rgba(245, 108, 108, 0.3);
}

.mode-icon.weak {
  background: linear-gradient(135deg, #e6a23c 0%, #ebb563 100%);
  color: white;
  box-shadow: 0 8px 20px rgba(230, 162, 60, 0.3);
}

.mode-info h3 {
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  margin: 0 0 8px 0;
}

.mode-info p {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
}

.mode-check {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 14px;
}

.wrong-badge {
  position: absolute;
  top: 12px;
  right: 12px;
}

/* 设置卡片 */
.settings-section {
  margin-bottom: 32px;
}

.settings-card {
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 28px;
  margin: 0 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  margin-bottom: 24px;
}

.setting-item {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.setting-item label {
  font-size: 14px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
}

.setting-item .el-select {
  width: 100%;
}

.count-setting {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.count-setting label {
  font-size: 14px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
}

.count-buttons {
  display: flex;
  gap: 12px;
}

.count-btn {
  flex: 1;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  transition: all 0.3s ease;
}

.count-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.count-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-color: transparent;
}

/* 开始按钮 */
.start-section {
  text-align: center;
  padding: 0 24px;
}

.btn-start {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  padding: 18px 56px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 16px;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.btn-start:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 12px 35px rgba(102, 126, 234, 0.5);
}

.btn-start:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* 练习进行中界面 */
.practice-content {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.practice-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background: rgba(30, 30, 45, 0.8);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.btn-back {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-back:hover {
  background: rgba(255, 255, 255, 0.15);
}

.progress-info {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.current-num {
  font-size: 24px;
  font-weight: 700;
  color: #667eea;
}

.separator {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.4);
}

.total-num {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.6);
}

.header-center {
  flex: 1;
  max-width: 300px;
  margin: 0 24px;
}

.progress-bar {
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.stats-mini {
  display: flex;
  gap: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 16px;
  font-weight: 600;
}

.stat-item.correct {
  color: #67c23a;
}

.stat-item.wrong {
  color: #f56c6c;
}

.practice-body {
  flex: 1;
  display: flex;
  padding: 20px;
  gap: 20px;
  overflow: hidden;
  min-height: 0;
}

.question-area {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 24px;
  overflow-y: auto;
}

.question-wrapper {
  flex: 1;
}

.answer-feedback {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 24px;
  border-radius: 16px;
  margin-top: 24px;
}

.answer-feedback.correct {
  background: linear-gradient(135deg, #f0f9eb 0%, #e1f3d8 100%);
}

.answer-feedback.wrong {
  background: linear-gradient(135deg, #fef0f0 0%, #fde2e2 100%);
}

.feedback-icon {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.answer-feedback.correct .feedback-icon {
  background: #67c23a;
  color: white;
}

.answer-feedback.wrong .feedback-icon {
  background: #f56c6c;
  color: white;
}

.feedback-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.feedback-title {
  font-size: 18px;
  font-weight: 600;
}

.answer-feedback.correct .feedback-title {
  color: #67c23a;
}

.answer-feedback.wrong .feedback-title {
  color: #f56c6c;
}

.correct-answer {
  font-size: 14px;
  color: #909399;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #ebeef5;
}

.btn-nav {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: #f5f7fa;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  color: #606266;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-nav:hover:not(:disabled) {
  background: #e4e7ed;
}

.btn-nav:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-submit,
.btn-next {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 36px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.35);
}

.btn-submit:hover:not(:disabled),
.btn-next:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.45);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 题号导航 */
.question-nav {
  width: 240px;
  min-width: 240px;
  max-width: 240px;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 20px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.nav-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-shrink: 0;
}

.nav-title {
  font-size: 15px;
  font-weight: 600;
  color: #fff;
}

.nav-progress {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

.nav-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 6px;
  margin-bottom: 16px;
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  align-content: start;
  max-height: calc(100vh - 300px);
}

.nav-item {
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.6);
  transition: all 0.2s ease;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: scale(1.1);
}

.nav-item.current {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.nav-item.correct {
  background: #67c23a;
  color: white;
}

.nav-item.wrong {
  background: #f56c6c;
  color: white;
}

.nav-legend {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
  flex-shrink: 0;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: #909399;
}

.legend-item .dot {
  width: 10px;
  height: 10px;
  border-radius: 3px;
  flex-shrink: 0;
}

.dot.current { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.dot.correct { background: #67c23a; }
.dot.wrong { background: #f56c6c; }
.dot.unanswered { background: #f5f7fa; border: 1px solid #dcdfe6; }

/* 练习完成弹窗 */
.summary-dialog :deep(.el-dialog__header) {
  display: none;
}

.summary-content {
  text-align: center;
  padding: 20px 0;
}

.summary-header {
  margin-bottom: 24px;
}

.summary-header .el-icon {
  margin-bottom: 12px;
}

.summary-header .el-icon.excellent { color: #67c23a; }
.summary-header .el-icon.good { color: #e6a23c; }
.summary-header .el-icon.poor { color: #f56c6c; }

.summary-header h2 {
  margin: 0;
  font-size: 24px;
  color: #303133;
}

.score-display {
  margin-bottom: 32px;
}

.score-circle {
  width: 140px;
  height: 140px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
}

.score-circle.excellent {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%);
  box-shadow: 0 8px 30px rgba(103, 194, 58, 0.4);
}

.score-circle.good {
  background: linear-gradient(135deg, #e6a23c 0%, #ebb563 100%);
  box-shadow: 0 8px 30px rgba(230, 162, 60, 0.4);
}

.score-circle.poor {
  background: linear-gradient(135deg, #f56c6c 0%, #f89898 100%);
  box-shadow: 0 8px 30px rgba(245, 108, 108, 0.4);
}

.score-value {
  font-size: 48px;
  font-weight: 700;
  color: white;
  line-height: 1;
}

.score-unit {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.9);
}

.score-label {
  font-size: 14px;
  color: #909399;
}

.summary-stats {
  display: flex;
  justify-content: center;
  gap: 40px;
}

.summary-stat {
  text-align: center;
}

.summary-stat .stat-value {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: #303133;
}

.summary-stat.correct .stat-value { color: #67c23a; }
.summary-stat.wrong .stat-value { color: #f56c6c; }

.summary-stat .stat-label {
  font-size: 13px;
  color: #909399;
}

.summary-actions {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.btn-secondary,
.btn-primary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-secondary {
  background: #f5f7fa;
  color: #606266;
}

.btn-secondary:hover {
  background: #e4e7ed;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.35);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.45);
}

/* 动画 */
.slide-fade-enter-active {
  transition: all 0.4s ease;
}

.slide-fade-leave-active {
  transition: all 0.3s ease;
}

.slide-fade-enter-from {
  transform: translateY(-20px);
  opacity: 0;
}

.slide-fade-leave-to {
  opacity: 0;
}

.is-loading {
  animation: rotating 1s linear infinite;
}

@keyframes rotating {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 响应式 */
@media (max-width: 1200px) {
  .question-nav {
    width: 200px;
    min-width: 200px;
    max-width: 200px;
    padding: 16px;
  }
  
  .nav-grid {
    grid-template-columns: repeat(4, 1fr);
    max-height: calc(100vh - 280px);
  }
}

@media (max-width: 768px) {
  .mode-cards {
    grid-template-columns: 1fr;
  }
  
  .settings-grid {
    grid-template-columns: 1fr;
  }
  
  .count-buttons {
    flex-wrap: wrap;
  }
  
  .count-btn {
    flex: 0 0 calc(33.33% - 8px);
  }
  
  .practice-body {
    flex-direction: column;
    padding: 16px;
  }
  
  .question-nav {
    width: 100%;
    min-width: 100%;
    max-width: 100%;
    order: -1;
    padding: 16px;
  }
  
  .nav-grid {
    grid-template-columns: repeat(10, 1fr);
    max-height: 120px;
  }
  
  .nav-legend {
    grid-template-columns: repeat(4, 1fr);
  }
  
  .question-area {
    padding: 16px;
  }
  
  .action-buttons {
    flex-wrap: wrap;
  }
}
</style>
