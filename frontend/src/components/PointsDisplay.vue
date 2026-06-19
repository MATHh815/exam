<template>
  <div class="points-display">
    <div class="points-card">
      <div class="level-section">
        <div class="level-badge" :class="`level-${level}`">
          <Trophy class="level-icon" />
          <span class="level-text">Lv.{{ level }}</span>
        </div>
        <div class="level-info">
          <div class="level-title">{{ levelTitle }}</div>
          <div class="level-progress">
            <el-progress 
              :percentage="levelProgress" 
              :stroke-width="8"
              :show-text="false"
            />
            <div class="progress-text">
              {{ currentLevelPoints }} / {{ nextLevelPoints }} 积分
            </div>
          </div>
        </div>
      </div>

      <div class="stats-section">
        <div class="stat-item">
          <Coins class="stat-icon" />
          <div class="stat-content">
            <div class="stat-value">{{ totalPoints }}</div>
            <div class="stat-label">总积分</div>
          </div>
        </div>
        <div class="stat-item">
          <Calendar class="stat-icon" />
          <div class="stat-content">
            <div class="stat-value">{{ streakDays }}</div>
            <div class="stat-label">连续天数</div>
          </div>
        </div>
        <div class="stat-item">
          <TrendingUp class="stat-icon" />
          <div class="stat-content">
            <div class="stat-value">{{ todayPoints }}</div>
            <div class="stat-label">今日积分</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Trophy, Coins, Calendar, TrendingUp } from 'lucide-vue-next'
import { getUserPoints } from '@/api/points'
import { ElMessage } from 'element-plus'

const totalPoints = ref(0)
const level = ref(1)
const streakDays = ref(0)
const todayPoints = ref(0)
const lastActiveDate = ref(null)

const levelTitles = {
  1: '新手',
  2: '初学者',
  3: '学习者',
  4: '进阶者',
  5: '熟练者',
  6: '专家',
  7: '大师',
  8: '宗师',
  9: '传奇',
  10: '神话'
}

const levelTitle = computed(() => {
  return levelTitles[level.value] || `等级 ${level.value}`
})

// 计算当前等级所需积分
const currentLevelPoints = computed(() => {
  const prevLevel = level.value - 1
  return totalPoints.value - (prevLevel * prevLevel * 100)
})

// 计算下一等级所需积分
const nextLevelPoints = computed(() => {
  return (2 * level.value * 100)
})

// 计算等级进度百分比
const levelProgress = computed(() => {
  if (nextLevelPoints.value === 0) return 100
  return Math.min(100, Math.floor((currentLevelPoints.value / nextLevelPoints.value) * 100))
})

const loadPointsData = async () => {
  try {
    const response = await getUserPoints()
    if (response.data.success) {
      const data = response.data.data
      totalPoints.value = data.total_points
      level.value = data.level
      streakDays.value = data.streak_days
      todayPoints.value = data.today_points || 0
      lastActiveDate.value = data.last_active_date
    }
  } catch (error) {
    console.error('加载积分数据失败:', error)
    ElMessage.error('加载积分数据失败')
  }
}

onMounted(() => {
  loadPointsData()
})

defineExpose({
  refresh: loadPointsData
})
</script>

<style scoped>
.points-display {
  width: 100%;
}

.points-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 24px;
  color: white;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
}

.level-section {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.level-badge {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 3px solid rgba(255, 255, 255, 0.3);
  flex-shrink: 0;
}

.level-badge.level-1,
.level-badge.level-2,
.level-badge.level-3 {
  border-color: #cd7f32;
  box-shadow: 0 0 20px rgba(205, 127, 50, 0.5);
}

.level-badge.level-4,
.level-badge.level-5,
.level-badge.level-6 {
  border-color: #c0c0c0;
  box-shadow: 0 0 20px rgba(192, 192, 192, 0.5);
}

.level-badge.level-7,
.level-badge.level-8,
.level-badge.level-9,
.level-badge.level-10 {
  border-color: #ffd700;
  box-shadow: 0 0 20px rgba(255, 215, 0, 0.5);
}

.level-icon {
  width: 32px;
  height: 32px;
  margin-bottom: 4px;
}

.level-text {
  font-size: 16px;
  font-weight: bold;
}

.level-info {
  flex: 1;
}

.level-title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 12px;
}

.level-progress {
  width: 100%;
}

.progress-text {
  font-size: 12px;
  margin-top: 8px;
  opacity: 0.9;
}

.stats-section {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

.stat-icon {
  width: 32px;
  height: 32px;
  opacity: 0.9;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  line-height: 1;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  opacity: 0.8;
}

@media (max-width: 768px) {
  .level-section {
    flex-direction: column;
    text-align: center;
  }

  .stats-section {
    grid-template-columns: 1fr;
  }
}
</style>
