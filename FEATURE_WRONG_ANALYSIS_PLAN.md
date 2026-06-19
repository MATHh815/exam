# 错题智能分析系统 - 实施计划

## 📋 功能概述

为用户提供深度的错题分析，帮助识别薄弱环节，提供针对性的学习建议。

## 🎯 核心功能

### 1. 错题分析 Dashboard
- 错题总览（总数、分布、趋势）
- 错题分布图表（按科目/题型/知识点）
- 高频错题 Top 10
- 错题趋势分析
- 薄弱知识点识别

### 2. 智能分析
- 错题率计算
- 知识点掌握度评估
- 学习建议生成
- 复习优先级排序

### 3. 数据导出
- 错题列表导出（Excel/PDF）
- 分析报告导出

## 🏗️ 技术架构

### 后端 API

#### 1. 错题统计 API
```python
GET /api/statistics/wrong-questions/overview
返回：
{
  "total_wrong": 150,
  "wrong_rate": 0.25,
  "improvement_rate": 0.15,  # 相比上周
  "by_subject": [...],
  "by_type": [...],
  "by_knowledge": [...]
}
```

#### 2. 错题分布 API
```python
GET /api/statistics/wrong-questions/distribution
参数：dimension (subject/type/knowledge)
返回：分布数据
```

#### 3. 高频错题 API
```python
GET /api/statistics/wrong-questions/frequent
返回：Top 10 错题
```

#### 4. 错题趋势 API
```python
GET /api/statistics/wrong-questions/trend
参数：days (默认30天)
返回：每日错题数和错题率
```

#### 5. 薄弱知识点 API
```python
GET /api/statistics/weak-points
返回：掌握度最低的知识点
```

### 前端页面

#### 1. 错题分析页面
路径：`/wrong-analysis`

组件结构：
```
WrongAnalysis.vue
├─ 错题概览卡片
├─ 错题分布图表（饼图/柱状图）
├─ 高频错题列表
├─ 错题趋势图（折线图）
├─ 薄弱知识点卡片
└─ 学习建议面板
```

#### 2. 新增图表组件
- `WrongDistributionChart.vue` - 错题分布图
- `FrequentWrongList.vue` - 高频错题列表
- `WeakPointsCard.vue` - 薄弱知识点卡片

## 📊 数据模型

利用现有的 `PracticeRecord` 表：
```python
# 不需要新增表，使用现有数据
PracticeRecord:
  - is_correct (False 表示错题)
  - question_id
  - created_at
  - time_spent
```

## 🎨 UI 设计

### 页面布局
```
┌─────────────────────────────────────────────┐
│         错题智能分析                         │
├──────────────────────┬──────────────────────┤
│  错题总览             │  错题趋势图           │
│  - 总数 150          │  (30天折线图)         │
│  - 错题率 25%        │                      │
│  - 改善率 +15%       │                      │
├──────────────────────┴──────────────────────┤
│         错题分布（按科目/题型/知识点）        │
│         (饼图 + 柱状图)                      │
├──────────────────────┬──────────────────────┤
│  高频错题 Top 10      │  薄弱知识点           │
│  (列表)              │  (卡片)              │
├──────────────────────┴──────────────────────┤
│         智能学习建议                         │
└─────────────────────────────────────────────┘
```

### 配色方案
- 错题：`#ef4444` (红色)
- 改善：`#10b981` (绿色)
- 警告：`#f59e0b` (橙色)
- 信息：`#3b82f6` (蓝色)

## 📝 实施步骤

### Step 1: 后端 API 开发
1. 创建统计服务 `wrong_analysis_service.py`
2. 实现 5 个分析 API
3. 添加路由 `wrong_analysis.py`
4. 编写测试

### Step 2: 前端组件开发
1. 创建错题分析页面
2. 创建图表组件
3. 创建 API 调用函数
4. 集成到路由

### Step 3: 测试与优化
1. 功能测试
2. 性能优化
3. UI 调整

## 🚀 开始实施

现在开始实施 Step 1...
