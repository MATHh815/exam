# API 文档

## 概述

考公考研考编系统提供 RESTful API，所有 API 端点都以 `/api` 为前缀。

**基础 URL**: `http://localhost:5000/api`

**认证方式**: JWT (JSON Web Token)

**内容类型**: `application/json`

## 目录

- [认证接口](#认证接口)
- [题库接口](#题库接口)
- [练习接口](#练习接口)
- [考试接口](#考试接口)
- [统计接口](#统计接口)
- [数据导入导出接口](#数据导入导出接口)
- [积分系统接口](#积分系统接口)
- [成就系统接口](#成就系统接口)
- [每日任务接口](#每日任务接口)
- [响应格式](#响应格式)
- [错误代码](#错误代码)

## 通用说明

### 请求头

所有需要认证的接口都需要在请求头中包含 JWT 令牌：

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

### 响应格式

#### 成功响应

```json
{
  "success": true,
  "data": { ... },
  "message": "操作成功",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### 错误响应

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": { ... }
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### 分页响应

```json
{
  "success": true,
  "data": {
    "items": [ ... ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 100,
      "total_pages": 5
    }
  }
}
```

---

## 认证接口

### 用户注册

注册新用户账户。

**端点**: `POST /api/auth/register`

**认证**: 不需要

**请求体**:

```json
{
  "username": "string (3-50字符)",
  "password": "string (8-128字符)",
  "email": "string (有效邮箱)",
  "nickname": "string (可选)"
}
```

**响应**: `201 Created`

```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "username": "testuser",
      "email": "test@example.com",
      "nickname": "测试用户",
      "role": "user",
      "created_at": "2024-01-01T00:00:00Z"
    }
  },
  "message": "注册成功"
}
```

**错误**:
- `400` - 验证错误（用户名/邮箱已存在）
- `500` - 服务器错误

---

### 用户登录

用户登录并获取访问令牌。

**端点**: `POST /api/auth/login`

**认证**: 不需要

**请求体**:

```json
{
  "username": "string",
  "password": "string"
}
```

**响应**: `200 OK`

```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
      "id": 1,
      "username": "testuser",
      "email": "test@example.com",
      "role": "user"
    }
  },
  "message": "登录成功"
}
```

**错误**:
- `401` - 用户名或密码错误
- `500` - 服务器错误

---

### 刷新令牌

使用刷新令牌获取新的访问令牌。

**端点**: `POST /api/auth/refresh`

**认证**: 需要（刷新令牌）

**请求头**:
```
Authorization: Bearer <refresh_token>
```

**响应**: `200 OK`

```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

---

### 获取用户信息

获取当前登录用户的详细信息。

**端点**: `GET /api/auth/profile`

**认证**: 需要

**响应**: `200 OK`

```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "username": "testuser",
      "email": "test@example.com",
      "nickname": "测试用户",
      "avatar": "https://example.com/avatar.jpg",
      "role": "user",
      "created_at": "2024-01-01T00:00:00Z"
    }
  }
}
```

---

### 更新用户信息

更新当前用户的个人信息。

**端点**: `PUT /api/auth/profile`

**认证**: 需要

**请求体**:

```json
{
  "nickname": "string (可选)",
  "email": "string (可选)",
  "avatar": "string (可选)"
}
```

**响应**: `200 OK`

```json
{
  "success": true,
  "data": {
    "user": { ... }
  },
  "message": "更新成功"
}
```

---

## 题库接口

### 获取题目列表

获取题目列表，支持分页和筛选。

**端点**: `GET /api/questions`

**认证**: 需要

**查询参数**:
- `page` (int, 可选): 页码，默认 1
- `page_size` (int, 可选): 每页数量，默认 20
- `exam_type` (string, 可选): 考试类型 (civil_service, postgraduate, public_institution)
- `question_type` (string, 可选): 题目类型 (single_choice, multiple_choice, true_false, fill_blank, essay)
- `subject` (string, 可选): 科目
- `chapter` (string, 可选): 章节
- `difficulty` (int, 可选): 难度 (1-5)
- `keyword` (string, 可选): 关键词搜索

**响应**: `200 OK`

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "exam_type": "civil_service",
        "question_type": "single_choice",
        "subject": "行测",
        "chapter": "数量关系",
        "difficulty": 3,
        "content": "题目内容...",
        "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
        "correct_answer": "A",
        "explanation": "解析内容...",
        "tags": ["数学", "计算"],
        "created_at": "2024-01-01T00:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 100,
      "total_pages": 5
    }
  }
}
```

---

### 获取单个题目

获取指定题目的详细信息。

**端点**: `GET /api/questions/:id`

**认证**: 需要

**响应**: `200 OK`

```json
{
  "success": true,
  "data": {
    "question": { ... }
  }
}
```

**错误**:
- `404` - 题目不存在

---

### 创建题目

创建新题目（仅管理员）。

**端点**: `POST /api/questions`

**认证**: 需要（管理员）

**请求体**:

```json
{
  "exam_type": "civil_service",
  "question_type": "single_choice",
  "subject": "行测",
  "chapter": "数量关系",
  "difficulty": 3,
  "content": "题目内容...",
  "options": ["A. 选项1", "B. 选项2", "C. 选项3", "D. 选项4"],
  "correct_answer": "A",
  "explanation": "解析内容...",
  "tags": ["数学", "计算"]
}
```

**响应**: `201 Created`

```json
{
  "success": true,
  "data": {
    "question": { ... }
  },
  "message": "创建成功"
}
```

---

### 更新题目

更新指定题目（仅管理员）。

**端点**: `PUT /api/questions/:id`

**认证**: 需要（管理员）

**请求体**: 同创建题目

**响应**: `200 OK`

---

### 删除题目

软删除指定题目（仅管理员）。

**端点**: `DELETE /api/questions/:id`

**认证**: 需要（管理员）

**响应**: `200 OK`

```json
{
  "success": true,
  "message": "删除成功"
}
```

---

### 批量导入题目

批量导入题目（仅管理员）。

**端点**: `POST /api/questions/import`

**认证**: 需要（管理员）

**请求体**:

```json
{
  "questions": [
    { ... },
    { ... }
  ]
}
```

**响应**: `201 Created`

```json
{
  "success": true,
  "data": {
    "imported_count": 50,
    "failed_count": 2,
    "errors": [
      {
        "index": 5,
        "error": "验证错误"
      }
    ]
  },
  "message": "导入完成"
}
```

---

### 随机获取题目

随机获取指定数量的题目。

**端点**: `GET /api/questions/random`

**认证**: 需要

**查询参数**:
- `count` (int, 必需): 题目数量
- `exam_type` (string, 可选): 考试类型
- `subject` (string, 可选): 科目
- `difficulty` (int, 可选): 难度

**响应**: `200 OK`

```json
{
  "success": true,
  "data": {
    "questions": [ ... ]
  }
}
```

---

## 练习接口

### 开始练习

开始新的练习会话。

**端点**: `POST /api/practice/start`

**认证**: 需要

**请求体**:

```json
{
  "exam_type": "civil_service",
  "subject": "行测",
  "chapter": "数量关系",
  "difficulty": 3,
  "count": 10
}
```

**响应**: `200 OK`

```json
{
  "success": true,
  "data": {
    "session_id": "uuid",
    "questions": [ ... ]
  }
}
```

---

### 提交练习答案

提交单个题目的答案并获取即时反馈。

**端点**: `POST /api/practice/submit`

**认证**: 需要

**请求体**:

```json
{
  "question_id": 1,
  "user_answer": "A"
}
```

**响应**: `200 OK`

```json
{
  "success": true,
  "data": {
    "is_correct": true,
    "correct_answer": "A",
    "explanation": "解析内容...",
    "record_id": 123
  }
}
```

---

### 获取练习历史

获取用户的练习历史记录。

**端点**: `GET /api/practice/history`

**认证**: 需要

**查询参数**:
- `page` (int, 可选): 页码
- `page_size` (int, 可选): 每页数量

**响应**: `200 OK`

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "question_id": 10,
        "question_content": "题目内容...",
        "user_answer": "A",
        "correct_answer": "A",
        "is_correct": true,
        "time_spent": 30,
        "created_at": "2024-01-01T00:00:00Z"
      }
    ],
    "pagination": { ... }
  }
}
```

---

### 获取错题本

获取用户的错题本。

**端点**: `GET /api/practice/wrong-book`

**认证**: 需要

**响应**: `200 OK`

```json
{
  "success": true,
  "data": {
    "wrong_questions": [
      {
        "id": 1,
        "question": { ... },
        "wrong_count": 3,
        "mastered": false,
        "last_wrong_at": "2024-01-01T00:00:00Z"
      }
    ]
  }
}
```

---

### 从错题本移除

从错题本中移除指定题目。

**端点**: `DELETE /api/practice/wrong-book/:id`

**认证**: 需要

**响应**: `200 OK`

```json
{
  "success": true,
  "message": "移除成功"
}
```

---

## 考试接口

### 获取试卷列表

获取可用的试卷列表。

**端点**: `GET /api/exams`

**认证**: 需要

**查询参数**:
- `exam_type` (string, 可选): 考试类型
- `page` (int, 可选): 页码
- `page_size` (int, 可选): 每页数量

**响应**: `200 OK`

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "name": "2024年国考行测模拟卷一",
        "exam_type": "civil_service",
        "description": "模拟真实考试环境",
        "duration": 120,
        "total_score": 100,
        "pass_score": 60,
        "question_count": 100,
        "is_published": true,
        "created_at": "2024-01-01T00:00:00Z"
      }
    ],
    "pagination": { ... }
  }
}
```

---

### 获取试卷详情

获取指定试卷的详细信息。

**端点**: `GET /api/exams/:id`

**认证**: 需要

**响应**: `200 OK`

```json
{
  "success": true,
  "data": {
    "paper": {
      "id": 1,
      "name": "2024年国考行测模拟卷一",
      "exam_type": "civil_service",
      "duration": 120,
      "total_score": 100,
      "questions": [
        {
          "id": 1,
          "order": 1,
          "score": 2,
          "question": { ... }
        }
      ]
    }
  }
}
```

---

### 创建试卷

创建新试卷（仅管理员）。

**端点**: `POST /api/exams`

**认证**: 需要（管理员）

**请求体**:

```json
{
  "name": "试卷名称",
  "exam_type": "civil_service",
  "description": "试卷描述",
  "duration": 120,
  "total_score": 100,
  "pass_score": 60,
  "questions": [
    {
      "question_id": 1,
      "order": 1,
      "score": 2
    }
  ]
}
```

**响应**: `201 Created`

---

### 开始考试

开始新的考试会话。

**端点**: `POST /api/exams/:id/start`

**认证**: 需要

**响应**: `200 OK`

```json
{
  "success": true,
  "data": {
    "session": {
      "id": 1,
      "paper_id": 1,
      "start_time": "2024-01-01T00:00:00Z",
      "end_time": "2024-01-01T02:00:00Z",
      "status": "in_progress"
    }
  }
}
```

---

### 提交单题答案

在考试过程中提交单个题目的答案。

**端点**: `POST /api/exams/sessions/:id/answer`

**认证**: 需要

**请求体**:

```json
{
  "question_id": 1,
  "answer": "A"
}
```

**响应**: `200 OK`

```json
{
  "success": true,
  "message": "答案已保存"
}
```

---

### 提交试卷

提交整份试卷并获取成绩。

**端点**: `POST /api/exams/sessions/:id/submit`

**认证**: 需要

**响应**: `200 OK`

```json
{
  "success": true,
  "data": {
    "result": {
      "id": 1,
      "session_id": 1,
      "score": 85.5,
      "total_score": 100,
      "correct_count": 85,
      "wrong_count": 15,
      "accuracy": 0.85,
      "time_spent": 7200,
      "details": [
        {
          "question_id": 1,
          "user_answer": "A",
          "correct_answer": "A",
          "is_correct": true,
          "score": 2
        }
      ]
    }
  }
}
```

---

### 获取考试结果

获取指定考试的结果详情。

**端点**: `GET /api/exams/results/:id`

**认证**: 需要

**响应**: `200 OK`

```json
{
  "success": true,
  "data": {
    "result": { ... }
  }
}
```

---

### 获取考试历史

获取用户的所有考试记录。

**端点**: `GET /api/exams/results`

**认证**: 需要

**查询参数**:
- `page` (int, 可选): 页码
- `page_size` (int, 可选): 每页数量

**响应**: `200 OK`

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "paper_name": "2024年国考行测模拟卷一",
        "score": 85.5,
        "accuracy": 0.85,
        "created_at": "2024-01-01T00:00:00Z"
      }
    ],
    "pagination": { ... }
  }
}
```

