<template>
  <div class="statistics-container">
    <!-- 顶部横幅 -->
    <div class="page-banner">
      <div class="banner-bg"></div>
      <div class="banner-content">
        <div class="banner-left">
          <div class="banner-icon">
            <el-icon :size="48"><DataAnalysis /></el-icon>
          </div>
          <div class="banner-text">
            <h1>学习统计</h1>
            <p>全面分析学习数据，助你高效提升</p>
          </div>
        </div>
        <div class="banner-right">
          <div class="date-picker-wrapper">
            <el-icon><Calendar /></el-icon>
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              @change="handleDateChange"
              :clearable="true"
              :popper-options="{ placement: 'bottom-end' }"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 学习概览 -->
    <div class="overview-section" v-loading="overviewLoading">
      <div class="section-header">
        <div class="section-title">
          <el-icon><TrendCharts /></el-icon>
          <span>学习概览</span>
        </div>
      </div>
      <div class="overview-cards">
        <div class="overview-card practice">
          <div class="card-icon">
            <el-icon :size="28"><Edit /></el-icon>
          </div>
          <div class="card-info">
            <span class="card-value">{{ overview.total_practice || 0 }}</span>
            <span class="card-label">练习题数</span>
          </div>
          <div class="card-decoration"></div>
        </div>
        
        <div class="overview-card correct">
          <div class="card-icon">
            <el-icon :size="28"><CircleCheck /></el-icon>
          </div>
          <div class="card-info">
            <span class="card-value">{{ overview.total_correct || 0 }}</span>
            <span class="card-label">正确题数</span>
          </div>
          <div class="card-decoration"></div>
        </div>
        
        <div class="overview-card accuracy">
          <div class="card-icon">
            <el-icon :size="28"><Aim /></el-icon>
          </div>
          <div class="card-info">
            <span class="card-value">{{ (overview.accuracy || 0).toFixed(1) }}<small>%</small></span>
            <span class="card-label">正确率</span>
          </div>
          <div class="card-decoration"></div>
        </div>
        
        <div class="overview-card duration">
          <div class="card-icon">
            <el-icon :size="28"><Timer /></el-icon>
          </div>
          <div class="card-info">
            <span class="card-value">{{ overview.total_duration || 0 }}</span>
            <span class="card-label">学习时长(分钟)</span>
          </div>
          <div class="card-decoration"></div>
        </div>
        
        <div class="overview-card exams">
          <div class="card-icon">
            <el-icon :size="28"><Document /></el-icon>
          </div>
          <div class="card-info">
            <span class="card-value">{{ overview.total_exams || 0 }}</span>
            <span class="card-label">考试次数</span>
          </div>
          <div class="card-decoration"></div>
        </div>
        
        <div class="overview-card days">
          <div class="card-icon">
            <el-icon :size="28"><Calendar /></el-icon>
          </div>
          <div class="card-info">
            <span class="card-value">{{ overview.study_days || 0 }}</span>
            <span class="card-label">学习天数</span>
          </div>
          <div class="card-decoration"></div>
        </div>
      </div>
    </div>

    <!-- 学习趋势 -->
    <div class="trend-section" v-loading="trendLoading">
      <div class="section-card">
        <div class="section-header">
          <div class="section-title">
            <el-icon><TrendCharts /></el-icon>
            <span>学习趋势</span>
          </div>
          <div class="section-actions">
            <div class="trend-tabs">
              <button 
                v-for="option in trendOptions" 
                :key="option.value"
                class="trend-tab"
                :class="{ active: trendDays === option.value }"
                @click="trendDays = option.value; loadTrend()"
              >
                {{ option.label }}
              </button>
            </div>
          </div>
        </div>
        <div class="trend-chart">
          <TrendLine
            v-if="trendData.length > 0"
            :trend-data="trendData"
            :show-data-zoom="trendDays > 30"
            height="400px"
          />
          <div v-else class="empty-state">
            <el-icon :size="64" color="#c0c4cc"><PieChart /></el-icon>
            <p>暂无学习数据</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 知识点分析 -->
    <div class="knowledge-section" v-loading="knowledgeLoading">
      <div class="section-header">
        <div class="section-title">
          <el-icon><Connection /></el-icon>
          <span>知识点掌握情况</span>
        </div>
      </div>
      <div class="knowledge-grid">
        <div class="knowledge-radar-card">
          <div class="card-header">
            <span>知识点雷达图</span>
          </div>
          <div class="radar-wrapper">
            <KnowledgeRadar
              v-if="knowledgePoints.length > 0"
              :knowledge-points="knowledgePoints"
              height="400px"
            />
            <div v-else class="empty-state">
              <el-icon :size="64" color="#c0c4cc"><DataBoard /></el-icon>
              <p>暂无知识点数据</p>
            </div>
          </div>
        </div>
        
        <div class="knowledge-table-card">
          <div class="card-header">
            <span>知识点详情</span>
            <el-tag v-if="weakCount > 0" type="danger" size="small">
              {{ weakCount }} 个薄弱项
            </el-tag>
          </div>
          <div class="table-wrapper">
            <el-table
              :data="knowledgePoints"
              style="width: 100%"
              max-height="380"
              :default-sort="{ prop: 'accuracy', order: 'ascending' }"
              :row-class-name="tableRowClassName"
            >
              <el-table-column prop="subject" label="科目" width="90">
                <template #default="{ row }">
                  <span class="subject-tag">{{ row.subject }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="chapter" label="章节" min-width="140" show-overflow-tooltip />
              <el-table-column prop="total_count" label="答题数" width="80" align="center">
                <template #default="{ row }">
                  <span class="count-value">{{ row.total_count }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="correct_count" label="正确数" width="80" align="center">
                <template #default="{ row }">
                  <span class="count-value correct">{{ row.correct_count }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="accuracy" label="正确率" width="110" align="center" sortable>
                <template #default="{ row }">
                  <div class="accuracy-cell">
                    <div class="accuracy-bar">
                      <div 
                        class="accuracy-fill" 
                        :class="getAccuracyClass(row.accuracy)"
                        :style="{ width: row.accuracy + '%' }"
                      ></div>
                    </div>
                    <span class="accuracy-text" :class="getAccuracyClass(row.accuracy)">
                      {{ row.accuracy.toFixed(0) }}%
                    </span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="is_weak" label="状态" width="80" align="center">
                <template #default="{ row }">
                  <span v-if="row.is_weak" class="weak-badge">薄弱</span>
                  <span v-else class="normal-badge">正常</span>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </div>
    </div>

    <!-- 考试统计 -->
    <div class="exam-section" v-loading="examStatsLoading">
      <div class="section-card">
        <div class="section-header">
          <div class="section-title">
            <el-icon><Medal /></el-icon>
            <span>考试统计</span>
          </div>
        </div>
        <div class="exam-stats" v-if="examStats.total_exams > 0">
          <div class="exam-stat-card">
            <div class="stat-ring total">
              <span class="ring-value">{{ examStats.total_exams || 0 }}</span>
            </div>
            <span class="stat-label">考试次数</span>
          </div>
          <div class="exam-stat-card">
            <div class="stat-ring average">
              <span class="ring-value">{{ (examStats.average_score || 0).toFixed(0) }}</span>
            </div>
            <span class="stat-label">平均分</span>
          </div>
          <div class="exam-stat-card">
            <div class="stat-ring highest">
              <span class="ring-value">{{ (examStats.highest_score || 0).toFixed(0) }}</span>
            </div>
            <span class="stat-label">最高分</span>
          </div>
          <div class="exam-stat-card">
            <div class="stat-ring accuracy">
              <span class="ring-value">{{ (examStats.average_accuracy || 0).toFixed(0) }}<small>%</small></span>
            </div>
            <span class="stat-label">平均正确率</span>
          </div>
        </div>
        <div v-else class="empty-state">
          <el-icon :size="64" color="#c0c4cc"><Document /></el-icon>
          <p>暂无考试数据</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  DataAnalysis, Calendar, TrendCharts, Edit, CircleCheck, Aim, 
  Timer, Document, Connection, Medal, PieChart, DataBoard 
} from '@element-plus/icons-vue'
import { getOverview, getKnowledgeAnalysis, getTrend, getExamStatistics } from '../api/statistics'
import TrendLine from '../components/TrendLine.vue'
import KnowledgeRadar from '../components/KnowledgeRadar.vue'

// 日期范围
const dateRange = ref(null)

// 趋势选项
const trendOptions = [
  { label: '7天', value: 7 },
  { label: '14天', value: 14 },
  { label: '30天', value: 30 },
  { label: '90天', value: 90 }
]

// 学习概览数据
const overview = ref({})
const overviewLoading = ref(false)

// 学习趋势数据
const trendData = ref([])
const trendDays = ref(7)
const trendLoading = ref(false)

// 知识点数据
const knowledgePoints = ref([])
const knowledgeLoading = ref(false)

// 考试统计数据
const examStats = ref({})
const examStatsLoading = ref(false)

// 薄弱项数量
const weakCount = computed(() => {
  return knowledgePoints.value.filter(item => item.is_weak).length
})

// 获取正确率样式类
function getAccuracyClass(accuracy) {
  if (accuracy >= 80) return 'high'
  if (accuracy >= 60) return 'medium'
  return 'low'
}

// 表格行样式
function tableRowClassName({ row }) {
  if (row.is_weak) return 'weak-row'
  return ''
}

// 加载学习概览
const loadOverview = async () => {
  overviewLoading.value = true
  try {
    const params = {}
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    
    const res = await getOverview(params)
    if (res.success) {
      overview.value = res.data
    }
  } catch (error) {
    console.error('加载学习概览失败:', error)
    ElMessage.error('加载学习概览失败')
  } finally {
    overviewLoading.value = false
  }
}

// 加载学习趋势
const loadTrend = async () => {
  trendLoading.value = true
  try {
    const res = await getTrend({ days: trendDays.value })
    if (res.success) {
      trendData.value = res.data.trend || []
    }
  } catch (error) {
    console.error('加载学习趋势失败:', error)
    ElMessage.error('加载学习趋势失败')
  } finally {
    trendLoading.value = false
  }
}

// 加载知识点分析
const loadKnowledgeAnalysis = async () => {
  knowledgeLoading.value = true
  try {
    const params = {}
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    
    const res = await getKnowledgeAnalysis(params)
    if (res.success) {
      knowledgePoints.value = res.data.knowledge_points || []
    }
  } catch (error) {
    console.error('加载知识点分析失败:', error)
    ElMessage.error('加载知识点分析失败')
  } finally {
    knowledgeLoading.value = false
  }
}

// 加载考试统计
const loadExamStatistics = async () => {
  examStatsLoading.value = true
  try {
    const params = {}
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    
    const res = await getExamStatistics(params)
    if (res.success) {
      examStats.value = res.data
    }
  } catch (error) {
    console.error('加载考试统计失败:', error)
    ElMessage.error('加载考试统计失败')
  } finally {
    examStatsLoading.value = false
  }
}

// 日期范围变化处理
const handleDateChange = () => {
  loadOverview()
  loadKnowledgeAnalysis()
  loadExamStatistics()
}

// 加载所有数据
const loadAllData = () => {
  loadOverview()
  loadTrend()
  loadKnowledgeAnalysis()
  loadExamStatistics()
}

onMounted(() => {
  loadAllData()
})
</script>


<style scoped>
.statistics-container {
  min-height: 100vh;
  background: transparent;
  padding-bottom: 40px;
}

/* 顶部横幅 */
.page-banner {
  position: relative;
  padding: 40px 24px;
  background: linear-gradient(135deg, #0c1445 0%, #1a0a2e 50%, #16213e 100%);
  overflow: hidden;
}

.banner-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: 
    radial-gradient(2px 2px at 10% 20%, rgba(255, 255, 255, 0.9) 50%, transparent 50%),
    radial-gradient(2px 2px at 30% 60%, rgba(255, 255, 255, 0.7) 50%, transparent 50%),
    radial-gradient(2px 2px at 50% 30%, rgba(255, 255, 255, 0.8) 50%, transparent 50%),
    radial-gradient(2px 2px at 70% 80%, rgba(255, 255, 255, 0.6) 50%, transparent 50%),
    radial-gradient(2px 2px at 90% 40%, rgba(255, 255, 255, 0.9) 50%, transparent 50%),
    radial-gradient(1px 1px at 15% 45%, rgba(255, 255, 255, 0.6) 50%, transparent 50%),
    radial-gradient(1px 1px at 35% 85%, rgba(255, 255, 255, 0.5) 50%, transparent 50%),
    radial-gradient(1px 1px at 55% 15%, rgba(255, 255, 255, 0.7) 50%, transparent 50%),
    radial-gradient(1px 1px at 75% 55%, rgba(255, 255, 255, 0.6) 50%, transparent 50%),
    radial-gradient(1px 1px at 85% 25%, rgba(255, 255, 255, 0.8) 50%, transparent 50%),
    radial-gradient(3px 3px at 25% 50%, rgba(255, 255, 255, 1) 50%, transparent 50%),
    radial-gradient(3px 3px at 65% 20%, rgba(255, 255, 255, 0.9) 50%, transparent 50%),
    radial-gradient(ellipse at 20% 80%, rgba(14, 165, 233, 0.3) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 30%, rgba(99, 102, 241, 0.25) 0%, transparent 50%);
  animation: banner-stars 5s ease-in-out infinite;
}

@keyframes banner-stars {
  0%, 100% { opacity: 0.7; }
  50% { opacity: 1; }
}

.banner-content {
  position: relative;
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.banner-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.banner-icon {
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  backdrop-filter: blur(10px);
}

.banner-text h1 {
  margin: 0 0 8px 0;
  font-size: 32px;
  font-weight: 700;
  color: white;
}

.banner-text p {
  margin: 0;
  font-size: 16px;
  color: rgba(255, 255, 255, 0.9);
}

.date-picker-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(255, 255, 255, 0.15);
  padding: 8px 16px;
  border-radius: 12px;
  backdrop-filter: blur(10px);
  color: white;
}

.date-picker-wrapper :deep(.el-date-editor) {
  --el-date-editor-width: 260px;
}

.date-picker-wrapper :deep(.el-input__wrapper) {
  background: transparent;
  box-shadow: none;
}

.date-picker-wrapper :deep(.el-input__inner) {
  color: white;
}

.date-picker-wrapper :deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.7);
}

