@echo off
echo 正在清理 Python 缓存...

REM 删除所有 __pycache__ 目录
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

REM 删除所有 .pyc 文件
del /s /q *.pyc 2>nul

echo 缓存清理完成！
echo.
echo 现在可以重新启动后端服务器
pause
