# 开发指南

本文档提供考公考研考编系统的开发规范、最佳实践和工作流程指南。

## 目录

- [开发环境设置](#开发环境设置)
- [项目结构](#项目结构)
- [代码规范](#代码规范)
- [开发工作流](#开发工作流)
- [测试指南](#测试指南)
- [API 开发](#api-开发)
- [数据库开发](#数据库开发)
- [前端开发](#前端开发)
- [调试技巧](#调试技巧)
- [常见问题](#常见问题)

## 开发环境设置

### 后端开发环境

#### 1. 安装 Python 和依赖

```bash
# 确保 Python 3.9+
python --version

# 创建虚拟环境
cd exam/backend
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```bash
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=dev-secret-key
JWT_SECRET_KEY=dev-jwt-secret-key
DATABASE_URL=sqlite:///exam.db
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

#### 3. 初始化数据库

```bash
# 使用 Flask-Migrate
flask db upgrade

# 或使用初始化脚本
python init_db.py
```

#### 4. 运行开发服务器

```bash
# 方式一：使用 Flask CLI
flask run

# 方式二：使用 run.py
python run.py

# 方式三：使用 --no-reload 避免 watchdog 问题
python run.py --no-reload
```

### 前端开发环境

#### 1. 安装 Node.js 和依赖

```bash
# 确保 Node.js 16+
node --version
npm --version

# 安装依赖
cd exam/frontend
npm install
```

#### 2. 配置环境变量

编辑 `.env.development`:

```bash
VITE_API_BASE_URL=http://localhost:5000/api
VITE_APP_TITLE=考公考研考编系统（开发）
```

#### 3. 运行开发服务器

```bash
npm run dev
```

访问 http://localhost:5173

### 开发工具推荐

#### IDE/编辑器

- **VS Code** (推荐)
  - 插件：Python, Pylance, Vue - Official, ESLint, Prettier
- **PyCharm Professional**
- **WebStorm**

#### VS Code 配置

创建 `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/exam/backend/venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  },
  "[javascript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[vue]": {
    "editor.defaultFormatter": "Vue.volar"
  }
}
```

## 项目结构

### 后端结构

```
backend/
├── app/
│   ├── __init__.py          # 应用工厂
│   ├── models/              # 数据模型
│   │   ├── user.py
│   │   ├── question.py
│   │   ├── exam.py
│   │   ├── practice.py
│   │   └── statistics.py
│   ├── routes/              # API 路由
│   │   ├── auth.py
│   │   ├── questions.py
│   │   ├── practice.py
│   │   ├── exams.py
│   │   └── statistics.py
│   ├── services/            # 业务逻辑
│   │   ├── auth_service.py
│   │   ├── question_service.py
│   │   ├── practice_service.py
│   │   ├── exam_service.py
│   │   └── statistics_service.py
│   ├── schemas/             # 数据验证
│   │   ├── user_schema.py
│   │   ├── question_schema.py
│   │   └── exam_schema.py
│   └── utils/               # 工具函数
│       ├── decorators.py
│       ├── validators.py
│       ├── exceptions.py
│       └── response.py
├── tests/                   # 测试文件
├── migrations/              # 数据库迁移
├── config.py                # 配置
└── run.py                   # 启动脚本
```

### 前端结构

```
frontend/
├── src/
│   ├── api/                 # API 调用
│   ├── components/          # 可复用组件
│   ├── views/               # 页面视图
│   ├── stores/              # Pinia 状态管理
│   ├── router/              # 路由配置
│   ├── utils/               # 工具函数
│   ├── App.vue
│   └── main.js
├── public/
└── package.json
```

## 代码规范

### Python 代码规范

#### 遵循 PEP 8

```python
# 好的示例
def calculate_exam_score(answers: dict, correct_answers: dict) -> float:
    """
    计算考试成绩。
    
    Args:
        answers: 用户答案字典
        correct_answers: 正确答案字典
    
    Returns:
        float: 成绩（0-100）
    """
    correct_count = sum(
        1 for q_id, answer in answers.items()
        if answer == correct_answers.get(q_id)
    )
    return (correct_count / len(correct_answers)) * 100


# 避免的示例
def calc(a,b):
    c=0
    for i in a:
        if i==b[i]:c+=1
    return c/len(b)*100
```

#### 命名规范

```python
# 类名：大驼峰
class UserService:
    pass

# 函数/方法名：小写+下划线
def get_user_by_id(user_id):
    pass

# 常量：大写+下划线
MAX_QUESTIONS_PER_EXAM = 100

# 私有方法：前缀下划线
def _internal_helper():
    pass
```

#### 类型注解

```python
from typing import List, Optional, Dict

def get_questions(
    exam_type: str,
    limit: int = 20,
    offset: int = 0
) -> List[Dict]:
    """获取题目列表"""
    pass

def find_user(user_id: int) -> Optional[User]:
    """查找用户，可能返回 None"""
    pass
```

#### 文档字符串

```python
def create_exam_session(user_id: int, paper_id: int) -> ExamSession:
    """
    创建考试会话。
    
    Args:
        user_id: 用户 ID
        paper_id: 试卷 ID
    
    Returns:
        ExamSession: 创建的考试会话对象
    
    Raises:
        ResourceNotFoundError: 用户或试卷不存在
        BusinessLogicError: 用户已有进行中的考试
    
    Example:
        >>> session = create_exam_session(1, 10)
        >>> print(session.status)
        'in_progress'
    """
    pass
```

### JavaScript/Vue 代码规范

#### Vue 3 组合式 API

```vue
<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

// Props
const props = defineProps({
  questionId: {
    type: Number,
    required: true
  }
})

// Emits
const emit = defineEmits(['answer-submitted'])

// 响应式数据
const answer = ref('')
const loading = ref(false)

// 计算属性
const isValid = computed(() => answer.value.trim().length > 0)

// 方法
const submitAnswer = async () => {
  loading.value = true
  try {
    await api.submitAnswer(props.questionId, answer.value)
    emit('answer-submitted', answer.value)
  } catch (error) {
    console.error('提交失败:', error)
  } finally {
    loading.value = false
  }
}

// 生命周期
onMounted(() => {
  console.log('组件已挂载')
})
</script>

<template>
  <div class="answer-form">
    <input v-model="answer" :disabled="loading" />
    <button @click="submitAnswer" :disabled="!isValid || loading">
      提交
    </button>
  </div>
</template>

<style scoped>
.answer-form {
  padding: 20px;
}
</style>
```

#### 命名规范

```javascript
// 组件名：大驼峰
// QuestionCard.vue, ExamTimer.vue

// 变量/函数：小驼峰
const userName = 'test'
function getUserInfo() {}

// 常量：大写+下划线
const API_BASE_URL = 'http://localhost:5000'

// 私有变量：前缀下划线
const _internalState = {}
```

### Git 提交规范

使用 Conventional Commits：

```bash
# 格式
<type>(<scope>): <subject>

# 类型
feat:     新功能
fix:      修复 bug
docs:     文档更新
style:    代码格式（不影响功能）
refactor: 重构
test:     测试相关
chore:    构建/工具相关

# 示例
feat(auth): 添加用户注册功能
fix(exam): 修复考试计时器bug
docs(api): 更新API文档
refactor(question): 重构题目查询逻辑
test(practice): 添加练习服务单元测试
```

## 开发工作流

### 1. 创建功能分支

```bash
git checkout -b feature/user-authentication
```

### 2. 开发功能

按照任务列表 (`.kiro/specs/exam-system/tasks.md`) 进行开发。

### 3. 编写测试

```bash
# 后端测试
cd exam/backend
pytest tests/test_new_feature.py

# 前端测试
cd exam/frontend
npm run test -- NewComponent.test.js
```

### 4. 代码检查

```bash
# 后端
black app/
isort app/
flake8 app/

# 前端
npm run lint
npm run format
```

### 5. 提交代码

```bash
git add .
git commit -m "feat(auth): 实现用户注册功能"
git push origin feature/user-authentication
```

### 6. 创建 Pull Request

在 GitHub/GitLab 上创建 PR，等待代码审查。

## 测试指南

### 后端测试

#### 单元测试

```python
# tests/test_auth_service.py
import pytest
from app.services.auth_service import AuthService
from app.utils.exceptions import ValidationError

def test_register_user_success(app):
    """测试用户注册成功"""
    with app.app_context():
        user = AuthService.register(
            username='testuser',
            password='password123',
            email='test@example.com'
        )
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'

def test_register_duplicate_username(app):
    """测试重复用户名注册失败"""
    with app.app_context():
        AuthService.register('testuser', 'pass123', 'test1@example.com')
        
        with pytest.raises(ValidationError):
            AuthService.register('testuser', 'pass456', 'test2@example.com')
```

#### 属性测试

```python
# tests/test_exam_properties.py
from hypothesis import given, strategies as st
from app.services.exam_service import ExamService

@given(
    answers=st.dictionaries(
        st.integers(min_value=1, max_value=100),
        st.sampled_from(['A', 'B', 'C', 'D'])
    )
)
def test_score_calculation_property(app, answers):
    """
    Feature: exam-system, Property 8: 考试成绩计算正确性
    对于任意试卷和用户答案，计算的总分应该等于所有正确题目的分值之和
    """
    with app.app_context():
        # 测试逻辑
        pass
```

#### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定文件
pytest tests/test_auth_service.py

# 运行特定测试
pytest tests/test_auth_service.py::test_register_user_success

# 带覆盖率
pytest --cov=app --cov-report=html

# 详细输出
pytest -v -s
```

### 前端测试

#### 组件测试

```javascript
// tests/QuestionCard.test.js
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import QuestionCard from '@/components/QuestionCard.vue'

describe('QuestionCard', () => {
  it('renders question content', () => {
    const wrapper = mount(QuestionCard, {
      props: {
        question: {
          content: '测试题目',
          options: ['A. 选项1', 'B. 选项2']
        }
      }
    })
    
    expect(wrapper.text()).toContain('测试题目')
  })
  
  it('emits answer when option clicked', async () => {
    const wrapper = mount(QuestionCard, {
      props: {
        question: {
          content: '测试题目',
          options: ['A. 选项1', 'B. 选项2']
        }
      }
    })
    
    await wrapper.find('.option').trigger('click')
    expect(wrapper.emitted('answer-selected')).toBeTruthy()
  })
})
```

#### 运行测试

```bash
# 运行所有测试
npm run test

# 运行特定文件
npm run test -- QuestionCard.test.js

# 监听模式
npm run test:watch

# 覆盖率
npm run test:coverage
```

## API 开发

### 创建新的 API 端点

#### 1. 定义数据模型 (models/)

```python
# app/models/resource.py
from app import db
from datetime import datetime

class Resource(db.Model):
    __tablename__ = 'resources'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat()
        }
```

#### 2. 创建验证模式 (schemas/)

```python
# app/schemas/resource_schema.py
from marshmallow import Schema, fields, validate

class ResourceSchema(Schema):
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100)
    )
```

#### 3. 实现业务逻辑 (services/)

```python
# app/services/resource_service.py
from app import db
from app.models.resource import Resource
from app.utils.exceptions import ResourceNotFoundError

class ResourceService:
    @staticmethod
    def create(name):
        resource = Resource(name=name)
        db.session.add(resource)
        db.session.commit()
        return resource
    
    @staticmethod
    def get_by_id(resource_id):
        resource = Resource.query.get(resource_id)
        if not resource:
            raise ResourceNotFoundError('资源', resource_id)
        return resource
```

#### 4. 创建路由 (routes/)

```python
# app/routes/resources.py
from flask import Blueprint
from app.services.resource_service import ResourceService
from app.schemas.resource_schema import ResourceSchema
from app.utils.decorators import jwt_required_with_user
from app.utils.validators import validate_with_schema
from app.utils.response import success_response

bp = Blueprint('resources', __name__, url_prefix='/api/resources')

@bp.route('', methods=['POST'])
@jwt_required_with_user
@validate_with_schema(ResourceSchema)
def create_resource(current_user, validated_data):
    """创建资源"""
    resource = ResourceService.create(**validated_data)
    return success_response(
        data={'resource': resource.to_dict()},
        message='创建成功',
        status_code=201
    )

@bp.route('/<int:id>')
@jwt_required_with_user
def get_resource(current_user, id):
    """获取资源"""
    resource = ResourceService.get_by_id(id)
    return success_response(data={'resource': resource.to_dict()})
```

#### 5. 注册蓝图

```python
# app/__init__.py
from app.routes import resources

app.register_blueprint(resources.bp)
```

## 数据库开发

### 创建迁移

```bash
# 创建新迁移
flask db migrate -m "Add new table"

# 应用迁移
flask db upgrade

# 回滚迁移
flask db downgrade

# 查看迁移历史
flask db history
```

### 数据库查询最佳实践

```python
# 使用 eager loading 避免 N+1 查询
from sqlalchemy.orm import joinedload

questions = Question.query.options(
    joinedload(Question.created_by_user)
).all()

# 使用分页
from flask import request

page = request.args.get('page', 1, type=int)
per_page = request.args.get('per_page', 20, type=int)

pagination = Question.query.paginate(
    page=page,
    per_page=per_page,
    error_out=False
)

# 使用索引
# 在模型中定义
class Question(db.Model):
    __table_args__ = (
        db.Index('idx_exam_type', 'exam_type'),
        db.Index('idx_subject', 'subject'),
    )
```

## 前端开发

### 状态管理 (Pinia)

```javascript
// stores/exam.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useExamStore = defineStore('exam', () => {
  // State
  const currentSession = ref(null)
  const answers = ref({})
  
  // Getters
  const answeredCount = computed(() => {
    return Object.keys(answers.value).length
  })
  
  // Actions
  function startExam(session) {
    currentSession.value = session
    answers.value = {}
  }
  
  function submitAnswer(questionId, answer) {
    answers.value[questionId] = answer
  }
  
  return {
    currentSession,
    answers,
    answeredCount,
    startExam,
    submitAnswer
  }
})
```

### API 调用封装

```javascript
// api/exams.js
import request from '@/utils/request'

export default {
  // 获取试卷列表
  getExams(params) {
    return request.get('/exams', { params })
  },
  
  // 开始考试
  startExam(examId) {
    return request.post(`/exams/${examId}/start`)
  },
  
  // 提交答案
  submitAnswer(sessionId, data) {
    return request.post(`/exams/sessions/${sessionId}/answer`, data)
  }
}
```

### 路由守卫

```javascript
// router/index.js
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next('/login')
  } else if (to.meta.requiresAdmin && !userStore.isAdmin) {
    next('/403')
  } else {
    next()
  }
})
```

## 调试技巧

### 后端调试

#### 使用 Flask 调试器

```python
# 在代码中设置断点
import pdb; pdb.set_trace()

# 或使用 ipdb（更友好）
import ipdb; ipdb.set_trace()
```

#### 日志调试

```python
from flask import current_app

current_app.logger.debug(f'User ID: {user_id}')
current_app.logger.info(f'Processing request: {request.path}')
current_app.logger.error(f'Error occurred: {str(e)}', exc_info=True)
```

### 前端调试

#### Vue Devtools

安装 Vue Devtools 浏览器扩展进行调试。

#### Console 调试

```javascript
console.log('数据:', data)
console.table(users)  // 表格形式
console.time('操作')
// ... 代码
console.timeEnd('操作')  // 显示耗时
```

## 常见问题

### 后端问题

**Q: ImportError: cannot import name 'EVENT_TYPE_CLOSED'**

A: watchdog 版本冲突，使用 `python run.py --no-reload` 或升级 watchdog

**Q: 数据库迁移失败**

A: 删除 migrations 文件夹，重新初始化
```bash
rm -rf migrations
flask db init
flask db migrate
flask db upgrade
```

### 前端问题

**Q: npm install 失败**

A: 清除缓存重试
```bash
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

**Q: CORS 错误**

A: 检查后端 CORS 配置和前端 API_BASE_URL

---

**最后更新**: 2024-12-11
