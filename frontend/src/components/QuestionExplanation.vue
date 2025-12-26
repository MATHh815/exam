<template>
  <div class="question-explanation">
    <el-divider content-position="left">
      <el-icon><Document /></el-icon>
      <span class="divider-text">题目解析</span>
    </el-divider>
    
    <div class="explanation-content">
      <!-- 正确答案 -->
      <div class="correct-answer-section">
        <div class="section-title">
          <el-icon class="title-icon"><CircleCheck /></el-icon>
          <span>正确答案</span>
        </div>
        <div class="correct-answer-content">
          {{ formatCorrectAnswer }}
        </div>
      </div>

      <!-- 详细解析 -->
      <div v-if="explanation" class="explanation-section">
        <div class="section-title">
          <el-icon class="title-icon"><Reading /></el-icon>
          <span>详细解析</span>
        </div>
        <div class="explanation-text" v-html="formatExplanation"></div>
      </div>

      <!-- 知识点提示 -->
      <div v-if="hasKnowledgePoints" class="knowledge-points-section">
        <div class="section-title">
          <el-icon class="title-icon"><Notebook /></el-icon>
          <span>相关知识点</span>
        </div>
        <div class="knowledge-points">
          <el-tag
            v-for="(point, index) in knowledgePoints"
            :key="index"
            type="info"
            effect="plain"
            size="small"
          >
            {{ point }}
          </el-tag>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Document, CircleCheck, Reading, Notebook } from '@element-plus/icons-vue'

const props = defineProps({
  // 题目解析内容
  explanation: {
    type: String,
    required: true
  },
  // 正确答案
  correctAnswer: {
    type: [String, Array],
    required: true
  },
  // 题目类型
  questionType: {
    type: String,
    default: 'single_choice'
  },
  // 知识点（可选）
  knowledgePoints: {
    type: Array,
    default: () => []
  }
})

// 格式化正确答案显示
const formatCorrectAnswer = computed(() => {
  if (Array.isArray(props.correctAnswer)) {
    // 多选题答案
    return props.correctAnswer.join('、')
  }
  
  // 判断题特殊处理
  if (props.questionType === 'true_false') {
    return props.correctAnswer === 'true' || props.correctAnswer === true ? '正确' : '错误'
  }
  
  return props.correctAnswer
})

// 格式化解析内容（支持简单的HTML和换行）
const formatExplanation = computed(() => {
  if (!props.explanation) return ''
  
  let formatted = props.explanation
  
  // 处理换行
  formatted = formatted.replace(/\n/g, '<br>')
  
  // 处理加粗（**文本**）
  formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
  
  // 处理斜体（*文本*）
  formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>')
  
  // 处理代码块（`代码`）
  formatted = formatted.replace(/`(.*?)`/g, '<code>$1</code>')
  
  return formatted
})

// 是否有知识点
const hasKnowledgePoints = computed(() => {
  return props.knowledgePoints && props.knowledgePoints.length > 0
})
</script>

<style scoped>
.question-explanation {
  margin-top: 30px;
  padding: 20px;
  background: #f8f9fa;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
}

:deep(.el-divider__text) {
  background: #f8f9fa;
  color: #303133;
}

.divider-text {
  margin-left: 8px;
  font-weight: bold;
  color: #303133;
}

.explanation-content {
  padding: 10px 0;
}

.correct-answer-section,
.explanation-section,
.knowledge-points-section {
  margin-bottom: 20px;
}

.correct-answer-section:last-child,
.explanation-section:last-child,
.knowledge-points-section:last-child {
  margin-bottom: 0;
}

.section-title {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  font-weight: bold;
  color: #303133;
  font-size: 15px;
}

.title-icon {
  margin-right: 8px;
  color: #409eff;
}

.correct-answer-content {
  padding: 14px 18px;
  background: #f0f9eb;
  border-left: 4px solid #67c23a;
  border-radius: 4px;
  color: #67c23a;
  font-weight: bold;
  font-size: 16px;
}

.explanation-text {
  padding: 14px 18px;
  background: #fff;
  border-left: 4px solid #409eff;
  border-radius: 4px;
  line-height: 1.9;
  color: #303133;
  font-size: 16px;
}

.explanation-text :deep(strong) {
  color: #303133;
  font-weight: bold;
}

.explanation-text :deep(em) {
  font-style: italic;
  color: #606266;
}

.explanation-text :deep(code) {
  padding: 2px 6px;
  background: #f5f7fa;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  color: #e6a23c;
}

.knowledge-points {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  padding: 8px 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .question-explanation {
    padding: 15px;
  }
  
  .correct-answer-content,
  .explanation-text {
    padding: 10px 12px;
    font-size: 14px;
  }
}
</style>
