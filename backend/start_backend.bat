@echo off
echo ========================================
echo 启动考试系统后端
echo ========================================
echo.

REM 检查虚拟环境
if not exist "venv\Scripts\activate.bat" (
    echo [错误] 虚拟环境不存在，请先创建虚拟环境
    echo 运行: python -m venv venv
    pause
    exit /b 1
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 检查数据库
if not exist "instance\exam.db" (
    echo [提示] 数据库不存在，正在初始化...
    python init_db.py
    echo.
)

echo [启动] 后端服务启动中...
echo [地址] http://localhost:5000
echo [提示] 按 Ctrl+C 停止服务
echo.
python run.py
