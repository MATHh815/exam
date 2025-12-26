<template>
  <div class="ai-analysis-container">
    <!-- 顶部横幅 -->
    <div class="page-banner">
      <div class="banner-bg"></div>
      <div class="banner-content">
        <div class="banner-icon">
          <el-icon :size="48"><MagicStick /></el-icon>
        </div>
        <div class="banner-text">
          <h1>AI 智能分析</h1>
          <p>基于你的学习数据，AI 为你提供个性化的知识点分析和学习建议</p>
        </div>
        <div class="banner-action">
          <button class="btn-analyze" @click="startAnalysis" :disabled="analyzing">
            <el-icon v-if="!analyzing"><Cpu /></el-icon>
            <el-icon v-else class="is-loading"><Loading /></el-icon>
            <span>{{ analyzing ? '分析中...' : '开始分析' }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 分析状态 -->
    <div v-if="analyzing" class="analyzing-section">
      <div class="analyzing-card">
        <div class="analyzing-animation">
          <div class="pulse-ring"></div>
          <div class="pulse-ring delay-1"></div>
          <div class="pulse-ring delay-2"></div>
          <el-icon :size="48" class="ai-icon"><Cpu /></el-icon>
        </div>
        <h3>AI 正在分析你的学习数据...</h3>
        <p>{{ analyzeStatus }}</p>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: analyzeProgress + '%' }"></div>
        </div>
      </div>
    </div>

    <!-- 分析结果 -->
    <div v-else-if="analysisResult" class="analysis-results">
      <!-- 综合评分 -->
      <div class="score-section">
        <div class="score-card">
          <div class="score-ring" :class="getScoreLevel(analysisResult.overallScore)">
            <svg viewBox="0 0 100 100">
              <circle class="bg" cx="50" cy="50" r="45" />
              <circle 
                class="progress" 
                cx="50" cy="50" r="45"
                :stroke-dasharray="283"
                :stroke-dashoffset="283 - (283 * analysisResult.overallScore / 100)"
              />
            </svg>
            <div class="score-value">
              <span class="number">{{ analysisResult.overallScore }}</span>
              <span class="label">综合评分</span>
            </div>
          </div>
          <div class="score-details">
            <div class="detail-item">
              <span class="detail-label">学习活跃度</span>
              <div class="detail-bar">
                <div class="bar-fill" :style="{ width: analysisResult.activityScore + '%' }"></div>
              </div>
              <span class="detail-value">{{ analysisResult.activityScore }}%</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">知识掌握度</span>
              <div class="detail-bar">
                <div class="bar-fill" :style="{ width: analysisResult.masteryScore + '%' }"></div>
              </div>
              <span class="detail-value">{{ analysisResult.masteryScore }}%</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">学习效率</span>
              <div class="detail-bar">
                <div class="bar-fill" :style="{ width: analysisResult.efficiencyScore + '%' }"></div>
              </div>
              <span class="detail-value">{{ analysisResult.efficiencyScore }}%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 优势与薄弱点 -->
      <div class="strengths-weaknesses">
        <!-- 优势知识点 -->
        <div class="analysis-card strengths">
          <div class="card-header">
            <div class="header-icon success">
              <el-icon :size="24"><TrophyBase /></el-icon>
            </div>
            <div class="header-text">
              <h3>优势知识点</h3>
              <p>你在这些领域表现出色</p>
            </div>
          </div>
          <div class="knowledge-list">
            <div 
              v-for="(item, index) in analysisResult.strengths" 
              :key="'strength-' + index"
              class="knowledge-item"
              :style="{ animationDelay: index * 0.1 + 's' }"
            >
              <div class="item-rank success">{{ index + 1 }}</div>
              <div class="item-content">
                <div class="item-header">
                  <span class="item-name">{{ item.name }}</span>
                  <span class="item-score success">{{ item.accuracy }}%</span>
                </div>
                <div class="item-bar">
                  <div class="bar-fill success" :style="{ width: item.accuracy + '%' }"></div>
                </div>
                <div class="item-meta">
                  <span>{{ item.subject }}</span>
                  <span>答题 {{ item.totalCount }} 次</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 薄弱知识点 -->
        <div class="analysis-card weaknesses">
          <div class="card-header">
            <div class="header-icon danger">
              <el-icon :size="24"><Warning /></el-icon>
            </div>
            <div class="header-text">
              <h3>薄弱知识点</h3>
              <p>建议重点加强这些领域</p>
            </div>
          </div>
          <div class="knowledge-list">
            <div 
              v-for="(item, index) in analysisResult.weaknesses" 
              :key="'weakness-' + index"
              class="knowledge-item"
              :style="{ animationDelay: index * 0.1 + 's' }"
            >
              <div class="item-rank danger">{{ index + 1 }}</div>
              <div class="item-content">
                <div class="item-header">
                  <span class="item-name">{{ item.name }}</span>
                  <span class="item-score danger">{{ item.accuracy }}%</span>
                </div>
                <div class="item-bar">
                  <div class="bar-fill danger" :style="{ width: item.accuracy + '%' }"></div>
                </div>
                <div class="item-meta">
                  <span>{{ item.subject }}</span>
                  <span>错误 {{ item.wrongCount }} 次</span>
                </div>
              </div>
              <button class="btn-practice" @click="practiceWeakness(item)">
                <el-icon><VideoPlay /></el-icon>
                强化练习
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- AI 学习建议 -->
      <div class="recommendations-section">
        <div class="section-header">
          <div class="section-title">
            <el-icon><ChatDotRound /></el-icon>
            <span>AI 学习建议</span>
          </div>
        </div>
        <div class="recommendations-grid">
          <div 
            v-for="(rec, index) in analysisResult.recommendations" 
            :key="'rec-' + index"
            class="recommendation-card"
            :style="{ animationDelay: index * 0.15 + 's' }"
          >
            <div class="rec-icon" :class="rec.type">
              <el-icon :size="28">
                <component :is="getRecIcon(rec.type)" />
              </el-icon>
            </div>
            <div class="rec-content">
              <h4>{{ rec.title }}</h4>
              <p>{{ rec.description }}</p>
            </div>
            <div class="rec-action" v-if="rec.action">
              <button class="btn-action" @click="handleRecAction(rec)">
                {{ rec.actionText }}
                <el-icon><ArrowRight /></el-icon>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 学习计划 -->
      <div class="study-plan-section">
        <div class="section-header">
          <div class="section-title">
            <el-icon><Calendar /></el-icon>
            <span>个性化学习计划</span>
          </div>
          <button class="btn-regenerate" @click="regeneratePlan">
            <el-icon><Refresh /></el-icon>
            重新生成
          </button>
        </div>
        <div class="plan-timeline">
          <div 
            v-for="(day, index) in analysisResult.studyPlan" 
            :key="'day-' + index"
            class="plan-day"
            :style="{ animationDelay: index * 0.1 + 's' }"
          >
            <div class="day-marker">
              <div class="marker-dot"></div>
              <div class="marker-line" v-if="index < analysisResult.studyPlan.length - 1"></div>
            </div>
            <div class="day-content">
              <div class="day-header">
                <span class="day-label">{{ day.dayLabel }}</span>
                <span class="day-date">{{ day.date }}</span>
              </div>
              <div class="day-tasks">
                <div v-for="(task, tIndex) in day.tasks" :key="'task-' + tIndex" class="task-item">
                  <el-icon class="task-icon"><CircleCheck /></el-icon>
                  <span class="task-text">{{ task }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <div class="empty-icon">
        <el-icon :size="80"><DataAnalysis /></el-icon>
      </div>
      <h3>开始你的 AI 智能分析</h3>
      <p>点击上方"开始分析"按钮，AI 将根据你的学习数据生成个性化分析报告</p>
      <div class="feature-list">
        <div class="feature-item">
          <el-icon><TrophyBase /></el-icon>
          <span>识别优势知识点</span>
        </div>
        <div class="feature-item">
          <el-icon><Warning /></el-icon>
          <span>发现薄弱环节</span>
        </div>
        <div class="feature-item">
          <el-icon><ChatDotRound /></el-icon>
          <span>获取学习建议</span>
        </div>
        <div class="feature-item">
          <el-icon><Calendar /></el-icon>
          <span>生成学习计划</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, markRaw } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  MagicStick, Cpu, Loading, TrophyBase, Warning, ChatDotRound,
  Calendar, Refresh, ArrowRight, CircleCheck, DataAnalysis,
  VideoPlay, Clock, Aim, Reading, EditPen, TrendCharts
} from '@element-plus/icons-vue'
import { getAIAnalysis, generateStudyPlan } from '../api/ai'

