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
