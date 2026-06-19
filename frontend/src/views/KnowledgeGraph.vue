<template>
  <div class="knowledge-graph">
    <div class="graph-header">
      <Network class="header-icon" />
      <h1 class="gradient-text">知识点关系图谱</h1>
    </div>

    <!-- 筛选控制 -->
    <div class="graph-controls">
      <el-select v-model="filters.subject" placeholder="选择科目" clearable size="large" @change="loadGraphData">
        <el-option label="全部科目" value="" />
        <el-option label="Python" value="Python" />
        <el-option label="数据结构" value="数据结构" />
        <el-option label="算法" value="算法" />
      </el-select>
      
      <el-select v-model="filters.masteryRange" placeholder="掌握度筛选" clearable size="large" @change="applyMasteryFilter">
        <el-option label="全部" value="" />
        <el-option label="未掌握 (0-40%)" value="0-40" />
        <el-option label="部分掌握 (40-70%)" value="40-70" />
        <el-option label="已掌握 (70-100%)" value="70-100" />
      </el-select>
      
      <el-button type="primary" :icon="RefreshCw" @click="loadGraphData" size="large">
        刷新
      </el-button>
      
      <el-button :icon="Target" @click="showPathPanel = !showPathPanel" size="large">
        学习路径
      </el-button>
    </div>

    <div class="graph-container">
      <!-- 图谱画布 -->
      <div class="graph-canvas" :class="{ 'with-panel': showDetailPanel || showPathPanel }">
        <div v-if="loading" class="loading-state">
          <el-skeleton :rows="8" animated />
        </div>
        
        <div v-else-if="graphData.nodes.length === 0" class="empty-state">
          <Network class="empty-icon" />
          <p>暂无知识点数据</p>
        </div>
        
        <v-chart
          v-else
          ref="chartRef"
          :option="chartOption"
          autoresize
          @click="handleNodeClick"
        />
      </div>

      <!-- 知识点详情面板 -->
      <transition name="slide">
        <div v-if="showDetailPanel && selectedKnowledge" class="detail-panel">
          <div class="panel-header">
            <h3>{{ selectedKnowledge.name }}</h3>
            <X class="close-icon" @click="closeDetailPanel" />
          </div>
          
          <div class="panel-content">
            <!-- 掌握度 -->
            <div class="mastery-section">
              <div class="mastery-ring">
                <el-progress
                  type="circle"
                  :percentage="selectedKnowledge.mastery.mastery_score"
                  :width="120"
                  :stroke-width="12"
                  :color="getMasteryColor(selectedKnowledge.mastery.mastery_score)"
                />
              </div>
              <div class="mastery-stats">
                <div class="stat-item">
                  <span class="label">练习次数</span>
                  <span class="value">{{ selectedKnowledge.mastery.practice_count }}</span>
                </div>
                <div class="stat-item">
                  <span class="label">正确次数</span>
                  <span class="value">{{ selectedKnowledge.mastery.correct_count }}</span>
                </div>
                <div class="stat-item">
                  <span class="label">正确率</span>
                  <span class="value">{{ selectedKnowledge.mastery.correct_rate }}%</span>
                </div>
              </div>
            </div>

            <!-- 基本信息 -->
            <div class="info-section">
              <div class="info-item">
                <BookOpen class="info-icon" />
                <span>科目: {{ selectedKnowledge.subject }}</span>
              </div>
              <div class="info-item">
                <Layers class="info-icon" />
                <span>章节: {{ selectedKnowledge.chapter }}</span>
              </div>
              <div class="info-item">
                <BarChart class="info-icon" />
                <span>难度: {{ getDifficultyText(selectedKnowledge.difficulty) }}</span>
              </div>
              <div class="info-item">
                <FileText class="info-icon" />
                <span>题目数: {{ selectedKnowledge.questionCount }}</span>
              </div>
            </div>

            <!-- 前置知识点 -->
            <div v-if="selectedKnowledge.prerequisites.length > 0" class="relation-section">
              <h4><ArrowLeft class="section-icon" />前置知识点</h4>
              <div class="relation-list">
                <div
                  v-for="kp in selectedKnowledge.prerequisites"
                  :key="kp.id"
                  class="relation-item"
                  @click="loadKnowledgeDetail(kp.id)"
                >
                  <span class="relation-name">{{ kp.name }}</span>
                  <span class="relation-mastery" :style="{ color: getMasteryColor(kp.mastery) }">
                    {{ kp.mastery }}%
                  </span>
                </div>
              </div>
            </div>

            <!-- 后续知识点 -->
            <div v-if="selectedKnowledge.nextPoints.length > 0" class="relation-section">
              <h4><ArrowRight class="section-icon" />后续知识点</h4>
              <div class="relation-list">
                <div
                  v-for="kp in selectedKnowledge.nextPoints"
                  :key="kp.id"
                  class="relation-item"
                  @click="loadKnowledgeDetail(kp.id)"
                >
                  <span class="relation-name">{{ kp.name }}</span>
                  <span class="relation-mastery" :style="{ color: getMasteryColor(kp.mastery) }">
                    {{ kp.mastery }}%
                  </span>
                </div>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="action-buttons">
              <el-button type="primary" :icon="Play" @click="startPractice">
                开始练习
              </el-button>
            </div>
          </div>
        </div>
      </transition>

      <!-- 学习路径面板 -->
      <transition name="slide">
        <div v-if="showPathPanel" class="path-panel">
          <div class="panel-header">
            <h3>推荐学习路径</h3>
            <X class="close-icon" @click="showPathPanel = false" />
          </div>
          
          <div class="panel-content">
            <div v-if="loadingPath" class="loading-state">
              <el-skeleton :rows="5" animated />
            </div>
            
            <div v-else class="path-list">
              <div
                v-for="(item, index) in learningPath"
                :key="item.id"
                class="path-item"
                @click="loadKnowledgeDetail(item.id)"
              >
                <div class="path-index">{{ index + 1 }}</div>
                <div class="path-content">
                  <div class="path-name">{{ item.name }}</div>
                  <div class="path-reason">{{ item.reason }}</div>
                  <div class="path-meta">
                    <span class="path-subject">{{ item.subject }}</span>
                    <span class="path-mastery" :style="{ color: getMasteryColor(item.mastery) }">
                      掌握度: {{ item.mastery }}%
                    </span>
                  </div>
                </div>
                <ChevronRight class="path-arrow" />
              </div>
            </div>
          </div>
        </div>
      </transition>
    </div>

    <!-- 图例 -->
    <div class="graph-legend">
      <div class="legend-item">
        <div class="legend-color" style="background: #f56c6c"></div>
        <span>未掌握 (0-40%)</span>
      </div>
      <div class="legend-item">
        <div class="legend-color" style="background: #e6a23c"></div>
        <span>部分掌握 (40-70%)</span>
      </div>
      <div class="legend-item">
        <div class="legend-color" style="background: #67c23a"></div>
        <span>已掌握 (70-100%)</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  Network, RefreshCw, Target, X, BookOpen, Layers, BarChart, FileText,
  ArrowLeft, ArrowRight, Play, ChevronRight
} from 'lucide-vue-next'
import { ElMessage } from 'element-plus'
import { getGraphData, getKnowledgeDetail, getLearningPath } from '@/api/knowledgeGraph'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { GraphChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { useRouter } from 'vue-router'

use([CanvasRenderer, GraphChart, TooltipComponent, LegendComponent])

const router = useRouter()

// 状态
const loading = ref(false)
const loadingPath = ref(false)
const graphData = ref({ nodes: [], edges: [], categories: [] })
const selectedKnowledge = ref(null)
const learningPath = ref([])
const showDetailPanel = ref(false)
const showPathPanel = ref(false)
const chartRef = ref(null)

// 筛选条件
const filters = ref({
  subject: '',
  chapter: '',
  masteryRange: ''
})

// 图表配置
const chartOption = computed(() => {
  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        if (params.dataType === 'node') {
          const data = params.data
          return `
            <div style="padding: 8px;">
              <div style="font-weight: bold; margin-bottom: 4px;">${data.name}</div>
              <div>掌握度: ${data.mastery}%</div>
              <div>练习次数: ${data.practiceCount}</div>
              <div>正确率: ${data.correctRate}%</div>
            </div>
          `
        }
        return ''
      },
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      borderColor: 'rgba(255, 255, 255, 0.2)',
      textStyle: { color: '#fff' }
    },
    legend: {
      show: false
    },
    series: [
      {
        type: 'graph',
        layout: 'force',
        data: graphData.value.nodes,
        links: graphData.value.edges,
        categories: graphData.value.categories,
        roam: true,
        label: {
          show: true,
          position: 'bottom',
          formatter: '{b}',
          color: '#fff',
          fontSize: 12
        },
        labelLayout: {
          hideOverlap: true
        },
        emphasis: {
          focus: 'adjacency',
          label: {
            fontSize: 14,
            fontWeight: 'bold'
          },
          lineStyle: {
            width: 4
          }
        },
        force: {
          repulsion: 200,
          gravity: 0.1,
          edgeLength: 150,
          layoutAnimation: true
        },
        itemStyle: {
          borderColor: 'rgba(255, 255, 255, 0.3)',
          borderWidth: 2
        },
        lineStyle: {
          color: 'source',
          curveness: 0.2,
          opacity: 0.6
        },
        symbolSize: (value, params) => {
          return Math.max(30, params.data.value / 2 + 20)
        }
      }
    ]
  }
})

