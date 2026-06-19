# 知识点关系图谱功能完成

## 📋 功能概述

知识点关系图谱是一个可视化工具，通过图形化方式展示知识点之间的依赖关系，帮助用户：
- 理解知识点结构和依赖关系
- 查看个人掌握度分布
- 获取个性化学习路径推荐
- 规划最优学习顺序

## ✅ 已完成功能

### 后端实现 (100%)

#### 1. 数据模型 (`app/models/knowledge_graph.py`)
- **KnowledgeRelation**: 知识点关系模型
  - 前置依赖关系 (prerequisite)
  - 相关关系 (related)
  - 相似关系 (similar)
  - 关系强度 (0-1)

- **UserKnowledgeMastery**: 用户知识点掌握度
  - 掌握度分数 (0-100)
  - 练习统计
  - 最近表现记录

#### 2. 业务服务 (`app/services/knowledge_graph_service.py`)
- `get_graph_data()`: 获取图谱数据（节点+边）
- `get_knowledge_detail()`: 获取知识点详情
- `get_learning_path()`: 智能学习路径推荐
- `update_mastery()`: 更新掌握度
- `_calculate_mastery_score()`: 掌握度计算算法
- `_calculate_recommendation_score()`: 推荐分数计算

#### 3. API 路由 (`app/routes/knowledge_graph.py`)
- `GET /api/knowledge-graph/data` - 获取图谱数据
- `GET /api/knowledge-graph/detail/:id` - 获取知识点详情
- `GET /api/knowledge-graph/path` - 获取学习路径
- `POST /api/knowledge-graph/mastery/update` - 更新掌握度

#### 4. 数据初始化
- `migrate_knowledge_graph.py`: 数据库迁移脚本
- `init_knowledge_graph.py`: 初始化示例数据
  - 创建知识点关系（30+条）
  - 生成示例掌握度数据

### 前端实现 (100%)

#### 1. 主页面 (`views/KnowledgeGraph.vue`)
- **图谱可视化**
  - ECharts Graph 力导向布局
  - 节点大小表示重要程度
  - 节点颜色表示掌握度
  - 边表示依赖关系
  - 支持缩放、平移、拖拽

- **筛选控制**
  - 科目筛选
  - 掌握度范围筛选
  - 实时刷新

- **知识点详情面板**
  - 掌握度环形图
  - 练习统计
  - 基本信息
  - 前置知识点列表
  - 后续知识点列表
  - 快速开始练习

- **学习路径面板**
  - 智能推荐Top 20
  - 推荐理由说明
  - 掌握度显示
  - 一键跳转详情

#### 2. API 客户端 (`api/knowledgeGraph.js`)
- 完整的 API 调用封装
- 统一的错误处理

#### 3. 路由配置
- 已添加 `/knowledge-graph` 路由

## 🎨 核心算法

### 1. 掌握度计算公式
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

### 2. 学习路径推荐算法
```python
推荐分数 = (
    未掌握优先分 (0-40分) +
    前置知识完成度 (0-30分) +
    重要程度 (0-20分) +
    难度适中 (0-10分)
)

优先级规则:
1. 前置知识点已掌握 (>70%)
2. 当前知识点未掌握 (<40%)
3. 重要程度高 (被多个知识点依赖)
4. 难度适中 (medium)
```

### 3. 重要程度计算
```python
importance = min(
    outgoing_relations_count * 2 +  # 被依赖次数
    question_count / 10,             # 题目数量
    10                               # 最大值10
)
```

## 📊 数据结构

### 图谱数据格式
```json
{
  "nodes": [
    {
      "id": "kp_1",
      "name": "变量与数据类型",
      "category": "未掌握",
      "mastery": 35.5,
      "importance": 8,
      "subject": "Python",
      "chapter": "第1章",
      "difficulty": "easy",
      "questionCount": 50,
      "practiceCount": 120,
      "correctRate": 65.5,
      "value": 35.5
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
    {"name": "未掌握", "color": "#f56c6c"},
    {"name": "部分掌握", "color": "#e6a23c"},
    {"name": "已掌握", "color": "#67c23a"}
  ]
}
```

## 🎯 功能特点

### 1. 可视化效果
- **力导向布局**: 自动排列节点位置
- **颜色编码**: 红→黄→绿表示掌握度
- **大小编码**: 节点大小表示重要程度
- **交互操作**: 点击、悬停、拖拽、缩放

### 2. 智能推荐
- **前置检查**: 确保前置知识已掌握
- **个性化**: 基于用户掌握度
- **优先级**: 未掌握的重要知识点优先
- **推荐理由**: 清晰说明推荐原因

### 3. 详细信息
- **掌握度分析**: 环形图+统计数据
- **关系展示**: 前置/后续/相关知识点
- **快速操作**: 一键开始练习
- **关联导航**: 点击跳转相关知识点

