<template>
  <div class="answer-options">
    <!-- 单选题 -->
    <el-radio-group
      v-if="questionType === 'single_choice'"
      :model-value="selectedAnswer"
      @change="handleSelect"
      :disabled="disabled"
      class="option-group"
    >
      <el-radio
        v-for="(option, index) in formattedOptions"
        :key="index"
        :label="option.value"
        :class="getOptionClass(option.value)"
        class="option-item"
      >
        <span class="option-label">{{ option.label }}</span>
        <span class="option-text">{{ option.text }}</span>
        <el-icon v-if="showCorrectIcon(option.value)" class="correct-icon">
          <Check />
        </el-icon>
        <el-icon v-if="showWrongIcon(option.value)" class="wrong-icon">
          <Close />
        </el-icon>
      </el-radio>
    </el-radio-group>

    <!-- 多选题 -->
    <el-checkbox-group
      v-else-if="questionType === 'multiple_choice'"
      :model-value="multipleChoiceValue"
      @change="handleSelect"
      :disabled="disabled"
      class="option-group"
    >
      <el-checkbox
        v-for="(option, index) in formattedOptions"
        :key="index"
        :label="option.value"
        :class="getOptionClass(option.value)"
        class="option-item"
      >
        <span class="option-label">{{ option.label }}</span>
        <span class="option-text">{{ option.text }}</span>
        <el-icon v-if="showCorrectIcon(option.value)" class="correct-icon">
          <Check />
        </el-icon>
        <el-icon v-if="showWrongIcon(option.value)" class="wrong-icon">
          <Close />
        </el-icon>
      </el-checkbox>
    </el-checkbox-group>

    <!-- 判断题 -->
    <el-radio-group
      v-else-if="questionType === 'true_false'"
      :model-value="selectedAnswer"
      @change="handleSelect"
      :disabled="disabled"
      class="option-group true-false-group"
    >
      <el-radio
        label="true"
        :class="getOptionClass('true')"
        class="option-item"
      >
        <span class="option-text">正确</span>
        <el-icon v-if="showCorrectIcon('true')" class="correct-icon">
          <Check />
        </el-icon>
        <el-icon v-if="showWrongIcon('true')" class="wrong-icon">
          <Close />
        </el-icon>
      </el-radio>
      <el-radio
        label="false"
        :class="getOptionClass('false')"
        class="option-item"
      >
        <span class="option-text">错误</span>
        <el-icon v-if="showCorrectIcon('false')" class="correct-icon">
          <Check />
        </el-icon>
        <el-icon v-if="showWrongIcon('false')" class="wrong-icon">
          <Close />
        </el-icon>
      </el-radio>
    </el-radio-group>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { Check, Close } from '@element-plus/icons-vue'