// 加载图谱数据
const loadGraphData = async () => {
  loading.value = true
  try {
    const params = {
      subject: filters.value.subject || undefined
    }
    
    // 应用掌握度筛选
    if (filters.value.masteryRange) {
      const [min, max] = filters.value.masteryRange.split('-').map(Number)
      params.min_mastery = min
      params.max_mastery = max
    }
    
    const response = await getGraphData(params)
    if (response.data.success) {
      graphData.value = response.data.data
      
      // 为节点添加颜色
      graphData.value.nodes.forEach(node => {
        node.itemStyle = {
          color: getMasteryColor(node.mastery)
        }
      })
    }
  } catch (error) {
    console.error('加载图谱数据失败:', error)
    ElMessage.error('加载图谱数据失败')
  } finally {
    loading.value = false
  }
}

// 加载知识点详情
const loadKnowledgeDetail = async (knowledgeId) => {
  try {
    const response = await getKnowledgeDetail(knowledgeId)
    if (response.data.success) {
      selectedKnowledge.value = response.data.data
      showDetailPanel.value = true
      showPathPanel.value = false
    }
  } catch (error) {
    console.error('加载知识点详情失败:', error)
    ElMessage.error('加载知识点详情失败')
  }
}

// 加载学习路径
const loadLearningPath = async () => {
  loadingPath.value = true
  try {
    const params = {
      subject: filters.value.subject || undefined
    }
    
    const response = await getLearningPath(params)
    if (response.data.success) {
      learningPath.value = response.data.data
    }
  } catch (error) {
    console.error('加载学习路径失败:', error)
    ElMessage.error('加载学习路径失败')
  } finally {
    loadingPath.value = false
  }
}