---

## 统计接口

### 获取学习概览

获取用户的学习数据概览。

**端点**: `GET /api/statistics/overview`

**认证**: 需要

**查询参数**:
- `start_date` (string, 可选): 开始日期 (YYYY-MM-DD)
- `end_date` (string, 可选): 结束日期 (YYYY-MM-DD)

**响应**: `200 OK`

```json
{
  "success": true,
  "data": {
    "overview": {
      "total_practice_count": 500,
      "total_correct_count": 425,
      "accuracy": 0.85,
      "total_study_duration": 3600,
      "total_exam_count": 10,
      "average_exam_score": 82.5
    }
  }
}
```

---

### 获取知识点分析

获取按知识点统计的正确率分析。

**端点**: `GET /api/statistics/knowledge`

**认证**: 需要

**响应**: `200 OK`

```json
{
  "success": true,
  "data": {
    "knowledge_points": [
      {
        "subject": "行测",
        "chapter": "数量关系",
        "practice_count": 100,
        "correct_count": 85,
        "accuracy": 0.85
      },
      {
        "subject": "行测",
        "chapter": "言语理解",
        "practice_count": 120,
        "correct_count": 96,
        "accuracy": 0.80
      }
    ]
  }
}
```

---

### 获取学习趋势

获取一段时间内的学习趋势数据。

