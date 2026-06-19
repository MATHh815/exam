# Dashboard 集成指南

## 🎯 目标

将新创建的组件集成到 Dashboard，打造现代化的学习中心。

## 📦 可用组件

### 已创建的组件
1. ✅ **ProgressRing** - 进度环形图
2. ✅ **AccuracyTrend** - 正确率趋势图
3. ✅ **StudyCalendar** - 学习日历
4. ✅ **SubjectRadar** - 科目雷达图
5. ✅ **DailyGoals** - 今日目标

### 工具函数
1. ✅ **useCountUp** - 数字滚动动画
2. ✅ **useChartTheme** - 图表主题
3. ✅ **chartConfig** - 图表配置

## 🚀 快速集成

### 方法 1: 在现有 Dashboard 中添加

打开 `exam/frontend/src/views/Dashboard.vue`，在合适的位置添加：

```vue
<script setup>
// 添加导入
import ProgressRing from '../components/charts/ProgressRing.vue'
import AccuracyTrend from '../components/charts/AccuracyTrend.vue'
import StudyCalendar from '../components/StudyCalendar.vue'
import SubjectRadar from '../components/charts/SubjectRadar.vue'
import DailyGoals from '../components/DailyGoals.vue'
import { useCountUp } from '../composables/useCountUp'

// 准备数据
const trendData = ref([])
const calendarData = ref([])
const subjectData = ref([])
const dailyGoals = ref([])

// 在 onMounted 中加载数据
onMounted(async () => {
  // ... 现有代码
  
  // 加载趋势数据
  try {
    const response = await getAccuracyTrend({ days: 7 })
    if (response.data) {
      trendData.value = response.data.map(item => ({
        date: item.date.substring(5),
        accuracy: item.accuracy
      }))
    }
  } catch (error) {
    console.error('加载趋势数据失败:', error)
  }
  
  // 加载日历数据
  try {
    const response = await getStudyCalendar({ days: 90 })
    if (response.data) {
      calendarData.value = response.data
    }
  } catch (error) {
    console.error('加载日历数据失败:', error)
  }
})
</script>

<template>
  <div class="dashboard-container">
    <!-- 在合适的位置添加新组件 -->
    
    <!-- 第一行：进度和趋势 -->
    <div class="dashboard-row">
      <el-card class="chart-card">
        <template #header>
          <span>今日学习进度</span>
        </template>
        <ProgressRing 
          :value="overview.practice_count || 0" 
          :total="50" 
          label="今日目标"
        />
      </el-card>

      <el-card class="chart-card">
        <template #header>
          <span>正确率趋势</span>
        </template>
        <AccuracyTrend :data="trendData" :days="7" />
      </el-card>
    </div>

    <!-- 第二行：今日目标和科目雷达 -->
    <div class="dashboard-row">
      <el-card class="chart-card">
        <DailyGoals :goals="dailyGoals" />
      </el-card>

      <el-card class="chart-card">
        <template #header>
          <span>科目掌握度</span>
        </template>
        <SubjectRadar :data="subjectData" />
      </el-card>
    </div>

    <!-- 第三行：学习日历 -->
    <el-card class="calendar-card">
      <StudyCalendar 
        :data="calendarData" 
        :days="90"
        @day-click="handleDayClick"
      />
    </el-card>

    <!-- 保留原有的其他内容 -->
  </div>
</template>

<style scoped>
.dashboard-row {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  margin-bottom: 24px;
}

.chart-card {
  background: rgba(255, 255, 255, 0.08) !important;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  border-radius: 16px !important;
}

.calendar-card {
  background: rgba(255, 255, 255, 0.08) !important;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  border-radius: 16px !important;
  margin-bottom: 24px;
}

@media (max-width: 992px) {
  .dashboard-row {
    grid-template-columns: 1fr;
  }
}
</style>
```

### 方法 2: 使用演示页面

访问 `http://localhost:5173/components-demo` 查看所有组件效果。

## 📊 数据格式说明

### 1. 趋势数据 (AccuracyTrend)
```javascript
const trendData = [
  { date: '12-26', accuracy: 0.89 },  // accuracy: 0-1
  { date: '12-27', accuracy: 0.92 },
  // ...
]
```

### 2. 日历数据 (StudyCalendar)
```javascript
const calendarData = [
  {
    date: '2025-12-26',
    count: 50,        // 练习题数
    duration: 120,    // 学习时长（分钟）
    accuracy: 0.85    // 正确率
  },
  // ...
]
```