// 处理节点点击
const handleNodeClick = (params) => {
  if (params.dataType === 'node') {
    const nodeId = params.data.id.replace('kp_', '')
    loadKnowledgeDetail(parseInt(nodeId))
  }
}

// 关闭详情面板
const closeDetailPanel = () => {
  showDetailPanel.value = false
  selectedKnowledge.value = null
}

// 应用掌握度筛选
const applyMasteryFilter = () => {
  loadGraphData()
}

// 开始练习
const startPractice = () => {
  if (selectedKnowledge.value) {
    router.push({
      name: 'practice',
      query: { knowledge_point_id: selectedKnowledge.value.id }
    })
  }
}

// 获取掌握度颜色
const getMasteryColor = (mastery) => {
  if (mastery < 40) return '#f56c6c'
  if (mastery < 70) return '#e6a23c'
  return '#67c23a'
}

// 获取难度文本
const getDifficultyText = (difficulty) => {
  const map = {
    'easy': '简单',
    'medium': '中等',
    'hard': '困难'
  }
  return map[difficulty] || difficulty
}

onMounted(() => {
  loadGraphData()
  loadLearningPath()
})
</script>

<style scoped>
.knowledge-graph {
  padding: 20px;
  max-width: 1600px;
  margin: 0 auto;
}

