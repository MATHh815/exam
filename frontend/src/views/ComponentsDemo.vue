<template>
  <div class="components-demo">
    <div class="demo-header">
      <h1>UI 组件演示</h1>
      <p>Phase 1 新创建的组件展示</p>
    </div>

    <div class="demo-grid">
      <!-- 进度环形图 -->
      <el-card class="demo-card">
        <template #header>
          <div class="card-header">
            <span>进度环形图 (ProgressRing)</span>
            <el-button type="primary" size="small" @click="randomProgress">
              随机数据
            </el-button>
          </div>
        </template>
        <ProgressRing 
          :value="progressValue" 
          :total="100" 
          label="今日完成度"
          @click="handleProgressClick"
        />
      </el-card>

      <!-- 正确率趋势图 -->
      <el-card class="demo-card">
        <template #header>
          <div class="card-header">
            <span>正确率趋势图 (AccuracyTrend)</span>
            <el-button type="primary" size="small" @click="randomTrend">
              随机数据
            </el-button>
          </div>
        </template>
        <AccuracyTrend :data="trendData" :days="7" />
      </el-card>

      <!-- 学习日历 -->
      <el-card class="demo-card full-width">
        <template #header>
          <div class="card-header">
            <span>学习日历 (StudyCalendar)</span>
            <el-button type="primary" size="small" @click="randomCalendar">
              随机数据
            </el-button>
          </div>
        </template>
        <StudyCalendar 
          :data="calendarData" 
          :days="90"
          @day-click="handleDayClick"
        />
      </el-card>

      <!-- 数字滚动动画演示 -->
      <el-card class="demo-card">
        <template #header>
          <div class="card-header">
            <span>数字滚动动画 (useCountUp)</span>
            <el-button type="primary" size="small" @click="randomNumber">
              随机数字
            </el-button>
          </div>
        </template>
        <div class="number-demo">
          <div class="big-number">{{ displayValue }}</div>
          <div class="number-label">累计练习题数</div>
        </div>
      </el-card>

      <!-- 科目雷达图 -->
      <el-card class="demo-card">
        <template #header>
          <div class="card-header">
            <span>科目雷达图 (SubjectRadar)</span>
            <el-button type="primary" size="small" @click="randomSubject">
              随机数据
            </el-button>
          </div>
        </template>
        <SubjectRadar :data="subjectData" />
      </el-card>

      <!-- 今日目标 -->
      <el-card class="demo-card full-width">
        <DailyGoals :goals="dailyGoals" />
      </el-card>

      <!-- 使用说明 -->
      <el-card class="demo-card full-width">
        <template #header>
          <span>使用说明</span>
        </template>
        <div class="usage-info">
          <h4>✅ Phase 1 组件已全部完成！</h4>
          <ul>
            <li>✅ ProgressRing - 进度环形图</li>
            <li>✅ AccuracyTrend - 正确率趋势图</li>
            <li>✅ StudyCalendar - 学习日历</li>
            <li>✅ SubjectRadar - 科目雷达图</li>
            <li>✅ DailyGoals - 今日目标</li>
            <li>✅ useCountUp - 数字滚动动画</li>
          </ul>
          <p>查看详细文档：</p>
          <code>exam/frontend/COMPONENTS_USAGE_GUIDE.md</code>
          <p style="margin-top: 16px;">集成指南：</p>
          <code>exam/DASHBOARD_INTEGRATION_GUIDE.md</code>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import ProgressRing from '../components/charts/ProgressRing.vue'
import AccuracyTrend from '../components/charts/AccuracyTrend.vue'
import StudyCalendar from '../components/StudyCalendar.vue'
import SubjectRadar from '../components/charts/SubjectRadar.vue'
import DailyGoals from '../components/DailyGoals.vue'
import { useCountUp } from '../composables/useCountUp'
import { EditPen, Clock, TrendCharts } from '@element-plus/icons-vue'
import dayjs from 'dayjs'

// 进度数据
const progressValue = ref(65)

// 趋势数据
const trendData = ref([
  { date: '12-20', accuracy: 0.82 },
  { date: '12-21', accuracy: 0.85 },
  { date: '12-22', accuracy: 0.88 },
  { date: '12-23', accuracy: 0.86 },
  { date: '12-24', accuracy: 0.90 },
  { date: '12-25', accuracy: 0.87 },
  { date: '12-26', accuracy: 0.89 }
])

