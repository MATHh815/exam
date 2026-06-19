# 部署指南

本文档提供考公考研考编系统在生产环境中的部署指南。

## 目录

- [部署架构](#部署架构)
- [前置要求](#前置要求)
- [数据库迁移](#数据库迁移)
- [后端部署](#后端部署)
- [前端部署](#前端部署)
- [Nginx 配置](#nginx-配置)
- [Docker 部署](#docker-部署)
- [环境变量配置](#环境变量配置)
- [SSL/HTTPS 配置](#sslhttps-配置)
- [监控和日志](#监控和日志)
- [备份策略](#备份策略)
- [性能优化](#性能优化)
- [故障排除](#故障排除)

## 部署架构

### 推荐架构

```
                    Internet
                       |
                   [Nginx]
                  (反向代理)
                       |
        +--------------+--------------+
        |                             |
   [静态文件]                    [Gunicorn]
   (Vue Build)                  (Flask App)
                                      |
                                [PostgreSQL]
                                  (数据库)
```

### 组件说明

- **Nginx**: 反向代理、静态文件服务、SSL 终止
- **Gunicorn**: Python WSGI HTTP 服务器
- **Flask**: 后端应用
- **PostgreSQL**: 生产数据库（推荐）
- **Vue (Build)**: 前端静态文件

## 前置要求

### 服务器要求

- **操作系统**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **CPU**: 2 核心以上
- **内存**: 4GB 以上
- **存储**: 20GB 以上
- **网络**: 公网 IP 或域名

### 软件要求

- Python 3.9+
- Node.js 16+
- PostgreSQL 13+ 或 MySQL 8+
- Nginx 1.18+
- Git

## 数据库迁移

### 从 SQLite 迁移到 PostgreSQL

#### 1. 安装 PostgreSQL

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# CentOS/RHEL
sudo yum install postgresql-server postgresql-contrib
sudo postgresql-setup initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### 2. 创建数据库和用户

```bash
sudo -u postgres psql

# 在 PostgreSQL 命令行中
CREATE DATABASE exam_system;
CREATE USER exam_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE exam_system TO exam_user;
\q
```

#### 3. 导出 SQLite 数据

```bash
cd exam/backend
python -c "
from app import create_app
from app.services.data_service import DataService

app = create_app()
with app.app_context():
    data = DataService.export_data(format='json')
    with open('export.json', 'w', encoding='utf-8') as f:
        import json
        json.dump(data, f, ensure_ascii=False, indent=2)
"
```

#### 4. 更新配置

编辑 `.env` 文件：

```bash
DATABASE_URL=postgresql://exam_user:your_secure_password@localhost/exam_system
```

#### 5. 初始化新数据库

```bash
flask db upgrade
```

#### 6. 导入数据

```bash
python -c "
from app import create_app
from app.services.data_service import DataService
import json

app = create_app()
with app.app_context():
    with open('export.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    DataService.import_data(data, format='json')
"
```

## 后端部署

### 1. 准备服务器

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装依赖
sudo apt install python3-pip python3-venv nginx postgresql -y
```

### 2. 克隆代码

```bash
cd /var/www
sudo git clone <repository-url> exam-system
sudo chown -R $USER:$USER exam-system
cd exam-system/exam/backend
```

### 3. 创建虚拟环境

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

### 4. 配置环境变量

```bash
cp .env.example .env
nano .env
```

生产环境配置示例：

```bash
FLASK_ENV=production
SECRET_KEY=your-very-secure-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

DATABASE_URL=postgresql://exam_user:password@localhost/exam_system

CORS_ORIGINS=https://yourdomain.com

LOG_LEVEL=INFO
LOG_FILE=/var/log/exam-system/app.log
```

### 5. 初始化数据库

```bash
flask db upgrade
python init_db.py  # 可选：创建初始数据
```

### 6. 测试运行

```bash
gunicorn -w 4 -b 127.0.0.1:5000 "app:create_app()"
```

### 7. 创建 Systemd 服务

创建 `/etc/systemd/system/exam-backend.service`:

```ini
[Unit]
Description=Exam System Backend
After=network.target postgresql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/exam-system/exam/backend
Environment="PATH=/var/www/exam-system/exam/backend/venv/bin"
ExecStart=/var/www/exam-system/exam/backend/venv/bin/gunicorn \
    -w 4 \
    -b 127.0.0.1:5000 \
    --access-logfile /var/log/exam-system/access.log \
    --error-logfile /var/log/exam-system/error.log \
    --log-level info \
    "app:create_app()"

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo mkdir -p /var/log/exam-system
sudo chown www-data:www-data /var/log/exam-system
sudo systemctl daemon-reload
sudo systemctl start exam-backend
sudo systemctl enable exam-backend
sudo systemctl status exam-backend
```

## 前端部署

### 1. 构建前端

```bash
cd /var/www/exam-system/exam/frontend

# 安装依赖
npm install

# 配置生产环境变量
nano .env.production
```

`.env.production` 内容：

```bash
VITE_API_BASE_URL=https://yourdomain.com/api
VITE_APP_TITLE=考公考研考编系统
```

构建：

```bash
npm run build
```

### 2. 部署静态文件

```bash
sudo mkdir -p /var/www/exam-frontend
sudo cp -r dist/* /var/www/exam-frontend/
sudo chown -R www-data:www-data /var/www/exam-frontend
```

## Nginx 配置

### 创建 Nginx 配置

创建 `/etc/nginx/sites-available/exam-system`:

```nginx
# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS 配置
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL 证书
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # 日志
    access_log /var/log/nginx/exam-access.log;
    error_log /var/log/nginx/exam-error.log;

    # 前端静态文件
    location / {
        root /var/www/exam-frontend;
        try_files $uri $uri/ /index.html;
        
        # 缓存静态资源
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # 后端 API 代理
    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 文件上传大小限制
    client_max_body_size 10M;

    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript 
               application/x-javascript application/xml+rss 
               application/json application/javascript;
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/exam-system /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Docker 部署

### 1. 创建 Dockerfile

**后端 Dockerfile** (`exam/backend/Dockerfile`):

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# 复制应用代码
COPY . .

# 创建日志目录
RUN mkdir -p /app/logs

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app()"]
```

**前端 Dockerfile** (`exam/frontend/Dockerfile`):

```dockerfile
FROM node:16-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### 2. 创建 docker-compose.yml

```yaml
version: '3.8'

services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: exam_system
      POSTGRES_USER: exam_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - exam-network

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://exam_user:${DB_PASSWORD}@db/exam_system
      SECRET_KEY: ${SECRET_KEY}
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      FLASK_ENV: production
    depends_on:
      - db
    networks:
      - exam-network
    volumes:
      - ./backend/logs:/app/logs

  frontend:
    build: ./frontend
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - backend
    networks:
      - exam-network
    volumes:
      - ./nginx/ssl:/etc/nginx/ssl

volumes:
  postgres_data:

networks:
  exam-network:
    driver: bridge
```

### 3. 部署

```bash
# 创建 .env 文件
cat > .env << EOF
DB_PASSWORD=your_secure_password
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret_key
EOF

# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 初始化数据库
docker-compose exec backend flask db upgrade
```

## 环境变量配置

### 生产环境必需变量

```bash
# Flask 配置
FLASK_ENV=production
SECRET_KEY=<生成强随机密钥>
JWT_SECRET_KEY=<生成强随机密钥>

# 数据库
DATABASE_URL=postgresql://user:password@host:port/database

# CORS
CORS_ORIGINS=https://yourdomain.com

# 日志
LOG_LEVEL=INFO
LOG_FILE=/var/log/exam-system/app.log

# JWT 配置
JWT_ACCESS_TOKEN_EXPIRES=900  # 15分钟
JWT_REFRESH_TOKEN_EXPIRES=604800  # 7天
```

### 生成安全密钥

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## SSL/HTTPS 配置

### 使用 Let's Encrypt

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 自动续期
sudo certbot renew --dry-run
```

### 手动证书配置

如果使用自己的证书：

```bash
sudo mkdir -p /etc/nginx/ssl
sudo cp your-cert.crt /etc/nginx/ssl/
sudo cp your-key.key /etc/nginx/ssl/
sudo chmod 600 /etc/nginx/ssl/your-key.key
```

## 监控和日志

### 日志管理

#### 后端日志

```bash
# 查看实时日志
sudo tail -f /var/log/exam-system/app.log

# 查看错误日志
sudo tail -f /var/log/exam-system/error.log

# 日志轮转配置
sudo nano /etc/logrotate.d/exam-system
```

`/etc/logrotate.d/exam-system`:

```
/var/log/exam-system/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload exam-backend > /dev/null 2>&1 || true
    endscript
}
```

#### Nginx 日志

```bash
# 访问日志
sudo tail -f /var/log/nginx/exam-access.log

# 错误日志
sudo tail -f /var/log/nginx/exam-error.log
```

### 性能监控

推荐使用以下工具：

- **Prometheus + Grafana**: 系统和应用监控
- **ELK Stack**: 日志聚合和分析
- **New Relic / Datadog**: APM 监控

## 备份策略

### 数据库备份

#### 自动备份脚本

创建 `/usr/local/bin/backup-exam-db.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/var/backups/exam-system"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/exam_db_$DATE.sql.gz"

mkdir -p $BACKUP_DIR

# 备份数据库
pg_dump -U exam_user exam_system | gzip > $BACKUP_FILE

# 保留最近30天的备份
find $BACKUP_DIR -name "exam_db_*.sql.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_FILE"
```

设置定时任务：

```bash
sudo chmod +x /usr/local/bin/backup-exam-db.sh
sudo crontab -e

# 每天凌晨2点备份
0 2 * * * /usr/local/bin/backup-exam-db.sh
```

### 文件备份

```bash
# 备份上传的文件和日志
tar -czf /var/backups/exam-files-$(date +%Y%m%d).tar.gz \
    /var/www/exam-system/exam/backend/instance \
    /var/log/exam-system
```

## 性能优化

### 数据库优化

```sql
-- 创建索引
CREATE INDEX idx_questions_exam_type ON questions(exam_type);
CREATE INDEX idx_questions_subject ON questions(subject);
CREATE INDEX idx_practice_records_user_id ON practice_records(user_id);
CREATE INDEX idx_exam_results_user_id ON exam_results(user_id);

-- 分析表
ANALYZE questions;
ANALYZE practice_records;
ANALYZE exam_results;
```

### Gunicorn 优化

```bash
# 计算 worker 数量：(2 x CPU核心数) + 1
gunicorn -w 9 \
    --worker-class=gevent \
    --worker-connections=1000 \
    --max-requests=1000 \
    --max-requests-jitter=100 \
    -b 127.0.0.1:5000 \
    "app:create_app()"
```

### Nginx 优化

在 nginx.conf 中添加：

```nginx
# Worker 进程数
worker_processes auto;

# 连接数
events {
    worker_connections 2048;
    use epoll;
}

# 缓存
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=1g;
```

## 故障排除

### 后端无法启动

```bash
# 检查服务状态
sudo systemctl status exam-backend

# 查看日志
sudo journalctl -u exam-backend -n 50

# 检查端口占用
sudo netstat -tlnp | grep 5000
```

### 数据库连接失败

```bash
# 检查 PostgreSQL 状态
sudo systemctl status postgresql

# 测试连接
psql -U exam_user -d exam_system -h localhost

# 检查配置
sudo nano /etc/postgresql/13/main/pg_hba.conf
```

### Nginx 502 错误

```bash
# 检查后端是否运行
curl http://127.0.0.1:5000/api/health

# 检查 Nginx 配置
sudo nginx -t

# 查看错误日志
sudo tail -f /var/log/nginx/exam-error.log
```

### 性能问题

```bash
# 检查系统资源
htop
df -h
free -m

# 检查数据库性能
sudo -u postgres psql exam_system -c "SELECT * FROM pg_stat_activity;"

# 检查慢查询
sudo -u postgres psql exam_system -c "SELECT query, calls, total_time FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
```

## 安全检查清单

- [ ] 使用强密码和密钥
- [ ] 启用 HTTPS
- [ ] 配置防火墙
- [ ] 定期更新系统和依赖
- [ ] 限制数据库访问
- [ ] 配置日志监控
- [ ] 设置自动备份
- [ ] 使用非 root 用户运行服务
- [ ] 配置速率限制
- [ ] 定期安全审计

## 更新和维护

### 应用更新

```bash
cd /var/www/exam-system
git pull origin main

# 后端更新
cd exam/backend
source venv/bin/activate
pip install -r requirements.txt
flask db upgrade
sudo systemctl restart exam-backend

# 前端更新
cd ../frontend
npm install
npm run build
sudo cp -r dist/* /var/www/exam-frontend/
```

### 零停机更新

使用 Gunicorn 的优雅重启：

```bash
# 发送 HUP 信号
sudo systemctl reload exam-backend
```

---

**最后更新**: 2024-12-11
