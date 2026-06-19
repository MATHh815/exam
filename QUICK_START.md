# 快速开始指南

## 新电脑首次运行

### 方法一：自动初始化（推荐）

1. **安装依赖**
   ```bash
   # 后端依赖
   cd exam/backend
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   
   # 前端依赖
   cd ../frontend
   npm install
   ```

2. **一键启动**
   ```bash
   cd exam
   start_all.bat
   ```
   
   脚本会自动检测数据库是否存在，如果不存在会提示初始化。

### 方法二：手动初始化

1. **后端设置**
   ```bash
   cd exam/backend
   
   # 创建虚拟环境
   python -m venv venv
   
   # 激活虚拟环境
   venv\Scripts\activate
   
   # 安装依赖
   pip install -r requirements.txt
   
   # 初始化数据库
   python setup_database.py
   
   # 启动后端
   python run.py
   ```

2. **前端设置**（新终端）
   ```bash
   cd exam/frontend
   
   # 安装依赖
   npm install
   
   # 启动前端
   npm run dev
   ```

### 方法三：使用批处理脚本

```bash
# 初始化数据库
cd exam/backend
setup_database.bat

# 启动项目
cd ..
start_all.bat
```

## 默认账号

- **管理员**: admin / admin123
- **学生**: student / student123

## 访问地址

- **前端**: http://localhost:5173
- **后端**: http://localhost:5000
- **API 文档**: http://localhost:5000/api/docs

## 验证安装

```bash
cd exam/backend
python diagnose_auth.py
```

应该看到所有检查项都显示 ✓

## 常见问题

### 1. 数据库未初始化

**错误**: `no such table: users`

**解决**:
```bash
cd exam/backend
python setup_database.py
```

### 2. 端口被占用

修改配置文件中的端口号：
- 后端: `exam/backend/run.py`
- 前端: `exam/frontend/vite.config.js`

### 3. 依赖安装失败

```bash
# 升级 pip
python -m pip install --upgrade pip

# 清除 npm 缓存
npm cache clean --force
```

## 下一步

- 查看 [API 文档](API_DOCUMENTATION.md)
- 查看 [部署指南](DEPLOYMENT_GUIDE.md)
- 查看 [功能路线图](FEATURE_ROADMAP.md)

---

**提示**: 第一次运行必须初始化数据库，之后可以直接使用 `start_all.bat` 启动。
