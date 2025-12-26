# 统计模块实现文档

## 概述

统计模块为用户提供全面的学习数据分析和可视化功能，帮助用户了解学习进度、掌握薄弱环节、追踪学习趋势。

## 实现内容

### 1. 统计 API 封装 (statistics.js)

实现了四个核心 API 接口的封装：

#### 1.1 获取学习概览 (getOverview)
- **功能**: 获取用户的学习概览统计数据
- **参数**: 
  - `start_date`: 开始日期（可选，格式：YYYY-MM-DD）
  - `end_date`: 结束日期（可选，格式：YYYY-MM-DD）
- **返回数据**:
  - `total_practice`: 练习题总数
  - `total_correct`: 正确题数
  - `accuracy`: 正确率
  - `total_duration`: 学习时长（分钟）
  - `total_exams`: 考试次数
  - `study_days`: 学习天数
  - `wrong_count`: 错题数

#### 1.2 获取知识点分析 (getKnowledgeAnalysis)
- **功能**: 获取按知识点统计的学习数据
- **参数**: 
  - `start_date`: 开始日期（可选）
  - `end_date`: 结束日期（可选）
- **返回数据**:
  - `knowledge_points`: 知识点数组
    - `subject`: 科目
    - `chapter`: 章节
    - `total_count`: 答题总数
    - `correct_count`: 正确数
    - `accuracy`: 正确率
    - `is_weak`: 是否为薄弱项

#### 1.3 获取学习趋势 (getTrend)
- **功能**: 获取指定天数内的学习趋势数据
- **参数**: 
  - `days`: 天数（默认7天，最多365天）
- **返回数据**:
  - `trend`: 趋势数据数组
    - `date`: 日期
    - `practice_count`: 练习题数
    - `correct_count`: 正确题数
    - `accuracy`: 正确率
    - `study_duration`: 学习时长
    - `exam_count`: 考试次数

#### 1.4 获取考试统计 (getExamStatistics)
- **功能**: 获取考试历史统计数据
- **参数**: 
  - `start_date`: 开始日期（可选）
  - `end_date`: 结束日期（可选）
- **返回数据**:
  - `total_exams`: 考试总次数
  - `average_score`: 平均分
  - `average_accuracy`: 平均正确率
  - `highest_score`: 最高分
  - `lowest_score`: 最低分
  - `recent_exams`: 最近考试记录

### 2. 统计图表组件

#### 2.1 StatisticsChart.vue - 通用统计图表组件
- **功能**: 提供柱状图、折线图、饼图三种图表类型
- **Props**:
  - `type`: 图表类型（bar/line/pie）
  - `title`: 图表标题
  - `data`: 图表数据
  - `height`: 图表高度（默认400px）
  - `showLegend`: 是否显示图例（默认true）
- **特性**:
  - 基于 ECharts 实现
  - 支持自适应调整大小
  - 提供交互式提示框
  - 支持多种数据系列

#### 2.2 KnowledgeRadar.vue - 知识点雷达图组件
- **功能**: 以雷达图形式展示各知识点的掌握情况
- **Props**:
  - `title`: 图表标题（默认"知识点掌握情况"）
  - `knowledgePoints`: 知识点数据数组
  - `height`: 图表高度（默认500px）
- **特性**:
  - 直观展示多个知识点的正确率
  - 支持悬停查看详细信息
  - 自动计算雷达图指标
  - 渐变色填充区域

#### 2.3 TrendLine.vue - 学习趋势折线图组件
- **功能**: 展示一段时间内的学习趋势变化
- **Props**:
  - `title`: 图表标题（默认"学习趋势"）
  - `trendData`: 趋势数据数组
  - `height`: 图表高度（默认400px）
  - `showDataZoom`: 是否显示数据缩放（默认false）
- **特性**:
  - 多条折线展示不同指标
  - 双Y轴设计（题数/次数 和 正确率/时长）
  - 平滑曲线效果
  - 支持数据缩放（适用于长时间数据）
  - 区域填充效果

### 3. 统计页面 (Statistics.vue)

#### 3.1 页面结构
统计页面分为四个主要区域：

1. **日期范围选择器**
   - 支持选择自定义日期范围
   - 影响学习概览、知识点分析和考试统计

2. **学习概览卡片**
   - 展示6个核心指标
   - 响应式网格布局
   - 加载状态提示

3. **学习趋势卡片**
   - 天数选择器（7/14/30/90天）
   - TrendLine 组件展示趋势
   - 空状态提示

4. **知识点分析卡片**
   - 左侧：KnowledgeRadar 雷达图
   - 右侧：知识点详情表格
   - 表格支持排序
   - 正确率标签颜色区分（绿色≥80%，黄色≥60%，红色<60%）
   - 薄弱项标记

