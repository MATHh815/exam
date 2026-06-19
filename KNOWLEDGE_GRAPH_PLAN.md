# 知识点关系图谱 - 实现计划

## 📋 功能概述

知识点关系图谱是一个可视化工具，展示知识点之间的依赖关系，帮助用户：
1. 理解知识点结构
2. 发现学习路径
3. 查看掌握度分布
4. 规划学习顺序

## 🎯 核心功能

### 1. 知识点图谱可视化
- 节点：知识点
- 边：依赖关系（prerequisite/related）
- 颜色：掌握度（红→黄→绿）
- 大小：重要程度
- 交互：点击查看详情

### 2. 掌握度计算
- 基于答题正确率
- 基于练习次数
- 基于最近表现
- 综合评分（0-100）

### 3. 学习路径推荐
- 基础知识点优先
- 未掌握知识点优先
- 依赖关系排序
- 个性化推荐

### 4. 知识点详情
- 知识点名称
- 掌握度百分比
- 相关题目数量
- 练习记录
- 推荐题目

## 🏗️ 技术架构

### 后端设计

#### 数据模型
```python
# 知识点模型（已存在）
class KnowledgePoint:
    - id
    - name
    - subject
    - chapter
    - difficulty
    - description

# 知识点关系模型（新增）
class KnowledgeRelation:
    - id
    - source_id (前置知识点)
    - target_id (目标知识点)
    - relation_type (prerequisite/related/similar)
    - strength (关系强度 0-1)

# 用户知识点掌握度（新增）
class UserKnowledgeMastery:
    - id
    - user_id
    - knowledge_point_id
    - mastery_score (0-100)
    - practice_count
    - correct_count
    - last_practice_date
    - updated_at
```

#### API 接口
```
GET  /api/knowledge-graph/data          # 获取图谱数据
GET  /api/knowledge-graph/mastery       # 获取掌握度数据
GET  /api/knowledge-graph/path          # 获取学习路径
GET  /api/knowledge-graph/detail/:id    # 获取知识点详情
POST /api/knowledge-graph/relations     # 创建知识点关系（管理员）
```

### 前端设计

#### 主要组件
```
KnowledgeGraph.vue          # 主页面
├── GraphCanvas.vue         # 图谱画布（ECharts Graph）
├── KnowledgeDetail.vue     # 知识点详情面板
├── PathRecommendation.vue  # 学习路径推荐
└── GraphControls.vue       # 图谱控制（筛选/缩放）
```

#### 可视化库选择
- **ECharts Graph** (推荐)
  - 优点：功能强大，配置灵活，性能好
  - 支持力导向布局
  - 支持交互操作
  - 已在项目中使用

- 备选：D3.js / Cytoscape.js

## 📊 数据结构

### 图谱数据格式
```json
{
  "nodes": [
    {
      "id": "kp_1",
      "name": "变量与数据类型",
      "category": "基础",
      "mastery": 85,
      "importance": 10,
      "subject": "Python",
      "chapter": "第1章",
      "questionCount": 50,
      "practiceCount": 120
    }
  ],
  "edges": [
    {
      "source": "kp_1",
      "target": "kp_2",
      "type": "prerequisite",
      "strength": 0.9
    }
  ],
  "categories": [
    {"name": "基础", "color": "#409eff"},
    {"name": "进阶", "color": "#67c23a"},
    {"name": "高级", "color": "#e6a23c"}
  ]
}
```

### 掌握度计算公式
```python
mastery_score = (
    correct_rate * 0.5 +           # 正确率权重 50%
    practice_factor * 0.3 +        # 练习次数权重 30%
    recent_performance * 0.2       # 最近表现权重 20%
) * 100

# 练习次数因子（0-1）
practice_factor = min(practice_count / 20, 1.0)

# 最近表现（最近10次的正确率）
recent_performance = recent_correct / recent_total
```

## 🎨 UI 设计

