<template>
  <div class="exam-container">
    <!-- 加载状态 -->
    <el-skeleton v-if="loading" :rows="10" animated />
    
    <!-- 考试界面 -->
    <div v-else-if="examStore.isExamInProgress" class="exam-content">
      <!-- 顶部工具栏 -->
      <div class="exam-header">
        <div class="header-left">
          <h2 class="exam-title">{{ examStore.currentPaper?.name }}</h2>
          <el-tag type="info">{{ examTypeLabel }}</el-tag>
        </div>
        
        <div class="header-right">
          <ExamTimer 
            ref="timerRef"
            :duration="examStore.timeRemaining"
            :enable-voice="true"
            @timeout="handleTimeout"
            @tick="handleTimerTick"
            @voice-reminder="handleVoiceReminder"
          />
          <!-- AI 助手按钮 -->
          <el-tooltip content="AI 智能助手" placement="bottom">
            <el-button 
              type="info" 
              circle
              @click="toggleAIChat"
            >
              <el-icon><ChatDotRound /></el-icon>
            </el-button>
          </el-tooltip>
          <el-button 
            type="primary" 
            @click="handleSubmit"
            :loading="submitting"
          >
            提交试卷
          </el-button>
        </div>
      </div>
      
      <!-- 主体内容 -->
      <el-row :gutter="20" class="exam-body">
        <!-- 左侧：题目区域 -->
        <el-col :span="18">
          <div class="question-area">
            <!-- 题目卡片 -->
            <QuestionCard
              v-if="currentQuestion"
              :question="currentQuestion"
              :show-answer="false"
              :show-explanation="false"
              :user-answer="examStore.getAnswer(currentQuestion.id)"
              @answer-change="handleAnswerChange"
            />
            
            <!-- 导航按钮 -->
            <div class="question-nav-buttons">
              <el-button 
                @click="previousQuestion"
                :disabled="currentQuestionIndex === 0"
              >
                <el-icon><ArrowLeft /></el-icon>
                上一题
              </el-button>
              
              <el-button 
                type="primary"
                @click="nextQuestion"
                :disabled="currentQuestionIndex === questions.length - 1"
              >
                下一题
                <el-icon><ArrowRight /></el-icon>
              </el-button>
            </div>
          </div>
        </el-col>
        
        <!-- 右侧：进度和题号导航 -->
        <el-col :span="6">
          <div class="sidebar">
            <!-- 答题进度 -->
            <ExamProgress
              :answered-count="examStore.answeredCount"
              :total-count="examStore.totalQuestions"
              :questions="questions"
              :answered-question-ids="examStore.answers"
              :current-question-id="currentQuestion?.id"
              @navigate="navigateToQuestion"
            />
            
            <!-- 自动保存状态 -->
            <div class="auto-save-status">
              <el-icon v-if="examStore.autoSaveStatus === 'saved'" class="status-icon saved">
                <CircleCheck />
              </el-icon>
              <el-icon v-else-if="examStore.autoSaveStatus === 'saving'" class="status-icon saving">
                <Loading />
              </el-icon>
              <el-icon v-else class="status-icon error">
                <CircleClose />
              </el-icon>
              <span class="status-text">
                {{ autoSaveStatusText }}
              </span>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>
    
    <!-- 考试未开始或已结束 -->
    <el-empty v-else description="没有进行中的考试" />
    
    <!-- 考试专用 AI 助手（带题目上下文） -->
    <AIChat 
      ref="aiChatRef"
      v-if="examStore.isExamInProgress"
      :question-context="currentQuestionContext"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  ArrowLeft, 
  ArrowRight, 
  CircleCheck, 
  CircleClose, 
  Loading,
  ChatDotRound
} from '@element-plus/icons-vue'
import { useExamStore } from '../stores/exam'
import { getExamPaper } from '../api/exams'
import QuestionCard from '../components/QuestionCard.vue'
import ExamTimer from '../components/ExamTimer.vue'
import ExamProgress from '../components/ExamProgress.vue'
import AIChat from '../components/AIChat.vue'
import examVoice from '../utils/examVoice'

const route = useRoute()
const router = useRouter()
const examStore = useExamStore()

const loading = ref(false)
const submitting = ref(false)
const currentQuestionIndex = ref(0)
const timerRef = ref(null)
const aiChatRef = ref(null)
const isNewExam = ref(false) // 标记是否是新开始的考试

