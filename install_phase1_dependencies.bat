@echo off
echo ========================================
echo 安装第一阶段功能增强依赖包
echo ========================================
echo.

echo [1/3] 激活 Python 虚拟环境...
cd backend
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo 虚拟环境已激活
) else (
    echo 错误: 虚拟环境不存在，请先创建虚拟环境
    echo 运行: python -m venv venv
    pause
    exit /b 1
)

echo.
echo [2/3] 安装 Python 依赖包...
pip install APScheduler==3.10.4
pip install reportlab==4.0.7
pip install Markdown==3.5.1
echo Python 依赖包安装完成

echo.
echo [3/3] 安装前端依赖包...
cd ..\frontend
call npm install dompurify@^3.0.6
call npm install vue-cal@^4.9.0
echo 前端依赖包安装完成

echo.
echo ========================================
echo 所有依赖包安装完成！
echo ========================================
echo.
echo 新增的 Python 包:
echo   - APScheduler 3.10.4 (定时任务)
echo   - ReportLab 4.0.7 (PDF 生成)
echo   - Markdown 3.5.1 (Markdown 处理)
echo.
echo 新增的前端包:
echo   - dompurify 3.0.6 (XSS 防护)
echo   - vue-cal 4.9.0 (日历组件)
echo.
echo 注意: marked 已经安装 (版本 17.0.1)
echo.
pause
