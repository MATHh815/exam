<template>
  <div class="exam-result-container">
    <!-- 加载状态 -->
    <el-skeleton v-if="loading" :rows="10" animated />
    
    <!-- 结果展示 -->
    <div v-else-if="result" class="result-content">
      <!-- 成绩卡片 -->
      <el-card class="score-card" shadow="hover">
        <div class="score-header">
          <el-icon class="result-icon" :class="passClass">
            <component :is="passIcon" />
          </el-icon>
          <h2 class="result-title">{{ passText }}</h2>
        </div>
        
        <div class="score-body">
          <div class="score-main">
            <div class="score-value">{{ result.score }}</div>
            <div class="score-label">得分</div>
          </div>
          
          <el-divider direction="vertical" />
          
          <div class="score-stats">
            <div class="stat-item">
              <span class="stat-label">总分</span>
              <span class="stat-value">{{ result.total_score }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">正确率</span>
              <span class="stat-value">{{ (result.accuracy * 100).toFixed(1) }}%</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">正确题数</span>
              <span class="stat-value">{{ result.correct_count }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">错误题数</span>
              <span class="stat-value">{{ result.wrong_count }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">用时</span>
              <span class="stat-value">{{ formatTime(result.time_spent) }}</span>
            </div>
          </div>
        </div>
      </el-card>
      
      <!-- 试卷信息 -->
      <el-card class="paper-info-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>试卷信息</span>
          </div>
        </template>
        
        <el-descriptions :column="2" border>
          <el-descriptions-item label="试卷名称">
            {{ paperInfo?.name }}
          </el-descriptions-item>
          <el-descriptions-item label="考试类型">
            {{ examTypeLabel }}
          </el-descriptions-item>
          <el-descriptions-item label="考试时长">
            {{ paperInfo?.duration }} 分钟
          </el-descriptions-item>
          <el-descriptions-item label="及格分数">
            {{ paperInfo?.pass_score }}
          </el-descriptions-item>
          <el-descriptions-item label="考试时间" :span="2">
            {{ formatDateTime(result.created_at) }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>
      
      <!-- 详细解析 -->
      <el-card class="details-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>答题详情</span>
            <el-radio-group v-model="filterType" size="small">
              <el-radio-button label="all">全部</el-radio-button>
              <el-radio-button label="correct">正确</el-radio-button>
              <el-radio-button label="wrong">错误</el-radio-button>
            </el-radio-group>
          </div>
        </template>
        
        <div class="question-list">
          <div 
            v-for="(detail, index) in filteredDetails" 
            :key="detail.question_id"
            class="question-detail-item"
          >
            <div class="question-header">
              <div class="question-number">
                <el-tag :type="detail.is_correct ? 'success' : 'danger'" size="large">
                  第 {{ index + 1 }} 题
                </el-tag>
                <el-tag v-if="detail.is_correct" type="success" effect="plain">
                  <el-icon><CircleCheck /></el-icon>
                  正确
                </el-tag>
                <el-tag v-else type="danger" effect="plain">
                  <el-icon><CircleClose /></el-icon>
                  错误
                </el-tag>
                <span class="question-score">{{ detail.score }} 分</span>
              </div>
            </div>
            
            <!-- 题目内容 -->
            <QuestionCard
              v-if="detail.question"
              :question="detail.question"
              :show-correct-answer="true"
              :show-explanation="true"
              :show-result="true"
              :user-answer="detail.user_answer"
              :disabled="true"
            />
          </div>
        </div>
      </el-card>
      
      <!-- 操作按钮 -->
      <div class="action-buttons">
        <el-button @click="goBack">返回</el-button>
        <el-button @click="goHome">
          <el-icon><HomeFilled /></el-icon>
          返回首页
        </el-button>
        <el-button type="primary" @click="viewHistory">查看考试历史</el-button>
        <el-button type="success" @click="retakeExam">再考一次</el-button>
      </div>
    </div>
    
    <!-- 未找到结果 -->
    <el-empty v-else description="未找到考试结果" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  CircleCheck, 
  CircleClose, 
  SuccessFilled, 
  WarningFilled,
  HomeFilled
} from '@element-plus/icons-vue'
import { getExamResult, getExamPaper } from '../api/exams'
import QuestionCard from '../components/QuestionCard.vue'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const result = ref(null)
const paperInfo = ref(null)
const filterType = ref('all')

// 是否及格
const isPassed = computed(() => {
  if (!result.value || !paperInfo.value) return false
  return result.value.score >= paperInfo.value.pass_score
})

// 及格状态样式类
const passClass = computed(() => {
  return isPassed.value ? 'pass' : 'fail'
})

// 及格状态图标
const passIcon = computed(() => {
  return isPassed.value ? SuccessFilled : WarningFilled
})

// 及格状态文本
const passText = computed(() => {
  return isPassed.value ? '恭喜通过！' : '未通过'
})

// 考试类型标签
const examTypeLabel = computed(() => {
  const typeMap = {
    'civil_service': '公务员考试',
    'postgraduate': '研究生考试',
    'public_institution': '事业编考试'
  }
  return typeMap[paperInfo.value?.exam_type] || '考试'
})

// 过滤后的详情列表
const filteredDetails = computed(() => {
  if (!result.value?.details) return []
  
  const details = result.value.details
  
  if (filterType.value === 'correct') {
    return details.filter(d => d.is_correct)
  } else if (filterType.value === 'wrong') {
    return details.filter(d => !d.is_correct)
  }
  
  return details
})

/**
 * 格式化时间（秒转为分秒）
 */
function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${minutes} 分 ${secs} 秒`
}

/**
 * 格式化日期时间
 */
function formatDateTime(dateString) {
  if (!dateString) return ''
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
 * 加载考试结果
 */
async function loadResult() {
  const resultId = route.params.resultId
  
  if (!resultId) {
    ElMessage.error('缺少结果ID')
    router.push('/dashboard')
    return
  }
  
  try {
    loading.value = true
    
    // 获取考试结果
    const response = await getExamResult(resultId, true)
    
    if (response.success) {
      result.value = response.data
      
      // 获取试卷信息
      const paperResponse = await getExamPaper(response.data.paper_id, false)
      if (paperResponse.success) {
        paperInfo.value = paperResponse.data
      }
    } else {
      throw new Error(response.error?.message || '获取考试结果失败')
    }
  } catch (error) {
    console.error('加载结果失败:', error)
    ElMessage.error(error.message || '加载结果失败')
    router.push('/dashboard')
  } finally {
    loading.value = false
  }
}

/**
 * 返回
 */
function goBack() {
  router.back()
}

/**
 * 返回首页
 */
function goHome() {
  router.push('/dashboard')
}

/**
 * 查看考试历史
 */
function viewHistory() {
  router.push('/exam-history')
}

/**
 * 再考一次
 */
function retakeExam() {
  if (paperInfo.value) {
    router.push(`/exam/${paperInfo.value.id}`)
  }
}

onMounted(() => {
  loadResult()
})
</script>

<style scoped>
.exam-result-container {
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 20px;
}

.result-content {
  max-width: 1200px;
  margin: 0 auto;
}

.score-card {
  margin-bottom: 20px;
}

.score-header {
  text-align: center;
  padding: 20px 0;
}

.result-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.result-icon.pass {
  color: #67c23a;
}

.result-icon.fail {
  color: #e6a23c;
}

.result-title {
  margin: 0;
  font-size: 28px;
  font-weight: 600;
  color: #303133;
}

.score-body {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 40px;
  padding: 20px 0;
}

.score-main {
  text-align: center;
}

.score-value {
  font-size: 72px;
  font-weight: bold;
  color: #409eff;
  line-height: 1;
  margin-bottom: 8px;
}

.score-label {
  font-size: 16px;
  color: #909399;
}

.score-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.paper-info-card,
.details-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.question-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.question-detail-item {
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.question-header {
  margin-bottom: 16px;
}

.question-number {
  display: flex;
  align-items: center;
  gap: 12px;
}

.question-score {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding: 20px 0;
}

:deep(.el-divider--vertical) {
  height: auto;
  margin: 0;
}
</style>