**端点**: `GET /api/statistics/trend`

**认证**: 需要

**查询参数**:
- `start_date` (string, 可选): 开始日期
- `end_date` (string, 可选): 结束日期
- `granularity` (string, 可选): 粒度 (day, week, month)

**响应**: `200 OK`

```json
{
  "success": true,
  "data": {
    "trend": [
      {
        "date": "2024-01-01",
        "practice_count": 50,
        "correct_count": 42,
        "accuracy": 0.84,
        "study_duration": 120
      }
    ]
  }
}
```

---

### 获取考试统计

获取用户的考试统计数据。

**端点**: `GET /api/statistics/exams`

**认证**: 需要

**响应**: `200 OK`

```json
{
  "success": true,
  "data": {
    "exam_stats": {
      "total_exams": 10,
      "average_score": 82.5,
      "highest_score": 95,
      "lowest_score": 70,
      "score_trend": [
        {
          "exam_name": "模拟卷一",
          "score": 80,
          "date": "2024-01-01"
        }
      ]
    }
  }
}
```

---

## 数据导入导出接口

### 导出数据

导出用户数据。

**端点**: `POST /api/data/export`

**认证**: 需要

**请求体**:

```json
{
  "format": "json",
  "data_types": ["questions", "practice_records", "exam_results"]
}
```

**响应**: `200 OK`

返回文件下载或数据 JSON。

---

### 导入数据

导入数据到系统。

**端点**: `POST /api/data/import`

**认证**: 需要（管理员）

**请求体**: 根据格式而定

**响应**: `200 OK`

```json
{
  "success": true,
  "data": {
    "imported_count": 100,
    "failed_count": 5
  }
}
```

---

## 错误代码

| 错误代码 | HTTP 状态码 | 描述 |
|---------|-----------|------|
| VALIDATION_ERROR | 400 | 请求数据验证失败 |
| AUTHENTICATION_ERROR | 401 | 认证失败或令牌无效 |
| AUTHORIZATION_ERROR | 403 | 权限不足 |
| RESOURCE_NOT_FOUND | 404 | 资源不存在 |
| RESOURCE_CONFLICT | 409 | 资源冲突（如用户名已存在） |
| BUSINESS_LOGIC_ERROR | 422 | 业务逻辑错误 |
| INTERNAL_SERVER_ERROR | 500 | 服务器内部错误 |