5. **考试统计卡片**
   - 展示考试次数、平均分、最高分、平均正确率
   - 空状态提示

#### 3.2 功能特性
- **数据加载**: 页面加载时自动获取所有统计数据
- **日期筛选**: 支持按日期范围筛选数据
- **响应式设计**: 适配不同屏幕尺寸
- **加载状态**: 每个区域独立的加载状态
- **错误处理**: 友好的错误提示
- **空状态**: 无数据时显示空状态提示

#### 3.3 路由配置
- **路径**: `/statistics`
- **名称**: `statistics`
- **权限**: 需要登录（requiresAuth: true）

#### 3.4 导航入口
在 Dashboard 页面添加了"学习统计"按钮，方便用户快速访问。

## 技术栈

- **Vue 3**: 使用 Composition API
- **Element Plus**: UI 组件库
- **ECharts 5**: 图表库
- **vue-echarts**: Vue 3 的 ECharts 封装
- **Axios**: HTTP 请求

## 使用示例

### 在其他页面中使用图表组件

```vue
<template>
  <div>
    <!-- 使用通用图表组件 -->
    <StatisticsChart
      type="bar"
      title="答题统计"
      :data="chartData"
      height="400px"
    />

    <!-- 使用雷达图组件 -->
    <KnowledgeRadar
      :knowledge-points="knowledgeData"
      height="500px"
    />

    <!-- 使用趋势图组件 -->
    <TrendLine
      :trend-data="trendData"
      :show-data-zoom="true"
      height="450px"
    />
  </div>
</template>

<script setup>
import StatisticsChart from '@/components/StatisticsChart.vue'
import KnowledgeRadar from '@/components/KnowledgeRadar.vue'
import TrendLine from '@/components/TrendLine.vue'

// 准备数据...
</script>
```

### 调用统计 API

```javascript
import { getOverview, getKnowledgeAnalysis, getTrend, getExamStatistics } from '@/api/statistics'

// 获取学习概览
const overview = await getOverview({
  start_date: '2024-01-01',
  end_date: '2024-12-31'
})

// 获取知识点分析
const knowledge = await getKnowledgeAnalysis({
  start_date: '2024-01-01',
  end_date: '2024-12-31'
})

// 获取学习趋势
const trend = await getTrend({ days: 30 })

// 获取考试统计
const examStats = await getExamStatistics({
  start_date: '2024-01-01',
  end_date: '2024-12-31'
})
```

## 响应式设计

统计页面针对不同屏幕尺寸进行了优化：

- **桌面端**: 多列布局，充分利用屏幕空间
- **平板端**: 自适应列数，保持良好的可读性
- **移动端**: 单列布局，优化触摸操作

## 数据可视化设计原则

1. **清晰性**: 使用合适的图表类型展示数据
2. **一致性**: 统一的颜色方案和样式
3. **交互性**: 提供悬停提示和数据缩放
4. **响应性**: 图表自适应容器大小
5. **可访问性**: 提供文字说明和空状态提示

## 后续优化建议

1. **数据导出**: 支持导出统计数据为 Excel/PDF
2. **对比分析**: 支持多个时间段的对比
3. **目标设置**: 允许用户设置学习目标并追踪进度
4. **智能建议**: 基于统计数据提供学习建议
5. **分享功能**: 支持分享学习成果
6. **缓存优化**: 缓存统计数据减少请求次数

## 验证需求

本模块实现满足以下需求：

- ✅ 需求 6.1: 学习概览统计
- ✅ 需求 6.2: 知识点分析
- ✅ 需求 6.3: 学习趋势展示
- ✅ 需求 6.4: 考试历史统计
- ✅ 需求 6.5: 时间范围过滤

## 相关文件

### API 层
- `exam/frontend/src/api/statistics.js` - 统计 API 封装
- `exam/frontend/src/api/index.js` - API 统一导出

### 组件层
- `exam/frontend/src/components/StatisticsChart.vue` - 通用图表组件
- `exam/frontend/src/components/KnowledgeRadar.vue` - 知识点雷达图
- `exam/frontend/src/components/TrendLine.vue` - 学习趋势折线图

### 视图层
- `exam/frontend/src/views/Statistics.vue` - 统计页面
- `exam/frontend/src/views/Dashboard.vue` - 仪表盘（添加了统计入口）

### 路由
- `exam/frontend/src/router/index.js` - 路由配置

## 总结

统计模块为用户提供了全面的学习数据分析功能，通过直观的图表和数据展示，帮助用户：

1. 了解整体学习情况
2. 识别薄弱知识点
3. 追踪学习进度
4. 分析考试表现
5. 制定学习计划

模块采用组件化设计，图表组件可复用，易于维护和扩展。
