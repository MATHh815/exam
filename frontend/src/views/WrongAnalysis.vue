<template>
  <div class="wrong-analysis-container">
    <div class="page-header">
      <h1>错题智能分析</h1>
      <p>深度分析错题，精准定位薄弱环节</p>
    </div>

    <!-- 错题概览 -->
    <div class="overview-section">
      <el-card class="overview-card" shadow="hover" v-loading="loading.overview">
        <template #header>
          <div class="card-header">
            <span class="card-title">错题概览</span>
            <el-select v-model="selectedDays" @change="loadData" size="small" style="width: 120px">
              <el-option label="最近7天" :value="7" />
              <el-option label="最近30天" :value="30" />
              <el-option label="最近90天" :value="90" />
            </el-select>
          </div>
        </template>
        
        <div class="overview-stats">
          <div class="stat-item">
            <div class="stat-icon error">
              <el-icon><CircleClose /></el-icon>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ overview.wrong_count || 0 }}</span>
              <span class="stat-label">错题总数</span>
            </div>
          </div>
          
          <div class="stat-item">
            <div class="stat-icon warning">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ formatPercent(overview.wrong_rate) }}</span>
              <span class="stat-label">错题率</span>
            </div>
          </div>
          
          <div class="stat-item">
            <div class="stat-icon" :class="overview.improvement_rate >= 0 ? 'success' : 'error'">
              <el-icon><TrendCharts /></el-icon>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ formatImprovement(overview.improvement_rate) }}</span>
              <span class="stat-label">改善率</span>
            </div>
          </div>
          
          <div class="stat-item">
            <div class="stat-icon info">
              <el-icon><Document /></el-icon>
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ overview.total_count || 0 }}</span>
              <span class="stat-label">练习总数</span>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 图表区域 -->
    <div class="charts-grid">
      <!-- 错题趋势 -->
      <el-card class="chart-card" shadow="hover" v-loading="loading.trend">
        <template #header>
          <span class="card-title">错题趋势</span>
        </template>
        <div ref="trendChart" class="chart-container"></div>
      </el-card>

      <!-- 错题分布 -->
      <el-card class="chart-card" shadow="hover" v-loading="loading.distribution">
        <template #header>
          <div class="card-header">
            <span class="card-title">错题分布</span>
            <el-radio-group v-model="distributionDimension" @change="loadDistribution" size="small">
              <el-radio-button label="subject">科目</el-radio-button>
              <el-radio-button label="type">题型</el-radio-button>
            </el-radio-group>
          </div>
        </template>
        <div ref="distributionChart" class="chart-container"></div>
      </el-card>
    </div>

    <!-- 详细分析 -->
    <div class="analysis-grid">
      <!-- 高频错题 -->
      <el-card class="analysis-card" shadow="hover" v-loading="loading.frequent">
        <template #header>
          <span class="card-title">高频错题 Top 10</span>
        </template>
        <el-empty v-if="!frequentWrong.length" description="暂无数据" :image-size="80" />
        <div v-else class="frequent-list">
          <div v-for="(item, index) in frequentWrong" :key="item.question_id" class="frequent-item">
            <div class="frequent-rank">{{ index + 1 }}</div>
            <div class="frequent-content">
              <div class="frequent-text">{{ item.content }}</div>
              <div class="frequent-meta">
                <el-tag size="small">{{ item.subject }}</el-tag>
                <el-tag size="small" type="info">{{ getQuestionTypeLabel(item.question_type) }}</el-tag>
                <span class="frequent-count">错误 {{ item.wrong_count }} 次</span>
              </div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 薄弱知识点 -->
      <el-card class="analysis-card" shadow="hover" v-loading="loading.weakPoints">
        <template #header>
          <span class="card-title">薄弱知识点</span>
        </template>
        <el-empty v-if="!weakPoints.length" description="暂无数据" :image-size="80" />
        <div v-else class="weak-points-list">
          <div v-for="point in weakPoints" :key="point.knowledge_point" class="weak-point-item">
            <div class="weak-point-header">
              <span class="weak-point-name">{{ point.knowledge_point }}</span>
              <span class="weak-point-mastery" :class="getMasteryClass(point.mastery)">
                掌握度 {{ formatPercent(point.mastery) }}
              </span>
            </div>
            <el-progress 
              :percentage="point.mastery * 100" 
              :color="getMasteryColor(point.mastery)"
              :show-text="false"
            />
            <div class="weak-point-stats">
              <span>练习 {{ point.total }} 题</span>
              <span>错误 {{ point.wrong }} 题</span>
            </div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 学习建议 -->
    <el-card class="suggestions-card" shadow="hover" v-loading="loading.suggestions">
      <template #header>
        <span class="card-title">智能学习建议</span>
      </template>
      <el-empty v-if="!suggestions.length" description="暂无建议" :image-size="80" />
      <div v-else class="suggestions-list">
        <div v-for="(suggestion, index) in suggestions" :key="index" class="suggestion-item">
          <el-icon class="suggestion-icon"><Lightbulb /></el-icon>
          <span class="suggestion-text">{{ suggestion }}</span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { CircleClose, Warning, TrendCharts, Document, Lightbulb } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import {
  getWrongOverview,
  getWrongDistribution,
  getFrequentWrong,
  getWrongTrend,
  getWeakPoints,
  getLearningSuggestions
} from '../api/wrongAnalysis'