/* 区块通用样式 */
.overview-section,
.trend-section,
.knowledge-section,
.exam-section {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
}

.overview-section {
  margin-top: -30px;
  position: relative;
  z-index: 10;
}

.trend-section,
.knowledge-section,
.exam-section {
  margin-top: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
  color: white;
}

.section-title .el-icon {
  color: #818cf8;
}

.section-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

/* 学习概览卡片 */
.overview-cards {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
}

.overview-card {
  position: relative;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  padding: 24px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  overflow: hidden;
  transition: all 0.3s ease;
}

.overview-card:hover {
  transform: translateY(-4px);
  background: rgba(255, 255, 255, 0.15);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.25);
}

.card-decoration {
  position: absolute;
  top: -20px;
  right: -20px;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  opacity: 0.1;
}

.overview-card.practice .card-decoration { background: #409eff; }
.overview-card.correct .card-decoration { background: #67c23a; }
.overview-card.accuracy .card-decoration { background: #e6a23c; }
.overview-card.duration .card-decoration { background: #f56c6c; }
.overview-card.exams .card-decoration { background: #909399; }
.overview-card.days .card-decoration { background: #6366f1; }

.card-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.overview-card.practice .card-icon { background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%); }
.overview-card.correct .card-icon { background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%); }
.overview-card.accuracy .card-icon { background: linear-gradient(135deg, #e6a23c 0%, #ebb563 100%); }
.overview-card.duration .card-icon { background: linear-gradient(135deg, #f56c6c 0%, #f89898 100%); }
.overview-card.exams .card-icon { background: linear-gradient(135deg, #909399 0%, #b1b3b8 100%); }
.overview-card.days .card-icon { background: linear-gradient(135deg, #6366f1 0%, #818cf8 100%); }

.card-info {
  text-align: center;
}

.card-value {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: white;
  line-height: 1.2;
}

.card-value small {
  font-size: 16px;
  font-weight: 500;
}

.card-label {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
}

/* 学习趋势 */
.trend-tabs {
  display: flex;
  gap: 8px;
  background: rgba(255, 255, 255, 0.1);
  padding: 4px;
  border-radius: 10px;
}

.trend-tab {
  padding: 8px 16px;
  background: transparent;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  transition: all 0.3s ease;
}

.trend-tab:hover {
  color: white;
}

.trend-tab.active {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.trend-chart {
  margin-top: 20px;
}

/* 知识点分析 */
.knowledge-grid {
  display: grid;
  grid-template-columns: 1fr 1.2fr;
  gap: 24px;
}

.knowledge-radar-card,
.knowledge-table-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 16px;
  font-weight: 600;
  color: white;
}

.radar-wrapper {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.table-wrapper {
  max-height: 420px;
  overflow: auto;
}

.subject-tag {
  display: inline-block;
  padding: 2px 8px;
  background: #ecf5ff;
  color: #409eff;
  border-radius: 4px;
  font-size: 12px;
}

.count-value {
  font-weight: 600;
  color: #606266;
}

.count-value.correct {
  color: #67c23a;
}

.accuracy-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.accuracy-bar {
  flex: 1;
  height: 6px;
  background: #ebeef5;
  border-radius: 3px;
  overflow: hidden;
}

.accuracy-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.accuracy-fill.high { background: linear-gradient(90deg, #67c23a, #85ce61); }
.accuracy-fill.medium { background: linear-gradient(90deg, #e6a23c, #ebb563); }
.accuracy-fill.low { background: linear-gradient(90deg, #f56c6c, #f89898); }

.accuracy-text {
  font-size: 12px;
  font-weight: 600;
  min-width: 36px;
}

.accuracy-text.high { color: #67c23a; }
.accuracy-text.medium { color: #e6a23c; }
.accuracy-text.low { color: #f56c6c; }

.weak-badge {
  display: inline-block;
  padding: 2px 8px;
  background: linear-gradient(135deg, #fef0f0, #fde2e2);
  color: #f56c6c;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
}

.normal-badge {
  color: #c0c4cc;
  font-size: 12px;
}

:deep(.weak-row) {
  background: #fef0f0 !important;
}

/* 考试统计 */
.exam-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  padding: 20px 0;
}

.exam-stat-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.stat-ring {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.stat-ring::before {
  content: '';
  position: absolute;
  inset: 4px;
  border-radius: 50%;
  background: white;
}

.stat-ring.total { background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%); }
.stat-ring.average { background: linear-gradient(135deg, #67c23a 0%, #85ce61 100%); }
.stat-ring.highest { background: linear-gradient(135deg, #e6a23c 0%, #ebb563 100%); }
.stat-ring.accuracy { background: linear-gradient(135deg, #6366f1 0%, #818cf8 100%); }

.ring-value {
  position: relative;
  z-index: 1;
  font-size: 28px;
  font-weight: 700;
  color: white;
}

.ring-value small {
  font-size: 14px;
}

.stat-ring::before {
  background: rgba(30, 30, 50, 0.9) !important;
}

.exam-stat-card .stat-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: rgba(255, 255, 255, 0.5);
}

.empty-state p {
  margin: 16px 0 0;
  font-size: 14px;
}

/* 表格玻璃效果 */
.table-wrapper :deep(.el-table) {
  background: transparent !important;
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: rgba(255, 255, 255, 0.05);
  --el-table-row-hover-bg-color: rgba(255, 255, 255, 0.1);
  --el-table-border-color: rgba(255, 255, 255, 0.1);
  --el-table-text-color: rgba(255, 255, 255, 0.9);
  --el-table-header-text-color: rgba(255, 255, 255, 0.9);
}

.table-wrapper :deep(.el-table th.el-table__cell) {
  background: rgba(255, 255, 255, 0.05) !important;
}

.table-wrapper :deep(.el-table td.el-table__cell) {
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.table-wrapper :deep(.weak-row) {
  background: rgba(245, 108, 108, 0.15) !important;
}

.count-value {
  color: rgba(255, 255, 255, 0.9) !important;
}

.subject-tag {
  background: rgba(64, 158, 255, 0.2) !important;
  color: #60a5fa !important;
}

/* 响应式 */
@media (max-width: 1200px) {
  .overview-cards {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .knowledge-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .page-banner {
    padding: 24px 16px;
  }
  
  .banner-content {
    flex-direction: column;
    gap: 20px;
  }
  
  .banner-left {
    flex-direction: column;
    text-align: center;
  }
  
  .overview-section,
  .trend-section,
  .knowledge-section,
  .exam-section {
    padding: 0 16px;
  }
  
  .overview-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .section-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .exam-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
