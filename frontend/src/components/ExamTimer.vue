<template>
  <div class="exam-timer" :class="{ 'timer-warning': isWarning, 'timer-danger': isDanger }">
    <el-icon class="timer-icon"><Clock /></el-icon>
    <span class="timer-text">{{ formattedTime }}</span>
    <!-- 语音开关 -->
    <el-tooltip :content="voiceEnabled ? '关闭语音提醒' : '开启语音提醒'" placement="bottom">
      <el-icon 
        class="voice-toggle" 
        :class="{ 'voice-off': !voiceEnabled }"
        @click="toggleVoice"
      >
        <Microphone v-if="voiceEnabled" />
        <Mute v-else />
      </el-icon>
    </el-tooltip>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { Clock, Microphone, Mute } from '@element-plus/icons-vue'
import examVoice from '../utils/examVoice'

const props = defineProps({
  // 总时长（秒）
  duration: {
    type: Number,
    required: true
  },
  // 是否自动开始
  autoStart: {
    type: Boolean,
    default: true
  },
  // 是否启用语音提醒
  enableVoice: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['timeout', 'tick', 'voiceReminder'])

// 剩余时间（秒）
const remainingTime = ref(props.duration)
// 定时器ID
let timerId = null
// 语音开关
const voiceEnabled = ref(props.enableVoice)
// 已播放的提醒记录（避免重复播放）
const playedReminders = ref(new Set())

// 格式化时间显示
const formattedTime = computed(() => {
  const hours = Math.floor(remainingTime.value / 3600)
  const minutes = Math.floor((remainingTime.value % 3600) / 60)
  const seconds = remainingTime.value % 60
  
  if (hours > 0) {
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  }
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
})

// 是否进入警告状态（剩余时间少于10分钟）
const isWarning = computed(() => {
  return remainingTime.value <= 600 && remainingTime.value > 300
})

// 是否进入危险状态（剩余时间少于5分钟）
const isDanger = computed(() => {
  return remainingTime.value <= 300
})

/**
 * 切换语音开关
 */
function toggleVoice() {
  voiceEnabled.value = !voiceEnabled.value
  examVoice.setEnabled(voiceEnabled.value)
}

/**
 * 检查并播放时间提醒
 */
function checkTimeReminder(seconds) {
  if (!voiceEnabled.value) return
  
  // 15分钟提醒 (900秒)
  if (seconds === 900 && !playedReminders.value.has('15min')) {
    playedReminders.value.add('15min')
    examVoice.announce15Minutes()
    emit('voiceReminder', '15min')
  }
  // 10分钟提醒 (600秒)
  else if (seconds === 600 && !playedReminders.value.has('10min')) {
    playedReminders.value.add('10min')
    examVoice.announce10Minutes()
    emit('voiceReminder', '10min')
  }
  // 5分钟提醒 (300秒)
  else if (seconds === 300 && !playedReminders.value.has('5min')) {
    playedReminders.value.add('5min')
    examVoice.announce5Minutes()
    emit('voiceReminder', '5min')
  }
  // 1分钟提醒 (60秒)
  else if (seconds === 60 && !playedReminders.value.has('1min')) {
    playedReminders.value.add('1min')
    examVoice.announce1Minute()
    emit('voiceReminder', '1min')
  }
}

// 开始倒计时
function start() {
  if (timerId) return
  
  timerId = setInterval(() => {
    if (remainingTime.value > 0) {
      remainingTime.value--
      emit('tick', remainingTime.value)
      
      // 检查时间提醒
      checkTimeReminder(remainingTime.value)
      
      if (remainingTime.value === 0) {
        stop()
        // 播放考试结束提醒
        if (voiceEnabled.value) {
          examVoice.announceExamEnd()
        }
        emit('timeout')
      }
    }
  }, 1000)
}

// 停止倒计时
function stop() {
  if (timerId) {
    clearInterval(timerId)
    timerId = null
  }
}

// 重置倒计时
function reset(newDuration) {
  stop()
  remainingTime.value = newDuration || props.duration
  playedReminders.value.clear()
}

/**
 * 播放考试开始语音
 */
function announceStart() {
  if (voiceEnabled.value) {
    examVoice.announceExamStart()
  }
}

// 暴露方法给父组件
defineExpose({
  start,
  stop,
  reset,
  remainceTime: remainingTime,
  announceStart,
  toggleVoice
})

// 监听 duration 变化
watch(() => props.duration, (newDuration, oldDuration) => {
  // 当 duration 从 0 变为正数时，重新初始化并启动计时器
  if (newDuration > 0 && (oldDuration === 0 || oldDuration === undefined)) {
    console.log('[ExamTimer] Duration changed from', oldDuration, 'to', newDuration, '- restarting timer')
    remainingTime.value = newDuration
    playedReminders.value.clear()
    // 如果设置了自动启动，重新启动计时器
    if (props.autoStart) {
      stop()
      start()
    }
  } else if (newDuration !== remainingTime.value) {
    remainingTime.value = newDuration
  }
})

onMounted(() => {
  // 设置语音状态
  examVoice.setEnabled(voiceEnabled.value)
  
  // 只有当 duration > 0 时才自动启动
  if (props.autoStart && props.duration > 0) {
    console.log('[ExamTimer] Auto-starting with duration:', props.duration)
    start()
  } else if (props.autoStart && props.duration === 0) {
    console.log('[ExamTimer] Duration is 0, waiting for valid duration before starting')
  }
})

onUnmounted(() => {
  stop()
  examVoice.stop()
})
</script>

<style scoped>
.exam-timer {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background-color: #f5f7fa;
  border-radius: 4px;
  font-size: 16px;
  font-weight: 500;
  color: #606266;
  transition: all 0.3s;
}

.timer-icon {
  font-size: 18px;
}

.timer-text {
  font-family: 'Courier New', monospace;
  letter-spacing: 1px;
}

.voice-toggle {
  font-size: 16px;
  cursor: pointer;
  margin-left: 4px;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.3s;
  color: #409eff;
}

.voice-toggle:hover {
  background-color: rgba(64, 158, 255, 0.1);
}

.voice-toggle.voice-off {
  color: #909399;
}

.timer-warning {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.timer-warning .timer-icon {
  color: #e6a23c;
}

.timer-warning .voice-toggle {
  color: #e6a23c;
}

.timer-danger {
  background-color: #fef0f0;
  color: #f56c6c;
  animation: pulse 1s infinite;
}

.timer-danger .timer-icon {
  color: #f56c6c;
}

.timer-danger .voice-toggle {
  color: #f56c6c;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}
</style>
