# 路由守卫和权限控制实现文档

## 概述

本文档描述了考公考研考编系统前端的路由守卫和权限控制实现。

## 实现的功能

### 1. 登录状态检查

路由守卫会检查用户的登录状态：

- **已登录用户**：可以访问需要认证的页面
- **未登录用户**：访问需要认证的页面时，会被重定向到登录页

```javascript
// 检查登录状态
if (!userStore.isLoggedIn) {
  // 未登录，重定向到登录页
  ElMessage.warning('请先登录')
  next({
    name: 'login',
    query: { redirect: to.fullPath } // 保存目标路由，登录后跳转
  })
  return
}
```

### 2. 管理员权限检查

对于需要管理员权限的页面（如题库管理、试卷管理），路由守卫会检查用户角色：

- **管理员用户**：可以访问管理页面
- **普通用户**：访问管理页面时，会被拒绝并重定向到仪表盘

```javascript
// 检查管理员权限
if (requiresAdmin && !userStore.isAdmin) {
  // 非管理员访问管理员页面
  ElMessage.error('您没有权限访问该页面')
  next({ name: 'dashboard' })
  return
}
```

### 3. 未登录重定向

当未登录用户尝试访问需要认证的页面时：

1. 显示提示消息："请先登录"
2. 重定向到登录页
3. 在 URL 中保存原始目标路径（通过 `redirect` 查询参数）
4. 登录成功后，自动跳转到原始目标页面

```javascript
// 登录组件中的重定向处理
const redirect = route.query.redirect || '/'
router.push(redirect)
```

## 路由元信息配置

每个路由可以通过 `meta` 字段配置权限要求：

```javascript
{
  path: '/dashboard',
  name: 'dashboard',
  component: () => import('../views/Dashboard.vue'),
  meta: { 
    requiresAuth: true,  // 需要登录
    title: '仪表盘' 
  }
}

{
  path: '/questions',
  name: 'questions',
  component: () => import('../views/QuestionManagement.vue'),
  meta: { 
    requiresAuth: true,      // 需要登录
    requiresAdmin: true,     // 需要管理员权限
    title: '题库管理' 
  }
}

{
  path: '/login',
  name: 'login',
  component: () => import('../views/Login.vue'),
  meta: { 
    requiresAuth: false,  // 不需要登录
    title: '登录' 
  }
}
```

## 用户体验优化

### 1. 已登录用户访问登录页

如果已登录用户访问登录或注册页面，会自动重定向到仪表盘：

```javascript
if ((to.name === 'login' || to.name === 'register') && userStore.isLoggedIn) {
  next({ name: 'dashboard' })
  return
}
```

### 2. 令牌过期处理

如果用户信息不完整，路由守卫会尝试重新获取用户信息：

```javascript
if (!userStore.user) {
  try {
    await userStore.fetchUserInfo()
  } catch (error) {
    // 获取用户信息失败，可能是令牌过期
    ElMessage.error('登录已过期，请重新登录')
    next({
      name: 'login',
      query: { redirect: to.fullPath }
    })
    return
  }
}
```

### 3. 友好的错误提示

使用 Element Plus 的消息组件显示友好的提示信息：

- 未登录：`ElMessage.warning('请先登录')`
- 权限不足：`ElMessage.error('您没有权限访问该页面')`
- 令牌过期：`ElMessage.error('登录已过期，请重新登录')`

## 需要管理员权限的页面

以下页面需要管理员权限：

1. **题库管理** (`/questions`)
   - 创建、编辑、删除题目
   - 批量导入题目

2. **试卷管理** (`/exam-papers`)
   - 创建、编辑、删除试卷
   - 设置试卷题目和分值

## 测试场景

### 场景 1：未登录用户访问受保护页面

1. 用户未登录
2. 访问 `/dashboard`
3. 显示提示："请先登录"
4. 重定向到 `/login?redirect=/dashboard`
5. 登录成功后自动跳转到 `/dashboard`

### 场景 2：普通用户访问管理页面

1. 用户已登录（普通用户）
2. 访问 `/questions`
3. 显示提示："您没有权限访问该页面"
4. 重定向到 `/dashboard`

### 场景 3：管理员访问管理页面

1. 用户已登录（管理员）
2. 访问 `/questions`
3. 成功访问题库管理页面

### 场景 4：已登录用户访问登录页

1. 用户已登录
2. 访问 `/login`
3. 自动重定向到 `/dashboard`

## 相关文件

- `exam/frontend/src/router/index.js` - 路由配置和守卫实现
- `exam/frontend/src/stores/user.js` - 用户状态管理
- `exam/frontend/src/views/Login.vue` - 登录组件（包含重定向处理）

## 验证需求

本实现满足以下需求：

- **需求 9.3**：WHEN 访问受保护资源 THEN 系统 SHALL 验证请求中的身份令牌

实现的具体功能：

1. ✅ 实现登录状态检查
2. ✅ 实现管理员权限检查
3. ✅ 实现未登录重定向
4. ✅ 保存原始目标路径，登录后自动跳转
5. ✅ 令牌过期自动处理
6. ✅ 友好的用户提示信息