// 数据
const selectedDays = ref(30)
const distributionDimension = ref('subject')
const overview = ref({})
const trendData = ref([])
const distributionData = ref([])
const frequentWrong = ref([])
const weakPoints = ref([])
const suggestions = ref([])

// 加载状态
const loading = reactive({
  overview: false,
  trend: false,
  distribution: false,
  frequent: false,
  weakPoints: false,
  suggestions: false
})

// 图表实例
const trendChart = ref(null)
const distributionChart = ref(null)
let trendChartInstance = null
let distributionChartInstance = null

// 格式化函数
function formatPercent(value) {
  if (value === undefined || value === null) return '0%'
  return `${(value * 100).toFixed(1)}%`
}

function formatImprovement(value) {
  if (value === undefined || value === null) return '0%'
  const sign = value >= 0 ? '+' : ''
  return `${sign}${(value * 100).toFixed(1)}%`
}

function getQuestionTypeLabel(type) {
  const labels = {
    single_choice: '单选题',
    multiple_choice: '多选题',
    true_false: '判断题',
    fill_blank: '填空题',
    essay: '简答题'
  }
  return labels[type] || type
}

function getMasteryClass(mastery) {
  if (mastery >= 0.8) return 'high'
  if (mastery >= 0.6) return 'medium'
  return 'low'
}

function getMasteryColor(mastery) {
  if (mastery >= 0.8) return '#10b981'
  if (mastery >= 0.6) return '#f59e0b'
  return '#ef4444'
}

// 加载数据
async function loadData() {
  await Promise.all([
    loadOverview(),
    loadTrend(),
    loadDistribution(),
    loadFrequent(),
    loadWeakPoints(),
    loadSuggestions()
  ])
}

async function loadOverview() {
  loading.overview = true
  try {
    const response = await getWrongOverview({ days: selectedDays.value })
    if (response.data) {
      overview.value = response.data
    }
  } catch (error) {
    console.error('加载错题概览失败:', error)
    ElMessage.error('加载错题概览失败')
  } finally {
    loading.overview = false
  }
}

async function loadTrend() {
  loading.trend = true
  try {
    const response = await getWrongTrend({ days: selectedDays.value })
    if (response.data) {
      trendData.value = response.data
      await nextTick()
      renderTrendChart()
    }
  } catch (error) {
    console.error('加载错题趋势失败:', error)
  } finally {
    loading.trend = false
  }
}

async function loadDistribution() {
  loading.distribution = true
  try {
    const response = await getWrongDistribution({
      dimension: distributionDimension.value,
      days: selectedDays.value
    })
    if (response.data) {
      distributionData.value = response.data
      await nextTick()
      renderDistributionChart()
    }
  } catch (error) {
    console.error('加载错题分布失败:', error)
  } finally {
    loading.distribution = false
  }
}

async function loadFrequent() {
  loading.frequent = true
  try {
    const response = await getFrequentWrong({ limit: 10 })
    if (response.data) {
      frequentWrong.value = response.data
    }
  } catch (error) {
    console.error('加载高频错题失败:', error)
  } finally {
    loading.frequent = false
  }
}

async function loadWeakPoints() {
  loading.weakPoints = true
  try {
    const response = await getWeakPoints({ limit: 10 })
    if (response.data) {
      weakPoints.value = response.data
    }
  } catch (error) {
    console.error('加载薄弱知识点失败:', error)
  } finally {
    loading.weakPoints = false
  }
}

async function loadSuggestions() {
  loading.suggestions = true
  try {
    const response = await getLearningSuggestions()
    if (response.data) {
      suggestions.value = response.data
    }
  } catch (error) {
    console.error('加载学习建议失败:', error)
  } finally {
    loading.suggestions = false
  }
}

