# 考试题目问题排查指南

## 问题：开始考试后没有显示做题界面

### 快速诊断

#### 步骤 1：检查浏览器控制台

1. 打开浏览器开发者工具（按 F12）
2. 切换到 **Console** 标签
3. 点击"开始考试"
4. 查看控制台输出，寻找以下信息：
   - `正在获取试卷详情，paperId: X`
   - `试卷API响应: {...}`
   - `试卷数据: {...}`
   - `题目数量: X`

#### 步骤 2：检查网络请求

1. 在开发者工具中切换到 **Network** 标签
2. 找到 `/api/exams/{paperId}?include_questions=true` 请求
3. 点击该请求，查看 **Response** 标签
4. 检查响应数据中是否有 `questions` 字段
5. 检查 `questions` 数组是否为空

**正常响应示例：**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "公务员考试模拟卷",
    "exam_type": "civil_service",
    "duration": 120,
    "total_score": 100,
    "questions": [
      {
        "id": 1,
        "content": "题目内容...",
        "question_type": "single_choice",
        "options": ["A", "B", "C", "D"],
        "order": 1,
        "score": 2
      }
      // ... 更多题目
    ]
  }
}
```

**异常响应示例：**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "公务员考试模拟卷",
    "questions": []  // ❌ 题目数组为空
  }
}
```

#### 步骤 3：检查后端日志

查看后端控制台输出：

```bash
cd exam/backend
# 如果使用 run.py
python run.py

# 查看日志输出
[DEBUG] 获取试卷 1, include_questions=True
[DEBUG] 试卷 1 包含 10 道题目
```

如果看到 `包含 0 道题目`，说明试卷确实没有题目。

### 解决方案

#### 方案 1：使用脚本检查试卷

```bash
cd exam/backend

# 检查所有试卷的题目情况
python check_paper_questions.py --check
```

输出示例：
```
============================================================
检查试卷题目情况
============================================================

找到 2 个已发布的试卷

试卷 ID: 1
试卷名称: 公务员考试模拟卷
考试类型: civil_service
考试时长: 120 分钟
总分: 100
题目数量: 0
⚠️  警告：该试卷没有题目！
------------------------------------------------------------

试卷 ID: 2
试卷名称: 研究生考试模拟卷
考试类型: postgraduate
考试时长: 180 分钟
总分: 150
题目数量: 20
✓ 该试卷有题目
------------------------------------------------------------
```

#### 方案 2：为试卷添加题目

如果发现试卷没有题目，可以使用脚本自动添加：

```bash
# 为试卷 ID 为 1 的试卷添加示例题目
python check_paper_questions.py --add 1
```

或者通过管理界面手动添加：

1. 登录管理员账号
2. 进入"试卷管理"页面
3. 选择要编辑的试卷
4. 点击"添加题目"
5. 从题库中选择题目并设置分值
6. 保存

#### 方案 3：使用种子数据脚本

如果数据库中完全没有数据，可以运行种子数据脚本：

```bash
cd exam/backend

# 运行种子数据脚本
python seed_exam_data.py
```

这将创建：
- 示例用户（包括管理员）
- 示例题目（各种类型）
- 示例试卷（包含题目）

### 数据库直接检查

如果需要直接查看数据库：

```bash
cd exam/backend/instance

# 使用 SQLite 命令行工具
sqlite3 exam.db

# 或者使用 Python
python
```

```python
# 在 Python 中检查
import sqlite3
conn = sqlite3.connect('instance/exam.db')
cursor = conn.cursor()

# 检查试卷
cursor.execute("SELECT id, name, is_published FROM exam_papers")
print("试卷列表:")
for row in cursor.fetchall():
    print(f"  ID: {row[0]}, 名称: {row[1]}, 已发布: {row[2]}")

# 检查试卷题目关联
cursor.execute("""
    SELECT ep.id, ep.name, COUNT(epq.id) as question_count
    FROM exam_papers ep
    LEFT JOIN exam_paper_questions epq ON ep.id = epq.paper_id
    GROUP BY ep.id
""")
print("\n试卷题目统计:")
for row in cursor.fetchall():
    print(f"  试卷 {row[0]} ({row[1]}): {row[2]} 道题目")

conn.close()
```

### 预防措施

#### 1. 在发布试卷前验证

修改 `exam/backend/app/services/exam_paper_service.py` 中的 `publish_paper` 方法已经包含了验证：

```python
def publish_paper(paper_id: int) -> ExamPaper:
    # ...
    # 检查试卷是否有题目
    question_count = ExamPaperQuestion.query.filter_by(paper_id=paper_id).count()
    if question_count == 0:
        raise RuntimeError('试卷必须至少包含一道题目才能发布')
    # ...
```

#### 2. 在开始考试前验证

修改 `exam/backend/app/services/exam_service.py` 中的 `start_exam` 方法已经包含了验证：

```python
def start_exam(user_id: int, paper_id: int) -> ExamSession:
    # ...
    # 验证试卷是否有题目
    question_count = ExamPaperQuestion.query.filter_by(paper_id=paper_id).count()
    if question_count == 0:
        raise RuntimeError('该试卷暂无题目，无法开始考试')
    # ...
```

#### 3. 前端显示题目数量

在试卷列表中显示题目数量，让用户知道试卷是否有题目。

### 常见错误信息

| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| "该试卷暂无题目，无法开始考试" | 试卷没有添加题目 | 使用管理界面或脚本添加题目 |
| "试卷不存在" | 试卷ID错误或已删除 | 检查试卷ID是否正确 |
| "试卷未发布，无法开始考试" | 试卷未发布 | 在管理界面发布试卷 |
| "已有进行中的考试，请先完成或提交" | 用户有未完成的考试 | 完成或提交之前的考试 |

### 联系支持

如果以上方法都无法解决问题，请提供以下信息：

1. 浏览器控制台的完整日志
2. 后端日志输出
3. 试卷ID和用户ID
4. `check_paper_questions.py --check` 的输出结果

## 相关文档

- [EXAM_NO_QUESTIONS_FIX.md](./EXAM_NO_QUESTIONS_FIX.md) - 详细的技术修复方案
- [SEED_DATA_GUIDE.md](./SEED_DATA_GUIDE.md) - 种子数据使用指南
- [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) - API 文档
