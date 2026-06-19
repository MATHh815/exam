# 故障排除指南

本文档收集了考公考研考编系统开发和部署过程中的常见问题及解决方案。

## 目录

- [后端问题](#后端问题)
- [前端问题](#前端问题)
- [数据库问题](#数据库问题)
- [部署问题](#部署问题)
- [性能问题](#性能问题)

---

## 后端问题

### 1. Watchdog 导入错误

**错误信息**:
```
ImportError: cannot import name 'EVENT_TYPE_CLOSED' from 'watchdog.events'
```

**原因**: Flask/Werkzeug 与 watchdog 库版本不兼容

**解决方案**:

方案一（推荐）：使用 --no-reload 标志
```bash
python run.py --no-reload
```

方案二：升级 watchdog
```bash
pip install --upgrade watchdog
```

方案三：降级 watchdog
```bash
pip install watchdog==2.1.9
```

---

### 2. 模块未找到错误

**错误信息**:
```
ModuleNotFoundError: No module named 'flask'
```

**原因**: 虚拟环境未激活或依赖未安装

**解决方案**:
```bash
# 激活虚拟环境
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

---

### 3. 数据库表不存在

**错误信息**:
```
sqlalchemy.exc.OperationalError: no such table: users
```

**原因**: 数据库未初始化或迁移未执行

**解决方案**:
```bash
# 方案一：使用 Flask-Migrate
flask db upgrade

# 方案二：使用初始化脚本
python init_db.py

# 方案三：重新创建数据库
rm instance/exam.db
flask db upgrade
```

---

### 4. JWT 令牌错误

**错误信息**:
```
jwt.exceptions.DecodeError: Not enough segments
```

**原因**: JWT 令牌格式错误或已过期

**解决方案**:
```python
# 检查令牌格式
# 正确格式: Bearer <token>

# 前端请求示例
headers: {
  'Authorization': `Bearer ${token}`
}

# 检查令牌是否过期
# 重新登录获取新令牌
```

---

### 5. CORS 错误

**错误信息**:
```
Access to XMLHttpRequest has been blocked by CORS policy
```

**原因**: 跨域配置不正确

**解决方案**:

检查后端 `.env` 文件:
```bash
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

检查 Flask-CORS 配置:
```python
# app/__init__.py
from flask_cors import CORS

CORS(app, resources={
    r"/api/*": {
        "origins": os.getenv('CORS_ORIGINS', '').split(','),
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

---

### 6. 数据库连接失败

**错误信息**:
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**原因**: 数据库服务未启动或连接配置错误

**解决方案**:

检查 PostgreSQL 服务:
```bash
# 检查状态
sudo systemctl status postgresql

# 启动服务
sudo systemctl start postgresql
```

检查连接字符串:
```bash
# .env 文件
DATABASE_URL=postgresql://user:password@localhost:5432/exam_system
```

测试连接:
```bash
psql -U exam_user -d exam_system -h localhost
```

---

### 7. 端口已被占用

**错误信息**:
```
OSError: [Errno 48] Address already in use
```

**原因**: 端口 5000 已被其他进程占用

**解决方案**:

查找占用进程:
```bash
# Windows
netstat -ano | findstr :5000

# macOS/Linux
lsof -i :5000
```

终止进程:
```bash
# Windows
taskkill /PID <PID> /F

# macOS/Linux
kill -9 <PID>
```

或使用其他端口:
```bash
flask run --port 5001
```

---

## 前端问题

### 1. npm install 失败

**错误信息**:
```
npm ERR! code ERESOLVE
npm ERR! ERESOLVE unable to resolve dependency tree
```

**原因**: 依赖冲突或缓存问题

**解决方案**:
```bash
# 清除缓存
rm -rf node_modules package-lock.json
npm cache clean --force

# 重新安装
npm install

# 如果仍然失败，使用 --legacy-peer-deps
npm install --legacy-peer-deps
```

---

### 2. Vite 启动失败

**错误信息**:
```
Error: Cannot find module '@vitejs/plugin-vue'
```

**原因**: 依赖未正确安装

**解决方案**:
```bash
# 重新安装依赖
npm install

# 或单独安装缺失的包
npm install @vitejs/plugin-vue --save-dev
```

---

### 3. API 请求失败

**错误信息**:
```
Network Error
```

**原因**: 后端未启动或 API 地址配置错误

**解决方案**:

1. 确认后端已启动:
```bash
curl http://localhost:5000/api/health
```

2. 检查前端配置:
```bash
# .env.development
VITE_API_BASE_URL=http://localhost:5000/api
```

3. 检查浏览器控制台网络请求

---

### 4. 路由 404 错误

**错误信息**: 刷新页面后显示 404

**原因**: 单页应用路由配置问题

**解决方案**:

开发环境：Vite 自动处理

生产环境：配置 Nginx
```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```

---

### 5. 组件样式不生效

**原因**: scoped 样式或 CSS 导入问题

**解决方案**:

检查 scoped 属性:
```vue
<style scoped>
/* 样式只作用于当前组件 */
</style>
```

检查全局样式导入:
```javascript
// main.js
import './assets/styles/main.css'
```

---

## 数据库问题

### 1. 迁移冲突

**错误信息**:
```
alembic.util.exc.CommandError: Target database is not up to date
```

**原因**: 数据库版本与迁移脚本不一致

**解决方案**:
```bash
# 查看当前版本
flask db current

# 查看迁移历史
flask db history

# 强制升级到最新版本
flask db upgrade head

# 如果仍有问题，重置迁移
rm -rf migrations
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

---

### 2. 数据迁移失败

**错误信息**: 从 SQLite 迁移到 PostgreSQL 时数据丢失

**解决方案**:

使用数据导出导入功能:
```bash
# 1. 导出 SQLite 数据
python -c "
from app import create_app
from app.services.data_service import DataService
import json

app = create_app()
with app.app_context():
    data = DataService.export_data(format='json')
    with open('backup.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
"

# 2. 切换到 PostgreSQL
# 修改 .env 中的 DATABASE_URL

# 3. 初始化新数据库
flask db upgrade

# 4. 导入数据
python -c "
from app import create_app
from app.services.data_service import DataService
import json

app = create_app()
with app.app_context():
    with open('backup.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    DataService.import_data(data, format='json')
"
```

---

### 3. 外键约束错误

**错误信息**:
```
IntegrityError: FOREIGN KEY constraint failed
```

**原因**: 尝试删除被引用的记录

**解决方案**:

使用软删除:
```python
# 不要物理删除
# db.session.delete(question)

# 使用软删除
question.is_deleted = True
db.session.commit()
```

或级联删除:
```python
class Question(db.Model):
    # 定义级联删除
    practice_records = db.relationship(
        'PracticeRecord',
        backref='question',
        cascade='all, delete-orphan'
    )
```

---

## 部署问题

### 1. Gunicorn 启动失败

**错误信息**:
```
ModuleNotFoundError: No module named 'app'
```

**原因**: 工作目录或 Python 路径不正确

**解决方案**:

检查 systemd 服务配置:
```ini
[Service]
WorkingDirectory=/var/www/exam-system/exam/backend
Environment="PATH=/var/www/exam-system/exam/backend/venv/bin"
ExecStart=/var/www/exam-system/exam/backend/venv/bin/gunicorn \
    -w 4 \
    -b 127.0.0.1:5000 \
    "app:create_app()"
```

---

### 2. Nginx 502 Bad Gateway

**原因**: 后端服务未运行或连接失败

**解决方案**:

1. 检查后端服务:
```bash
sudo systemctl status exam-backend
curl http://127.0.0.1:5000/api/health
```

2. 检查 Nginx 配置:
```nginx
location /api {
    proxy_pass http://127.0.0.1:5000;
    # 确保端口正确
}
```

3. 查看日志:
```bash
sudo tail -f /var/log/nginx/error.log
sudo journalctl -u exam-backend -n 50
```

---

### 3. 静态文件 404

**原因**: 静态文件路径配置错误

**解决方案**:

检查 Nginx 配置:
```nginx
location / {
    root /var/www/exam-frontend;
    try_files $uri $uri/ /index.html;
}
```

检查文件权限:
```bash
sudo chown -R www-data:www-data /var/www/exam-frontend
sudo chmod -R 755 /var/www/exam-frontend
```

---

### 4. SSL 证书错误

**错误信息**: 证书无效或过期

**解决方案**:

使用 Let's Encrypt 自动续期:
```bash
# 测试续期
sudo certbot renew --dry-run

# 手动续期
sudo certbot renew

# 设置自动续期
sudo crontab -e
# 添加: 0 0 * * * certbot renew --quiet
```

---

## 性能问题

### 1. API 响应慢

**原因**: 数据库查询未优化

**解决方案**:

1. 添加数据库索引:
```sql
CREATE INDEX idx_questions_exam_type ON questions(exam_type);
CREATE INDEX idx_practice_records_user_id ON practice_records(user_id);
```

2. 使用 eager loading:
```python
questions = Question.query.options(
    joinedload(Question.created_by_user)
).all()
```

3. 启用查询缓存

---

### 2. 前端加载慢

**原因**: 资源未优化

**解决方案**:

1. 启用代码分割:
```javascript
// router/index.js
const Dashboard = () => import('@/views/Dashboard.vue')
```

2. 压缩资源:
```bash
npm run build
# Vite 自动压缩
```

3. 使用 CDN

---

### 3. 数据库连接池耗尽

**错误信息**:
```
QueuePool limit of size 5 overflow 10 reached
```

**原因**: 连接未正确释放

**解决方案**:

调整连接池配置:
```python
# config.py
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
    'max_overflow': 20
}
```

确保使用上下文管理器:
```python
with app.app_context():
    # 数据库操作
    pass
```

---

## 获取帮助

如果以上解决方案都无法解决你的问题：

1. 查看详细日志
2. 搜索错误信息
3. 查看项目 Issues
4. 提交新的 Issue（包含错误信息和环境信息）

---

**最后更新**: 2024-12-11
