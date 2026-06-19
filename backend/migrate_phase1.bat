@echo off
echo ========================================
echo 第一阶段功能增强 - 数据库迁移
echo ========================================
echo.

echo [1/2] 激活虚拟环境...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo 虚拟环境已激活
) else (
    echo 错误: 虚拟环境不存在
    pause
    exit /b 1
)

echo.
echo [2/2] 执行数据库迁移...
echo.

REM 使用 Flask-Migrate 命令
echo 生成迁移脚本...
flask db migrate -m "Add Phase 1 enhancement models"

echo.
echo 迁移脚本已生成，请检查 migrations/versions/ 目录
echo.
pause

echo.
echo 应用迁移到数据库...
flask db upgrade

echo.
echo ========================================
echo 数据库迁移完成！
echo ========================================
echo.
pause
