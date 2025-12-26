# 数据导入导出功能

## 概述

数据导入导出功能允许管理员将系统数据导出为 JSON 或 SQL 格式，并从这些格式导入数据。这对于数据备份、迁移和恢复非常有用。

## API 端点

### 导出数据

#### 导出为 JSON
```
GET /api/data/export/json
```
- **权限**: 需要管理员权限
- **响应**: JSON 文件下载
- **文件名格式**: `exam_data_export_YYYYMMDD_HHMMSS.json`

#### 导出为 SQL
```
GET /api/data/export/sql
```
- **权限**: 需要管理员权限
- **响应**: SQL 文件下载
- **文件名格式**: `exam_data_export_YYYYMMDD_HHMMSS.sql`

### 导入数据

#### 从 JSON 导入
```
POST /api/data/import/json
```
- **权限**: 需要管理员权限
- **请求体**: 
  - `file`: JSON 文件（必需）
  - `clear_existing`: 是否清空现有数据（可选，默认 false）
- **响应**: 导入统计信息

#### 从 SQL 导入
```
POST /api/data/import/sql
```
- **权限**: 需要管理员权限
- **请求体**: 
  - `file`: SQL 文件（必需）
- **响应**: 导入统计信息

## 使用示例

### 使用 curl 导出数据

```bash
# 导出为 JSON
curl -X GET http://localhost:5000/api/data/export/json \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -o backup.json

# 导出为 SQL
curl -X GET http://localhost:5000/api/data/export/sql \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -o backup.sql
```

### 使用 curl 导入数据

```bash
# 从 JSON 导入（不清空现有数据）
curl -X POST http://localhost:5000/api/data/import/json \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "file=@backup.json"

# 从 JSON 导入（清空现有数据）
curl -X POST http://localhost:5000/api/data/import/json \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "file=@backup.json" \
  -F "clear_existing=true"

# 从 SQL 导入
curl -X POST http://localhost:5000/api/data/import/sql \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "file=@backup.sql"
```

## 数据格式

### JSON 格式

JSON 导出包含元数据和数据两部分：

```json
{
  "metadata": {
    "export_time": "2024-01-01T00:00:00",
    "version": "1.0.0"
  },
  "data": {
    "users": [...],
    "questions": [...],
    "exam_papers": [...],
    ...
  }
}
```

### SQL 格式

SQL 导出包含标准的 INSERT 语句：

```sql
-- 数据导出
-- 导出时间: 2024-01-01T00:00:00
-- 版本: 1.0.0

-- 表: users
INSERT INTO users (id, username, email, ...) VALUES (1, 'admin', 'admin@example.com', ...);

-- 表: questions
INSERT INTO questions (id, exam_type, content, ...) VALUES (1, 'civil_service', '题目内容', ...);
```

## 导出顺序

数据按照以下顺序导出（考虑外键依赖关系）：

1. User（用户）
2. Question（题目）
3. ExamPaper（试卷）
4. ExamPaperQuestion（试卷题目关联）
5. ExamSession（考试会话）
6. ExamResult（考试结果）
7. PracticeRecord（练习记录）
8. WrongQuestion（错题本）
9. StudyStatistics（学习统计）

## 注意事项

1. **权限要求**: 所有导入导出操作都需要管理员权限
2. **数据一致性**: 导入时会保持数据的完整性和一致性
3. **清空数据**: 使用 `clear_existing=true` 时会清空所有现有数据，请谨慎使用
4. **JSON 字段**: 系统会正确处理 JSON 类型字段（如题目的 options 和 tags）
5. **时间戳**: 时间戳会以 ISO 8601 格式导出和导入

## 测试

数据导入导出功能包含完整的单元测试和属性测试：

```bash
# 运行所有数据服务测试
pytest tests/test_data_service.py -v

# 运行属性测试
pytest tests/test_data_service.py::TestDataService::test_property_json_roundtrip_consistency -v
pytest tests/test_data_service.py::TestDataService::test_property_sql_roundtrip_consistency -v
```

属性测试验证了**数据导出往返一致性**（Property 15）：
- 对于任意数据集，导出后再导入应该得到相同的数据
- 测试覆盖 JSON 和 SQL 两种格式
- 每个测试运行 20 个随机生成的示例

## 故障排除

### 导入失败

如果导入失败，检查：
1. 文件格式是否正确
2. 是否有足够的权限
3. 数据库连接是否正常
4. 日志文件中的详细错误信息

### 数据不一致

如果导入后数据不一致：
1. 确认导出和导入使用相同的格式
2. 检查是否有外键约束冲突
3. 验证 JSON 字段是否正确解析