// 渲染图表
function renderTrendChart() {
  if (!trendChart.value || !trendData.value.length) return
  
  if (!trendChartInstance) {
    trendChartInstance = echarts.init(trendChart.value)
  }
  
  const dates = trendData.value.map(item => item.date.substring(5))
  const wrongRates = trendData.value.map(item => (item.wrong_rate * 100).toFixed(1))
  
  const option = {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderColor: 'transparent',
      textStyle: { color: '#fff' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.2)' } },
      axisLabel: { color: 'rgba(255, 255, 255, 0.7)' }
    },
    yAxis: {
      type: 'value',
      name: '错题率(%)',
      axisLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.2)' } },
      axisLabel: { color: 'rgba(255, 255, 255, 0.7)' },
      splitLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.1)' } }
    },
    series: [{
      data: wrongRates,
      type: 'line',
      smooth: true,
      symbol: 'circle',
      symbolSize: 6,
      lineStyle: { color: '#ef4444', width: 2 },
      itemStyle: { color: '#ef4444' },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(239, 68, 68, 0.3)' },
            { offset: 1, color: 'rgba(239, 68, 68, 0.05)' }
          ]
        }
      }
    }]
  }
  
  trendChartInstance.setOption(option)
}

function renderDistributionChart() {
  if (!distributionChart.value || !distributionData.value.length) return
  
  if (!distributionChartInstance) {
    distributionChartInstance = echarts.init(distributionChart.value)
  }
  
  const option = {
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderColor: 'transparent',
      textStyle: { color: '#fff' }
    },
    legend: {
      orient: 'vertical',
      right: '10%',
      top: 'center',
      textStyle: { color: 'rgba(255, 255, 255, 0.7)' }
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['35%', '50%'],
      data: distributionData.value,
      emphasis: {
        itemStyle: {
          shadowBlur: 10,
          shadowOffsetX: 0,
          shadowColor: 'rgba(0, 0, 0, 0.5)'
        }
      },
      label: {
        color: 'rgba(255, 255, 255, 0.7)'
      }
    }]
  }
  
  distributionChartInstance.setOption(option)
}

// 窗口大小改变时重新渲染图表
function handleResize() {
  trendChartInstance?.resize()
  distributionChartInstance?.resize()
}

onMounted(() => {
  loadData()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  trendChartInstance?.dispose()
  distributionChartInstance?.dispose()
})
</script>

<style scoped>
.wrong-analysis-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 600;
  color: #fff;
  margin: 0 0 8px 0;
}

.page-header p {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
}

/* 概览统计 */
.overview-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-icon.error {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.stat-icon.warning {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.stat-icon.success {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.stat-icon.info {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #fff;
}

.stat-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

/* 图表区域 */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  margin: 24px 0;
}

.chart-card {
  min-height: 400px;
}

.chart-container {
  width: 100%;
  height: 320px;
}

/* 分析区域 */
.analysis-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  margin: 24px 0;
}

.analysis-card {
  min-height: 400px;
}

/* 高频错题 */
.frequent-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.frequent-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
}

.frequent-rank {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: #fff;
  flex-shrink: 0;
}

.frequent-content {
  flex: 1;
  min-width: 0;
}

.frequent-text {
  font-size: 14px;
  color: #fff;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.frequent-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.frequent-count {
  font-size: 12px;
  color: #ef4444;
  font-weight: 500;
}

/* 薄弱知识点 */
.weak-points-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.weak-point-item {
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
}

.weak-point-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.weak-point-name {
  font-size: 14px;
  font-weight: 500;
  color: #fff;
}

.weak-point-mastery {
  font-size: 13px;
  font-weight: 500;
}

.weak-point-mastery.high {
  color: #10b981;
}

.weak-point-mastery.medium {
  color: #f59e0b;
}

.weak-point-mastery.low {
  color: #ef4444;
}

.weak-point-stats {
  display: flex;
  gap: 16px;
  margin-top: 8px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

/* 学习建议 */
.suggestions-card {
  margin-top: 24px;
}

.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.suggestion-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  background: rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.2);
  border-radius: 8px;
}

.suggestion-icon {
  font-size: 20px;
  color: #667eea;
  flex-shrink: 0;
  margin-top: 2px;
}

.suggestion-text {
  font-size: 14px;
  color: #fff;
  line-height: 1.6;
}

/* 响应式 */
@media (max-width: 992px) {
  .overview-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .charts-grid,
  .analysis-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .overview-stats {
    grid-template-columns: 1fr;
  }
}

/* 卡片样式覆盖 */
:deep(.el-card) {
  background: rgba(255, 255, 255, 0.08) !important;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  border-radius: 16px !important;
}

:deep(.el-card__header) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
  padding: 16px 20px !important;
}

:deep(.el-card__body) {
  padding: 20px !important;
}
</style>