### 4. 筛选功能
- **科目筛选**: 按科目查看
- **掌握度筛选**: 未掌握/部分掌握/已掌握
- **实时更新**: 筛选后立即刷新图谱

## 📁 文件结构

```
backend/
├── app/
│   ├── models/
│   │   └── knowledge_graph.py           # 数据模型
│   ├── services/
│   │   └── knowledge_graph_service.py   # 业务逻辑
│   └── routes/
│       └── knowledge_graph.py           # API 路由
├── migrate_knowledge_graph.py           # 数据库迁移
└── init_knowledge_graph.py              # 数据初始化

frontend/
├── src/
│   ├── views/
│   │   └── KnowledgeGraph.vue           # 主页面 (700+ 行)
│   ├── api/
│   │   └── knowledgeGraph.js            # API 客户端
│   └── router/
│       └── index.js                     # 路由配置（已更新）
```

## 🚀 部署步骤

### 1. 数据库迁移
```bash
cd exam/backend
python migrate_knowledge_graph.py
```

### 2. 初始化数据
```bash
python init_knowledge_graph.py
```

### 3. 访问页面
```
http://localhost:5173/knowledge-graph
```

## 📝 使用说明

### 查看知识图谱
1. 访问知识图谱页面
2. 查看所有知识点及其关系
3. 节点颜色表示掌握度
4. 节点大小表示重要程度

### 筛选知识点
1. 选择科目（Python/数据结构/算法）
2. 选择掌握度范围
3. 点击刷新按钮

### 查看详情
1. 点击图谱中的节点
2. 右侧显示详情面板
3. 查看掌握度、练习统计
4. 查看前置和后续知识点
5. 点击"开始练习"跳转练习页面

### 学习路径
1. 点击"学习路径"按钮
2. 查看推荐的学习顺序
3. 查看推荐理由
4. 点击知识点查看详情

### 图谱操作
- **缩放**: 鼠标滚轮
- **平移**: 鼠标拖拽空白区域
- **拖动节点**: 鼠标拖拽节点
- **查看详情**: 点击节点
- **悬停提示**: 鼠标悬停在节点上

## 🎨 UI 设计特点

### 深色主题
- 玻璃态（Glassmorphism）设计
- 半透明背景
- 模糊效果
- 渐变色彩

### 视觉元素
- 环形进度图
- 渐变按钮
- 图标发光效果
- 平滑动画过渡

### 响应式设计
- 桌面端：侧边面板
- 移动端：全屏面板
- 自适应布局

## 🔧 技术实现

### 后端技术
- Flask Blueprint 模块化
- SQLAlchemy ORM
- 复杂查询优化
- 算法实现

### 前端技术
- Vue 3 Composition API
- ECharts Graph 图表
- 力导向布局算法
- Lucide Vue 图标
- Element Plus UI

### 核心功能
- 图数据结构
- 力导向布局
- 掌握度计算
- 路径推荐算法

## 📊 示例数据

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

## 🎯 核心优势

1. **可视化直观**: 图形化展示知识结构
2. **个性化推荐**: 基于掌握度智能推荐
3. **交互友好**: 丰富的交互操作
4. **算法科学**: 多维度计算掌握度
5. **美观界面**: 深色主题，流畅动画

## 🔄 与其他功能整合

### 练习系统
- 点击"开始练习"跳转练习页面
- 练习后自动更新掌握度
- 掌握度实时反映在图谱中

### 统计系统
- 掌握度数据来源于练习记录
- 正确率、练习次数统计
- 最近表现追踪

### 学习计划
- 可基于推荐路径制定学习计划
- 按顺序学习知识点
- 追踪学习进度

## 📈 未来扩展

### 短期优化
- [ ] 知识点搜索功能
- [ ] 自定义布局算法
- [ ] 导出图片功能
- [ ] 分享功能

### 中期功能
- [ ] 多科目切换动画
- [ ] 学习进度动画
- [ ] 协作学习（查看他人图谱）
- [ ] 知识点笔记集成

### 长期规划
- [ ] AI 智能推荐路径
- [ ] 个性化图谱定制
- [ ] 3D 可视化
- [ ] VR/AR 支持

## 🎉 总结

知识点关系图谱功能已完整实现，包括：
- ✅ 完整的后端 API（4个接口）
- ✅ 精美的图谱可视化
- ✅ 智能学习路径推荐
- ✅ 掌握度计算算法
- ✅ 详细的知识点信息
- ✅ 深色主题设计

用户可以通过图谱直观地了解知识结构，获取个性化学习建议，提升学习效率！

---

**实现时间**: 约4小时
**代码行数**: 约1500行
**功能完整度**: 100%
**测试状态**: 待测试
