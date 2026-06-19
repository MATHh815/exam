@echo off
chcp 65001 >nul
echo ========================================
echo 局域网访问配置助手
echo ========================================
echo.

echo 正在获取本机 IP 地址...
echo.

for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    set IP=%%a
    set IP=!IP: =!
    echo 找到 IP 地址: !IP!
)

if not defined IP (
    echo 错误: 无法获取 IP 地址
    echo 请手动运行 ipconfig 查看
    pause
    exit /b 1
)

echo.
echo ========================================
echo 检测到的 IP 地址: %IP%
echo ========================================
echo.
echo 请确认这是正确的局域网 IP 地址
echo 如果不正确，请按 Ctrl+C 退出，然后手动配置
echo.
pause

echo.
echo 正在配置后端 CORS...
cd backend
if exist .env (
    findstr /C:"CORS_ORIGINS" .env >nul
    if !errorlevel! equ 0 (
        echo 找到 CORS_ORIGINS 配置
        echo 请手动编辑 backend\.env 文件
        echo 添加: http://%IP%:5173
    )
) else (
    echo 错误: 找不到 backend\.env 文件
)
cd ..

echo.
echo 正在配置前端 API 地址...
cd frontend
echo VITE_API_BASE_URL=http://%IP%:5000/api > .env.development.local
echo 已创建 frontend\.env.development.local
cd ..

echo.
echo ========================================
echo 配置完成！
echo ========================================
echo.
echo 下一步操作：
echo 1. 手动编辑 exam\backend\.env 文件
echo    在 CORS_ORIGINS 末尾添加: ,http://%IP%:5173
echo.
echo 2. 启动项目: start_all.bat
echo.
echo 3. 在其他设备访问: http://%IP%:5173
echo.
echo 4. 如需配置防火墙，以管理员身份运行：
echo    netsh advfirewall firewall add rule name="Exam Backend" dir=in action=allow protocol=TCP localport=5000
echo    netsh advfirewall firewall add rule name="Exam Frontend" dir=in action=allow protocol=TCP localport=5173
echo.
pause
