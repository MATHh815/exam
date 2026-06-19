# 项目部署指南

## 在新电脑上运行项目

### 前置要求

1. **Python 3.8+** 已安装
2. **Node.js 16+** 已安装
3. **Git** 已安装（如果从 GitHub 克隆）

### 快速部署步骤

#### 1. 获取项目代码

```bash
# 如果从 GitHub 克隆
git clone <your-repo-url>
cd exam

# 或者直接复制整个 exam 文件夹到新电脑
```

#### 2. 后端设置

```bash
cd exam/backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库（重要！）
python setup_database.py

# 可选：初始化其他数据
python init_achievements.py
python init_user_points.py

# 启动后端
python run.py
```

后端将在 `http://localhost:5000` 运行

#### 3. 前端设置

打开新的终端窗口：

```bash
cd exam/frontend

# 安装依赖
npm install

# 启动前端
npm run dev
```

前端将在 `http://localhost:5173` 运行

### 一键启动（Windows）

项目根目录提供了一键启动脚本：

```bash
cd exam
start_all.bat
```

这个脚本会：
1. 检查并激活后端虚拟环境
2. 启动后端服务器
3. 启动前端开发服务器

### 默认账号

数据库初始化后会自动创建以下账号：

- **管理员账号**
  - 用户名: `admin`
  - 密码: `admin123`

- **学生账号**
  - 用户名: `student`
  - 密码: `student123`

### 验证部署

1. **检查后端**
   ```bash
   cd exam/backend
   python diagnose_auth.py
   ```
   应该看到所有检查项都显示 ✓

2. **访问前端**
   - 打开浏览器访问 `http://localhost:5173`
   - 使用 admin/admin123 登录
   - 确认可以正常访问各个功能

### 数据库文件位置

- SQLite 数据库文件: `exam/backend/instance/exam.db`
- 如果需要重置数据库，删除此文件后重新运行 `python setup_database.py`

### 常见问题

#### 1. 数据库表不存在错误

**症状**: 登录时返回 401 或 500 错误

**解决方案**:
```bash
cd exam/backend
python setup_database.py
```

#### 2. 端口被占用

**症状**: 启动时提示端口已被使用

**解决方案**:
- 后端: 修改 `exam/backend/run.py` 中的端口号
- 前端: 修改 `exam/frontend/vite.config.js` 中的端口号

#### 3. 依赖安装失败

**后端依赖问题**:
```bash
# 升级 pip
python -m pip install --upgrade pip

# 重新安装
pip install -r requirements.txt
```

**前端依赖问题**:
```bash
# 清除缓存
npm cache clean --force

# 重新安装
rm -rf node_modules package-lock.json
npm install
```

#### 4. CORS 跨域错误

**症状**: 前端无法访问后端 API

**解决方案**: 检查 `exam/backend/config.py` 中的 CORS 配置
```python
# 开发环境允许所有来源
CORS_ORIGINS = ['*']
```

### 环境配置（可选）

创建 `exam/backend/.env` 文件自定义配置：

```env
# Flask 配置
SECRET_KEY=your-secret-key-here
FLASK_ENV=development

# 数据库配置
DATABASE_URL=sqlite:///exam.db

# JWT 配置
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRES=900
JWT_REFRESH_TOKEN_EXPIRES=604800

# CORS 配置
CORS_ORIGINS=http://localhost:5173

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### 生产环境部署

生产环境建议使用：

1. **数据库**: PostgreSQL 或 MySQL（而不是 SQLite）
2. **Web 服务器**: Gunicorn + Nginx
3. **进程管理**: Supervisor 或 systemd
4. **前端**: 构建静态文件并使用 Nginx 托管

详细的生产环境部署指南请参考 `DEPLOYMENT.md`

### 项目结构

```
exam/
├── backend/              # 后端代码
│   ├── app/             # 应用代码
│   ├── instance/        # 数据库文件
│   ├── venv/            # 虚拟环境
│   ├── setup_database.py  # 数据库初始化脚本
│   ├── requirements.txt   # Python 依赖
│   └── run.py           # 启动文件
├── frontend/            # 前端代码
│   ├── src/            # 源代码
│   ├── node_modules/   # Node 依赖
│   └── package.json    # 前端依赖配置
└── start_all.bat       # 一键启动脚本
```

### 备份和迁移

#### 备份数据库
```bash
# 复制数据库文件
cp exam/backend/instance/exam.db exam/backend/instance/exam.db.backup
```

#### 迁移到新电脑
1. 复制整个 `exam` 文件夹
2. 在新电脑上重新安装依赖
3. 数据库文件会自动保留所有数据

### 技术支持

如遇到问题，请查看：
- `exam/AUTH_DATABASE_FIX.md` - 认证问题解决方案
- `exam/TROUBLESHOOTING.md` - 常见问题排查
- `exam/API_DOCUMENTATION.md` - API 文档

---

**最后更新**: 2025-12-26
