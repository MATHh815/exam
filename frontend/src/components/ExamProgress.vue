<template>
  <div class="exam-progress">
    <div class="progress-header">
      <span class="progress-label">答题进度</span>
      <span class="progress-stats">{{ answeredCount }} / {{ totalCount }}</span>
    </div>
    
    <el-progress 
      :percentage="percentage" 
      :color="progressColor"
      :stroke-width="12"
    />
    
    <div v-if="showQuestionNav" class="question-nav">
      <div 
        v-for="(question, index) in questions" 
        :key="question.id"
        class="question-item"
        :class="{
          'answered': isAnswered(question.id),
          'current': currentQuestionId === question.id
        }"
        @click="$emit('navigate', question.id)"
      >
        {{ index + 1 }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  // 已答题数
  answeredCount: {
    type: Number,
    required: true
  },
  // 总题数
  totalCount: {
    type: Number,
    required: true
  },
  // 题目列表（用于显示题号导航）
  questions: {
    type: Array,
    default: () => []
  },
  // 已答题目ID集合
  answeredQuestionIds: {
    type: Object,
    default: () => ({})
  },
  // 当前题目ID
  currentQuestionId: {
    type: Number,
    default: null
  },
  // 是否显示题号导航
  showQuestionNav: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['navigate'])

// 计算进度百分比
const percentage = computed(() => {
  if (props.totalCount === 0) return 0
  return Math.round((props.answeredCount / props.totalCount) * 100)
})

// 进度条颜色
const progressColor = computed(() => {
  const percent = percentage.value
  if (percent < 30) return '#f56c6c'
  if (percent < 70) return '#e6a23c'
  return '#67c23a'
})

// 判断题目是否已答
function isAnswered(questionId) {
  return questionId in props.answeredQuestionIds
}
</script>

<style scoped>
.exam-progress {
  padding: 16px;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.progress-label {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.progress-stats {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.question-nav {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(40px, 1fr));
  gap: 8px;
  margin-top: 16px;
  max-height: 200px;
  overflow-y: auto;
}

.question-item {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  color: #606266;
  cursor: pointer;
  transition: all 0.3s;
  background-color: #fff;
}

.question-item:hover {
  border-color: #409eff;
  color: #409eff;
}

.question-item.answered {
  background-color: #67c23a;
  border-color: #67c23a;
  color: #fff;
}

.question-item.current {
  border-color: #409eff;
  border-width: 2px;
  font-weight: bold;
}

.question-item.answered.current {
  background-color: #67c23a;
  border-color: #409eff;
}

/* 滚动条样式 */
.question-nav::-webkit-scrollbar {
  width: 6px;
}

.question-nav::-webkit-scrollbar-thumb {
  background-color: #dcdfe6;
  border-radius: 3px;
}

.question-nav::-webkit-scrollbar-thumb:hover {
  background-color: #c0c4cc;
}
</style>