const router = useRouter()

// 是否使用真实API（后端准备好后改为true）
const USE_REAL_API = false

// 分析状态
const analyzing = ref(false)
const analyzeStatus = ref('')
const analyzeProgress = ref(0)
const analysisResult = ref(null)

// 获取评分等级
function getScoreLevel(score) {
  if (score >= 80) return 'excellent'
  if (score >= 60) return 'good'
  return 'poor'
}

// 获取建议图标
function getRecIcon(type) {
  const icons = {
    practice: markRaw(EditPen),
    review: markRaw(Reading),
    focus: markRaw(Aim),
    schedule: markRaw(Clock),
    trend: markRaw(TrendCharts)
  }
  return icons[type] || markRaw(ChatDotRound)
}

// 开始分析
async function startAnalysis() {
  analyzing.value = true
  analyzeProgress.value = 0
  
  // 模拟分析过程
  const steps = [
    { status: '正在收集学习数据...', progress: 20 },
    { status: '分析答题记录...', progress: 40 },
    { status: '识别知识点掌握情况...', progress: 60 },
    { status: '生成个性化建议...', progress: 80 },
    { status: '完成分析报告...', progress: 100 }
  ]
  
  for (const step of steps) {
    analyzeStatus.value = step.status
    analyzeProgress.value = step.progress
    await new Promise(resolve => setTimeout(resolve, 800))
  }
  
  // 获取分析数据
  if (USE_REAL_API) {
    try {
      const response = await getAIAnalysis({ days: 30 })
      analysisResult.value = response.data
      ElMessage.success('分析完成！')
    } catch (error) {
      console.error('AI分析失败:', error)
      ElMessage.error('分析失败，请稍后重试')
    }
  } else {
    // 使用模拟数据
    analysisResult.value = generateMockData()
    ElMessage.success('分析完成！')
  }
  analyzing.value = false
}