### 3. 科目数据 (SubjectRadar)
```javascript
const subjectData = [
  { value: 85 },  // 行测
  { value: 78 },  // 申论
  { value: 92 },  // 数学
  { value: 88 },  // 英语
  { value: 75 }   // 专业课
]
```

### 4. 今日目标 (DailyGoals)
```javascript
const dailyGoals = [
  {
    title: '练习题目',
    current: 35,
    target: 50,
    unit: '题',
    icon: EditPen,
    color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    completed: false
  },
  // ...
]
```

## 🎨 布局建议

### 推荐布局 1: 网格布局
```
┌─────────────────┬─────────────────┐
│  进度环形图      │  正确率趋势      │
├─────────────────┼─────────────────┤
│  今日目标        │  科目雷达图      │
├─────────────────┴─────────────────┤
│         学习日历（全宽）            │
├─────────────────┬─────────────────┤
│  数据统计        │  最近活动        │
└─────────────────┴─────────────────┘
```

### 推荐布局 2: 卡片流
```
┌─────────────────────────────────────┐
│         欢迎横幅（全宽）             │
├─────────────────┬─────────────────┐
│  进度环形图      │  今日目标        │
├─────────────────┴─────────────────┤
│         正确率趋势（全宽）           │
├─────────────────┬─────────────────┤
│  科目雷达图      │  数据统计        │
├─────────────────┴─────────────────┤
│         学习日历（全宽）             │
└─────────────────────────────────────┘
```

## 🔧 API 集成

### 创建 API 函数

在 `exam/frontend/src/api/statistics.js` 中添加：

```javascript
// 获取正确率趋势
export function getAccuracyTrend(params) {
  return request({
    url: '/api/statistics/accuracy-trend',
    method: 'get',
    params
  })
}

// 获取学习日历数据
export function getStudyCalendar(params) {
  return request({
    url: '/api/statistics/calendar',
    method: 'get',
    params
  })
}

// 获取科目掌握度
export function getSubjectMastery(params) {
  return request({
    url: '/api/statistics/subject-mastery',
    method: 'get',
    params
  })
}

// 获取今日目标
export function getDailyGoals() {
  return request({
    url: '/api/daily-tasks/goals',
    method: 'get'
  })
}
```

### 后端 API 实现（可选）

如果后端还没有这些 API，可以先使用模拟数据：

```javascript
// 模拟数据
const mockTrendData = [
  { date: '12-20', accuracy: 0.82 },
  { date: '12-21', accuracy: 0.85 },
  { date: '12-22', accuracy: 0.88 },
  { date: '12-23', accuracy: 0.86 },
  { date: '12-24', accuracy: 0.90 },
  { date: '12-25', accuracy: 0.87 },
  { date: '12-26', accuracy: 0.89 }
]

// 在组件中使用
onMounted(() => {
  trendData.value = mockTrendData
})
```

## 💡 优化建议

### 1. 加载状态
```vue
<div v-loading="loading">
  <ProgressRing v-if="!loading" :value="data" />
</div>
```

### 2. 错误处理
```vue
<el-empty v-if="error" description="加载失败" />
<ProgressRing v-else :value="data" />
```

### 3. 骨架屏
```vue
<el-skeleton v-if="loading" :rows="5" animated />
<ProgressRing v-else :value="data" />
```

### 4. 数据缓存
```javascript
import { useStorage } from '@vueuse/core'

const cachedData = useStorage('dashboard-data', null)

if (cachedData.value) {
  data.value = cachedData.value
} else {
  const response = await fetchData()
  cachedData.value = response.data
  data.value = response.data
}
```

## 🎯 完整示例

查看 `exam/frontend/src/views/ComponentsDemo.vue` 获取完整的使用示例。

## 📱 响应式设计

所有组件都已包含响应式设计，会自动适配：
- 桌面端（> 992px）：2 列布局
- 平板端（768px - 992px）：2 列布局
- 移动端（< 768px）：1 列布局

## 🐛 常见问题

### Q: 图表不显示？
A: 确保容器有明确的高度，检查数据格式是否正确。

### Q: 动画卡顿？
A: 减少同时运行的动画数量，使用 `v-if` 延迟加载。

### Q: 数据不更新？
A: 确保使用 `ref()` 创建响应式数据。

## 📚 相关文档

- `COMPONENTS_USAGE_GUIDE.md` - 组件使用指南
- `PHASE1_COMPONENTS_CREATED.md` - 组件详细说明
- `UI_QUICK_START.md` - 快速开始

---

**准备好了吗？** 开始集成新组件，打造漂亮的 Dashboard！
