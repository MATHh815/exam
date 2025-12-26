# 考公考研考编系统 - 前端

基于 Vue 3 + Vite + Element Plus 的现代化前端应用。

## 技术栈

- **框架**: Vue 3.4+ (Composition API)
- **构建工具**: Vite 5.0+
- **路由**: Vue Router 4.2+
- **状态管理**: Pinia 2.1+
- **UI 组件库**: Element Plus 2.5+
- **HTTP 客户端**: Axios 1.6+
- **图表库**: ECharts 5.4+ (vue-echarts)
- **样式**: Sass

## 项目结构

```
exam/frontend/
├── src/
│   ├── api/              # API 接口封装
│   │   └── index.js      # API 统一导出
│   ├── components/       # 可复用组件
│   ├── router/           # 路由配置
│   │   └── index.js      # 路由定义和守卫
│   ├── stores/           # Pinia 状态管理
│   │   └── index.js      # Store 统一导出
│   ├── utils/            # 工具函数
│   │   ├── request.js    # Axios 封装（拦截器）
│   │   └── storage.js    # LocalStorage 封装
│   ├── views/            # 页面视图
│   ├── App.vue           # 根组件
│   └── main.js           # 应用入口
├── public/               # 静态资源
├── .env.development      # 开发环境配置
├── .env.production       # 生产环境配置
├── index.html            # HTML 模板
├── vite.config.js        # Vite 配置
└── package.json          # 项目依赖
```

## 快速开始

### 安装依赖

```bash
npm install
```

### 开发模式

```bash
npm run dev
```

应用将在 http://localhost:5173 启动

### 构建生产版本

```bash
npm run build
```

构建产物将输出到 `dist/` 目录

### 预览生产构建

```bash
npm run preview
```

### 运行测试

```bash
npm run test
```

### 代码检查

```bash
npm run lint
```

## 核心配置

### API 请求配置

API 请求已通过 `src/utils/request.js` 进行封装，包含：

- **请求拦截器**: 自动添加 JWT Token
- **响应拦截器**: 统一错误处理和消息提示
- **超时设置**: 10 秒超时
- **基础 URL**: 通过环境变量配置

### 路由配置

路由配置位于 `src/router/index.js`：

- 使用 HTML5 History 模式
- 支持路由懒加载
- 全局路由守卫（认证检查将在后续任务中实现）

### 状态管理

使用 Pinia 进行状态管理：

- 模块化 Store 设计
- 支持 TypeScript 类型推断
- 开发工具集成

### 环境变量

开发环境 (`.env.development`):
```
VITE_API_BASE_URL=http://localhost:5000/api
VITE_APP_TITLE=考公考研考编系统
```

生产环境 (`.env.production`):
```
VITE_API_BASE_URL=/api
VITE_APP_TITLE=考公考研考编系统
```

## 开发规范

### 组件命名

- 组件文件使用 PascalCase: `UserProfile.vue`
- 组件名称使用 PascalCase: `<UserProfile />`

### 代码风格

- 使用 Composition API (`<script setup>`)
- 使用 ESLint 进行代码检查
- 遵循 Vue 3 官方风格指南

### API 调用

```javascript
import request from '@/utils/request'

// GET 请求
const data = await request.get('/endpoint')

// POST 请求
const result = await request.post('/endpoint', { data })
```

### 状态管理

```javascript
import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null,
    token: null
  }),
  actions: {
    async login(credentials) {
      // 登录逻辑
    }
  }
})
```

## 已完成功能

### ✅ 任务 20: 认证模块

已实现完整的用户认证功能：

- **API 封装** (`src/api/auth.js`): 登录、注册、用户信息、修改密码等接口
- **状态管理** (`src/stores/user.js`): 用户状态、令牌管理、自动持久化
- **登录注册页面** (`src/views/Login.vue`, `src/views/Register.vue`): 美观的表单界面和完整验证
- **用户信息页面** (`src/views/Profile.vue`): 查看和编辑个人信息、修改密码

详细说明请查看 [AUTHENTICATION_MODULE.md](./AUTHENTICATION_MODULE.md)

## 后续开发任务

根据实施计划 (tasks.md)，后续将实现：

1. ~~**任务 20**: 认证模块（登录、注册、用户信息）~~ ✅ 已完成
2. **任务 21**: 题库模块（题目展示、管理）
3. **任务 22**: 练习模块（练习页面、历史记录）
4. **任务 23**: 考试模块（考试页面、结果展示、试卷管理）
5. **任务 24**: 错题本模块
6. **任务 25**: 统计模块（图表展示）
7. **任务 26**: 仪表盘
8. **任务 27**: 响应式设计和优化
9. **任务 28**: 路由守卫和权限控制

## 常见问题

### 端口冲突

如果 5173 端口被占用，可以在 `vite.config.js` 中修改端口：

```javascript
server: {
  port: 3000  // 修改为其他端口
}
```

### API 代理配置

开发环境下，所有 `/api` 请求会被代理到 `http://localhost:5000`，配置位于 `vite.config.js`：

```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:5000',
      changeOrigin: true
    }
  }
}
```

### 跨域问题

开发环境通过 Vite 代理解决跨域问题。生产环境需要后端配置 CORS 或使用 Nginx 反向代理。

## 相关文档

- [Vue 3 官方文档](https://cn.vuejs.org/)
- [Vite 官方文档](https://cn.vitejs.dev/)
- [Element Plus 官方文档](https://element-plus.org/zh-CN/)
- [Pinia 官方文档](https://pinia.vuejs.org/zh/)
- [Vue Router 官方文档](https://router.vuejs.org/zh/)

## 许可证

MIT
