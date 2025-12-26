<template>
  <el-card class="question-card" :class="{ 'answered': answered }">
    <!-- 题目头部信息 -->
    <template #header>
      <div class="question-header">
        <div class="question-meta">
          <el-tag :type="getQuestionTypeColor(question.question_type)" size="small">
            {{ getQuestionTypeLabel(question.question_type) }}
          </el-tag>
          <el-tag type="info" size="small" v-if="question.subject">
            {{ question.subject }}
          </el-tag>
          <el-tag v-if="question.difficulty" size="small" :type="getDifficultyColor(question.difficulty)">
            难度: {{ '★'.repeat(question.difficulty) }}
          </el-tag>
          <span v-if="showOrder" class="question-order">第 {{ order }} 题</span>
        </div>
        <div v-if="showScore && score" class="question-score">
          {{ score }} 分
        </div>
      </div>
    </template>

    <!-- 题目内容 -->
    <div class="question-content">
      <div class="question-text" v-html="formatContent(question.content)"></div>
      
      <!-- 答案选项组件 -->
      <AnswerOptions
        v-if="isChoiceQuestion"
        :options="question.options"
        :question-type="question.question_type"
        :selected-answer="selectedAnswer"
        :correct-answer="showCorrectAnswer ? question.correct_answer : null"
        :disabled="disabled"
        @select="handleAnswerSelect"
      />

      <!-- 填空题/简答题输入框 -->
      <div v-else-if="question.question_type === 'fill_blank' || question.question_type === 'essay'" class="answer-input">
        <el-input
          v-model="inputAnswer"
          :type="question.question_type === 'essay' ? 'textarea' : 'text'"
          :rows="question.question_type === 'essay' ? 6 : 1"
          :placeholder="question.question_type === 'essay' ? '请输入答案...' : '请填写答案'"
          :disabled="disabled"
          @change="handleInputChange"
        />
      </div>

      <!-- 答题结果反馈 -->
      <div v-if="showResult" class="answer-result">
        <el-alert
          :type="isCorrect ? 'success' : 'error'"
          :title="isCorrect ? '回答正确！' : '回答错误'"
          :closable="false"
          show-icon
        />
      </div>

      <!-- 题目解析 -->
      <QuestionExplanation
        v-if="showExplanation && question.explanation"
        :explanation="question.explanation"
        :correct-answer="question.correct_answer"
        :question-type="question.question_type"
      />

      <!-- 题目标签 -->
      <div v-if="question.tags && question.tags.length > 0" class="question-tags">
        <el-tag
          v-for="tag in question.tags"
          :key="tag"
          size="small"
          effect="plain"
        >
          {{ tag }}
        </el-tag>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import AnswerOptions from './AnswerOptions.vue'
import QuestionExplanation from './QuestionExplanation.vue'

