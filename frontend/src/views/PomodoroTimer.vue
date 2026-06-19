<template>
  <div class="pomodoro-timer">
    <div class="timer-header">
      <Clock class="header-icon" />
      <h1 class="gradient-text">番茄钟学习计时器</h1>
    </div>

    <div class="timer-container">
      <!-- 主计时器 -->
      <div class="timer-circle" :class="{ 'active': isRunning, 'break': sessionType !== 'focus' }">
        <svg class="progress-ring" width="300" height="300">
          <circle
            class="progress-ring-bg"
            cx="150"
            cy="150"
            r="135"
          />
          <circle
            class="progress-ring-progress"
            cx="150"
            cy="150"
            r="135"
            :stroke-dasharray="circumference"
            :stroke-dashoffset="progressOffset"
          />
        </svg>
        
        <div class="timer-content">
          <div class="time-display">{{ formattedTime }}</div>
          <div class="session-label">{{ sessionLabel }}</div>
          <div class="session-count" v-if="sessionType === 'focus'">
            第 {{ todayStats.today_sessions + 1 }} 个番茄钟
          </div>
        </div>
      </div>

      <!-- 控制按钮 -->
      <div class="timer-controls">
        <el-button
          v-if="!isRunning"
          type="primary"
          size="large"
          :icon="Play"
          @click="startTimer"
          class="control-btn start-btn"
        >
          开始专注
        </el-button>
        
        <template v-else>
          <el-button
            type="warning"
            size="large"
            :icon="Pause"
            @click="pauseTimer"
            class="control-btn"
          >
            暂停
          </el-button>
          <el-button
            type="danger"
            size="large"
            :icon="Square"
            @click="stopTimer"
            class="control-btn"
          >
            结束
          </el-button>
        </template>
      </div>

      <!-- 设置选项 -->
      <div class="timer-settings">
        <div class="setting-item">
          <span class="setting-label">专注时长</span>
          <el-select v-model="focusDuration" :disabled="isRunning" size="large">
            <el-option :value="25" label="25 分钟" />
            <el-option :value="45" label="45 分钟" />
            <el-option :value="50" label="50 分钟" />
          </el-select>
        </div>
        
        <div class="setting-item">
          <span class="setting-label">学习科目</span>
          <el-input
            v-model="currentSubject"
            placeholder="输入学习科目"
            :disabled="isRunning"
            size="large"
          />
        </div>
      </div>
    </div>

    <!-- 今日统计 -->
    <div class="today-stats">
      <div class="stat-card">
        <Target class="stat-icon" />
        <div class="stat-content">
          <div class="stat-value">{{ todayStats.today_sessions }}</div>
          <div class="stat-label">今日完成</div>
        </div>
      </div>
      
      <div class="stat-card">
        <Clock class="stat-icon" />
        <div class="stat-content">
          <div class="stat-value">{{ todayStats.today_focus_time }}</div>
          <div class="stat-label">专注分钟</div>
        </div>
      </div>
      
      <div class="stat-card">
        <Flame class="stat-icon" />
        <div class="stat-content">
          <div class="stat-value">{{ todayStats.current_streak }}</div>
          <div class="stat-label">连续天数</div>
        </div>
      </div>
      
      <div class="stat-card">
        <Award class="stat-icon" />
        <div class="stat-content">
          <div class="stat-value">{{ todayStats.total_sessions }}</div>
          <div class="stat-label">累计完成</div>
        </div>
      </div>
    </div>

    <!-- 趋势图表 -->
    <div class="trend-section">
      <h3>学习趋势</h3>
      <div class="chart-container">
        <v-chart :option="trendChartOption" autoresize />
      </div>
    </div>

    <!-- 最近会话 -->
    <div class="recent-sessions">
      <h3>最近会话</h3>
      <div class="session-list">
        <div
          v-for="session in recentSessions"
          :key="session.id"
          class="session-item"
          :class="{ 'interrupted': session.status === 'interrupted' }"
        >
          <div class="session-icon">
            <CheckCircle v-if="session.status === 'completed'" />
            <XCircle v-else />
          </div>
          <div class="session-info">
            <div class="session-subject">{{ session.subject || '未指定科目' }}</div>
            <div class="session-time">{{ formatSessionTime(session.start_time) }}</div>
          </div>
          <div class="session-duration">{{ session.duration }} 分钟</div>
          <div class="session-points" v-if="session.points_earned > 0">
            <Coins class="coin-icon" />
            +{{ session.points_earned }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { Clock, Play, Pause, Square, Target, Flame, Award, CheckCircle, XCircle, Coins } from 'lucide-vue-next'
import { ElMessage, ElNotification } from 'element-plus'
import { completeSession, interruptSession, getStats, getRecentSessions, getDailyTrend } from '@/api/pomodoro'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'

use([CanvasRenderer, LineChart, GridComponent, TooltipComponent, LegendComponent])

// 计时器状态
const isRunning = ref(false)
const isPaused = ref(false)
const timeLeft = ref(25 * 60) // 秒
const focusDuration = ref(25) // 分钟
const sessionType = ref('focus') // focus/short_break/long_break
const currentSubject = ref('')

// 统计数据
const todayStats = ref({
  today_sessions: 0,
  today_focus_time: 0,
  current_streak: 0,
  total_sessions: 0
})
const recentSessions = ref([])
const trendData = ref([])

// 计时器
let timerInterval = null
let startTime = null

// 圆形进度
const circumference = 2 * Math.PI * 135
const progressOffset = computed(() => {
  const totalSeconds = focusDuration.value * 60
  const progress = timeLeft.value / totalSeconds
  return circumference * (1 - progress)
})

// 格式化时间显示
const formattedTime = computed(() => {
  const minutes = Math.floor(timeLeft.value / 60)
  const seconds = timeLeft.value % 60
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`
})

// 会话标签
const sessionLabel = computed(() => {
  const labels = {
    'focus': '专注时间',
    'short_break': '短休息',
    'long_break': '长休息'
  }
  return labels[sessionType.value] || '专注时间'
})

// 趋势图表配置
const trendChartOption = computed(() => {
  const dates = trendData.value.map(d => d.date.slice(5))
  const sessions = trendData.value.map(d => d.sessions)
  const focusTime = trendData.value.map(d => d.focus_time)
  
  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderColor: 'rgba(255, 255, 255, 0.2)',
      textStyle: { color: '#fff' }
    },
    legend: {
      data: ['完成数', '专注时长'],
      textStyle: { color: 'rgba(255, 255, 255, 0.8)' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.2)' } },
      axisLabel: { color: 'rgba(255, 255, 255, 0.6)' }
    },
    yAxis: [
      {
        type: 'value',
        name: '完成数',
        axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.2)' } },
        axisLabel: { color: 'rgba(255, 255, 255, 0.6)' },
        splitLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.1)' } }
      },
      {
        type: 'value',
        name: '时长(分钟)',
        axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.2)' } },
        axisLabel: { color: 'rgba(255, 255, 255, 0.6)' },
        splitLine: { show: false }
      }
    ],
    series: [
      {
        name: '完成数',
        type: 'line',
        data: sessions,
        smooth: true,
        itemStyle: { color: '#409eff' },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
              { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
            ]
          }
        }
      },
      {
        name: '专注时长',
        type: 'line',
        yAxisIndex: 1,
        data: focusTime,
        smooth: true,
        itemStyle: { color: '#67c23a' },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0, y: 0, x2: 0, y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(103, 194, 58, 0.3)' },
              { offset: 1, color: 'rgba(103, 194, 58, 0.05)' }
            ]
          }
        }
      }
    ]
  }
})

// 开始计时
const startTimer = () => {
  isRunning.value = true
  isPaused.value = false
  timeLeft.value = focusDuration.value * 60
  startTime = Date.now()
  
  timerInterval = setInterval(() => {
    timeLeft.value--
    
    if (timeLeft.value <= 0) {
      finishSession()
    }
  }, 1000)
  
  ElMessage.success('开始专注，加油！')
}

// 暂停计时
const pauseTimer = () => {
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
  isPaused.value = true
  isRunning.value = false
  ElMessage.info('已暂停')
}

// 停止计时
const stopTimer = () => {
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
  
  const completedMinutes = Math.floor((focusDuration.value * 60 - timeLeft.value) / 60)
  
  if (completedMinutes >= 5) {
    // 中断会话
    handleInterrupt(completedMinutes)
  } else {
    isRunning.value = false
    isPaused.value = false
    timeLeft.value = focusDuration.value * 60
    ElMessage.warning('会话已取消')
  }
}

// 完成会话
const finishSession = async () => {
  if (timerInterval) {
    clearInterval(timerInterval)
    timerInterval = null
  }
  
  isRunning.value = false
  
  try {
    const response = await completeSession({
      duration: focusDuration.value,
      session_type: sessionType.value,
      subject: currentSubject.value || '未指定科目'
    })
    
    if (response.data.success) {
      const result = response.data.data
      
      // 播放完成音效
      playNotificationSound()
      
      // 显示奖励通知
      ElNotification({
        title: '🎉 番茄钟完成！',
        message: `获得 ${result.points_earned} 积分！`,
        type: 'success',
        duration: 5000
      })
      
      // 显示成就
      if (result.achievements && result.achievements.length > 0) {
        result.achievements.forEach(achievement => {
          ElNotification({
            title: `🏆 ${achievement.title}`,
            message: achievement.description,
            type: 'success',
            duration: 5000
          })
        })
      }
      
      // 刷新数据
      await loadData()
    }
  } catch (error) {
    console.error('完成会话失败:', error)
    ElMessage.error('完成会话失败')
  }
  
  timeLeft.value = focusDuration.value * 60
}

// 处理中断
const handleInterrupt = async (completedMinutes) => {
  try {
    await interruptSession({
      duration: completedMinutes,
      session_type: sessionType.value,
      subject: currentSubject.value || '未指定科目'
    })
    
    ElMessage.warning(`会话已中断，已完成 ${completedMinutes} 分钟`)
    await loadData()
  } catch (error) {
    console.error('中断会话失败:', error)
  }
  
  isRunning.value = false
  isPaused.value = false
  timeLeft.value = focusDuration.value * 60
}

// 播放提示音
const playNotificationSound = () => {
  const audio = new Audio('/notification.mp3')
  audio.play().catch(() => {
    // 忽略播放失败
  })
}

// 格式化会话时间
const formatSessionTime = (timeStr) => {
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 加载数据
const loadData = async () => {
  try {
    // 加载统计
    const statsRes = await getStats()
    if (statsRes.data.success) {
      todayStats.value = statsRes.data.data
    }
    
    // 加载最近会话
    const sessionsRes = await getRecentSessions(7)
    if (sessionsRes.data.success) {
      recentSessions.value = sessionsRes.data.data.slice(0, 10)
    }
    
    // 加载趋势
    const trendRes = await getDailyTrend(14)
    if (trendRes.data.success) {
      trendData.value = trendRes.data.data
    }
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

onMounted(() => {
  loadData()
})

onUnmounted(() => {
  if (timerInterval) {
    clearInterval(timerInterval)
  }
})
</script>

<style scoped>
.pomodoro-timer {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.timer-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-bottom: 40px;
}

.header-icon {
  width: 40px;
  height: 40px;
  color: #409eff;
  filter: drop-shadow(0 0 12px rgba(64, 158, 255, 0.6));
}

.gradient-text {
  font-size: 32px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
}

.timer-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 32px;
  padding: 40px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  margin-bottom: 32px;
}

.timer-circle {
  position: relative;
  width: 300px;
  height: 300px;
}

.progress-ring {
  transform: rotate(-90deg);
}

.progress-ring-bg {
  fill: none;
  stroke: rgba(255, 255, 255, 0.1);
  stroke-width: 12;
}

.progress-ring-progress {
  fill: none;
  stroke: #409eff;
  stroke-width: 12;
  stroke-linecap: round;
  transition: stroke-dashoffset 0.3s ease;
}

.timer-circle.active .progress-ring-progress {
  stroke: #67c23a;
  filter: drop-shadow(0 0 12px rgba(103, 194, 58, 0.6));
}

.timer-circle.break .progress-ring-progress {
  stroke: #e6a23c;
}

.timer-content {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.time-display {
  font-size: 64px;
  font-weight: 700;
  color: white;
  line-height: 1;
  margin-bottom: 12px;
  text-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.session-label {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.8);
  margin-bottom: 8px;
}

.session-count {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
}

.timer-controls {
  display: flex;
  gap: 16px;
}

.control-btn {
  min-width: 140px;
  height: 48px;
  font-size: 16px;
  font-weight: 600;
}

.start-btn {
  background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%) !important;
  border: none !important;
}

.timer-settings {
  display: flex;
  gap: 24px;
  width: 100%;
  max-width: 600px;
}

.setting-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.setting-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

.today-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  background: rgba(255, 255, 255, 0.08);
  transform: translateY(-2px);
}

.stat-icon {
  width: 40px;
  height: 40px;
  color: #409eff;
  filter: drop-shadow(0 2px 8px rgba(64, 158, 255, 0.4));
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: white;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

.trend-section,
.recent-sessions {
  padding: 24px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  margin-bottom: 24px;
}

.trend-section h3,
.recent-sessions h3 {
  color: white;
  font-size: 20px;
  margin: 0 0 20px 0;
}

.chart-container {
  height: 300px;
}

.session-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.session-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.session-item:hover {
  background: rgba(255, 255, 255, 0.08);
}

.session-item.interrupted {
  opacity: 0.6;
}

.session-icon {
  width: 32px;
  height: 32px;
  color: #67c23a;
}

.session-item.interrupted .session-icon {
  color: #f56c6c;
}

.session-info {
  flex: 1;
}

.session-subject {
  font-size: 15px;
  font-weight: 600;
  color: white;
  margin-bottom: 4px;
}

.session-time {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

.session-duration {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 500;
}

.session-points {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 12px;
  background: rgba(255, 215, 0, 0.2);
  border: 1px solid rgba(255, 215, 0, 0.3);
  border-radius: 12px;
  color: #ffd700;
  font-weight: 600;
  font-size: 14px;
}

.coin-icon {
  width: 16px;
  height: 16px;
}

@media (max-width: 768px) {
  .today-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .timer-settings {
    flex-direction: column;
  }
  
  .timer-controls {
    flex-direction: column;
    width: 100%;
  }
  
  .control-btn {
    width: 100%;
  }
}
</style>
