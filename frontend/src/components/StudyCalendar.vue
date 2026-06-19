<template>
  <div class="study-calendar">
    <div class="calendar-header">
      <h3>学习日历</h3>
      <div class="legend">
        <span class="legend-item">
          <span class="legend-box level-0"></span>
          <span class="legend-text">无</span>
        </span>
        <span class="legend-item">
          <span class="legend-box level-1"></span>
          <span class="legend-text">少</span>
        </span>
        <span class="legend-item">
          <span class="legend-box level-2"></span>
          <span class="legend-text">中</span>
        </span>
        <span class="legend-item">
          <span class="legend-box level-3"></span>
          <span class="legend-text">多</span>
        </span>
      </div>
    </div>
    
    <div class="calendar-grid">
      <div 
        v-for="(day, index) in calendarDays" 
        :key="index"
        class="calendar-day"
        :class="`level-${day.level}`"
        :title="getTooltip(day)"
        @click="handleDayClick(day)"
      >
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import dayjs from 'dayjs'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  days: {
    type: Number,
    default: 90
  }
})

const emit = defineEmits(['day-click'])

// 生成日历数据
const calendarDays = computed(() => {
  const days = []
  const today = dayjs()
  
  for (let i = props.days - 1; i >= 0; i--) {
    const date = today.subtract(i, 'day')
    const dateStr = date.format('YYYY-MM-DD')
    
    // 查找该日期的数据
    const dayData = props.data.find(d => d.date === dateStr)
    
    // 根据练习数量确定等级 (0-3)
    let level = 0
    if (dayData) {
      const count = dayData.count || 0
      if (count > 0 && count <= 10) level = 1
      else if (count > 10 && count <= 30) level = 2
      else if (count > 30) level = 3
    }
    
    days.push({
      date: dateStr,
      level,
      count: dayData?.count || 0,
      duration: dayData?.duration || 0,
      accuracy: dayData?.accuracy || 0
    })
  }
  
  return days
})

function getTooltip(day) {
  if (day.count === 0) {
    return `${day.date}\n无学习记录`
  }
  return `${day.date}\n练习: ${day.count}题\n时长: ${day.duration}分钟\n正确率: ${(day.accuracy * 100).toFixed(0)}%`
}

function handleDayClick(day) {
  emit('day-click', day)
}
</script>

<style scoped>
.study-calendar {
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.calendar-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  margin: 0;
}

.legend {
  display: flex;
  gap: 12px;
  align-items: center;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.legend-box {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.legend-text {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(12px, 1fr));
  gap: 3px;
  max-width: 100%;
}

.calendar-day {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  cursor: pointer;
  transition: all 0.2s;
}

.calendar-day.level-0 {
  background: rgba(255, 255, 255, 0.05);
}

.calendar-day.level-1 {
  background: rgba(102, 126, 234, 0.3);
}

.calendar-day.level-2 {
  background: rgba(102, 126, 234, 0.6);
}

.calendar-day.level-3 {
  background: rgba(102, 126, 234, 0.9);
}

.calendar-day:hover {
  transform: scale(1.3);
  box-shadow: 0 0 8px rgba(102, 126, 234, 0.5);
}

.legend-box.level-0 {
  background: rgba(255, 255, 255, 0.05);
}

.legend-box.level-1 {
  background: rgba(102, 126, 234, 0.3);
}

.legend-box.level-2 {
  background: rgba(102, 126, 234, 0.6);
}

.legend-box.level-3 {
  background: rgba(102, 126, 234, 0.9);
}

@media (max-width: 768px) {
  .calendar-grid {
    grid-template-columns: repeat(auto-fill, minmax(10px, 1fr));
    gap: 2px;
  }
  
  .calendar-day {
    width: 10px;
    height: 10px;
  }
  
  .legend {
    gap: 8px;
  }
  
  .legend-box {
    width: 10px;
    height: 10px;
  }
}
</style>
