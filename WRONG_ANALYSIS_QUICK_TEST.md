# 错题智能分析 - 快速测试指南

## 🚀 快速启动

### 1. 启动项目
```bash
cd exam
start_all.bat
```

等待后端和前端都启动完成。

### 2. 访问页面
```
前端: http://localhost:5173
后端: http://localhost:5000
```

### 3. 登录
```
用户名: student
密码: student123
```

---

## 🔍 测试步骤

### Step 1: 访问错题分析页面

1. 登录后，在侧边栏或导航栏找到"错题分析"
2. 或直接访问: `http://localhost:5173/wrong-analysis`

### Step 2: 查看错题概览

检查以下内容：
- [ ] 错题总数显示正确
- [ ] 错题率显示正确
- [ ] 改善率显示正确（可能为0）
- [ ] 练习总数显示正确

### Step 3: 查看错题趋势图

检查以下内容：
- [ ] 折线图正常显示
- [ ] 可以切换时间范围（7/30/90天）
- [ ] Hover 显示详细数据
- [ ] 图表动画流畅

### Step 4: 查看错题分布图

检查以下内容：
- [ ] 饼图正常显示
- [ ] 可以切换维度（科目/题型）
- [ ] 图例显示正确
- [ ] Hover 显示百分比

### Step 5: 查看高频错题

检查以下内容：
- [ ] 列表正常显示
- [ ] 显示题目内容（截断）
- [ ] 显示科目和题型标签
- [ ] 显示错误次数

### Step 6: 查看薄弱知识点

检查以下内容：
- [ ] 卡片列表正常显示
- [ ] 进度条颜色正确（红/橙/绿）
- [ ] 掌握度百分比正确
- [ ] 练习统计正确

### Step 7: 查看学习建议

检查以下内容：
- [ ] 建议列表正常显示
- [ ] 建议内容合理
- [ ] 图标显示正常

---

## 🧪 API 测试

### 方法 1: 使用测试脚本

```bash
cd exam/backend
python test_wrong_analysis_api.py
```

预期输出：
```
开始测试错题分析 API...
✓ 登录成功，token: eyJ0eXBlIjoiSldU...

=== 测试错题概览 ===
状态码: 200
响应: {
  "success": true,
  "data": {...}
}

=== 测试错题分布 ===
...

✓ 所有测试完成！
```

### 方法 2: 使用 curl

```bash
# 1. 登录获取 token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"student","password":"student123"}'

# 2. 使用 token 测试 API（替换 <token>）
curl -H "Authorization: Bearer <token>" \
  http://localhost:5000/api/statistics/wrong-questions/overview?days=30
```

### 方法 3: 使用 Postman

1. 导入以下请求：
   - POST `/api/auth/login` - 登录
   - GET `/api/statistics/wrong-questions/overview` - 错题概览
   - GET `/api/statistics/wrong-questions/distribution` - 错题分布
   - GET `/api/statistics/wrong-questions/frequent` - 高频错题
   - GET `/api/statistics/wrong-questions/trend` - 错题趋势
   - GET `/api/statistics/wrong-questions/weak-points` - 薄弱知识点
   - GET `/api/statistics/wrong-questions/suggestions` - 学习建议

2. 设置 Authorization: Bearer <token>

---

## 📱 响应式测试

### 桌面端测试
1. 浏览器窗口 > 992px
2. 检查 2列布局
3. 检查图表大小

### 平板端测试
1. 浏览器窗口 768-992px
2. 检查布局调整
3. 检查图表自适应

### 移动端测试
1. 浏览器窗口 < 768px
2. 检查 1列布局
3. 检查触摸交互

---

## 🐛 常见问题

### Q1: 页面显示"暂无数据"？

**原因**: 用户还没有练习记录或错题记录

**解决方案**:
1. 先去做一些练习题
2. 故意做错几道题
3. 刷新错题分析页面

### Q2: 图表不显示？

**原因**: 可能是数据加载失败或图表初始化失败

**解决方案**:
1. 打开浏览器控制台查看错误
2. 检查 API 是否正常返回数据
3. 刷新页面重试

### Q3: API 返回 401 错误？

**原因**: Token 过期或无效

**解决方案**:
1. 重新登录
2. 检查 token 是否正确设置

### Q4: 后端报错？

**原因**: 可能是数据库查询失败

**解决方案**:
1. 检查后端日志
2. 确认数据库表存在
3. 检查数据格式

---

## ✅ 测试检查清单

### 功能测试
- [ ] 错题概览数据正确
- [ ] 错题趋势图正常
- [ ] 错题分布图正常
- [ ] 高频错题列表正常
- [ ] 薄弱知识点正常
- [ ] 学习建议正常
- [ ] 时间范围切换正常
- [ ] 维度切换正常

### UI 测试
- [ ] 布局美观
- [ ] 颜色搭配合理
- [ ] 字体大小适中
- [ ] 间距合理
- [ ] 动画流畅
- [ ] 响应式正常

### 性能测试
- [ ] 页面加载快速（< 2秒）
- [ ] 图表渲染流畅
- [ ] 无明显卡顿
- [ ] 内存占用正常

### 兼容性测试
- [ ] Chrome 正常
- [ ] Firefox 正常
- [ ] Edge 正常
- [ ] Safari 正常（Mac）
- [ ] 移动端浏览器正常

---

## 📊 测试数据

### 如果没有足够的测试数据

可以手动创建一些练习记录：

```python
# exam/backend/create_test_data.py
from app import create_app, db
from app.models.practice import PracticeRecord
from datetime import datetime, timedelta
import random

app = create_app()

with app.app_context():
    user_id = 2  # student 用户ID
    
    # 创建30天的练习记录
    for i in range(30):
        date = datetime.now() - timedelta(days=i)
        
        # 每天10-20题
        for j in range(random.randint(10, 20)):
            record = PracticeRecord(
                user_id=user_id,
                question_id=random.randint(1, 100),
                is_correct=random.random() > 0.3,  # 30%错题率
                time_spent=random.randint(30, 120),
                created_at=date
            )
            db.session.add(record)
    
    db.session.commit()
    print('测试数据创建完成！')
```

---

## 🎯 预期结果

### 正常情况
- 所有数据正常显示
- 图表渲染正确
- 学习建议合理
- 无错误提示

### 异常情况
- 如果没有数据，显示"暂无数据"
- 如果 API 失败，显示错误提示
- 如果 token 过期，跳转到登录页

---

## 📝 测试报告模板

```markdown
# 错题分析测试报告

**测试时间**: 2025-12-26
**测试人员**: [你的名字]
**浏览器**: Chrome 120
**设备**: Windows 11

## 测试结果

### 功能测试
- [x] 错题概览 - 通过
- [x] 错题趋势 - 通过
- [x] 错题分布 - 通过
- [x] 高频错题 - 通过
- [x] 薄弱知识点 - 通过
- [x] 学习建议 - 通过

### UI 测试
- [x] 布局正常
- [x] 响应式正常
- [x] 动画流畅

### 性能测试
- [x] 加载速度快
- [x] 无卡顿

## 发现的问题
无

## 建议
无

## 总体评价
✅ 测试通过，功能正常
```

---

## 🎉 测试完成

如果所有测试都通过，恭喜！错题智能分析系统已经可以正常使用了！

**下一步**:
1. 收集用户反馈
2. 优化算法和界面
3. 继续开发其他功能（夜间模式、学习报告等）