const props = defineProps({
  // 题目数据
  question: {
    type: Object,
    required: true
  },
  // 题目序号
  order: {
    type: Number,
    default: null
  },
  // 是否显示序号
  showOrder: {
    type: Boolean,
    default: false
  },
  // 题目分值
  score: {
    type: Number,
    default: null
  },
  // 是否显示分值
  showScore: {
    type: Boolean,
    default: false
  },
  // 用户答案（外部传入）
  userAnswer: {
    type: [String, Array],
    default: null
  },
  // 是否显示正确答案
  showCorrectAnswer: {
    type: Boolean,
    default: false
  },
  // 是否显示解析
  showExplanation: {
    type: Boolean,
    default: false
  },
  // 是否显示答题结果
  showResult: {
    type: Boolean,
    default: false
  },
  // 是否禁用答题
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['answer-change'])

// 选择题答案 - 多选题需要数组
const selectedAnswer = ref(
  props.question.question_type === 'multiple_choice'
    ? (Array.isArray(props.userAnswer) ? props.userAnswer : (props.userAnswer ? [props.userAnswer] : []))
    : (props.userAnswer || null)
)
// 填空题/简答题答案
const inputAnswer = ref(props.userAnswer || '')

// 是否已答题
const answered = computed(() => {
  if (isChoiceQuestion.value) {
    return selectedAnswer.value !== null && selectedAnswer.value !== ''
  }
  return inputAnswer.value !== ''
})

// 是否为选择题
const isChoiceQuestion = computed(() => {
  return ['single_choice', 'multiple_choice', 'true_false'].includes(props.question.question_type)
})

// 答案是否正确
const isCorrect = computed(() => {
  if (!answered.value || !props.showResult) return false
  
  const userAns = isChoiceQuestion.value ? selectedAnswer.value : inputAnswer.value
  const correctAns = props.question.correct_answer
  
  if (props.question.question_type === 'multiple_choice') {
    // 多选题需要完全匹配
    if (Array.isArray(userAns) && Array.isArray(correctAns)) {
      return JSON.stringify(userAns.sort()) === JSON.stringify(correctAns.sort())
    }
    return false
  }
  
  return String(userAns).trim().toLowerCase() === String(correctAns).trim().toLowerCase()
})

// 监听外部传入的答案变化
watch(() => props.userAnswer, (newVal) => {
  if (isChoiceQuestion.value) {
    // 多选题需要数组
    if (props.question.question_type === 'multiple_choice') {
      selectedAnswer.value = Array.isArray(newVal) ? newVal : (newVal ? [newVal] : [])
    } else {
      selectedAnswer.value = newVal || null
    }
  } else {
    inputAnswer.value = newVal || ''
  }
})

// 处理选择题答案选择
const handleAnswerSelect = (answer) => {
  selectedAnswer.value = answer
  emit('answer-change', answer)
}

// 处理输入题答案变化
const handleInputChange = () => {
  emit('answer-change', inputAnswer.value)
}

// 格式化题目内容（支持简单的HTML）
const formatContent = (content) => {
  if (!content) return ''
  // 简单的换行处理
  return content.replace(/\n/g, '<br>')
}

// 获取题目类型标签
const getQuestionTypeLabel = (type) => {
  const labels = {
    'single_choice': '单选题',
    'multiple_choice': '多选题',
    'true_false': '判断题',
    'fill_blank': '填空题',
    'essay': '简答题'
  }
  return labels[type] || type
}

// 获取题目类型颜色
const getQuestionTypeColor = (type) => {
  const colors = {
    'single_choice': 'primary',
    'multiple_choice': 'success',
    'true_false': 'warning',
    'fill_blank': 'info',
    'essay': 'danger'
  }
  return colors[type] || ''
}

// 获取难度颜色
const getDifficultyColor = (difficulty) => {
  if (difficulty <= 2) return 'success'
  if (difficulty <= 3) return 'warning'
  return 'danger'
}
</script>

<style scoped>
.question-card {
  margin-bottom: 20px;
  background: #ffffff !important;
  border: 1px solid #e4e7ed !important;
  border-radius: 12px !important;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.question-card.answered {
  border-color: #409eff !important;
  box-shadow: 0 2px 12px rgba(64, 158, 255, 0.15);
}

.question-card :deep(.el-card__header) {
  background: #f8f9fa;
  border-bottom: 1px solid #e4e7ed;
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.question-meta {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}

.question-order {
  font-weight: bold;
  color: #303133;
  margin-left: 8px;
}

.question-score {
  font-weight: bold;
  color: #e6a23c;
  font-size: 16px;
}

.question-content {
  padding: 10px 0;
}

.question-text {
  font-size: 18px;
  line-height: 1.9;
  color: #303133;
  margin-bottom: 24px;
  white-space: pre-wrap;
  font-weight: 500;
}

.answer-input {
  margin: 20px 0;
}

.answer-input :deep(.el-input__wrapper),
.answer-input :deep(.el-textarea__inner) {
  background: #fff;
  border: 1px solid #dcdfe6;
  color: #303133;
}

.answer-input :deep(.el-input__inner),
.answer-input :deep(.el-textarea__inner) {
  color: #303133;
}

.answer-input :deep(.el-input__inner::placeholder),
.answer-input :deep(.el-textarea__inner::placeholder) {
  color: #909399;
}

.answer-result {
  margin: 20px 0;
}

.question-tags {
  margin-top: 20px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
</style>
