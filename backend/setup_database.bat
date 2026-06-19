@echo off
chcp 65001 >nul
echo ============================================================
echo 数据库初始化脚本
echo ============================================================
echo.

REM 检查虚拟环境
if not exist "venv\Scripts\activate.bat" (
    echo [错误] 虚拟环境不存在
    echo 请先运行: python -m venv venv
    pause
    exit /b 1
)

REM 激活虚拟环境
echo [1/3] 激活虚拟环境...
call venv\Scripts\activate.bat

REM 检查依赖
echo.
echo [2/3] 检查依赖...
python -c "import flask" 2>nul
if errorlevel 1 (
    echo [警告] 依赖未安装，正在安装...
    pip install -r requirements.txt
)

REM 初始化数据库
echo.
echo [3/3] 初始化数据库...
python setup_database.py

if errorlevel 1 (
    echo.
    echo [错误] 数据库初始化失败
    pause
    exit /b 1
)

echo.
echo ============================================================
echo ✅ 数据库初始化完成！
echo ============================================================
echo.
echo 可以使用以下账号登录：
echo   管理员 - 用户名: admin, 密码: admin123
echo   学生   - 用户名: student, 密码: student123
echo.
echo 下一步：
echo   1. 运行 python run.py 启动后端
echo   2. 或者返回上级目录运行 start_all.bat 启动完整项目
echo.
pause
