<template>
  <el-dialog
    :model-value="modelValue"
    :title="isEdit ? '编辑日程' : '创建日程'"
    width="600px"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
    >
      <el-form-item label="标题" prop="title">
        <el-input
          v-model="form.title"
          placeholder="例如：背英语单词"
          maxlength="200"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="活动类型" prop="activity_type">
        <el-select v-model="form.activity_type" placeholder="请选择活动类型" style="width: 100%">
          <el-option
            v-for="(label, value) in activityTypes"
            :key="value"
            :label="label"
            :value="value"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="科目" prop="subject">
        <el-select
          v-model="form.subject"
          placeholder="请选择科目（可选）"
          clearable
          style="width: 100%"
        >
          <el-option-group label="公共课">
            <el-option label="政治" value="politics" />
            <el-option label="英语" value="english" />
            <el-option label="数学" value="math" />
          </el-option-group>
          <el-option-group label="计算机专业课">
            <el-option label="数据结构" value="data_structure" />
            <el-option label="计算机组成原理" value="computer_organization" />
            <el-option label="操作系统" value="operating_system" />
            <el-option label="计算机网络" value="computer_network" />
          </el-option-group>
          <el-option-group label="其他专业课">
            <el-option label="经济学" value="economics" />
            <el-option label="管理学" value="management" />
            <el-option label="法学" value="law" />
            <el-option label="专业课一" value="major_course_1" />
            <el-option label="专业课二" value="major_course_2" />
          </el-option-group>
        </el-select>
      </el-form-item>

      <el-form-item label="日期" prop="schedule_date">
        <el-date-picker
          v-model="form.schedule_date"
          type="date"
          placeholder="选择日期"
          style="width: 100%"
          :disabled-date="disabledDate"
        />
      </el-form-item>

      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="开始时间" prop="start_time">
            <el-time-select
              v-model="form.start_time"
              start="00:00"
              step="00:15"
              end="23:45"
              placeholder="开始时间"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="结束时间" prop="end_time">
            <el-time-select
              v-model="form.end_time"
              start="00:00"
              step="00:15"
              end="23:45"
              placeholder="结束时间"
              :min-time="form.start_time"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="重复设置" prop="repeat_type">
        <el-radio-group v-model="form.repeat_type">
          <el-radio label="once">单次</el-radio>
          <el-radio label="daily">每天</el-radio>
          <el-radio label="weekly">每周</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item
        v-if="form.repeat_type === 'weekly'"
        label="重复日期"
        prop="repeat_days"
      >
        <el-checkbox-group v-model="repeatDaysArray">
          <el-checkbox label="1">周一</el-checkbox>
          <el-checkbox label="2">周二</el-checkbox>
          <el-checkbox label="3">周三</el-checkbox>
          <el-checkbox label="4">周四</el-checkbox>
          <el-checkbox label="5">周五</el-checkbox>
          <el-checkbox label="6">周六</el-checkbox>
          <el-checkbox label="7">周日</el-checkbox>
        </el-checkbox-group>
      </el-form-item>

      <el-form-item
        v-if="form.repeat_type !== 'once'"
        label="重复截止"
        prop="repeat_until"
      >
        <el-date-picker
          v-model="form.repeat_until"
          type="date"
          placeholder="选择截止日期"
          style="width: 100%"
          :disabled-date="disabledRepeatUntilDate"
        />
      </el-form-item>

      <el-form-item label="地点">
        <el-input
          v-model="form.location"
          placeholder="例如：图书馆、自习室"
          maxlength="200"
        />
      </el-form-item>

      <el-form-item label="描述">
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="3"
          placeholder="详细描述学习内容"
          maxlength="500"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="提醒">
        <el-row :gutter="10">
          <el-col :span="12">
            <el-switch v-model="form.is_reminder_enabled" />
          </el-col>
          <el-col :span="12">
            <el-select
              v-model="form.reminder_minutes"
              :disabled="!form.is_reminder_enabled"
              style="width: 100%"
            >
              <el-option label="提前5分钟" :value="5" />
              <el-option label="提前10分钟" :value="10" />
              <el-option label="提前15分钟" :value="15" />
              <el-option label="提前30分钟" :value="30" />
              <el-option label="提前1小时" :value="60" />
            </el-select>
          </el-col>
        </el-row>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="handleClose">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        {{ isEdit ? '保存' : '创建' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { createSchedule, updateSchedule } from '@/api/studySchedules'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  schedule: {
    type: Object,
    default: null
  },
  activityTypes: {
    type: Object,
    default: () => ({})
  },
  subjects: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue', 'success'])

// 状态
const formRef = ref(null)
const loading = ref(false)
const repeatDaysArray = ref([])

const defaultForm = {
  title: '',
  activity_type: '',
  subject: '',
  schedule_date: '',
  start_time: '',
  end_time: '',
  repeat_type: 'once',
  repeat_days: '',
  repeat_until: '',
  description: '',
  location: '',
  reminder_minutes: 15,
  is_reminder_enabled: true
}

const form = ref({ ...defaultForm })

// 计算属性
const isEdit = computed(() => !!props.schedule)

// 表单验证规则
const rules = {
  title: [
    { required: true, message: '请输入标题', trigger: 'blur' }
  ],
  activity_type: [
    { required: true, message: '请选择活动类型', trigger: 'change' }
  ],
  schedule_date: [
    { required: true, message: '请选择日期', trigger: 'change' }
  ],
  start_time: [
    { required: true, message: '请选择开始时间', trigger: 'change' }
  ],
  end_time: [
    { required: true, message: '请选择结束时间', trigger: 'change' }
  ],
  repeat_days: [
    {
      validator: (rule, value, callback) => {
        if (form.value.repeat_type === 'weekly' && repeatDaysArray.value.length === 0) {
          callback(new Error('请至少选择一天'))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ],
  repeat_until: [
    {
      validator: (rule, value, callback) => {
        if (form.value.repeat_type !== 'once' && !value) {
          callback(new Error('请选择重复截止日期'))
        } else {
          callback()
        }
      },
      trigger: 'change'
    }
  ]
}

// 方法
const disabledDate = (time) => {
  // 不能选择过去的日期
  return time.getTime() < Date.now() - 24 * 60 * 60 * 1000
}

const disabledRepeatUntilDate = (time) => {
  if (!form.value.schedule_date) return true
  // 截止日期必须在开始日期之后
  return time.getTime() < new Date(form.value.schedule_date).getTime()
}

const formatDate = (date) => {
  if (!date) return ''
  const d = new Date(date)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const handleClose = () => {
  emit('update:modelValue', false)
  formRef.value?.resetFields()
  form.value = { ...defaultForm }
  repeatDaysArray.value = []
}

const handleSubmit = async () => {
  try {
    await formRef.value.validate()

    loading.value = true

    // 准备提交数据
    const submitData = {
      ...form.value,
      schedule_date: formatDate(form.value.schedule_date),
      repeat_until: form.value.repeat_until ? formatDate(form.value.repeat_until) : null,
      repeat_days: repeatDaysArray.value.join(',')
    }

    let res
    if (isEdit.value) {
      res = await updateSchedule(props.schedule.id, submitData)
    } else {
      res = await createSchedule(submitData)
    }

    if (res.success) {
      ElMessage.success(isEdit.value ? '更新成功' : '创建成功')
      emit('success')
      handleClose()
    }
  } catch (error) {
    if (error !== false) { // 不是验证失败
      console.error('提交失败:', error)
      ElMessage.error(error.response?.data?.error?.message || '操作失败')
    }
  } finally {
    loading.value = false
  }
}

// 监听 schedule 变化，用于编辑
watch(() => props.schedule, (newSchedule) => {
  if (newSchedule) {
    form.value = {
      title: newSchedule.title,
      activity_type: newSchedule.activity_type,
      subject: newSchedule.subject || '',
      schedule_date: newSchedule.schedule_date,
      start_time: newSchedule.start_time,
      end_time: newSchedule.end_time,
      repeat_type: newSchedule.repeat_type || 'once',
      repeat_days: newSchedule.repeat_days || '',
      repeat_until: newSchedule.repeat_until || '',
      description: newSchedule.description || '',
      location: newSchedule.location || '',
      reminder_minutes: newSchedule.reminder_minutes || 15,
      is_reminder_enabled: newSchedule.is_reminder_enabled !== false
    }

    if (newSchedule.repeat_days) {
      repeatDaysArray.value = newSchedule.repeat_days.split(',')
    }
  }
}, { immediate: true })

// 监听 repeatDaysArray 变化
watch(repeatDaysArray, (newVal) => {
  form.value.repeat_days = newVal.join(',')
})
</script>

<style scoped>
:deep(.el-form-item__label) {
  font-weight: 500;
}

:deep(.el-checkbox) {
  margin-right: 15px;
}
</style>