---

## 示例代码

### JavaScript (Axios)

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json'
  }
});

// 添加请求拦截器（自动添加令牌）
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 登录示例
async function login(username, password) {
  const response = await api.post('/auth/login', {
    username,
    password
  });
  return response.data;
}

// 获取题目列表示例
async function getQuestions(params) {
  const response = await api.get('/questions', { params });
  return response.data;
}
```

### Python (Requests)

```python
import requests

BASE_URL = 'http://localhost:5000/api'

class ExamAPI:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
    
    def login(self, username, password):
        response = self.session.post(
            f'{BASE_URL}/auth/login',
            json={'username': username, 'password': password}
        )
        data = response.json()
        self.token = data['data']['access_token']
        self.session.headers.update({
            'Authorization': f'Bearer {self.token}'
        })
        return data
    
    def get_questions(self, **params):
        response = self.session.get(
            f'{BASE_URL}/questions',
            params=params
        )
        return response.json()
```

---

## 速率限制

- 未认证请求：100 请求/小时
- 已认证请求：1000 请求/小时
- 管理员请求：无限制

## 版本控制

当前 API 版本：v1

未来版本将通过 URL 路径区分：`/api/v2/...`

---

**最后更新**: 2024-12-11


---

## 学习计划接口

### 创建学习计划

**端点**: `POST /api/study-plans`

**认证**: 需要

**请求体**:
```json
{
  "name": "2024年公务员备考计划",
  "exam_type": "公务员",
  "target_date": "2024-12-31",
  "description": "全面备考公务员考试",
  "goals": [
    {
      "goal_type": "daily_practice",
      "target_value": 50
    },
    {
      "goal_type": "weekly_practice",
      "target_value": 400
    }
  ]
}
```

**响应**:
```json
{
  "success": true,
  "plan": {
    "id": 1,
    "user_id": 1,
    "name": "2024年公务员备考计划",
    "exam_type": "公务员",
    "target_date": "2024-12-31",
    "description": "全面备考公务员考试",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "goals": [...]
  }
}
```

### 获取学习计划列表

**端点**: `GET /api/study-plans`

**认证**: 需要

**查询参数**:
- `active_only` (boolean, 可选): 仅显示活跃计划

**响应**:
```json
{
  "success": true,
  "plans": [
    {
      "id": 1,
      "name": "2024年公务员备考计划",
      "exam_type": "公务员",
      "target_date": "2024-12-31",
      "is_active": true,
      "goals": [...]
    }
  ]
}
```

### 获取学习计划详情

**端点**: `GET /api/study-plans/:id`

**认证**: 需要

**响应**: 同创建学习计划响应

### 更新学习计划

**端点**: `PUT /api/study-plans/:id`

**认证**: 需要

**请求体**: 同创建学习计划请求体（所有字段可选）

**响应**: 同创建学习计划响应

### 删除学习计划

**端点**: `DELETE /api/study-plans/:id`

**认证**: 需要

**响应**:
```json
{
  "success": true,
  "message": "学习计划已删除"
}
```

### 更新学习进度

**端点**: `PUT /api/study-plans/:id/progress`

**认证**: 需要

**请求体**:
```json
{
  "goal_id": 1,
  "increment": 10
}
```

**响应**:
```json
{
  "success": true,
  "goal": {
    "id": 1,
    "current_value": 60,
    "target_value": 100,
    "is_completed": false
  }
}
```

### 获取学习报告

**端点**: `GET /api/study-plans/:id/report`

**认证**: 需要

**响应**:
```json
{
  "success": true,
  "total_practice_count": 500,
  "total_exam_count": 10,
  "total_study_duration": 3000,
  "goals": [
    {
      "id": 1,
      "goal_type": "daily_practice",
      "current_value": 50,
      "target_value": 50,
      "is_completed": true
    }
  ]
}
```

---

## 笔记接口

### 创建笔记

**端点**: `POST /api/notes`

**认证**: 需要

**请求体**:
```json
{
  "question_id": 123,
  "content": "# 解题思路\n\n这道题的关键是...",
  "tags": ["重点", "易错"]
}
```

**响应**:
```json
{
  "success": true,
  "note": {
    "id": 1,
    "user_id": 1,
    "question_id": 123,
    "content": "# 解题思路\n\n这道题的关键是...",
    "tags": ["重点", "易错"],
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

### 获取笔记列表

**端点**: `GET /api/notes`

**认证**: 需要

**查询参数**:
- `page` (integer, 可选): 页码，默认 1
- `page_size` (integer, 可选): 每页数量，默认 20
- `subject` (string, 可选): 科目筛选
- `chapter` (string, 可选): 章节筛选

**响应**:
```json
{
  "success": true,
  "notes": [...],
  "total": 50,
  "page": 1,
  "page_size": 20
}
```

### 搜索笔记

**端点**: `GET /api/notes/search`

**认证**: 需要

**查询参数**:
- `keyword` (string, 可选): 搜索关键词
- `subject` (string, 可选): 科目筛选
- `chapter` (string, 可选): 章节筛选
- `start_date` (string, 可选): 开始日期
- `end_date` (string, 可选): 结束日期
- `sort_by` (string, 可选): 排序方式（created_at_desc, created_at_asc, updated_at_desc, relevance）

**响应**: 同获取笔记列表

### 获取题目的笔记

**端点**: `GET /api/notes/question/:question_id`

**认证**: 需要

**响应**:
```json
{
  "success": true,
  "notes": [...]
}
```

### 更新笔记

**端点**: `PUT /api/notes/:id`

**认证**: 需要

**请求体**: 同创建笔记（所有字段可选）

**响应**: 同创建笔记响应

### 删除笔记

**端点**: `DELETE /api/notes/:id`

**认证**: 需要

**响应**:
```json
{
  "success": true,
  "message": "笔记已删除"
}
```

---

## 收藏接口

### 收藏题目

**端点**: `POST /api/bookmarks`

**认证**: 需要

**请求体**:
```json
{
  "question_id": 123,
  "tags": ["重点", "常考"],
  "note": "这道题经常出现在考试中"
}
```

**响应**:
```json
{
  "success": true,
  "bookmark": {
    "id": 1,
    "user_id": 1,
    "question_id": 123,
    "tags": ["重点", "常考"],
    "note": "这道题经常出现在考试中",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### 获取收藏列表

**端点**: `GET /api/bookmarks`

**认证**: 需要

**查询参数**:
- `page` (integer, 可选): 页码，默认 1
- `page_size` (integer, 可选): 每页数量，默认 20
- `exam_type` (string, 可选): 考试类型筛选
- `subject` (string, 可选): 科目筛选
- `chapter` (string, 可选): 章节筛选
- `difficulty` (integer, 可选): 难度筛选（1-3）
- `tag` (string, 可选): 标签筛选
- `sort_by` (string, 可选): 排序方式（created_at_desc, created_at_asc, difficulty_asc, difficulty_desc）

**响应**:
```json
{
  "success": true,
  "bookmarks": [
    {
      "id": 1,
      "question_id": 123,
      "tags": ["重点", "常考"],
      "note": "这道题经常出现在考试中",
      "created_at": "2024-01-01T00:00:00Z",
      "question": {
        "id": 123,
        "content": "题目内容...",
        "exam_type": "公务员",
        "subject": "行测",
        "chapter": "数量关系",
        "difficulty": 2
      }
    }
  ],
  "total": 50,
  "page": 1,
  "page_size": 20
}
```

### 检查题目是否已收藏

**端点**: `GET /api/bookmarks/question/:question_id`

**认证**: 需要

**响应**:
```json
{
  "success": true,
  "is_bookmarked": true,
  "bookmark": {...}
}
```

### 更新收藏

**端点**: `PUT /api/bookmarks/:id`

**认证**: 需要

**请求体**:
```json
{
  "tags": ["重点", "难题"],
  "note": "更新后的备注"
}
```

**响应**: 同收藏题目响应

### 取消收藏

**端点**: `DELETE /api/bookmarks/:id`

**认证**: 需要

**响应**:
```json
{
  "success": true,
  "message": "已取消收藏"
}
```

### 取消收藏（通过题目ID）

**端点**: `DELETE /api/bookmarks/question/:question_id`

**认证**: 需要

**响应**: 同取消收藏

### 获取收藏数量

**端点**: `GET /api/bookmarks/count`

**认证**: 需要

**响应**:
```json
{
  "success": true,
  "count": 50
}
```

---

## 提醒接口

### 创建提醒

**端点**: `POST /api/reminders`

**认证**: 需要

**请求体**:
```json
{
  "study_plan_id": 1,
  "reminder_type": "daily",
  "reminder_time": "09:00",
  "message": "该学习了！"
}
```

或（每周提醒）:
```json
{
  "study_plan_id": 1,
  "reminder_type": "weekly",
  "reminder_time": "09:00",
  "weekdays": [1, 3, 5],
  "message": "该学习了！"
}
```

**响应**:
```json
{
  "success": true,
  "reminder": {
    "id": 1,
    "study_plan_id": 1,
    "reminder_type": "daily",
    "reminder_time": "09:00",
    "weekdays": null,
    "message": "该学习了！",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### 获取提醒列表

**端点**: `GET /api/reminders`

**认证**: 需要

**查询参数**:
- `study_plan_id` (integer, 可选): 学习计划ID筛选
- `active_only` (boolean, 可选): 仅显示活跃提醒

**响应**:
```json
{
  "success": true,
  "reminders": [...]
}
```

### 更新提醒

**端点**: `PUT /api/reminders/:id`

**认证**: 需要

**请求体**: 同创建提醒（所有字段可选）

**响应**: 同创建提醒响应

### 删除提醒

**端点**: `DELETE /api/reminders/:id`

**认证**: 需要

**响应**:
```json
{
  "success": true,
  "message": "提醒已删除"
}
```

---

## 数据模型

### StudyPlan（学习计划）
```json
{
  "id": 1,
  "user_id": 1,
  "name": "计划名称",
  "exam_type": "考试类型",
  "target_date": "目标日期",
  "description": "计划描述",
  "is_active": true,
  "created_at": "创建时间",
  "updated_at": "更新时间",
  "deleted_at": null,
  "goals": [...]
}
```

### StudyGoal（学习目标）
```json
{
  "id": 1,
  "study_plan_id": 1,
  "goal_type": "daily_practice",
  "target_value": 50,
  "current_value": 30,
  "is_completed": false,
  "completed_at": null
}
```

**目标类型**:
- `daily_practice`: 每日练习题数
- `weekly_practice`: 每周练习题数
- `daily_duration`: 每日学习时长（分钟）
- `exam_count`: 考试次数

### QuestionNote（题目笔记）
```json
{
  "id": 1,
  "user_id": 1,
  "question_id": 123,
  "content": "笔记内容（Markdown格式）",
  "tags": ["标签1", "标签2"],
  "created_at": "创建时间",
  "updated_at": "更新时间",
  "deleted_at": null
}
```

### QuestionBookmark（题目收藏）
```json
{
  "id": 1,
  "user_id": 1,
  "question_id": 123,
  "tags": ["标签1", "标签2"],
  "note": "备注信息",
  "created_at": "创建时间"
}
```

### StudyReminder（学习提醒）
```json
{
  "id": 1,
  "study_plan_id": 1,
  "reminder_type": "daily",
  "reminder_time": "09:00",
  "weekdays": [1, 3, 5],
  "message": "提醒消息",
  "is_active": true,
  "created_at": "创建时间"
}
```

---

## 错误代码补充

### 学习计划相关
- `PLAN_NOT_FOUND`: 学习计划不存在
- `PLAN_ACCESS_DENIED`: 无权访问该学习计划
- `INVALID_GOAL_TYPE`: 无效的目标类型
- `INVALID_TARGET_VALUE`: 无效的目标值

### 笔记相关
- `NOTE_NOT_FOUND`: 笔记不存在
- `NOTE_ACCESS_DENIED`: 无权访问该笔记
- `INVALID_MARKDOWN`: 无效的 Markdown 格式
- `CONTENT_TOO_LONG`: 笔记内容过长（超过5000字符）

### 收藏相关
- `BOOKMARK_NOT_FOUND`: 收藏不存在
- `BOOKMARK_ACCESS_DENIED`: 无权访问该收藏
- `ALREADY_BOOKMARKED`: 题目已收藏
- `QUESTION_NOT_FOUND`: 题目不存在

### 提醒相关
- `REMINDER_NOT_FOUND`: 提醒不存在
- `REMINDER_ACCESS_DENIED`: 无权访问该提醒
- `INVALID_REMINDER_TYPE`: 无效的提醒类型
- `INVALID_REMINDER_TIME`: 无效的提醒时间

---

## 更新日志

### 2025-12-26
- 新增学习计划接口（7个端点）
- 新增笔记接口（7个端点）
- 新增收藏接口（8个端点）
- 新增提醒接口（5个端点）
- 新增相关数据模型文档
- 新增错误代码说明

---

**文档版本**: v1.1  
**最后更新**: 2025-12-26  
**维护者**: Kiro AI Assistant


---

## 积分系统接口

### 获取用户积分信息

获取当前用户的积分、等级、连续学习天数等信息。

**端点**: `GET /api/points`

**认证**: 需要

**请求参数**: 无

**响应示例**:

```json
{
  "success": true,
  "data": {
    "user_id": 1,
    "total_points": 1250,
    "level": 3,
    "streak_days": 7,
    "last_active_date": "2024-12-26",
    "today_points": 85,
    "created_at": "2024-12-01T10:00:00Z",
    "updated_at": "2024-12-26T15:30:00Z"
  }
}
```

**响应字段说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| user_id | integer | 用户ID |
| total_points | integer | 总积分 |
| level | integer | 当前等级 (level = floor(sqrt(total_points / 100))) |
| streak_days | integer | 连续学习天数 |
| last_active_date | string | 最后活跃日期 (YYYY-MM-DD) |
| today_points | integer | 今日获得积分 |
| created_at | string | 创建时间 (ISO 8601) |
| updated_at | string | 更新时间 (ISO 8601) |

**错误响应**:

- `401 Unauthorized`: 未登录或令牌无效
- `404 Not Found`: 用户积分记录不存在（首次访问会自动创建）

---

### 获取积分历史

获取用户的积分交易历史记录，支持分页。

**端点**: `GET /api/points/history`

**认证**: 需要

**请求参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| page | integer | 否 | 1 | 页码 |
| per_page | integer | 否 | 20 | 每页数量 (1-100) |

**响应示例**:

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 123,
        "user_id": 1,
        "points": 50,
        "transaction_type": "practice",
        "description": "完成练习",
        "reference_id": 456,
        "created_at": "2024-12-26T15:30:00Z"
      },
      {
        "id": 122,
        "user_id": 1,
        "points": 20,
        "transaction_type": "daily_task",
        "description": "完成每日任务：完成3次练习",
        "reference_id": 789,
        "created_at": "2024-12-26T14:20:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 45,
      "total_pages": 3
    }
  }
}
```

**交易类型说明**:

| 类型 | 说明 |
|------|------|
| practice | 练习奖励 |
| exam | 考试奖励 |
| achievement | 成就奖励 |
| daily_task | 每日任务奖励 |
| goal_completed | 学习目标完成奖励 |
| streak_bonus | 连续学习奖励 |

---

### 获取积分排行榜

获取积分排行榜，支持分页。

**端点**: `GET /api/points/leaderboard`

**认证**: 需要

**请求参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| page | integer | 否 | 1 | 页码 |
| per_page | integer | 否 | 20 | 每页数量 (1-100) |

**响应示例**:

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "rank": 1,
        "user_id": 5,
        "username": "学霸小王",
        "total_points": 5280,
        "level": 7,
        "streak_days": 30
      },
      {
        "rank": 2,
        "user_id": 12,
        "username": "努力学习中",
        "total_points": 4150,
        "level": 6,
        "streak_days": 15
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 156,
      "total_pages": 8
    },
    "current_user_rank": {
      "rank": 23,
      "user_id": 1,
      "username": "当前用户",
      "total_points": 1250,
      "level": 3,
      "streak_days": 7
    }
  }
}
```

---

## 成就系统接口

### 获取所有成就定义

获取系统中所有成就的定义信息。

**端点**: `GET /api/achievements`

**认证**: 需要

**请求参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| category | string | 否 | - | 成就类别 (learning/streak/milestone) |

**响应示例**:

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "初学者",
      "description": "完成第一次练习",
      "icon": "🎯",
      "category": "learning",
      "criteria": {
        "type": "practice_count",
        "target": 1
      },
      "points_reward": 10,
      "tier": "bronze",
      "is_active": true,
      "created_at": "2024-12-01T00:00:00Z"
    }
  ]
}
```

**成就类别说明**:

| 类别 | 说明 | 示例 |
|------|------|------|
| learning | 学习类成就 | 完成练习、答对题目 |
| streak | 连续类成就 | 连续学习天数 |
| milestone | 里程碑成就 | 积分达标、笔记数量 |

**成就等级说明**:

| 等级 | 说明 |
|------|------|
| bronze | 铜牌 |
| silver | 银牌 |
| gold | 金牌 |

---

### 获取成就详情

获取指定成就的详细信息。

**端点**: `GET /api/achievements/:id`

**认证**: 需要

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| id | integer | 成就ID |

**响应示例**:

```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "初学者",
    "description": "完成第一次练习",
    "icon": "🎯",
    "category": "learning",
    "criteria": {
      "type": "practice_count",
      "target": 1
    },
    "points_reward": 10,
    "tier": "bronze",
    "is_active": true,
    "created_at": "2024-12-01T00:00:00Z"
  }
}
```

---

### 获取用户成就

获取当前用户的成就列表，包括已获得、进行中和未解锁的成就。

**端点**: `GET /api/achievements/user`

**认证**: 需要

**请求参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| status | string | 否 | - | 成就状态 (earned/in_progress/locked) |

**响应示例**:

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "初学者",
      "description": "完成第一次练习",
      "icon": "🎯",
      "category": "learning",
      "criteria": {
        "type": "practice_count",
        "target": 1
      },
      "points_reward": 10,
      "tier": "bronze",
      "status": "earned",
      "progress": {
        "current": 1,
        "target": 1
      },
      "unlocked_at": "2024-12-15T10:30:00Z"
    },
    {
      "id": 2,
      "name": "勤奋学习",
      "description": "完成10次练习",
      "icon": "📚",
      "category": "learning",
      "criteria": {
        "type": "practice_count",
        "target": 10
      },
      "points_reward": 50,
      "tier": "silver",
      "status": "in_progress",
      "progress": {
        "current": 5,
        "target": 10
      },
      "unlocked_at": null
    },
    {
      "id": 3,
      "name": "学习大师",
      "description": "完成100次练习",
      "icon": "🏆",
      "category": "learning",
      "criteria": {
        "type": "practice_count",
        "target": 100
      },
      "points_reward": 200,
      "tier": "gold",
      "status": "locked",
      "progress": {
        "current": 5,
        "target": 100
      },
      "unlocked_at": null
    }
  ]
}
```

