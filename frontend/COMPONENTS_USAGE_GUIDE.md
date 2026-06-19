# 新组件使用指南

## 🚀 快速开始

### 1. 确认依赖已安装

```bash
cd exam/frontend
npm install
```

依赖包括：
- echarts
- vue-echarts  
- gsap
- @vueuse/core
- dayjs

### 2. 在 Dashboard 中使用

打开 `exam/frontend/src/views/Dashboard.vue`，添加以下导入：

```vue
<script setup>
// 导入新组件
import ProgressRing from '../components/charts/ProgressRing.vue'
import AccuracyTrend from '../components/charts/AccuracyTrend.vue'
import StudyCalendar from '../components/StudyCalendar.vue'

// 导入工具
import { useCountUp } from '../composables/useCountUp'
</script>
```

### 3. 添加到模板

```vue
<template>
  <div class="dashboard-container">
    <!-- 在合适的位置添加组件 -->
    
    <!-- 进度环形图 -->
    <el-card>
      <template #header>
        <span>今日学习进度</span>
      </template>
      <ProgressRing 
        :value="overview.practice_count || 0" 
        :total="50" 
        label="今日目标"
      />
    </el-card>

    <!-- 正确率趋势 -->
    <el-card>
      <template #header>
        <span>正确率趋势</span>
      </template>
      <AccuracyTrend 
        :data="trendData" 
        :days="7"
      />
    </el-card>

    <!-- 学习日历 -->
    <StudyCalendar 
      :data="calendarData" 
      :days="90"
    />
  </div>
</template>
```

### 4. 准备数据

```vue
<script setup>
import { ref, onMounted } from 'vue'

// 趋势数据（示例）
const trendData = ref([
  { date: '12-20', accuracy: 0.82 },
  { date: '12-21', accuracy: 0.85 },
  { date: '12-22', accuracy: 0.88 },
  { date: '12-23', accuracy: 0.86 },
  { date: '12-24', accuracy: 0.90 },
  { date: '12-25', accuracy: 0.87 },
  { date: '12-26', accuracy: 0.89 }
])

// 日历数据（示例）
const calendarData = ref([
  { date: '2025-12-01', count: 20, duration: 60, accuracy: 0.85 },
  { date: '2025-12-02', count: 35, duration: 90, accuracy: 0.88 },
  { date: '2025-12-03', count: 15, duration: 45, accuracy: 0.82 },
  // ... 更多数据
])

// 如果需要从 API 获取真实数据
onMounted(async () => {
  // TODO: 调用 API 获取数据
  // const response = await getStatistics()
  // trendData.value = response.data.trend
  // calendarData.value = response.data.calendar
})
</script>
```

## 📊 组件详细说明

### ProgressRing（进度环形图）

**Props:**
- `value` (Number): 当前值，默认 0
- `total` (Number): 总值，默认 100
- `label` (String): 标签文字，默认 '完成度'
- `color` (Array): 渐变色 [起始色, 结束色]，默认 ['#667eea', '#764ba2']

**Events:**
- `click`: 点击图表时触发

**示例:**
```vue
<ProgressRing 
  :value="45" 
  :total="100" 
  label="今日完成度"
  :color="['#10b981', '#059669']"
  @click="handleProgressClick"
/>
```

### AccuracyTrend（正确率趋势图）

**Props:**
- `data` (Array): 趋势数据数组
- `days` (Number): 显示天数，默认 7

**数据格式:**
```javascript
[
  { date: '12-26', accuracy: 0.89 },  // accuracy 为 0-1 的小数
  // ...
]
```

**示例:**
```vue
<AccuracyTrend 
  :data="last7Days" 
  :days="7"
/>
```

### StudyCalendar（学习日历）

**Props:**
- `data` (Array): 日历数据数组
- `days` (Number): 显示天数，默认 90

**Events:**
- `day-click`: 点击某一天时触发，参数为该天的数据

**数据格式:**
```javascript
[
  {
    date: '2025-12-26',
    count: 50,        // 练习题数
    duration: 120,    // 学习时长（分钟）
    accuracy: 0.85    // 正确率
  },
  // ...
]
```

