<template>
  <el-form 
    ref="formRef" 
    :model="formData" 
    :rules="rules" 
    label-width="100px"
    @submit.prevent="handleSubmit"
  >
    <el-form-item label="计划名称" prop="name">
      <el-input 
        v-model="formData.name" 
        placeholder="请输入计划名称"
        maxlength="100"
        show-word-limit
      />
    </el-form-item>

    <el-form-item label="考试类型" prop="exam_type">
      <el-select v-model="formData.exam_type" placeholder="请选择考试类型" style="width: 100%">
        <el-option label="公务员考试" value="civil_service" />
        <el-option label="考研" value="postgraduate" />
        <el-option label="事业编" value="public_institution" />
      </el-select>
    </el-form-item>

    <el-form-item label="开始日期" prop="start_date">
      <el-date-picker
        v-model="formData.start_date"
        type="date"
        placeholder="选择开始日期"
        style="width: 100%"
        :disabled-date="disabledStartDate"
      />
    </el-form-item>

    <el-form-item label="结束日期" prop="end_date">
      <el-date-picker
        v-model="formData.end_date"
        type="date"
        placeholder="选择结束日期"
        style="width: 100%"
        :disabled-date="disabledEndDate"
      />
    </el-form-item>

    <el-form-item label="计划描述" prop="description">
      <el-input
        v-model="formData.description"
        type="textarea"
        :rows="3"
        placeholder="请输入计划描述（选填）"
        maxlength="500"
        show-word-limit
      />
    </el-form-item>

    <el-divider content-position="left">学习目标</el-divider>

    <div v-for="(goal, index) in formData.goals" :key="index" class="goal-item">
      <el-card shadow="hover">
        <div class="goal-header">
          <span class="goal-title">目标 {{ index + 1 }}</span>
          <el-button 
            link 
            type="danger" 
            @click="removeGoal(index)"
            v-if="formData.goals.length > 1"
          >
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>

        <el-form-item 
          :prop="`goals.${index}.goal_type`" 
          :rules="rules.goal_type"
          label="目标类型"
        >
          <el-select 
            v-model="goal.goal_type" 
            placeholder="请选择目标类型" 
            style="width: 100%"
            @change="handleGoalTypeChange(index)"
          >
            <el-option-group label="练习数量">
              <el-option label="每日练习题数" value="daily_practice" />
              <el-option label="每周练习题数" value="weekly_practice" />
              <el-option label="每月练习题数" value="monthly_practice" />
              <el-option label="科目每日练习题数" value="subject_daily_practice" />
              <el-option label="科目每周练习题数" value="subject_weekly_practice" />
            </el-option-group>
            <el-option-group label="学习时长">
              <el-option label="每日学习时长（分钟）" value="daily_duration" />
              <el-option label="每周学习时长（分钟）" value="weekly_duration" />
              <el-option label="科目每日学习时长" value="subject_daily_duration" />
            </el-option-group>
            <el-option-group label="正确率">
              <el-option label="总体正确率（%）" value="accuracy_rate" />
              <el-option label="科目正确率（%）" value="subject_accuracy_rate" />
            </el-option-group>
            <el-option-group label="考试">
              <el-option label="考试次数" value="exam_count" />
              <el-option label="考试目标分数" value="exam_score" />
            </el-option-group>
            <el-option-group label="章节">
              <el-option label="章节完成数" value="chapter_completion" />
              <el-option label="科目章节完成数" value="subject_chapter_completion" />
            </el-option-group>
          </el-select>
        </el-form-item>

        <el-form-item 
          v-if="needsSubject(goal.goal_type)"
          :prop="`goals.${index}.subject`" 
          :rules="rules.subject"
          label="科目"
        >
          <el-select v-model="goal.subject" placeholder="请选择科目" style="width: 100%">
            <el-option label="行测" value="xingce" />
            <el-option label="申论" value="shenlun" />
            <el-option label="数学" value="math" />
            <el-option label="英语" value="english" />
            <el-option label="政治" value="politics" />
            <el-option label="专业课" value="major" />
          </el-select>
        </el-form-item>

        <el-form-item 
          :prop="`goals.${index}.target_value`" 
          :rules="rules.target_value"
          :label="getTargetValueLabel(goal.goal_type)"
        >
          <el-input-number 
            v-model="goal.target_value" 
            :min="getMinValue(goal.goal_type)" 
            :max="getMaxValue(goal.goal_type)"
            style="width: 100%"
          />
        </el-form-item>
      </el-card>
    </div>

    <el-button type="primary" plain @click="addGoal" style="width: 100%; margin-bottom: 20px">
      <el-icon><Plus /></el-icon>
      添加目标
    </el-button>

    <el-form-item>
      <el-button type="primary" @click="handleSubmit" :loading="loading">
        {{ isEdit ? '更新计划' : '创建计划' }}
      </el-button>
      <el-button @click="handleCancel">取消</el-button>
    </el-form-item>
  </el-form>