**成就状态说明**:

| 状态 | 说明 |
|------|------|
| earned | 已获得 |
| in_progress | 进行中（已有进度但未完成） |
| locked | 未解锁（无进度或进度为0） |

---

### 获取成就统计

获取用户的成就统计信息。

**端点**: `GET /api/achievements/stats`

**认证**: 需要

**请求参数**: 无

**响应示例**:

```json
{
  "success": true,
  "data": {
    "total_count": 24,
    "earned_count": 5,
    "in_progress_count": 8,
    "locked_count": 11,
    "total_points_earned": 180,
    "by_category": {
      "learning": {
        "total": 8,
        "earned": 2
      },
      "streak": {
        "total": 6,
        "earned": 1
      },
      "milestone": {
        "total": 10,
        "earned": 2
      }
    },
    "by_tier": {
      "bronze": {
        "total": 9,
        "earned": 3
      },
      "silver": {
        "total": 9,
        "earned": 2
      },
      "gold": {
        "total": 6,
        "earned": 0
      }
    }
  }
}
```

---

### 手动检查成就

手动触发成就检查，用于测试或补偿机制。

**端点**: `POST /api/achievements/check`

**认证**: 需要

**请求体**: 无

**响应示例**:

```json
{
  "success": true,
  "data": {
    "newly_unlocked": [
      {
        "id": 5,
        "name": "三天打卡",
        "description": "连续学习3天",
        "points_reward": 30,
        "tier": "bronze"
      }
    ],
    "checked_count": 24,
    "unlocked_count": 1
  }
}
```