// 生成模拟数据
function generateMockData() {
  return {
    overallScore: 72,
    activityScore: 85,
    masteryScore: 68,
    efficiencyScore: 75,
    strengths: [
      { name: '言语理解与表达', subject: '行测', accuracy: 92, totalCount: 156 },
      { name: '资料分析', subject: '行测', accuracy: 88, totalCount: 98 },
      { name: '常识判断', subject: '行测', accuracy: 85, totalCount: 124 },
      { name: '政治理论', subject: '申论', accuracy: 82, totalCount: 67 },
      { name: '时事政治', subject: '公共基础', accuracy: 80, totalCount: 89 }
    ],
    weaknesses: [
      { name: '数量关系', subject: '行测', accuracy: 45, wrongCount: 67 },
      { name: '判断推理-图形推理', subject: '行测', accuracy: 52, wrongCount: 48 },
      { name: '逻辑判断', subject: '行测', accuracy: 55, wrongCount: 42 },
      { name: '申论写作', subject: '申论', accuracy: 58, wrongCount: 35 },
      { name: '法律基础', subject: '公共基础', accuracy: 60, wrongCount: 28 }
    ],
    recommendations: [
      {
        type: 'practice',
        title: '重点突破数量关系',
        description: '你的数量关系正确率仅为45%，建议每天练习20道数量关系题目，重点掌握工程问题和行程问题。',
        action: 'practice',
        actionText: '开始练习'
      },
      {
        type: 'review',
        title: '复习图形推理技巧',
        description: '图形推理是你的薄弱项，建议系统学习图形推理的六大规律：位置、样式、属性、数量、特殊、空间。',
        action: 'review',
        actionText: '查看技巧'
      },
      {
        type: 'focus',
        title: '保持言语理解优势',
        description: '言语理解是你的强项，继续保持每日阅读习惯，可以适当减少练习量，把时间分配给薄弱科目。',
        action: null,
        actionText: ''
      },
      {
        type: 'schedule',
        title: '优化学习时间分配',
        description: '建议将60%的学习时间用于薄弱知识点，30%用于巩固中等水平知识点，10%用于保持优势。',
        action: 'schedule',
        actionText: '查看计划'
      }
    ],
    studyPlan: [
      {
        dayLabel: '今天',
        date: formatDate(0),
        tasks: [
          '数量关系专项练习 - 工程问题 (30题)',
          '图形推理基础规律学习 (1小时)',
          '错题本复习 (20分钟)'
        ]
      },
      {
        dayLabel: '明天',
        date: formatDate(1),
        tasks: [
          '数量关系专项练习 - 行程问题 (30题)',
          '图形推理练习 - 位置变化 (20题)',
          '言语理解保持练习 (15题)'
        ]
      },
      {
        dayLabel: '后天',
        date: formatDate(2),
        tasks: [
          '逻辑判断专项练习 (25题)',
          '图形推理练习 - 样式变化 (20题)',
          '模拟考试 - 行测半套 (60分钟)'
        ]
      },
      {
        dayLabel: '第4天',
        date: formatDate(3),
        tasks: [
          '数量关系综合练习 (25题)',
          '申论写作技巧学习 (1小时)',
          '错题本复习 (30分钟)'
        ]
      },
      {
        dayLabel: '第5天',
        date: formatDate(4),
        tasks: [
          '法律基础知识学习 (1小时)',
          '判断推理综合练习 (30题)',
          '周测试 - 完整模拟考试'
        ]
      }
    ]
  }
}