**示例:**
```vue
<StudyCalendar 
  :data="studyHistory" 
  :days="90"
  @day-click="showDayDetail"
/>

<script setup>
function showDayDetail(day) {
  console.log('点击了:', day.date)
  console.log('练习题数:', day.count)
}
</script>
```

## 🎨 自定义样式

### 修改颜色

```vue
<!-- 使用不同的渐变色 -->
<ProgressRing 
  :color="['#f093fb', '#f5576c']"  <!-- 粉色渐变 -->
/>

<ProgressRing 
  :color="['#4facfe', '#00f2fe']"  <!-- 蓝色渐变 -->
/>
```

### 调整大小

```vue
<style scoped>
/* 修改进度环大小 */
.progress-ring-container {
  height: 250px;  /* 默认 200px */
}

/* 修改趋势图高度 */
.accuracy-trend-container {
  height: 300px;  /* 默认 250px */
}
</style>
```

## 🔧 工具函数使用

### useCountUp（数字滚动动画）

```vue
<script setup>
import { ref } from 'vue'
import { useCountUp } from '@/composables/useCountUp'

const targetNumber = ref(1234)

const { displayValue } = useCountUp(targetNumber, {
  duration: 2,      // 动画时长（秒）
  decimals: 0,      // 小数位数
  delay: 0.5        // 延迟（秒）
})
</script>

<template>
  <div>{{ displayValue }}</div>
</template>
```

### useChartTheme（图表主题）

```vue
<script setup>
import { useChartTheme } from '@/composables/useChartTheme'

const { darkTheme, gradientColors } = useChartTheme()

// 在 ECharts 配置中使用
const chartOption = {
  ...darkTheme,
  series: [{
    areaStyle: {
      color: gradientColors.primary
    }
  }]
}
</script>
```

## 📱 响应式设计

所有组件都已包含响应式设计，会自动适配不同屏幕尺寸。

### 移动端优化建议

```vue
<style scoped>
@media (max-width: 768px) {
  /* 在移动端调整布局 */
  .dashboard-grid {
    grid-template-columns: 1fr;  /* 单列布局 */
  }
  
  /* 减小图表高度 */
  .chart-container {
    height: 200px;
  }
}
</style>
```

## 🐛 故障排除

### 问题 1: 图表不显示

**可能原因:**
- 容器没有高度
- 数据格式不正确
- ECharts 未正确导入

**解决方案:**
```vue
<style scoped>
.chart-container {
  height: 250px;  /* 确保有明确的高度 */
}
</style>
```

### 问题 2: 动画卡顿

**解决方案:**
- 减少同时运行的动画数量
- 降低动画时长
- 使用 `v-if` 延迟加载

```vue
<ProgressRing v-if="dataLoaded" />
```

### 问题 3: 数据不更新

**解决方案:**
确保使用响应式数据：
```javascript
const data = ref([])  // ✅ 正确
const data = []       // ❌ 错误
```

## 💡 最佳实践

### 1. 数据加载

```javascript
const loading = ref(true)
const data = ref([])

onMounted(async () => {
  try {
    loading.value = true
    const response = await fetchData()
    data.value = response.data
  } catch (error) {
    console.error('加载失败:', error)
  } finally {
    loading.value = false
  }
})
```

### 2. 错误处理

```vue
<template>
  <div v-loading="loading">
    <el-empty v-if="!data.length" description="暂无数据" />
    <ProgressRing v-else :value="data.value" />
  </div>
</template>
```

### 3. 性能优化

```javascript
// 使用计算属性处理数据
const chartData = computed(() => {
  return rawData.value.map(item => ({
    date: item.date.substring(5),
    accuracy: item.accuracy
  }))
})
```

## 📚 更多资源

- [ECharts 官方文档](https://echarts.apache.org/zh/index.html)
- [GSAP 动画库](https://greensock.com/gsap/)
- [VueUse 工具库](https://vueuse.org/)
- [Day.js 日期库](https://day.js.org/)

---

**需要帮助？** 查看 `PHASE1_COMPONENTS_CREATED.md` 获取更多详细信息。
