@echo off
echo ========================================
echo 考公考研考编系统 - Docker 测试脚本
echo ========================================
echo.

REM 检查Docker是否运行
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Docker未运行，请先启动Docker Desktop
    pause
    exit /b 1
)

echo [提示] 使用国内镜像源，构建速度更快
echo.

echo [1/6] 停止并清理旧容器...
docker-compose down -v

echo.
echo [2/6] 清理Docker缓存（可选，首次运行可跳过）...
echo 按任意键继续，或等待5秒自动继续...
timeout /t 5

echo.
echo [3/6] 构建Docker镜像（使用国内镜像源）...
docker-compose build --no-cache

if %errorlevel% neq 0 (
    echo.
    echo [错误] 构建失败！
    echo.
    echo 可能的原因：
    echo 1. 网络问题 - 请检查网络连接
    echo 2. Docker镜像源问题 - 查看 DOCKER_MIRROR_FIX.md
    echo 3. 磁盘空间不足 - 运行 docker system prune -a
    echo.
    pause
    exit /b 1
)

echo.
echo [4/6] 启动服务...
docker-compose up -d

echo.
echo [5/6] 等待服务启动（30秒）...
timeout /t 30 /nobreak

echo.
echo [6/6] 初始化数据库...
docker-compose exec backend python init_db.py

echo.
echo [7/7] 检查服务状态...
docker-compose ps
echo.

echo.
echo ========================================
echo 服务已启动！
echo ========================================
echo.
echo 访问地址:
echo   前端: http://localhost:5173
echo   后端: http://localhost:5000
echo   API文档: http://localhost:5000/api
echo.
echo 测试账户:
echo   用户名: admin
echo   密码: admin123
echo.
echo 查看日志:
echo   docker-compose logs -f
echo.
echo 停止服务:
echo   docker-compose down
echo.
echo ========================================
echo 现在可以在浏览器中测试登录功能了！
echo 打开 http://localhost:5173 并查看控制台日志
echo ========================================
echo.
pause