// 日历数据
const calendarData = ref(generateCalendarData())

// 数字滚动
const targetNumber = ref(1234)
const { displayValue } = useCountUp(targetNumber, { decimals: 0 })

// 科目数据
const subjectData = ref([
  { value: 85 },  // 行测
  { value: 78 },  // 申论
  { value: 92 },  // 数学
  { value: 88 },  // 英语
  { value: 75 }   // 专业课
])

// 今日目标
const dailyGoals = ref([
  {
    title: '练习题目',
    current: 35,
    target: 50,
    unit: '题',
    icon: EditPen,
    color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    completed: false
  },
  {
    title: '学习时长',
    current: 95,
    target: 120,
    unit: '分钟',
    icon: Clock,
    color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    completed: false
  },
  {
    title: '正确率',
    current: 88,
    target: 85,
    unit: '%',
    icon: TrendCharts,
    color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    completed: true
  }
])

// 生成日历数据
function generateCalendarData() {
  const data = []
  const today = dayjs()
  
  for (let i = 89; i >= 0; i--) {
    const date = today.subtract(i, 'day').format('YYYY-MM-DD')
    const count = Math.random() > 0.3 ? Math.floor(Math.random() * 60) : 0
    
    data.push({
      date,
      count,
      duration: count > 0 ? Math.floor(count * 2.5) : 0,
      accuracy: count > 0 ? 0.7 + Math.random() * 0.25 : 0
    })
  }
  
  return data
}

// 随机进度
function randomProgress() {
  progressValue.value = Math.floor(Math.random() * 100)
  ElMessage.success(`进度更新为 ${progressValue.value}%`)
}

// 随机趋势
function randomTrend() {
  trendData.value = trendData.value.map(item => ({
    ...item,
    accuracy: 0.7 + Math.random() * 0.25
  }))
  ElMessage.success('趋势数据已更新')
}

// 随机日历
function randomCalendar() {
  calendarData.value = generateCalendarData()
  ElMessage.success('日历数据已更新')
}

// 随机数字
function randomNumber() {
  targetNumber.value = Math.floor(Math.random() * 10000)
  ElMessage.success(`数字更新为 ${targetNumber.value}`)
}

// 进度点击
function handleProgressClick() {
  ElMessage.info('点击了进度环形图')
}

// 日期点击
function handleDayClick(day) {
  if (day.count > 0) {
    ElMessage.info(`${day.date}: 练习 ${day.count} 题，用时 ${day.duration} 分钟`)
  } else {
    ElMessage.info(`${day.date}: 无学习记录`)
  }
}

// 随机科目
function randomSubject() {
  subjectData.value = subjectData.value.map(() => ({
    value: Math.floor(Math.random() * 40) + 60
  }))
  ElMessage.success('科目数据已更新')
}
</script>

<style scoped>
.components-demo {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.demo-header {
  text-align: center;
  margin-bottom: 40px;
  color: #fff;
}

.demo-header h1 {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 12px 0;
  background: linear-gradient(90deg, #667eea, #764ba2);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.demo-header p {
  font-size: 16px;
  opacity: 0.8;
  margin: 0;
}

.demo-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.demo-card {
  background: rgba(255, 255, 255, 0.08) !important;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  border-radius: 16px !important;
}

.demo-card.full-width {
  grid-column: 1 / -1;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: #fff;
  font-weight: 600;
}

.number-demo {
  text-align: center;
  padding: 40px 20px;
}

.big-number {
  font-size: 64px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 12px;
}

.number-label {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.7);
}

.usage-info {
  color: rgba(255, 255, 255, 0.9);
}

.usage-info h4 {
  margin: 0 0 16px 0;
  color: #fff;
}

.usage-info ul {
  margin: 0 0 16px 0;
  padding-left: 20px;
}

.usage-info li {
  margin-bottom: 8px;
}

.usage-info p {
  margin: 16px 0 8px 0;
  color: rgba(255, 255, 255, 0.7);
}

.usage-info code {
  display: block;
  padding: 12px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 8px;
  color: #67c23a;
  font-family: 'Courier New', monospace;
  font-size: 13px;
}

@media (max-width: 992px) {
  .demo-grid {
    grid-template-columns: 1fr;
  }
}

:deep(.el-card__header) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
  padding: 16px 20px !important;
}

:deep(.el-card__body) {
  padding: 20px !important;
}
</style>
