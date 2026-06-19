<template>
  <div class="achievement-card" :class="[`tier-${achievement.tier}`, statusClass]">
    <div class="achievement-icon">
      <component :is="iconComponent" class="icon" />
      <div v-if="achievement.status === 'locked'" class="lock-overlay">
        <Lock class="lock-icon" />
      </div>
    </div>
    
    <div class="achievement-content">
      <div class="achievement-header">
        <h3 class="achievement-name">{{ achievement.name }}</h3>
        <el-tag :type="tierTagType" size="small">{{ tierText }}</el-tag>
      </div>
      
      <p class="achievement-description">{{ achievement.description }}</p>
      
      <div v-if="achievement.status === 'in_progress'" class="achievement-progress">
        <el-progress 
          :percentage="progressPercentage" 
          :stroke-width="6"
          :color="progressColor"
        />
        <span class="progress-text">{{ progressText }}</span>
      </div>
      
      <div class="achievement-footer">
        <div class="points-reward">
          <Coins class="coin-icon" />
          <span>{{ achievement.points_reward }} 积分</span>
        </div>
        <div v-if="achievement.unlocked_at" class="unlock-date">
          <Calendar class="calendar-icon" />
          <span>{{ formatDate(achievement.unlocked_at) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { 
  Trophy, Award, Star, Target, Flame, BookOpen, 
  CheckCircle, TrendingUp, Lock, Coins, Calendar 
} from 'lucide-vue-next'

const props = defineProps({
  achievement: {
    type: Object,
    required: true
  }
})

const iconMap = {
  'learning': BookOpen,
  'streak': Flame,
  'milestone': Trophy,
  'practice': Target,
  'exam': Award,
  'note': BookOpen,
  'bookmark': Star,
  'plan': CheckCircle,
  'task': TrendingUp
}

const iconComponent = computed(() => {
  return iconMap[props.achievement.category] || Trophy
})

const statusClass = computed(() => {
  return `status-${props.achievement.status || 'locked'}`
})

const tierTagType = computed(() => {
  const tierMap = {
    'bronze': 'warning',
    'silver': 'info',
    'gold': 'success'
  }
  return tierMap[props.achievement.tier] || 'info'
})

const tierText = computed(() => {
  const tierMap = {
    'bronze': '铜牌',
    'silver': '银牌',
    'gold': '金牌'
  }
  return tierMap[props.achievement.tier] || '未知'
})

const progressPercentage = computed(() => {
  if (!props.achievement.progress) return 0
  const { current, target } = props.achievement.progress
  return Math.min(100, Math.floor((current / target) * 100))
})

const progressText = computed(() => {
  if (!props.achievement.progress) return ''
  const { current, target } = props.achievement.progress
  return `${current} / ${target}`
})

const progressColor = computed(() => {
  const percentage = progressPercentage.value
  if (percentage >= 80) return '#67c23a'
  if (percentage >= 50) return '#e6a23c'
  return '#909399'
})

const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.achievement-card {
  display: flex;
  gap: 20px;
  padding: 24px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.achievement-card::before {
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

.achievement-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  border-color: rgba(102, 126, 234, 0.3);
}

.achievement-card:hover::before {
  opacity: 1;
}

.achievement-card.status-earned {
  border-color: rgba(16, 185, 129, 0.3);
  background: rgba(16, 185, 129, 0.1);
}

.achievement-card.status-earned::before {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(5, 150, 105, 0.15) 100%);
  opacity: 1;
}

.achievement-card.status-in_progress {
  border-color: rgba(245, 158, 11, 0.3);
}

.achievement-card.status-locked {
  opacity: 0.5;
  filter: grayscale(0.7);
}

.achievement-card.tier-bronze::after {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: linear-gradient(180deg, #cd7f32 0%, #b87333 100%);
  box-shadow: 0 0 10px rgba(205, 127, 50, 0.5);
}

.achievement-card.tier-silver::after {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: linear-gradient(180deg, #c0c0c0 0%, #a8a8a8 100%);
  box-shadow: 0 0 10px rgba(192, 192, 192, 0.5);
}

.achievement-card.tier-gold::after {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: linear-gradient(180deg, #ffd700 0%, #ffed4e 100%);
  box-shadow: 0 0 10px rgba(255, 215, 0, 0.6);
}

.achievement-icon {
  position: relative;
  width: 72px;
  height: 72px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
  z-index: 1;
}

.achievement-card.status-earned .achievement-icon {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  box-shadow: 0 4px 16px rgba(16, 185, 129, 0.4);
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 4px 16px rgba(16, 185, 129, 0.4);
  }
  50% {
    box-shadow: 0 4px 24px rgba(16, 185, 129, 0.6);
  }
}

.achievement-card.status-locked .achievement-icon {
  background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
  box-shadow: 0 4px 16px rgba(107, 114, 128, 0.3);
}

.icon {
  width: 36px;
  height: 36px;
  color: white;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

.lock-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  border-radius: 50%;
}

.lock-icon {
  width: 28px;
  height: 28px;
  color: white;
}

.achievement-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
  position: relative;
  z-index: 1;
}

.achievement-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.achievement-name {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  color: #fff;
}

.achievement-card.status-earned .achievement-name {
  color: #10b981;
}

.achievement-description {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
  line-height: 1.6;
}

.achievement-progress {
  display: flex;
  align-items: center;
  gap: 12px;
}

.achievement-progress :deep(.el-progress) {
  flex: 1;
}

.achievement-progress :deep(.el-progress-bar__outer) {
  background: rgba(255, 255, 255, 0.1) !important;
}

.achievement-progress :deep(.el-progress-bar__inner) {
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
}

.progress-text {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  white-space: nowrap;
  font-weight: 500;
}

.achievement-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: auto;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.points-reward,
.unlock-date {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
  font-weight: 500;
}

.points-reward {
  color: #ffd700;
}

.coin-icon {
  width: 18px;
  height: 18px;
  color: #ffd700;
  filter: drop-shadow(0 0 4px rgba(255, 215, 0, 0.5));
}

.calendar-icon {
  width: 16px;
  height: 16px;
}

/* Element Plus Tag 样式覆盖 */
:deep(.el-tag) {
  border: none;
  font-weight: 600;
  padding: 4px 12px;
}

:deep(.el-tag.el-tag--warning) {
  background: linear-gradient(135deg, rgba(205, 127, 50, 0.2) 0%, rgba(184, 115, 51, 0.2) 100%);
  color: #cd7f32;
}

:deep(.el-tag.el-tag--info) {
  background: linear-gradient(135deg, rgba(192, 192, 192, 0.2) 0%, rgba(168, 168, 168, 0.2) 100%);
  color: #c0c0c0;
}

:deep(.el-tag.el-tag--success) {
  background: linear-gradient(135deg, rgba(255, 215, 0, 0.2) 0%, rgba(255, 237, 78, 0.2) 100%);
  color: #ffd700;
}

@media (max-width: 768px) {
  .achievement-card {
    flex-direction: column;
    text-align: center;
    padding: 20px;
  }

  .achievement-icon {
    margin: 0 auto;
    width: 64px;
    height: 64px;
  }

  .icon {
    width: 32px;
    height: 32px;
  }

  .achievement-header {
    flex-direction: column;
    gap: 8px;
  }

  .achievement-footer {
    flex-direction: column;
    gap: 8px;
  }
}
</style>
