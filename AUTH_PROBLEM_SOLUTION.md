# 认证问题解决方案

## 问题描述
登录成功后立即出现多个"未授权，请重新登录"错误，导致用户无法正常使用系统。

## 根本原因分析

经过深入分析，问题的根本原因是：

1. **JWT Token过期时间过短** (15分钟)
2. **缺少自动Token刷新机制**
3. **数据库中可能缺少正确的用户数据**
4. **用户角色设置不正确**

## 解决方案

### 1. 立即修复 (推荐)

运行完整修复脚本：
```bash
# 在exam目录下运行
fix_auth_complete.bat
```

这个脚本会：
- 初始化数据库并创建测试用户
- 提供重启服务的指导
- 提供测试步骤

### 2. 手动修复步骤

#### 步骤1: 初始化数据库
```bash
cd exam
python init_database.py
```

#### 步骤2: 重启后端服务
```bash
cd exam/backend
python run.py
```

#### 步骤3: 重启前端服务
```bash
cd exam/frontend
npm run dev
```

#### 步骤4: 测试登录
使用以下账户：
- 管理员: `admin` / `123456`
- 测试用户: `testuser` / `123456`

### 3. 详细诊断

如果问题仍然存在，使用诊断工具：
1. 打开 `exam/diagnose_auth_issue.html`
2. 按顺序执行所有测试
3. 查看详细的错误信息

## 技术修复详情

### 1. JWT配置优化
- 访问令牌过期时间: 15分钟 → 1小时
- 文件: `exam/backend/.env`

### 2. 自动Token刷新
- 在401错误时自动尝试刷新token
- 刷新成功后重试原始请求
- 文件: `exam/frontend/src/utils/request.js`

### 3. 用户存储优化
- 改进初始化逻辑
- 优化状态恢复机制
- 文件: `exam/frontend/src/stores/user.js`

### 4. 路由守卫改进
- 优先检查token而不是用户对象
- 允许异步获取用户信息
- 文件: `exam/frontend/src/router/index.js`

## 测试工具

### 1. 基础测试
- `exam/frontend/test_auth_simple.html` - 简单认证测试
- `exam/test_token_refresh.html` - Token刷新测试

### 2. 完整诊断
- `exam/diagnose_auth_issue.html` - 完整的认证问题诊断工具

### 3. 调试脚本
- `exam/debug_auth.js` - 浏览器控制台调试脚本

## 验证修复效果

修复后应该看到：
1. ✅ 登录成功后不再出现401错误
2. ✅ 页面可以正常加载和导航
3. ✅ API请求正常工作
4. ✅ Token自动刷新机制工作正常

## 常见问题

### Q: 仍然出现401错误怎么办？
A: 
1. 确保后端服务已重启（JWT配置需要重启生效）
2. 清除浏览器localStorage
3. 使用诊断工具检查具体问题

### Q: 登录后立即跳转到登录页？
A: 
1. 检查浏览器控制台错误
2. 确认用户数据已正确保存到数据库
3. 验证用户角色设置正确

### Q: Token刷新不工作？
A: 
1. 检查refresh token是否存在
2. 确认后端refresh接口正常
3. 查看网络请求是否成功

## 联系支持

如果问题仍然存在，请提供：
1. 浏览器控制台错误信息
2. 网络请求详情
3. 诊断工具的测试结果

---

**最后更新**: 2024年1月9日
**版本**: 1.0.0