const props = defineProps({
  // 选项数据
  options: {
    type: [Array, Object],
    default: () => []
  },
  // 题目类型
  questionType: {
    type: String,
    required: true,
    validator: (value) => ['single_choice', 'multiple_choice', 'true_false'].includes(value)
  },
  // 已选答案
  selectedAnswer: {
    type: [String, Array],
    default: null
  },
  // 正确答案（用于显示对错）
  correctAnswer: {
    type: [String, Array],
    default: null
  },
  // 是否禁用
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['select'])

// 多选题的值（确保是数组）
const multipleChoiceValue = computed(() => {
  if (Array.isArray(props.selectedAnswer)) {
    return props.selectedAnswer
  }
  if (props.selectedAnswer) {
    return [props.selectedAnswer]
  }
  return []
})

// 格式化选项数据
const formattedOptions = computed(() => {
  if (!props.options) return []
  
  let optionsList = props.options
  
  // 如果是数组格式
  if (Array.isArray(optionsList)) {
    // 处理选项被合并成一个字符串的情况 ['A. 选项1\nB. 选项2']
    if (optionsList.length === 1 && typeof optionsList[0] === 'string' && optionsList[0].includes('\n')) {
      optionsList = optionsList[0].split('\n').filter(s => s.trim())
    }
    
    return optionsList.map((text, index) => {
      // 检查选项是否已经包含 "A. " 这样的前缀
      const match = String(text).match(/^([A-Z])\.\s*(.*)$/i)
      if (match) {
        return {
          label: match[1].toUpperCase(),
          value: match[1].toUpperCase(),
          text: match[2]
        }
      }
      // 没有前缀，自动添加
      return {
        label: String.fromCharCode(65 + index), // A, B, C, D...
        value: String.fromCharCode(65 + index),
        text: text
      }
    })
  }
  
  // 如果是对象格式 { "A": "选项A", "B": "选项B" }
  if (typeof optionsList === 'object') {
    return Object.entries(optionsList).map(([key, value]) => ({
      label: key,
      value: key,
      text: value
    }))
  }
  
  return []
})

// 处理选项选择
const handleSelect = (value) => {
  if (!props.disabled) {
    emit('select', value)
  }
}

// 获取选项样式类
const getOptionClass = (value) => {
  const classes = []
  
  // 如果显示正确答案
  if (props.correctAnswer !== null) {
    const isCorrect = isCorrectOption(value)
    const isSelected = isSelectedOption(value)
    
    if (isCorrect) {
      classes.push('option-correct')
    }
    
    if (isSelected && !isCorrect) {
      classes.push('option-wrong')
    }
  }
  
  return classes
}

// 判断是否为正确选项
const isCorrectOption = (value) => {
  if (props.correctAnswer === null) return false
  
  if (Array.isArray(props.correctAnswer)) {
    return props.correctAnswer.includes(value)
  }
  
  return String(props.correctAnswer) === String(value)
}

// 判断是否为已选选项
const isSelectedOption = (value) => {
  if (props.selectedAnswer === null) return false
  
  if (Array.isArray(props.selectedAnswer)) {
    return props.selectedAnswer.includes(value)
  }
  
  return String(props.selectedAnswer) === String(value)
}

// 是否显示正确图标
const showCorrectIcon = (value) => {
  return props.correctAnswer !== null && isCorrectOption(value)
}

// 是否显示错误图标
const showWrongIcon = (value) => {
  return props.correctAnswer !== null && isSelectedOption(value) && !isCorrectOption(value)
}
</script>

<style scoped>
.answer-options {
  margin: 20px 0;
}

.option-group {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.true-false-group {
  flex-direction: row;
  gap: 20px;
}

.option-item {
  width: 100%;
  padding: 16px 18px;
  background: #f8f9fa;
  border: 1px solid #e4e7ed;
  border-radius: 10px;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  position: relative;
}

.option-item:hover:not(.is-disabled) {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.option-item.is-checked {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.option-item.option-correct {
  border-color: #67c23a;
  background-color: #f0f9eb;
}

.option-item.option-wrong {
  border-color: #f56c6c;
  background-color: #fef0f0;
}

.option-label {
  font-weight: 700;
  margin-right: 12px;
  min-width: 28px;
  color: #409eff;
  font-size: 16px;
}

.option-text {
  flex: 1;
  color: #303133;
  line-height: 1.7;
  font-size: 16px;
  font-weight: 500;
}

.correct-icon {
  color: #67c23a;
  font-size: 20px;
  margin-left: 10px;
}

.wrong-icon {
  color: #f56c6c;
  font-size: 20px;
  margin-left: 10px;
}

/* 判断题特殊样式 */
.true-false-group .option-item {
  width: auto;
  min-width: 120px;
  justify-content: center;
}

/* Radio/Checkbox 样式覆盖 */
:deep(.el-radio__label),
:deep(.el-checkbox__label) {
  display: flex;
  align-items: center;
  width: 100%;
  color: #303133;
  font-size: 16px;
}

:deep(.el-radio__inner),
:deep(.el-checkbox__inner) {
  background: #fff;
  border-color: #dcdfe6;
}

:deep(.el-radio__input.is-checked .el-radio__inner),
:deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  background: #409eff;
  border-color: #409eff;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .option-item {
    padding: 12px;
  }
  
  .option-label {
    min-width: 20px;
    margin-right: 8px;
  }
  
  .true-false-group {
    flex-direction: column;
  }
  
  .true-false-group .option-item {
    width: 100%;
  }
}
</style>