// 监听题目索引变化，自动保存进度
watch(currentQuestionIndex, async (newIndex) => {
  if (examStore.isExamInProgress && examStore.currentSession) {
    try {
      await examStore.saveProgressToServer(newIndex)
    } catch (error) {
      // 进度保存失败不影响用户操作
      console.warn('保存进度失败:', error)
    }
  }
})

// 当前试卷的题目列表
const questions = computed(() => {
  return examStore.currentPaper?.questions || []
})

// 当前题目
const currentQuestion = computed(() => {
  return questions.value[currentQuestionIndex.value]
})

// 考试类型标签
const examTypeLabel = computed(() => {
  const typeMap = {
    'civil_service': '公务员考试',
    'postgraduate': '研究生考试',
    'public_institution': '事业编考试'
  }
  return typeMap[examStore.currentPaper?.exam_type] || '考试'
})

// 自动保存状态文本
const autoSaveStatusText = computed(() => {
  const statusMap = {
    'saved': '已保存',
    'saving': '保存中...',
    'error': '保存失败'
  }
  return statusMap[examStore.autoSaveStatus] || ''
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
    paperName: examStore.currentPaper?.name,
    examType: examStore.currentPaper?.exam_type
  }
})

/**
 * 切换 AI 助手显示
 */
function toggleAIChat() {
  if (aiChatRef.value) {
    aiChatRef.value.toggleChat()
  }
}

/**
 * 初始化考试
 */