---

## 每日任务接口

### 获取今日任务

获取当前用户今日的任务列表。如果今日任务尚未生成，会自动生成。

**端点**: `GET /api/daily-tasks`

**认证**: 需要

**请求参数**: 无

**响应示例**:

```json
{
  "success": true,
  "data": [
    {
      "id": 101,
      "user_id": 1,
      "task_type": "daily_practice",
      "title": "完成3次练习",
      "description": "今日完成3次练习",
      "target_value": 3,
      "current_progress": 1,
      "points_reward": 20,
      "is_completed": false,
      "task_date": "2024-12-26",
      "completed_at": null,
      "created_at": "2024-12-26T00:00:00Z"
    },
    {
      "id": 102,
      "user_id": 1,
      "task_type": "daily_questions",
      "title": "答对10道题目",
      "description": "今日答对10道题目",
      "target_value": 10,
      "current_progress": 5,
      "points_reward": 30,
      "is_completed": false,
      "task_date": "2024-12-26",
      "completed_at": null,
      "created_at": "2024-12-26T00:00:00Z"
    },
    {
      "id": 103,
      "user_id": 1,
      "task_type": "daily_study_time",
      "title": "学习30分钟",
      "description": "今日累计学习30分钟",
      "target_value": 30,
      "current_progress": 30,
      "points_reward": 25,
      "is_completed": true,
      "task_date": "2024-12-26",
      "completed_at": "2024-12-26T15:30:00Z",
      "created_at": "2024-12-26T00:00:00Z"
    }
  ]
}
```