</template>

<script setup>
import { ref, reactive, watch } from 'vue'
import { Delete, Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  plan: {
    type: Object,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['submit', 'cancel'])

const formRef = ref(null)
const isEdit = ref(!!props.plan)

const formData = reactive({
  name: '',
  exam_type: '',
  start_date: '',
  end_date: '',
  description: '',
  goals: [
    {
      goal_type: 'daily_practice',
      target_value: 10
    }
  ]
})

// 初始化表单数据
if (props.plan) {
  Object.assign(formData, {
    name: props.plan.name,
    exam_type: props.plan.exam_type,
    start_date: props.plan.start_date,
    end_date: props.plan.end_date,
    description: props.plan.description || '',
    goals: props.plan.goals?.map(g => ({
      goal_type: g.goal_type,
      target_value: g.target_value
    })) || []
  })
}

const rules = {
  name: [
    { required: true, message: '请输入计划名称', trigger: 'blur' },
    { min: 2, max: 100, message: '长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  exam_type: [
    { required: true, message: '请选择考试类型', trigger: 'change' }
  ],
  start_date: [
    { required: true, message: '请选择开始日期', trigger: 'change' }
  ],
  end_date: [
    { required: true, message: '请选择结束日期', trigger: 'change' }
  ],
  goal_type: [
    { required: true, message: '请选择目标类型', trigger: 'change' }
  ],
  subject: [
    { required: true, message: '请选择科目', trigger: 'change' }
  ],
  target_value: [
    { required: true, message: '请输入目标值', trigger: 'blur' },
    { type: 'number', min: 1, message: '目标值必须大于0', trigger: 'blur' }
  ]
}

// 需要科目的目标类型
const subjectRequiredTypes = [
  'subject_daily_practice',
  'subject_weekly_practice',
  'subject_daily_duration',
  'subject_accuracy_rate',
  'subject_chapter_completion'
]

const needsSubject = (goalType) => {
  return subjectRequiredTypes.includes(goalType)
}

const getTargetValueLabel = (goalType) => {
  if (goalType?.includes('duration')) return '目标时长（分钟）'
  if (goalType?.includes('accuracy')) return '目标正确率（%）'
  if (goalType?.includes('score')) return '目标分数'
  if (goalType?.includes('chapter')) return '章节数'
  if (goalType?.includes('exam_count')) return '考试次数'
  return '目标值'
}

const getMinValue = (goalType) => {
  if (goalType?.includes('accuracy')) return 1
  if (goalType?.includes('score')) return 0
  return 1
}

const getMaxValue = (goalType) => {
  if (goalType?.includes('accuracy')) return 100
  if (goalType?.includes('score')) return 150
  if (goalType?.includes('duration')) return 1440
  if (goalType?.includes('practice')) return 1000
  return 10000
}

const handleGoalTypeChange = (index) => {
  const goal = formData.goals[index]
  // 如果切换到不需要科目的类型，清空科目
  if (!needsSubject(goal.goal_type)) {
    goal.subject = undefined
  }
  // 根据目标类型设置合理的默认值
  if (goal.goal_type?.includes('accuracy')) {
    goal.target_value = 80
  } else if (goal.goal_type?.includes('duration')) {
    goal.target_value = 60
  } else if (goal.goal_type?.includes('score')) {
    goal.target_value = 100
  } else {
    goal.target_value = 10
  }
}

const disabledStartDate = (time) => {
  return time.getTime() < Date.now() - 8.64e7 // 不能选择过去的日期
}

const disabledEndDate = (time) => {
  // 结束日期不能早于开始日期
  if (formData.start_date) {
    const startTime = new Date(formData.start_date).getTime()
    return time.getTime() < startTime
  }
  return time.getTime() < Date.now() - 8.64e7
}

const addGoal = () => {
  formData.goals.push({
    goal_type: 'daily_practice',
    target_value: 10
  })
}

const removeGoal = (index) => {
  formData.goals.splice(index, 1)
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    
    // 格式化日期
    const startDate = formData.start_date instanceof Date 
      ? formData.start_date.toISOString().split('T')[0]
      : formData.start_date
    
    const endDate = formData.end_date instanceof Date 
      ? formData.end_date.toISOString().split('T')[0]
      : formData.end_date
    
    // 为每个目标添加 period_start 和 period_end
    const goalsWithPeriod = formData.goals.map(goal => ({
      ...goal,
      period_start: startDate,
      period_end: endDate
    }))
    
    const submitData = {
      ...formData,
      start_date: startDate,
      end_date: endDate,
      goals: goalsWithPeriod
    }
    
    emit('submit', submitData)
  } catch (error) {
    ElMessage.warning('请检查表单填写是否正确')
  }
}

const handleCancel = () => {
  emit('cancel')
}
</script>

<style scoped>
.goal-item {
  margin-bottom: 20px;
}

.goal-item :deep(.el-card) {
  border-radius: 12px;
  border: 2px solid #e4e7ed;
  transition: all 0.3s ease;
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
}

.goal-item :deep(.el-card:hover) {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
  transform: translateY(-2px);
}

.goal-item :deep(.el-card__body) {
  padding: 24px;
}

.goal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 2px solid #f0f2f5;
}

