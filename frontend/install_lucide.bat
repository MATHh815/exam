@echo off
chcp 65001 >nul
echo ========================================
echo 安装 lucide-vue-next 图标库
echo ========================================
echo.

echo [1/2] 安装 lucide-vue-next...
call npm install lucide-vue-next

if errorlevel 1 (
    echo.
    echo [错误] 安装失败
    echo.
    echo 请尝试:
    echo 1. 删除 node_modules 文件夹
    echo 2. 删除 package-lock.json
    echo 3. 重新运行此脚本
    echo.
    pause
    exit /b 1
)

echo.
echo [2/2] 验证安装...
if exist "node_modules\lucide-vue-next" (
    echo [✓] lucide-vue-next 安装成功！
) else (
    echo [✗] 安装验证失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 下一步:
echo 1. 重启 Vite 开发服务器
echo    - 在运行 npm run dev 的窗口按 Ctrl+C
echo    - 重新运行: npm run dev
echo.
echo 2. 刷新浏览器页面 (F5)
echo.
pause
