# 头像点击功能修复

## 问题描述
用户反馈在考试系统前端,点击头像无法跳转到个人信息页面进行信息修改。

## 问题分析
检查代码发现:
1. 后端已经实现了用户信息更新的 API (`PUT /api/auth/profile`)
2. 前端已经有完整的个人信息页面 (`Profile.vue`)
3. 路由配置正确 (`/profile`)
4. **但是** Dashboard 页面的头像没有添加点击事件

## 修复内容

### 1. 添加头像点击事件
在 `exam/frontend/src/views/Dashboard.vue` 中:

```vue
<!-- 修改前 -->
<div class="welcome-avatar">
  <el-avatar :size="80" :src="userStore.userInfo?.avatar">
    {{ (userStore.userInfo?.nickname || userStore.userInfo?.username)?.charAt(0) }}
  </el-avatar>
</div>

<!-- 修改后 -->
<div class="welcome-avatar" @click="goToProfile" title="点击查看个人信息">
  <el-avatar :size="80" :src="userStore.userInfo?.avatar" class="clickable-avatar">
    {{ (userStore.userInfo?.nickname || userStore.userInfo?.username)?.charAt(0) }}
  </el-avatar>
</div>
```

### 2. 添加跳转方法
```javascript
/**
 * 跳转到个人信息页面
 */
function goToProfile() {
  router.push('/profile')
}
```

### 3. 添加样式
```css
.welcome-avatar {
  flex-shrink: 0;
  cursor: pointer;
  transition: transform 0.3s;
}

.welcome-avatar:hover {
  transform: scale(1.05);
}

.clickable-avatar {
  cursor: pointer;
}
```

## 功能说明

### 用户信息修改流程
1. 用户在 Dashboard 页面点击头像
2. 跳转到个人信息页面 (`/profile`)
3. 点击"编辑信息"按钮
4. 修改昵称、邮箱、头像 URL
5. 点击"保存"按钮
6. 调用后端 API 更新信息
7. 更新成功后刷新本地用户信息

### 支持的修改项
- ✅ 昵称 (nickname)
- ✅ 邮箱 (email)
- ✅ 头像 URL (avatar)
- ✅ 密码修改 (通过"修改密码"按钮)
- ❌ 用户名 (username) - 不可修改

## 后端 API

### 获取用户信息
```
GET /api/auth/profile
Authorization: Bearer {access_token}
```

### 更新用户信息
```
PUT /api/auth/profile
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "nickname": "新昵称",
  "email": "new@example.com",
  "avatar": "https://example.com/avatar.jpg"
}
```

### 修改密码
```
POST /api/auth/change-password
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "old_password": "旧密码",
  "new_password": "新密码"
}
```

## 测试步骤

1. 启动前端和后端服务
2. 登录系统
3. 在 Dashboard 页面,鼠标悬停在头像上,应该看到:
   - 鼠标指针变为手型
   - 头像略微放大
   - 显示提示文字"点击查看个人信息"
4. 点击头像,应该跳转到个人信息页面
5. 点击"编辑信息"按钮
6. 修改昵称或邮箱
7. 点击"保存"
8. 应该看到"更新成功"的提示
9. 返回 Dashboard,头像旁边的昵称应该已更新

## 相关文件
- `exam/frontend/src/views/Dashboard.vue` - 仪表盘页面(头像显示)
- `exam/frontend/src/views/Profile.vue` - 个人信息页面
- `exam/frontend/src/api/auth.js` - 认证相关 API
- `exam/frontend/src/stores/user.js` - 用户状态管理
- `exam/backend/app/routes/auth.py` - 后端认证路由
- `exam/backend/app/services/auth_service.py` - 后端认证服务

## 注意事项
1. 头像 URL 需要是有效的图片链接
2. 邮箱格式会进行验证
3. 修改密码后会自动登出,需要重新登录
4. 用户名一旦注册后不可修改
