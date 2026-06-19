# 认证数据库问题修复

## 问题描述

用户在尝试登录和注册时遇到 500 Internal Server Error，后端日志显示：

```
✗ 用户表访问失败: (sqlite3.OperationalError) no such table: users
```

## 根本原因

数据库表未创建。虽然后端代码和模型定义都正确，但数据库中没有实际的表结构。

## 解决方案

### 1. 创建数据库设置脚本

创建了 `setup_database.py` 脚本，该脚本会：
- 创建所有数据库表（使用 `db.create_all()`）
- 初始化管理员和学生测试用户
- 验证数据库设置和登录功能

### 2. 执行数据库设置

```bash
cd exam/backend
python setup_database.py
```

### 3. 验证结果

创建了 `diagnose_auth.py` 诊断脚本来验证：
- ✅ 数据库连接正常
- ✅ 用户表存在，共有 2 个用户
- ✅ 密码验证成功
- ✅ 登录流程成功，JWT 令牌生成正常

## 创建的用户账号

### 管理员账号
- **用户名**: admin
- **密码**: admin123
- **邮箱**: admin@example.com
- **角色**: admin

### 学生账号
- **用户名**: student
- **密码**: student123
- **邮箱**: student@example.com
- **角色**: user

## 创建的数据库表

以下表已成功创建：

### 核心表
- `users` - 用户表
- `questions` - 题目表
- `exam_papers` - 试卷表
- `exam_paper_questions` - 试卷题目关联表
- `exam_sessions` - 考试会话表
- `exam_results` - 考试结果表
- `practice_records` - 练习记录表
- `wrong_questions` - 错题本表
- `study_statistics` - 学习统计表

### Phase 1 增强功能表
- `study_plans` - 学习计划表
- `study_goals` - 学习目标表
- `study_reminders` - 学习提醒表
- `question_notes` - 题目笔记表
- `question_bookmarks` - 题目收藏表
- `achievements` - 成就定义表
- `user_achievements` - 用户成就表
- `user_points` - 用户积分表
- `point_transactions` - 积分交易记录表
- `daily_tasks` - 每日任务表

### 考研功能表
- `graduate_schools` - 研究生院校表
- `graduate_majors` - 研究生专业表
- `score_lines` - 分数线表
- `exam_subjects` - 考试科目表

## 测试验证

### 登录测试
```bash
python diagnose_auth.py
```

输出结果：
```
✓ 登录成功
- 用户ID: 1
- 用户名: admin
- 访问令牌: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
- 刷新令牌: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 后续步骤

1. **重启后端服务**
   ```bash
   cd exam/backend
   python run.py
   ```

2. **测试前端登录**
   - 使用 admin/admin123 或 student/student123 登录
   - 验证 JWT 令牌正常工作
   - 确认 API 调用成功

3. **初始化其他数据**（可选）
   - 运行 `init_achievements.py` 初始化成就数据
   - 运行 `init_user_points.py` 初始化用户积分
   - 运行 `seed_exam_data.py` 添加示例题目

## 相关文件

- `exam/backend/setup_database.py` - 数据库设置脚本
- `exam/backend/diagnose_auth.py` - 认证诊断脚本
- `exam/backend/config.py` - 应用配置
- `exam/backend/app/routes/auth.py` - 认证路由
- `exam/backend/app/services/auth_service.py` - 认证服务

## 注意事项

1. **数据库文件位置**: `exam/backend/instance/exam.db`
2. **JWT 配置**: 使用环境变量或默认配置
3. **密码加密**: 使用 bcrypt 加密存储
4. **令牌过期时间**: 
   - 访问令牌: 15 分钟 (900 秒)
   - 刷新令牌: 7 天 (604800 秒)

## 问题解决

如果仍然遇到登录问题：

1. 检查数据库文件是否存在
2. 运行诊断脚本验证
3. 检查后端日志
4. 确认 JWT_SECRET_KEY 配置正确
5. 清除浏览器缓存和 localStorage

---

**修复时间**: 2025-12-26
**修复状态**: ✅ 完成