async function initExam() {
  const paperId = route.params.paperId
  const sessionId = route.query.sessionId
  
  if (!paperId) {
    ElMessage.error('缺少试卷ID')
    router.push('/dashboard')
    return
  }
  
  try {
    loading.value = true
    
    // 如果已经有进行中的考试会话，直接使用
    if (examStore.isExamInProgress && examStore.currentPaper?.id === parseInt(paperId)) {
      // 验证是否有题目
      if (!examStore.currentPaper.questions || examStore.currentPaper.questions.length === 0) {
        console.error('当前试卷没有题目')
        throw new Error('该试卷暂无题目，无法继续考试')
      }
      // 恢复到上次做到的题目
      currentQuestionIndex.value = examStore.currentQuestionIndex || 0
      return
    }
    
    // 获取试卷详情（包含题目）
    console.log('正在获取试卷详情，paperId:', paperId)
    const response = await getExamPaper(paperId, true)
    
    console.log('试卷API响应:', response)
    
    if (!response.success) {
      throw new Error(response.error?.message || '获取试卷失败')
    }
    
    const paperData = response.data
    console.log('试卷数据:', paperData)
    console.log('题目数量:', paperData.questions?.length)
    
    // 验证试卷是否有题目
    if (!paperData.questions || paperData.questions.length === 0) {
      console.error('试卷没有题目！')
      throw new Error('该试卷暂无题目，无法开始考试')
    }
    
    // 如果有 sessionId，说明是刚创建的会话，直接开始
    if (sessionId) {
      await examStore.beginExam(paperId, paperData, sessionId)
      isNewExam.value = true
      ElMessage.success('考试已开始')
      // 播放考试开始语音
      setTimeout(() => {
        if (timerRef.value) {
          timerRef.value.announceStart()
        }
      }, 500)
      return
    }
    
    // 尝试检查是否有进行中的会话（如果API失败也不影响）
    try {
      const { getCurrentSession } = await import('../api/exams')
      const sessionResponse = await getCurrentSession(paperId)
      
      if (sessionResponse.success && sessionResponse.data) {
        // 有进行中的会话，恢复它
        const existingSession = sessionResponse.data
        await examStore.resumeExam(existingSession, paperData)
        // 恢复到上次做到的题目
        currentQuestionIndex.value = existingSession.current_question_index || 0
        ElMessage.success('已恢复进行中的考试')
        return
      }
    } catch (sessionError) {
      // 获取会话失败，继续创建新会话
      console.warn('获取进行中会话失败，将创建新会话:', sessionError)
    }
    
    // 没有进行中的会话或获取失败，确认开始新考试
    await ElMessageBox.confirm(
      `确定开始考试《${paperData.name}》吗？考试时长 ${paperData.duration} 分钟。`,
      '开始考试',
      {
        confirmButtonText: '开始',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 开始考试
    await examStore.beginExam(paperId, paperData)
    isNewExam.value = true
    ElMessage.success('考试已开始')
    // 播放考试开始语音
    setTimeout(() => {
      if (timerRef.value) {
        timerRef.value.announceStart()
      }
    }, 500)
    
  } catch (error) {
    if (error !== 'cancel') {
      console.error('初始化考试失败:', error)
      ElMessage.error(error.message || '初始化考试失败')
      router.push('/exams')
    } else {
      router.push('/exams')
    }
  } finally {
    loading.value = false
  }
}

/**
 * 处理答案变化
 */
async function handleAnswerChange(answer) {
  if (!currentQuestion.value) return
  
  try {
    // 保存到服务器（自动保存），同时保存当前题目索引
    await examStore.saveAnswerToServer(currentQuestion.value.id, answer, currentQuestionIndex.value)
  } catch (error) {
    console.error('保存答案失败:', error)
    // 错误已在 store 中处理，这里只记录日志
  }
}

/**
 * 上一题
 */
function previousQuestion() {
  if (currentQuestionIndex.value > 0) {
    currentQuestionIndex.value--
  }
}

/**
 * 下一题
 */
function nextQuestion() {
  if (currentQuestionIndex.value < questions.value.length - 1) {
    currentQuestionIndex.value++
  }
}

/**
 * 导航到指定题目
 */
function navigateToQuestion(questionId) {
  const index = questions.value.findIndex(q => q.id === questionId)
  if (index !== -1) {
    currentQuestionIndex.value = index
  }
}

/**
 * 处理倒计时结束
 */
async function handleTimeout() {
  ElMessage.warning('考试时间已到，系统将自动提交试卷')
  await submitExam()
}

/**
 * 处理倒计时更新
 */
function handleTimerTick(remainingSeconds) {
  examStore.updateTimeRemaining(remainingSeconds)
}

/**
 * 处理语音提醒事件
 */
function handleVoiceReminder(type) {
  const messages = {
    '15min': '距离考试结束还有15分钟',
    '10min': '距离考试结束还有10分钟',
    '5min': '距离考试结束还有5分钟，请注意检查答题',
    '1min': '距离考试结束还有1分钟'
  }
  
  if (messages[type]) {
    ElMessage.warning({
      message: messages[type],
      duration: 5000,
      showClose: true
    })
  }
}

/**
 * 提交试卷
 */
async function handleSubmit() {
  try {
    // 检查是否有未答题目
    const unansweredCount = examStore.totalQuestions - examStore.answeredCount
    
    if (unansweredCount > 0) {
      await ElMessageBox.confirm(
        `还有 ${unansweredCount} 道题未作答，确定要提交试卷吗？`,
        '提交确认',
        {
          confirmButtonText: '确定提交',
          cancelButtonText: '继续答题',
          type: 'warning'
        }
      )
    } else {
      await ElMessageBox.confirm(
        '确定要提交试卷吗？提交后将无法修改答案。',
        '提交确认',
        {
          confirmButtonText: '确定提交',
          cancelButtonText: '再检查一下',
          type: 'warning'
        }
      )
    }
    
    await submitExam()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('提交失败:', error)
    }
  }
}

/**
 * 执行提交
 */
async function submitExam() {
  try {
    submitting.value = true
    
    const result = await examStore.finishExam()
    
    if (result.success) {
      ElMessage.success('试卷提交成功')
      // 跳转到结果页面
      router.push(`/exam/result/${result.result.id}`)
    }
  } catch (error) {
    console.error('提交试卷失败:', error)
    ElMessage.error(error.message || '提交试卷失败')
  } finally {
    submitting.value = false
  }
}

/**
 * 页面离开前确认
 */
function beforeUnloadHandler(e) {
  if (examStore.isExamInProgress) {
    e.preventDefault()
    e.returnValue = '考试正在进行中，确定要离开吗？'
    return e.returnValue
  }
}

onMounted(() => {
  initExam()
  // 添加页面离开前的警告
  window.addEventListener('beforeunload', beforeUnloadHandler)
})

onUnmounted(() => {
  window.removeEventListener('beforeunload', beforeUnloadHandler)
})
</script>

<style scoped>
.exam-container {
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 20px;
}

.exam-content {
  max-width: 1400px;
  margin: 0 auto;
}

.exam-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.exam-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.exam-body {
  margin-bottom: 20px;
}

.question-area {
  background-color: #fff;
  border-radius: 4px;
  padding: 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  min-height: 500px;
}

.question-nav-buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #ebeef5;
}

.sidebar {
  position: sticky;
  top: 20px;
}

.auto-save-status {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  padding: 12px;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.status-icon {
  font-size: 18px;
}

.status-icon.saved {
  color: #67c23a;
}

.status-icon.saving {
  color: #409eff;
  animation: rotate 1s linear infinite;
}

.status-icon.error {
  color: #f56c6c;
}

.status-text {
  font-size: 14px;
  color: #606266;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
