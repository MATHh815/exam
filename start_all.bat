@echo off
chcp 65001 >nul
echo ========================================
echo 考试系统 - 一键启动
echo ========================================
echo.

:: 检查是否在正确的目录
if not exist "backend" (
    echo [错误] 请在 exam 目录下运行此脚本
    pause
    exit /b 1
)

if not exist "frontend" (
    echo [错误] 请在 exam 目录下运行此脚本
    pause
    exit /b 1
)

echo [1/5] 检查后端依赖...
cd backend
python -c "import flask" 2>nul
if errorlevel 1 (
    echo [警告] Flask 未安装，正在安装依赖...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        cd ..
        pause
        exit /b 1
    )
)

echo [2/5] 检查数据库...
if not exist "instance\exam.db" (
    echo [警告] 数据库未初始化
    echo.
    set /p init="是否现在初始化数据库? (Y/N): "
    if /i "!init!"=="Y" (
        echo.
        echo 正在初始化数据库...
        python setup_database.py
        if errorlevel 1 (
            echo [错误] 数据库初始化失败
            cd ..
            pause
            exit /b 1
        )
        echo [✓] 数据库初始化成功
    ) else (
        echo [错误] 数据库未初始化，无法启动
        cd ..
        pause
        exit /b 1
    )
) else (
    echo [✓] 数据库已存在
)

echo [3/5] 初始化游戏化系统...
python init_user_points.py
if errorlevel 1 (
    echo [警告] 积分初始化失败，但继续启动...
)

echo.
echo [4/5] 启动后端服务器...
echo 后端将运行在: http://localhost:5000
echo.
start "考试系统 - 后端服务器" cmd /k "python run.py"

:: 等待后端启动
echo 等待后端服务器启动...
timeout /t 3 /nobreak >nul

cd ..\frontend

echo.
echo [5/5] 启动前端开发服务器...
echo 前端将运行在: http://localhost:5173
echo.

:: 检查 node_modules
if not exist "node_modules" (
    echo [警告] 依赖未安装，正在安装...
    echo 这可能需要几分钟...
    call npm install
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        cd ..
        pause
        exit /b 1
    )
)

:: 检查 lucide-vue-next
if not exist "node_modules\lucide-vue-next" (
    echo [警告] lucide-vue-next 未安装，正在安装...
    call npm install lucide-vue-next
    if errorlevel 1 (
        echo [错误] lucide-vue-next 安装失败
        echo 请手动运行: cd exam\frontend ^&^& npm install lucide-vue-next
        cd ..
        pause
        exit /b 1
    )
    echo [✓] lucide-vue-next 安装成功
)

start "考试系统 - 前端服务器" cmd /k "npm run dev"

cd ..

echo.
echo ========================================
echo 启动完成！
echo ========================================
echo.
echo 后端服务器: http://localhost:5000
echo 前端服务器: http://localhost:5173
echo.
echo 请等待几秒钟，然后在浏览器中访问:
echo http://localhost:5173
echo.
echo 按任意键打开浏览器...
pause >nul

start http://localhost:5173

echo.
echo 提示: 关闭此窗口不会停止服务器
echo 要停止服务器，请关闭对应的命令行窗口
echo.
pause