.goal-title {
  font-weight: 600;
  font-size: 16px;
  color: #303133;
  display: flex;
  align-items: center;
}

.goal-title::before {
  content: '';
  display: inline-block;
  width: 4px;
  height: 18px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 2px;
  margin-right: 10px;
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: #606266;
}

:deep(.el-input__inner),
:deep(.el-textarea__inner),
:deep(.el-select .el-input__inner) {
  border-radius: 8px;
  border: 1.5px solid #dcdfe6;
  transition: all 0.3s ease;
}

:deep(.el-input__inner:focus),
:deep(.el-textarea__inner:focus),
:deep(.el-select .el-input__inner:focus) {
  border-color: #409eff;
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.1);
}

:deep(.el-date-editor) {
  width: 100%;
}

:deep(.el-date-editor .el-input__inner) {
  border-radius: 8px;
}

:deep(.el-divider) {
  margin: 32px 0 24px 0;
}

:deep(.el-divider__text) {
  font-weight: 600;
  font-size: 16px;
  color: #303133;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

:deep(.el-button) {
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.3s ease;
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

:deep(.el-button--primary:hover) {
  background: linear-gradient(135deg, #5568d3 0%, #6a3f8f 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

:deep(.el-button--primary.is-plain) {
  background: white;
  border: 2px solid #667eea;
  color: #667eea;
}

:deep(.el-button--primary.is-plain:hover) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border-color: #764ba2;
  color: #764ba2;
}

:deep(.el-input-number) {
  width: 100%;
}

:deep(.el-input-number .el-input__inner) {
  text-align: left;
  padding-left: 15px;
}

:deep(.el-select-dropdown__item) {
  border-radius: 6px;
  margin: 2px 8px;
  padding: 8px 12px;
}

:deep(.el-select-group__title) {
  font-weight: 600;
  color: #909399;
  font-size: 13px;
  padding: 8px 12px;
}
</style>