**任务类型说明**:

| 类型 | 标题 | 目标 | 积分 |
|------|------|------|------|
| daily_practice | 完成3次练习 | 3 | 20 |
| daily_questions | 答对10道题目 | 10 | 30 |
| daily_study_time | 学习30分钟 | 30 | 25 |
| daily_notes | 创建2条笔记 | 2 | 15 |
| daily_review | 复习5道错题 | 5 | 20 |

**每日总积分**: 110分

---

### 完成任务

手动标记任务为完成状态（通常由系统自动完成）。

**端点**: `PUT /api/daily-tasks/:id/complete`

**认证**: 需要

**路径参数**:

| 参数 | 类型 | 说明 |
|------|------|------|
| id | integer | 任务ID |

**请求体**: 无

**响应示例**:

```json
{
  "success": true,
  "data": {
    "id": 101,
    "user_id": 1,
    "task_type": "daily_practice",
    "title": "完成3次练习",
    "description": "今日完成3次练习",
    "target_value": 3,
    "current_progress": 3,
    "points_reward": 20,
    "is_completed": true,
    "task_date": "2024-12-26",
    "completed_at": "2024-12-26T16:00:00Z",
    "created_at": "2024-12-26T00:00:00Z"
  },
  "message": "任务已完成，获得 20 积分"
}
```

