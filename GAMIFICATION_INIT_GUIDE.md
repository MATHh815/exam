# 游戏化系统初始化指南

## 问题描述

点击"游戏化"菜单时出现"基于了未知的路径格式"错误。

**原因**: 用户的积分记录尚未创建。

---

## 快速修复

### 方法 1: 运行初始化脚本（推荐）

在 `exam/backend` 目录下运行：

```bash
cd exam/backend
python init_user_points.py
```

**这会**:
- 为所有现有用户创建积分记录
- 初始化积分为 0
- 初始化等级为 1

### 方法 2: 运行成就初始化（包含积分初始化）

```bash
cd exam/backend
python init_achievements.py
```

选择 "yes" 重新初始化。

### 方法 3: 自动创建（刷新页面）

系统会在首次访问时自动创建积分记录。

**操作**:
1. 刷新浏览器页面 (F5)
2. 重新点击"游戏化"菜单
3. 系统会自动创建记录

---

## 验证

初始化成功后，你应该能看到：

### 积分展示
- 等级徽章: Lv.1
- 总积分: 0
- 连续天数: 0
- 今日积分: 0

### 成就列表
- 显示"还没有获得任何成就"
- 或显示已解锁的成就

### 快速入口
- 每日任务卡片
- 成就系统卡片

---

## 完整初始化流程

如果你是第一次使用游戏化系统，请按以下顺序初始化：

### 1. 数据库迁移

```bash
cd exam/backend
python migrate_phase1.py
```

### 2. 初始化成就

```bash
python init_achievements.py
```

### 3. 初始化用户积分

```bash
python init_user_points.py
```

### 4. 重启后端服务器

```bash
# 停止当前服务器 (Ctrl+C)
python run.py
```

### 5. 刷新前端页面

在浏览器中按 `F5` 或 `Ctrl+R`

---

## 常见问题

### Q1: 运行脚本时报错 "No module named 'app'"

**解决方案**:
```bash
# 确保在 backend 目录下
cd exam/backend

# 设置 PYTHONPATH
set PYTHONPATH=%CD%

# 再次运行脚本
python init_user_points.py
```

### Q2: 数据库表不存在

**错误信息**: `no such table: user_points`

**解决方案**:
```bash
cd exam/backend
python migrate_phase1.py
```

### Q3: 刷新页面后仍然报错

**可能原因**:
1. 后端服务器未重启
2. 数据库未提交更改
3. 浏览器缓存问题

**解决方案**:
1. 重启后端服务器
2. 清除浏览器缓存 (Ctrl+Shift+Delete)
3. 强制刷新 (Ctrl+Shift+R)

### Q4: 积分显示为 0 是正常的吗？

**是的！** 这是正常的。

新用户的初始状态：
- 总积分: 0
- 等级: 1
- 连续天数: 0
- 今日积分: 0

**获取积分的方式**:
1. 完成练习
2. 完成考试
3. 完成每日任务
4. 解锁成就

---

## 测试游戏化功能

### 1. 查看积分

访问: `/profile` → 点击"游戏化"菜单

应该看到：
- 等级徽章 (Lv.1)
- 积分统计
- 成就列表（空）
- 快速入口

### 2. 查看成就系统

访问: `/achievements`

应该看到：
- 24个成就定义
- 成就分类（学习、连续、里程碑）
- 成就等级（铜牌、银牌、金牌）
- 筛选功能

### 3. 查看每日任务

访问: `/daily-tasks`

应该看到：
- 5个每日任务
- 任务进度
- 积分奖励
- 任务统计

---

## 获取积分

### 方法 1: 完成练习

1. 访问"智能练习"
2. 完成练习题目
3. 提交答案
4. 获得积分 = 得分 + 连续奖励

### 方法 2: 完成考试

1. 访问"模拟考试"
2. 完成考试
3. 提交答案
4. 获得积分 = 得分×2 + 连续奖励

### 方法 3: 完成每日任务

1. 访问"每日任务"
2. 完成任务目标
3. 自动获得积分

### 方法 4: 解锁成就

1. 达成成就条件
2. 自动解锁成就
3. 获得成就积分奖励

---

## 数据库检查

如果问题仍未解决，检查数据库：

### 检查表是否存在

```sql
-- 在 SQLite 中
.tables

-- 应该看到:
-- user_points
-- point_transactions
-- achievements
-- user_achievements
-- daily_tasks
```

### 检查用户积分记录

```sql
SELECT * FROM user_points WHERE user_id = YOUR_USER_ID;
```

如果没有记录，运行 `init_user_points.py`

### 检查成就定义

```sql
SELECT COUNT(*) FROM achievements;
```

应该返回 24。如果不是，运行 `init_achievements.py`

---

## 调试技巧

### 1. 查看后端日志

```bash
# 查看完整日志
cat exam/backend/logs/app.log

# 查看错误日志
cat exam/backend/logs/app_error.log

# 实时查看日志
tail -f exam/backend/logs/app.log
```

### 2. 查看浏览器控制台

按 `F12` 打开开发者工具：
- Console: 查看 JavaScript 错误
- Network: 查看 API 请求状态

### 3. 测试 API

```bash
# 测试积分 API
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:5000/api/points

# 测试成就 API
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:5000/api/achievements

# 测试每日任务 API
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:5000/api/daily-tasks
```

---

## 相关文档

- `API_CONNECTION_GUIDE.md` - API 连接问题
- `PHASE1_TASK15_INTEGRATION.md` - 系统集成指南
- `API_DOCUMENTATION.md` - API 文档

---

**创建时间**: 2024-12-26  
**维护者**: Kiro AI Assistant

