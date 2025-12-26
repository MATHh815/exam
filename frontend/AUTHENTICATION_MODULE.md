# 前端认证模块实现说明

## 概述

本文档描述了任务 20（前端认证模块）的实现细节。该模块实现了完整的用户认证功能，包括 API 封装、状态管理、登录注册页面和用户信息页面。

## 实现的功能

### 1. 认证 API 封装 (任务 20.1)

**文件**: `src/api/auth.js`

实现了以下 API 接口封装：

- `register(data)` - 用户注册
- `login(data)` - 用户登录
- `logout()` - 用户登出
- `refreshToken()` - 刷新访问令牌
- `getProfile()` - 获取当前用户信息
- `updateProfile(data)` - 更新用户信息
- `changePassword(data)` - 修改密码
- `resetPassword(data)` - 重置密码

所有 API 调用都使用统一的 `request` 工具，自动处理令牌注入和错误处理。

### 2. 认证状态管理 (任务 20.2)

**文件**: `src/stores/user.js`

使用 Pinia 实现的用户状态管理，包含：

**状态**:
- `user` - 用户信息对象
- `accessToken` - 访问令牌
- `refreshToken` - 刷新令牌

**计算属性**:
- `isLoggedIn` - 是否已登录
- `isAdmin` - 是否为管理员
- `userInfo` - 用户信息

**方法**:
- `register()` - 用户注册（注册成功后自动登录）
- `login()` - 用户登录
- `logout()` - 用户登出
- `fetchUserInfo()` - 获取用户信息
- `refreshAccessToken()` - 刷新访问令牌
- `setTokens()` / `clearTokens()` - 令牌管理
- `setUser()` / `clearUser()` - 用户信息管理

**特性**:
- 自动持久化到 localStorage
- 页面刷新后自动恢复登录状态
- 令牌过期自动清除登录状态

### 3. 登录注册页面 (任务 20.3)

**文件**: 
- `src/views/Login.vue` - 登录/注册组合页面
- `src/views/Register.vue` - 独立注册页面

**Login.vue 特性**:
- 支持登录和注册模式切换
- 完整的表单验证
- 美观的渐变背景
- 响应式设计

**Register.vue 特性**:
- 独立的注册页面
- 完整的表单验证（用户名、邮箱、密码、确认密码）
- 注册成功后自动登录并跳转

**表单验证规则**:
- 用户名：3-20 个字符
- 密码：至少 6 个字符
- 邮箱：标准邮箱格式
- 确认密码：必须与密码一致

### 4. 用户信息页面 (任务 20.4)

**文件**: `src/views/Profile.vue`

**功能**:
- 查看用户信息（用户名、昵称、邮箱、角色、注册时间、更新时间）
- 编辑用户信息（昵称、邮箱、头像）
- 修改密码（需要输入旧密码）
- 信息展示和编辑模式切换

**特性**:
- 使用 Element Plus Descriptions 组件展示信息
- 表单验证
- 修改密码后自动登出并跳转到登录页

## 路由配置

更新了 `src/router/index.js`，添加了以下路由：

```javascript
/login       - 登录页面（不需要认证）
/register    - 注册页面（不需要认证）
/dashboard   - 仪表盘（需要认证）
/profile     - 个人信息页面（需要认证）
```

每个路由都配置了 `meta.requiresAuth` 标识，为后续的路由守卫实现做准备（任务 28）。

## 辅助页面

**文件**: `src/views/Dashboard.vue`

创建了一个简单的仪表盘页面作为首页，包含：
- 欢迎信息
- 当前用户信息展示
- 快速跳转到个人信息页
- 退出登录功能

## 使用示例

### 在组件中使用用户状态

```vue
<script setup>
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

// 检查登录状态
if (userStore.isLoggedIn) {
  console.log('用户已登录:', userStore.userInfo)
}

// 检查管理员权限
if (userStore.isAdmin) {
  console.log('当前用户是管理员')
}

// 登录
async function handleLogin() {
  await userStore.login({
    username: 'test',
    password: '123456'
  })
}

// 登出
async function handleLogout() {
  await userStore.logout()
}
</script>
```

### 调用认证 API

```javascript
import { login, register, getProfile } from '@/api/auth'

// 登录
const response = await login({
  username: 'test',
  password: '123456'
})

// 注册
const response = await register({
  username: 'newuser',
  password: '123456',
  email: 'user@example.com',
  nickname: '新用户'
})

// 获取用户信息
const response = await getProfile()
```

## 环境配置

确保 `.env.development` 和 `.env.production` 文件中配置了正确的 API 地址：

```bash
# 开发环境
VITE_API_BASE_URL=http://localhost:5000/api

# 生产环境
VITE_API_BASE_URL=/api
```

## 后续任务

以下功能将在后续任务中实现：

1. **任务 28**: 路由守卫和权限控制
   - 实现登录状态检查
   - 实现管理员权限检查
   - 实现未登录重定向

2. **任务 26**: 完善仪表盘
   - 实现快速入口
   - 实现学习数据概览
   - 实现最近活动展示

## 测试建议

1. **手动测试流程**:
   - 访问 `/register` 注册新用户
   - 注册成功后自动登录并跳转到首页
   - 访问 `/profile` 查看和编辑个人信息
   - 修改密码并验证需要重新登录
   - 退出登录并验证跳转到登录页
   - 访问 `/login` 使用已注册用户登录

2. **需要验证的功能**:
   - 表单验证是否正常工作
   - 令牌是否正确存储和使用
   - 页面刷新后登录状态是否保持
   - 错误提示是否友好
   - 响应式布局是否正常

## 注意事项

1. **安全性**:
   - 令牌存储在 localStorage 中
   - 所有 API 请求自动携带令牌
   - 令牌过期后自动清除登录状态

2. **用户体验**:
   - 所有表单都有完整的验证
   - 错误信息友好且明确
   - 加载状态有明确的视觉反馈
   - 页面布局美观且响应式

3. **代码质量**:
   - 使用 Composition API
   - 代码注释完整
   - 遵循 Vue 3 最佳实践
   - 使用 Element Plus 组件库

## 总结

任务 20（前端认证模块）已完全实现，包括：
- ✅ 20.1 实现认证 API 封装
- ✅ 20.2 实现认证状态管理
- ✅ 20.3 实现登录注册页面
- ✅ 20.4 实现用户信息页面

所有代码已通过语法检查，可以正常运行。用户可以开始测试认证功能，或继续实现后续任务。
