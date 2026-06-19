# 学习计划显示问题修复

## 问题描述

创建学习计划后，在"进行中"标签页中看不到创建的计划。

## 问题原因

前端代码访问 API 响应数据的路径不正确：

- **后端返回**: `{ success: true, data: { plans: [...], count: 5 } }`
- **前端访问**: `res.plans` ❌
- **应该访问**: `res.data.plans` ✓

## 修复方案

### 修改文件: `exam/frontend/src/views/StudyPlans.vue`

```javascript
// 修改前
const fetchPlans = async () => {
  loading.value = true
  try {
    const res = await getStudyPlans()
    plans.value = res.plans || []  // ❌ 错误
  } catch (error) {
    ElMessage.error('获取学习计划失败')
  } finally {
    loading.value = false
  }
}

// 修改后
const fetchPlans = async () => {
  loading.value = true
  try {
    const res = await getStudyPlans()
    console.log('获取到的学习计划数据:', res)
    plans.value = res.data?.plans || []  // ✓ 正确
  } catch (error) {
    console.error('获取学习计划失败:', error)
    ElMessage.error('获取学习计划失败')
  } finally {
    loading.value = false
  }
}
```

## 测试步骤

1. **启动后端服务器**:
   ```bash
   cd exam/backend
   python run.py
   ```

2. **启动前端开发服务器**:
   ```bash
   cd exam/frontend
   npm run dev
   ```

3. **测试 API**（可选）:
   ```bash
   cd exam/backend
   python test_study_plan_api.py
   ```

4. **在浏览器中测试**:
   - 访问 `http://localhost:5173`
   - 登录系统
   - 进入"学习计划"页面
   - 点击"创建计划"按钮
   - 填写计划信息并提交
   - 查看"进行中"标签页，应该能看到刚创建的计划

## 预期结果

- 创建计划后，计划会立即显示在"进行中"标签页
- 计划卡片显示计划名称、日期范围、进度等信息
- 可以查看、编辑、删除计划

## 其他可能的问题

如果修复后仍然看不到计划，请检查：

1. **浏览器控制台**：查看是否有 JavaScript 错误
2. **网络请求**：在开发者工具的 Network 标签中查看 API 请求是否成功
3. **后端日志**：查看后端是否正确处理了请求
4. **数据库**：确认数据是否正确保存到数据库中

## 调试命令

```bash
# 检查数据库中的学习计划
cd exam/backend
python -c "from app import create_app, db; from app.models.study_plan import StudyPlan; app = create_app(); app.app_context().push(); plans = StudyPlan.query.all(); print(f'共有 {len(plans)} 个学习计划'); [print(f'- {p.name} (ID: {p.id}, 状态: {p.status})') for p in plans]"
```