// 格式化日期
function formatDate(daysFromNow) {
  const date = new Date()
  date.setDate(date.getDate() + daysFromNow)
  return `${date.getMonth() + 1}月${date.getDate()}日`
}

// 练习薄弱知识点
function practiceWeakness(item) {
  ElMessage.info(`即将开始 ${item.name} 专项练习`)
  router.push({
    path: '/practice',
    query: { subject: item.subject, chapter: item.name }
  })
}

// 处理建议操作
function handleRecAction(rec) {
  switch (rec.action) {
    case 'practice':
      router.push('/practice')
      break
    case 'review':
      ElMessage.info('学习技巧功能开发中...')
      break
    case 'schedule':
      // 滚动到学习计划部分
      document.querySelector('.study-plan-section')?.scrollIntoView({ behavior: 'smooth' })
      break
    default:
      break
  }
}

// 重新生成学习计划
async function regeneratePlan() {
  ElMessage.info('正在重新生成学习计划...')
  
  if (USE_REAL_API) {
    try {
      const response = await generateStudyPlan({
        weaknesses: analysisResult.value?.weaknesses || [],
        days: 5
      })
      if (analysisResult.value) {
        analysisResult.value.studyPlan = response.data.studyPlan
      }
      ElMessage.success('学习计划已更新')
    } catch (error) {
      console.error('生成学习计划失败:', error)
      ElMessage.error('生成失败，请稍后重试')
    }
  } else {
    // 模拟重新生成
    setTimeout(() => {
      if (analysisResult.value) {
        // 随机调整任务顺序模拟重新生成
        analysisResult.value.studyPlan = analysisResult.value.studyPlan.map(day => ({
          ...day,
          tasks: [...day.tasks].sort(() => Math.random() - 0.5)
        }))
      }
      ElMessage.success('学习计划已更新')
    }, 1000)
  }
}
</script>


<style scoped>
.ai-analysis-container {
  min-height: 100vh;
  background: transparent;
  padding-bottom: 40px;
}

/* 顶部横幅 */
.page-banner {
  position: relative;
  padding: 40px 24px;
  background: linear-gradient(135deg, #1a0a2e 0%, #2d1b4e 50%, #0f0c29 100%);
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
    radial-gradient(ellipse at 20% 80%, rgba(139, 92, 246, 0.4) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 30%, rgba(59, 130, 246, 0.3) 0%, transparent 50%);
  animation: banner-stars 5s ease-in-out infinite;
}

@keyframes banner-stars {
  0%, 100% { opacity: 0.7; }
  50% { opacity: 1; }
}

.banner-content {
  position: relative;
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 24px;
}

.banner-icon {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.3) 0%, rgba(59, 130, 246, 0.3) 100%);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.banner-text {
  flex: 1;
}

.banner-text h1 {
  margin: 0 0 8px 0;
  font-size: 32px;
  font-weight: 700;
  color: white;
  background: linear-gradient(90deg, #fff 0%, #a78bfa 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.banner-text p {
  margin: 0;
  font-size: 16px;
  color: rgba(255, 255, 255, 0.9);
}

.btn-analyze {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 32px;
  background: linear-gradient(135deg, #8b5cf6 0%, #3b82f6 100%);
  color: white;
  border: none;
  border-radius: 14px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(139, 92, 246, 0.4);
}

.btn-analyze:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 25px rgba(139, 92, 246, 0.5);
}

.btn-analyze:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* 分析中状态 */
.analyzing-section {
  max-width: 600px;
  margin: 60px auto;
  padding: 0 24px;
}

.analyzing-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 24px;
  padding: 48px;
  text-align: center;
}

