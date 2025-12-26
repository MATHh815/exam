# 考公考研考编系统

一个综合性的在线学习和考试管理平台，支持公务员考试、研究生考试和事业编考试的题库练习、模拟考试、学习进度跟踪和成绩分析。

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![Vue](https://img.shields.io/badge/Vue-3.0-brightgreen.svg)](https://vuejs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 目录

- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [文档](#文档)
- [开发指南](#开发指南)
- [测试](#测试)
- [部署](#部署)
- [贡献](#贡献)
- [许可证](#许可证)

## 功能特性

### 核心功能

- ✅ **用户管理** - 注册、登录、个人信息管理、权限控制
- ✅ **题库管理** - 题目增删改查、批量导入、分类筛选
- ✅ **在线练习** - 随机抽题、专项练习、即时反馈、答题记录
- ✅ **模拟考试** - 计时考试、自动批改、成绩报告、详细解析
- ✅ **错题本** - 自动收集错题、针对性复习、掌握状态跟踪
- ✅ **学习统计** - 数据分析、知识点雷达图、学习趋势图表
- ✅ **试卷管理** - 创建试卷、发布管理、版本控制

### 技术亮点

- 🔐 JWT 认证和权限控制
- 📊 ECharts 数据可视化
- 🎯 属性测试保证代码正确性
- 📱 响应式设计，支持移动端
- ⚡ 性能优化（懒加载、代码分割）
- 🔄 数据导入导出功能
- 📝 完整的错误处理和日志系统

## 技术栈

### 后端

- **框架**: Flask 3.0
- **ORM**: SQLAlchemy 2.0
- **认证**: Flask-JWT-Extended
- **数据库**: SQLite（支持迁移到 PostgreSQL/MySQL）
- **测试**: Pytest + Hypothesis（属性测试）
- **验证**: Marshmallow
- **迁移**: Flask-Migrate

### 前端

- **框架**: Vue 3 (Composition API)
- **构建工具**: Vite
- **路由**: Vue Router 4
- **状态管理**: Pinia
- **UI 组件**: Element Plus
- **图表**: ECharts
- **HTTP 客户端**: Axios
- **测试**: Vitest

## 项目结构

```
exam/
├── backend/                    # Flask 后端
│   ├── app/
│   │   ├── models/            # 数据模型
│   │   │   ├── user.py        # 用户模型
│   │   │   ├── question.py    # 题目模型
│   │   │   ├── exam.py        # 考试模型
│   │   │   ├── practice.py    # 练习模型
│   │   │   └── statistics.py  # 统计模型
│   │   ├── routes/            # API 路由
│   │   │   ├── auth.py        # 认证路由
│   │   │   ├── questions.py   # 题库路由
│   │   │   ├── practice.py    # 练习路由
│   │   │   ├── exams.py       # 考试路由
│   │   │   └── statistics.py  # 统计路由
│   │   ├── services/          # 业务逻辑层
│   │   │   ├── auth_service.py
│   │   │   ├── question_service.py
│   │   │   ├── practice_service.py
│   │   │   ├── exam_service.py
│   │   │   └── statistics_service.py
│   │   ├── schemas/           # 数据验证模式
│   │   │   ├── user_schema.py
│   │   │   ├── question_schema.py
│   │   │   └── exam_schema.py
│   │   └── utils/             # 工具函数
│   │       ├── decorators.py  # 装饰器
│   │       ├── validators.py  # 验证器
│   │       ├── exceptions.py  # 自定义异常
│   │       └── response.py    # 响应格式化
│   ├── tests/                 # 测试文件
│   │   ├── test_auth_service.py
│   │   ├── test_statistics_service.py
│   │   ├── test_data_service.py
│   │   └── test_api_integration.py
│   ├── migrations/            # 数据库迁移
│   ├── instance/              # 实例文件（数据库）
│   ├── logs/                  # 日志文件
│   ├── config.py              # 配置文件
│   ├── run.py                 # 启动脚本
│   ├── init_db.py             # 数据库初始化
│   └── requirements.txt       # Python 依赖
│
└── frontend/                  # Vue 前端
    ├── src/
    │   ├── api/               # API 调用封装
    │   │   ├── auth.js
    │   │   ├── questions.js
    │   │   ├── practice.js
    │   │   ├── exams.js
    │   │   └── statistics.js
    │   ├── components/        # 可复用组件
    │   │   ├── QuestionCard.vue
    │   │   ├── AnswerOptions.vue
    │   │   ├── ExamTimer.vue
    │   │   ├── ExamProgress.vue
    │   │   ├── StatisticsChart.vue
    │   │   ├── KnowledgeRadar.vue
    │   │   └── TrendLine.vue
    │   ├── views/             # 页面视图
    │   │   ├── Login.vue
    │   │   ├── Register.vue
    │   │   ├── Dashboard.vue
    │   │   ├── QuestionManagement.vue
    │   │   ├── Exam.vue
    │   │   ├── ExamResult.vue
    │   │   ├── WrongBook.vue
    │   │   └── Statistics.vue
    │   ├── stores/            # Pinia 状态管理
    │   │   ├── user.js
    │   │   └── exam.js
    │   ├── router/            # 路由配置
    │   │   └── index.js
    │   ├── utils/             # 工具函数
    │   │   ├── request.js     # HTTP 请求封装
    │   │   ├── storage.js     # 本地存储
    │   │   ├── errorHandler.js
    │   │   └── performance.js
    │   ├── App.vue
    │   └── main.js
    ├── public/
    ├── package.json
    └── vite.config.js
```

## 快速开始

### 前置要求

- Python 3.9 或更高版本
- Node.js 16 或更高版本
- npm 或 yarn

### 后端设置

1. **创建虚拟环境并安装依赖**

```bash
cd exam/backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

2. **配置环境变量**

```bash
# Windows
copy .env.example .env

# macOS/Linux
cp .env.example .env

# 编辑 .env 文件，设置必要的配置
```

3. **初始化数据库**

```bash
# 使用 Flask-Migrate
flask db upgrade

# 或使用初始化脚本
python init_db.py
```

4. **运行开发服务器**

```bash
flask run
# 或
python run.py
```

后端服务将在 http://localhost:5000 运行

### 前端设置

1. **安装依赖**

```bash
cd exam/frontend
npm install
```

2. **运行开发服务器**

```bash
npm run dev
```

前端应用将在 http://localhost:5173 运行

### 访问应用

打开浏览器访问 http://localhost:5173，你将看到登录页面。

**默认管理员账户**（如果运行了初始化脚本）：
- 用户名: admin
- 密码: admin123

## 文档

### 核心文档
- [快速开始指南](GETTING_STARTED.md) - 详细的安装和配置指南
- [API 文档](API_DOCUMENTATION.md) - 完整的 API 接口文档
- [开发指南](DEVELOPMENT_GUIDE.md) - 开发规范和最佳实践
- [部署指南](DEPLOYMENT.md) - 生产环境部署说明

### 专题文档
- [故障排除指南](TROUBLESHOOTING.md) - 常见问题和解决方案
- [文档总结](DOCUMENTATION_SUMMARY.md) - 所有文档的索引和使用指南
- [错误处理指南](backend/ERROR_HANDLING_GUIDE.md) - 错误处理系统说明
- [数据导入导出](backend/DATA_IMPORT_EXPORT.md) - 数据迁移指南
- [快速参考](backend/QUICK_REFERENCE.md) - 后端开发快速参考

## 开发指南

### 代码规范

**后端 (Python)**
- 遵循 PEP 8 代码风格
- 使用 Black 进行代码格式化
- 使用 isort 排序导入
- 使用 Flake8 进行代码检查

```bash
black app/
isort app/
flake8 app/
```

**前端 (JavaScript/Vue)**
- 遵循 Vue 3 风格指南
- 使用 ESLint 进行代码检查
- 使用 Prettier 进行代码格式化

```bash
npm run lint
npm run format
```

### 开发工作流

1. 查看任务列表：`.kiro/specs/exam-system/tasks.md`
2. 选择一个任务开始开发
3. 创建功能分支：`git checkout -b feature/功能名称`
4. 编写代码和测试
5. 运行测试确保通过
6. 提交代码：`git commit -m "feat: 功能描述"`
7. 推送并创建 Pull Request

### Git 提交规范

使用 Conventional Commits 规范：

- `feat:` 新功能
- `fix:` 修复 bug
- `docs:` 文档更新
- `style:` 代码格式调整
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建/工具相关

## 测试

### 后端测试

```bash
cd exam/backend

# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_auth_service.py

# 运行带覆盖率的测试
pytest --cov=app --cov-report=html

# 运行属性测试
pytest tests/ -v -s
```

### 前端测试

```bash
cd exam/frontend

# 运行单元测试
npm run test

# 运行测试并生成覆盖率报告
npm run test:coverage

# 运行特定测试文件
npm run test -- QuestionCard.test.js
```

### 测试覆盖率

- 后端测试覆盖率目标：> 80%
- 前端测试覆盖率目标：> 70%

## 部署

### 开发环境

开发环境使用 Flask 内置服务器和 Vite 开发服务器。

### 生产环境

生产环境推荐使用：
- **后端**: Gunicorn + Nginx
- **前端**: 静态文件托管（Nginx/CDN）
- **数据库**: PostgreSQL 或 MySQL

详细部署步骤请参考 [DEPLOYMENT.md](DEPLOYMENT.md)

### Docker 部署

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

## 性能优化

- ✅ 数据库查询优化（索引、eager loading）
- ✅ 前端代码分割和懒加载
- ✅ 静态资源压缩和缓存
- ✅ API 响应缓存
- ✅ 图片懒加载

## 安全特性

- 🔐 JWT 令牌认证
- 🔒 密码 bcrypt 哈希
- 🛡️ CORS 跨域保护
- 🚫 SQL 注入防护（ORM）
- 🔍 输入验证和清理
- 📝 安全日志记录

## 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 常见问题

### 后端启动失败

**问题**: `ModuleNotFoundError: No module named 'flask'`

**解决**: 确保已激活虚拟环境并安装依赖
```bash
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 数据库错误

**问题**: `OperationalError: no such table`

**解决**: 运行数据库迁移
```bash
flask db upgrade
```

### CORS 错误

**问题**: 前端无法访问后端 API

**解决**: 检查 .env 文件中的 CORS_ORIGINS 配置
```
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

## 路线图

- [ ] 移动端应用（React Native）
- [ ] AI 智能推荐题目
- [ ] 实时对战答题
- [ ] 视频课程集成
- [ ] 社交学习功能

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 联系方式

如有问题或建议，请：
- 提交 Issue
- 发送邮件至：support@example.com
- 访问项目主页：https://github.com/yourusername/exam-system

## 致谢

感谢所有贡献者和开源社区的支持！

---

⭐ 如果这个项目对你有帮助，请给我们一个 Star！
