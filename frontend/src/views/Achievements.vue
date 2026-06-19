<template>
  <div class="achievements-page">
    <div class="page-header">
      <h1>
        <Award class="page-icon" />
        成就系统
      </h1>
      <p class="page-description">解锁成就，获得奖励，展示你的学习成果</p>
    </div>

    <!-- 积分展示 -->
    <PointsDisplay ref="pointsDisplayRef" />

    <!-- 成就统计 -->
    <div v-if="stats" class="achievement-stats">
      <div class="stat-card">
        <Trophy class="stat-icon earned" />
        <div class="stat-content">
          <div class="stat-value">{{ stats.earned_count }}</div>
          <div class="stat-label">已获得</div>
        </div>
      </div>
      <div class="stat-card">
        <TrendingUp class="stat-icon progress" />
        <div class="stat-content">
          <div class="stat-value">{{ stats.in_progress_count }}</div>
          <div class="stat-label">进行中</div>
        </div>
      </div>
      <div class="stat-card">
        <Lock class="stat-icon locked" />
        <div class="stat-content">
          <div class="stat-value">{{ stats.locked_count }}</div>
          <div class="stat-label">未解锁</div>
        </div>
      </div>
      <div class="stat-card highlight">
        <Star class="stat-icon" />
        <div class="stat-content">
          <div class="stat-value">{{ completionRate }}%</div>
          <div class="stat-label">完成率</div>
        </div>
      </div>
    </div>

    <!-- 筛选器 -->
    <div class="filters">
      <el-radio-group v-model="statusFilter" size="large">
        <el-radio-button value="all">全部</el-radio-button>
        <el-radio-button value="earned">已获得</el-radio-button>
        <el-radio-button value="in_progress">进行中</el-radio-button>
        <el-radio-button value="locked">未解锁</el-radio-button>
      </el-radio-group>

      <el-select v-model="categoryFilter" placeholder="选择类别" clearable size="large">
        <el-option label="全部类别" value="" />
        <el-option label="学习类" value="learning" />
        <el-option label="连续类" value="streak" />
        <el-option label="里程碑" value="milestone" />
      </el-select>

      <el-select v-model="tierFilter" placeholder="选择等级" clearable size="large">
        <el-option label="全部等级" value="" />
        <el-option label="铜牌" value="bronze" />
        <el-option label="银牌" value="silver" />
        <el-option label="金牌" value="gold" />
      </el-select>
    </div>

    <!-- 成就列表 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="5" animated />
    </div>

    <div v-else-if="filteredAchievements.length === 0" class="empty-state">
      <Award class="empty-icon" />
      <p>暂无成就</p>
    </div>

    <div v-else class="achievements-grid">
      <AchievementCard 
        v-for="achievement in filteredAchievements" 
        :key="achievement.id"
        :achievement="achievement"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Award, Trophy, TrendingUp, Lock, Star } from 'lucide-vue-next'
import PointsDisplay from '@/components/PointsDisplay.vue'
import AchievementCard from '@/components/AchievementCard.vue'
import { getUserAchievements, getAchievementStats } from '@/api/achievements'
import { ElMessage } from 'element-plus'

const pointsDisplayRef = ref(null)
const achievements = ref([])
const stats = ref(null)
const loading = ref(false)

const statusFilter = ref('all')
const categoryFilter = ref('')
const tierFilter = ref('')

const completionRate = computed(() => {
  if (!stats.value || stats.value.total_count === 0) return 0
  return Math.floor((stats.value.earned_count / stats.value.total_count) * 100)
})

const filteredAchievements = computed(() => {
  let result = achievements.value

  // 状态筛选
  if (statusFilter.value !== 'all') {
    result = result.filter(a => a.status === statusFilter.value)
  }

  // 类别筛选
  if (categoryFilter.value) {
    result = result.filter(a => a.category === categoryFilter.value)
  }

  // 等级筛选
  if (tierFilter.value) {
    result = result.filter(a => a.tier === tierFilter.value)
  }

  return result
})