.analyzing-animation {
  position: relative;
  width: 120px;
  height: 120px;
  margin: 0 auto 32px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pulse-ring {
  position: absolute;
  width: 100%;
  height: 100%;
  border: 2px solid rgba(139, 92, 246, 0.5);
  border-radius: 50%;
  animation: pulse-ring 2s ease-out infinite;
}

.pulse-ring.delay-1 { animation-delay: 0.5s; }
.pulse-ring.delay-2 { animation-delay: 1s; }

@keyframes pulse-ring {
  0% { transform: scale(0.8); opacity: 1; }
  100% { transform: scale(1.5); opacity: 0; }
}

.ai-icon {
  color: #a78bfa;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.analyzing-card h3 {
  margin: 0 0 12px 0;
  font-size: 20px;
  color: white;
}

.analyzing-card p {
  margin: 0 0 24px 0;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

.analyzing-section .progress-bar {
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
}

.analyzing-section .progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #8b5cf6 0%, #3b82f6 100%);
  border-radius: 4px;
  transition: width 0.5s ease;
}

/* 分析结果 */
.analysis-results {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px;
}

/* 综合评分 */
.score-section {
  margin-bottom: 32px;
}

.score-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 24px;
  padding: 32px;
  display: flex;
  align-items: center;
  gap: 48px;
}

.score-ring {
  position: relative;
  width: 180px;
  height: 180px;
  flex-shrink: 0;
}

.score-ring svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.score-ring circle {
  fill: none;
  stroke-width: 8;
  stroke-linecap: round;
}

.score-ring circle.bg {
  stroke: rgba(255, 255, 255, 0.1);
}

.score-ring circle.progress {
  transition: stroke-dashoffset 1s ease;
}