**错误响应**:

- `400 Bad Request`: 任务已完成或进度未达标
- `404 Not Found`: 任务不存在

---

### 获取任务统计

获取用户的任务统计信息。

**端点**: `GET /api/daily-tasks/stats`

**认证**: 需要

**请求参数**: 无

**响应示例**:

```json
{
  "success": true,
  "data": {
    "total_completed": 45,
    "streak_days": 7,
    "total_points_earned": 4950,
    "today_completed": 3,
    "today_total": 5,
    "completion_rate": 0.75,
    "best_streak": 15
  }
}
```

**字段说明**:

| 字段 | 类型 | 说明 |
|------|------|------|
| total_completed | integer | 累计完成任务数 |
| streak_days | integer | 连续完成天数 |
| total_points_earned | integer | 累计获得积分 |
| today_completed | integer | 今日已完成任务数 |
| today_total | integer | 今日总任务数 |
| completion_rate | float | 今日完成率 (0-1) |
| best_streak | integer | 最佳连续天数 |

---

### 获取任务模板

获取所有任务模板定义。

**端点**: `GET /api/daily-tasks/templates`

**认证**: 需要

**请求参数**: 无

**响应示例**:

```json
{
  "success": true,
  "data": [
    {
      "task_type": "daily_practice",
      "title": "完成3次练习",
      "description": "今日完成3次练习",
      "target_value": 3,
      "points_reward": 20
    },
    {
      "task_type": "daily_questions",
      "title": "答对10道题目",
      "description": "今日答对10道题目",
      "target_value": 10,
      "points_reward": 30
    }
  ]
}
```

---

## 错误代码补充

### 积分系统相关

| 错误代码 | HTTP 状态码 | 描述 |
|----------|-------------|------|
| POINTS_NOT_FOUND | 404 | 用户积分记录不存在 |
| INVALID_POINTS_AMOUNT | 400 | 无效的积分数量 |
| INSUFFICIENT_POINTS | 400 | 积分不足 |

### 成就系统相关

| 错误代码 | HTTP 状态码 | 描述 |
|----------|-------------|------|
| ACHIEVEMENT_NOT_FOUND | 404 | 成就不存在 |
| ACHIEVEMENT_ALREADY_UNLOCKED | 400 | 成就已解锁 |
| ACHIEVEMENT_CRITERIA_NOT_MET | 400 | 成就条件未满足 |

### 每日任务相关

| 错误代码 | HTTP 状态码 | 描述 |
|----------|-------------|------|
| TASK_NOT_FOUND | 404 | 任务不存在 |
| TASK_ALREADY_COMPLETED | 400 | 任务已完成 |
| TASK_PROGRESS_INSUFFICIENT | 400 | 任务进度不足 |
| TASK_NOT_TODAY | 400 | 不是今日任务 |

---

## 更新日志

### 2024-12-26

**新增接口**:
- 积分系统接口 (3个端点)
- 成就系统接口 (5个端点)
- 每日任务接口 (4个端点)

**新增功能**:
- 积分和等级系统
- 成就解锁机制
- 每日任务系统
- 连续学习追踪

**总计**: 新增 12 个 API 端点

---

**文档版本**: v1.2  
**最后更新**: 2024-12-26  
**维护者**: Kiro AI Assistant