const loadAchievements = async () => {
  loading.value = true
  try {
    const response = await getUserAchievements()
    if (response.data.success) {
      achievements.value = response.data.data
    }
  } catch (error) {
    console.error('加载成就失败:', error)
    ElMessage.error('加载成就失败')
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  try {
    const response = await getAchievementStats()
    if (response.data.success) {
      stats.value = response.data.data
    }
  } catch (error) {
    console.error('加载成就统计失败:', error)
  }
}

onMounted(() => {
  loadAchievements()
  loadStats()
})
</script>

<style scoped>
.achievements-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px;
}

.page-header {
  margin-bottom: 32px;
  text-align: center;
}

.page-header h1 {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 12px 0;
  color: #fff;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-icon {
  width: 36px;
  height: 36px;
  color: #667eea;
  filter: drop-shadow(0 0 8px rgba(102, 126, 234, 0.5));
}

.page-description {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}

.achievement-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin: 32px 0;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  border-color: rgba(102, 126, 234, 0.3);
}

.stat-card:hover::before {
  opacity: 1;
}

.stat-card.highlight {
  background: linear-gradient(135deg, rgba(255, 215, 0, 0.15) 0%, rgba(255, 237, 78, 0.15) 100%);
  border-color: rgba(255, 215, 0, 0.3);
}

.stat-card.highlight::before {
  background: linear-gradient(135deg, rgba(255, 215, 0, 0.2) 0%, rgba(255, 237, 78, 0.2) 100%);
  opacity: 1;
}

.stat-icon {
  width: 48px;
  height: 48px;
  position: relative;
  z-index: 1;
}

.stat-icon.earned {
  color: #10b981;
  filter: drop-shadow(0 0 8px rgba(16, 185, 129, 0.5));
}

.stat-icon.progress {
  color: #f59e0b;
  filter: drop-shadow(0 0 8px rgba(245, 158, 11, 0.5));
}

.stat-icon.locked {
  color: #6b7280;
  filter: drop-shadow(0 0 8px rgba(107, 114, 128, 0.3));
}

.stat-card.highlight .stat-icon {
  color: #ffd700;
  filter: drop-shadow(0 0 12px rgba(255, 215, 0, 0.6));
}

.stat-content {
  flex: 1;
  position: relative;
  z-index: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 6px;
  color: #fff;
}

.stat-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 500;
}

.filters {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  padding: 24px;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
}

.loading-container {
  padding: 20px;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: rgba(255, 255, 255, 0.5);
}

.empty-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  opacity: 0.3;
  color: rgba(255, 255, 255, 0.5);
}

.achievements-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Element Plus 组件样式覆盖 */
:deep(.el-radio-button__inner) {
  background: rgba(255, 255, 255, 0.05) !important;
  border-color: rgba(255, 255, 255, 0.1) !important;
  color: rgba(255, 255, 255, 0.7) !important;
  padding: 12px 20px;
  font-weight: 500;
}

:deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
  border-color: transparent !important;
  color: #fff !important;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

:deep(.el-select) {
  width: 180px;
}

:deep(.el-input__wrapper) {
  background: rgba(255, 255, 255, 0.05) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  box-shadow: none !important;
}

:deep(.el-input__wrapper:hover) {
  border-color: rgba(102, 126, 234, 0.3) !important;
}

:deep(.el-input__wrapper.is-focus) {
  border-color: #667eea !important;
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2) !important;
}

:deep(.el-input__inner) {
  color: #fff !important;
}

:deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.4) !important;
}

:deep(.el-select-dropdown) {
  background: rgba(30, 30, 50, 0.95) !important;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
}

:deep(.el-select-dropdown__item) {
  color: rgba(255, 255, 255, 0.8) !important;
}

:deep(.el-select-dropdown__item:hover) {
  background: rgba(102, 126, 234, 0.2) !important;
}

:deep(.el-select-dropdown__item.selected) {
  color: #667eea !important;
  font-weight: 600;
}

@media (max-width: 992px) {
  .achievement-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .achievements-page {
    padding: 16px;
  }

  .page-header h1 {
    font-size: 24px;
  }

  .achievement-stats {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .stat-card {
    padding: 16px;
  }

  .stat-icon {
    width: 40px;
    height: 40px;
  }

  .stat-value {
    font-size: 24px;
  }

  .filters {
    flex-direction: column;
    padding: 16px;
  }

  :deep(.el-select) {
    width: 100%;
  }
}
</style>