.score-ring.excellent circle.progress { stroke: url(#gradient-excellent); }
.score-ring.good circle.progress { stroke: url(#gradient-good); }
.score-ring.poor circle.progress { stroke: url(#gradient-poor); }

.score-ring.excellent circle.progress { stroke: #10b981; }
.score-ring.good circle.progress { stroke: #f59e0b; }
.score-ring.poor circle.progress { stroke: #ef4444; }

.score-value {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.score-value .number {
  display: block;
  font-size: 48px;
  font-weight: 700;
  color: white;
  line-height: 1;
}

.score-value .label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

.score-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.detail-label {
  width: 100px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.8);
}

.detail-bar {
  flex: 1;
  height: 10px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 5px;
  overflow: hidden;
}

.detail-bar .bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #8b5cf6 0%, #3b82f6 100%);
  border-radius: 5px;
  transition: width 1s ease;
}

.detail-value {
  width: 50px;
  text-align: right;
  font-size: 14px;
  font-weight: 600;
  color: white;
}

/* 优势与薄弱点 */
.strengths-weaknesses {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  margin-bottom: 32px;
}

.analysis-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 24px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.header-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.header-icon.success {
  background: linear-gradient(135deg, #10b981 0%, #34d399 100%);
}

.header-icon.danger {
  background: linear-gradient(135deg, #ef4444 0%, #f87171 100%);
}

.header-text h3 {
  margin: 0 0 4px 0;
  font-size: 18px;
  font-weight: 600;
  color: white;
}

.header-text p {
  margin: 0;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

.knowledge-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.knowledge-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  animation: fadeInUp 0.5s ease forwards;
  opacity: 0;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.item-rank {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
  color: white;
  flex-shrink: 0;
}

.item-rank.success { background: linear-gradient(135deg, #10b981 0%, #34d399 100%); }
.item-rank.danger { background: linear-gradient(135deg, #ef4444 0%, #f87171 100%); }

.item-content {
  flex: 1;
  min-width: 0;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.item-name {
  font-size: 14px;
  font-weight: 500;
  color: white;
}

.item-score {
  font-size: 14px;
  font-weight: 700;
}

.item-score.success { color: #10b981; }
.item-score.danger { color: #ef4444; }

.item-bar {
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 6px;
}

.item-bar .bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.8s ease;
}

.item-bar .bar-fill.success { background: linear-gradient(90deg, #10b981 0%, #34d399 100%); }
.item-bar .bar-fill.danger { background: linear-gradient(90deg, #ef4444 0%, #f87171 100%); }

.item-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.5);
}

.btn-practice {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 8px;
  font-size: 12px;
  font-weight: 500;
  color: #f87171;
  cursor: pointer;
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.btn-practice:hover {
  background: rgba(239, 68, 68, 0.3);
  transform: translateX(2px);
}

/* AI 学习建议 */
.recommendations-section {
  margin-bottom: 32px;
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
  color: #a78bfa;
}

.recommendations-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.recommendation-card {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  animation: fadeInUp 0.5s ease forwards;
  opacity: 0;
  transition: all 0.3s ease;
}

.recommendation-card:hover {
  transform: translateY(-4px);
  background: rgba(255, 255, 255, 0.15);
}

.rec-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.rec-icon.practice { background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%); }
.rec-icon.review { background: linear-gradient(135deg, #8b5cf6 0%, #a78bfa 100%); }
.rec-icon.focus { background: linear-gradient(135deg, #10b981 0%, #34d399 100%); }
.rec-icon.schedule { background: linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%); }
.rec-icon.trend { background: linear-gradient(135deg, #ec4899 0%, #f472b6 100%); }

.rec-content h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: white;
}

.rec-content p {
  margin: 0;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.6;
}

.btn-action {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 18px;
  background: rgba(139, 92, 246, 0.2);
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 10px;
  font-size: 13px;
  font-weight: 500;
  color: #a78bfa;
  cursor: pointer;
  transition: all 0.3s ease;
  align-self: flex-start;
}

.btn-action:hover {
  background: rgba(139, 92, 246, 0.3);
  transform: translateX(4px);
}

/* 学习计划 */
.study-plan-section {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  padding: 24px;
}

.btn-regenerate {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.8);
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-regenerate:hover {
  background: rgba(255, 255, 255, 0.15);
  color: white;
}

.plan-timeline {
  margin-top: 24px;
}

.plan-day {
  display: flex;
  gap: 20px;
  animation: fadeInUp 0.5s ease forwards;
  opacity: 0;
}

.day-marker {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 20px;
  flex-shrink: 0;
}

.marker-dot {
  width: 12px;
  height: 12px;
  background: linear-gradient(135deg, #8b5cf6 0%, #3b82f6 100%);
  border-radius: 50%;
  flex-shrink: 0;
}

.marker-line {
  width: 2px;
  flex: 1;
  background: rgba(139, 92, 246, 0.3);
  margin: 8px 0;
}

.day-content {
  flex: 1;
  padding-bottom: 24px;
}

.day-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.day-label {
  font-size: 16px;
  font-weight: 600;
  color: white;
}

.day-date {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
}

.day-tasks {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.task-icon {
  color: #a78bfa;
  font-size: 16px;
}

.task-text {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
}

/* 空状态 */
.empty-state {
  max-width: 600px;
  margin: 80px auto;
  padding: 0 24px;
  text-align: center;
}

.empty-icon {
  width: 160px;
  height: 160px;
  margin: 0 auto 32px;
  background: rgba(139, 92, 246, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #a78bfa;
}

.empty-state h3 {
  margin: 0 0 12px 0;
  font-size: 24px;
  font-weight: 600;
  color: white;
}

.empty-state > p {
  margin: 0 0 40px 0;
  font-size: 15px;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1.6;
}

.feature-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
}

.feature-item .el-icon {
  font-size: 20px;
  color: #a78bfa;
}

/* 加载动画 */
.is-loading {
  animation: rotating 1s linear infinite;
}

@keyframes rotating {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 响应式 */
@media (max-width: 992px) {
  .strengths-weaknesses {
    grid-template-columns: 1fr;
  }
  
  .recommendations-grid {
    grid-template-columns: 1fr;
  }
  
  .score-card {
    flex-direction: column;
    gap: 32px;
  }
}

@media (max-width: 768px) {
  .page-banner {
    padding: 24px 16px;
  }
  
  .banner-content {
    flex-direction: column;
    text-align: center;
  }
  
  .banner-text h1 {
    font-size: 24px;
  }
  
  .analysis-results {
    padding: 24px 16px;
  }
  
  .feature-list {
    grid-template-columns: 1fr;
  }
  
  .knowledge-item {
    flex-wrap: wrap;
  }
  
  .btn-practice {
    width: 100%;
    justify-content: center;
    margin-top: 8px;
  }
}
</style>