### 布局结构
```
┌─────────────────────────────────────────────────┐
│  知识点关系图谱                                    │
├─────────────────────────────────────────────────┤
│  [筛选] [科目▼] [章节▼] [掌握度▼] [重置]          │
├──────────────────────┬──────────────────────────┤
│                      │  知识点详情               │
│                      │  ┌──────────────────┐   │
│   图谱画布            │  │ 变量与数据类型    │   │
│   (ECharts Graph)    │  │ 掌握度: 85%      │   │
│                      │  │ 练习次数: 120    │   │
│                      │  │ 相关题目: 50     │   │
│                      │  └──────────────────┘   │
│                      │                          │
│                      │  学习路径推荐             │
│                      │  1. 变量与数据类型 ✓     │
│                      │  2. 控制流程 →          │
│                      │  3. 函数定义            │
└──────────────────────┴──────────────────────────┘
```

### 颜色方案
- **掌握度颜色**
  - 0-40%: #f56c6c (红色 - 未掌握)
  - 40-70%: #e6a23c (橙色 - 部分掌握)
  - 70-100%: #67c23a (绿色 - 已掌握)

- **关系类型颜色**
  - prerequisite: #409eff (蓝色 - 前置依赖)
  - related: #909399 (灰色 - 相关)
  - similar: #c0c4cc (浅灰 - 相似)

### 交互设计
- **节点点击**: 显示详情面板
- **节点悬停**: 高亮相关节点和边
- **节点拖拽**: 调整位置
- **画布缩放**: 鼠标滚轮
- **画布平移**: 鼠标拖拽

## 🔄 实现步骤

### Phase 1: 后端基础 (1天)
- [x] 创建数据模型
- [x] 实现掌握度计算服务
- [x] 创建 API 路由
- [x] 初始化示例数据

### Phase 2: 前端可视化 (2天)
- [x] 创建主页面组件
- [x] 集成 ECharts Graph
- [x] 实现图谱渲染
- [x] 添加交互功能

### Phase 3: 功能完善 (1天)
- [x] 知识点详情面板
- [x] 学习路径推荐
- [x] 筛选和搜索
- [x] 响应式设计

### Phase 4: 测试和优化 (0.5天)
- [x] API 测试
- [x] 前端测试
- [x] 性能优化
- [x] 文档编写

## 📝 示例数据

### Python 基础知识点关系
```
变量与数据类型 (基础)
  ├─→ 运算符与表达式 (基础)
  │    ├─→ 控制流程 (基础)
  │    │    ├─→ 函数定义 (进阶)
  │    │    │    ├─→ 递归 (进阶)
  │    │    │    └─→ 装饰器 (高级)
  │    │    └─→ 循环结构 (基础)
  │    └─→ 字符串操作 (基础)
  └─→ 列表与元组 (基础)
       ├─→ 字典与集合 (进阶)
       │    └─→ 推导式 (进阶)
       └─→ 迭代器与生成器 (高级)
```

## 🎯 成功指标

### 功能完整度
- [ ] 图谱正常显示
- [ ] 掌握度准确计算
- [ ] 交互流畅
- [ ] 路径推荐合理

### 性能指标
- [ ] 100个节点渲染 < 2秒
- [ ] 交互响应 < 100ms
- [ ] 内存占用 < 100MB

### 用户体验
- [ ] 界面美观
- [ ] 操作直观
- [ ] 信息清晰
- [ ] 响应式适配

## 🚀 未来扩展

### 短期
- [ ] 知识点搜索
- [ ] 自定义布局
- [ ] 导出图片
- [ ] 分享功能

### 中期
- [ ] 多科目切换
- [ ] 学习进度动画
- [ ] 协作学习
- [ ] 知识点笔记

### 长期
- [ ] AI 推荐路径
- [ ] 个性化图谱
- [ ] 3D 可视化
- [ ] VR/AR 支持

---

**预计完成时间**: 4-5天
**技术难度**: ⭐⭐⭐⭐ (4/5)
**用户价值**: ⭐⭐⭐⭐⭐ (5/5)