.graph-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-bottom: 32px;
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

.graph-controls {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
}

.graph-controls :deep(.el-select) {
  flex: 1;
  max-width: 200px;
}

.graph-container {
  display: flex;
  gap: 24px;
  margin-bottom: 24px;
}

.graph-canvas {
  flex: 1;
  height: 700px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 20px;
  transition: all 0.3s ease;
}

.graph-canvas.with-panel {
  flex: 0 0 calc(100% - 424px);
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: rgba(255, 255, 255, 0.6);
}

.empty-icon {
  width: 64px;
  height: 64px;
  margin-bottom: 16px;
  opacity: 0.3;
}

.detail-panel,
.path-panel {
  width: 400px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.panel-header h3 {
  margin: 0;
  color: white;
  font-size: 18px;
}

.close-icon {
  width: 24px;
  height: 24px;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  transition: all 0.3s ease;
}

.close-icon:hover {
  color: white;
  transform: rotate(90deg);
}

.panel-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.mastery-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  margin-bottom: 24px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
}

.mastery-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  width: 100%;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-item .label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.stat-item .value {
  font-size: 18px;
  font-weight: 600;
  color: white;
}

.info-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 24px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
}

.info-icon {
  width: 18px;
  height: 18px;
  color: #409eff;
}

.relation-section {
  margin-bottom: 24px;
}

.relation-section h4 {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 12px 0;
  color: white;
  font-size: 16px;
}

.section-icon {
  width: 20px;
  height: 20px;
  color: #409eff;
}

.relation-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.relation-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.relation-item:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateX(4px);
}

.relation-name {
  color: rgba(255, 255, 255, 0.9);
  font-size: 14px;
}

.relation-mastery {
  font-weight: 600;
  font-size: 14px;
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.action-buttons .el-button {
  flex: 1;
}

.path-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.path-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.path-item:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateX(4px);
}

.path-index {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  border-radius: 50%;
  color: white;
  font-weight: 600;
  font-size: 14px;
  flex-shrink: 0;
}

.path-content {
  flex: 1;
}

.path-name {
  color: white;
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 4px;
}

.path-reason {
  color: rgba(255, 255, 255, 0.6);
  font-size: 12px;
  margin-bottom: 8px;
}

.path-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
}

.path-subject {
  color: rgba(255, 255, 255, 0.7);
}

.path-mastery {
  font-weight: 600;
}

.path-arrow {
  width: 20px;
  height: 20px;
  color: rgba(255, 255, 255, 0.4);
  flex-shrink: 0;
}

.graph-legend {
  display: flex;
  justify-content: center;
  gap: 24px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 50%;
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from {
  transform: translateX(100%);
  opacity: 0;
}

.slide-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

@media (max-width: 1200px) {
  .graph-canvas.with-panel {
    flex: 1;
  }
  
  .detail-panel,
  .path-panel {
    position: fixed;
    right: 0;
    top: 0;
    bottom: 0;
    z-index: 1000;
  }
}
</style>
