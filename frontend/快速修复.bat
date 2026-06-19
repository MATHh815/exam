@echo off
chcp 65001 >nul
echo ========================================
echo 前端依赖快速修复
echo ========================================
echo.

echo 这个脚本会:
echo 1. 安装 lucide-vue-next 图标库
echo 2. 验证安装
echo.
echo 按任意键继续...
pause >nul

echo.
echo [1/2] 安装 lucide-vue-next...
call npm install lucide-vue-next

if errorlevel 1 (
    echo.
    echo [错误] 安装失败
    echo.
    echo 尝试完全重新安装:
    echo 1. 关闭 Vite 服务器 (Ctrl+C)
    echo 2. 删除 node_modules 文件夹
    echo 3. 运行: npm install
    echo.
    pause
    exit /b 1
)

echo.
echo [2/2] 验证安装...
if exist "node_modules\lucide-vue-next" (
    echo [✓] 安装成功！
) else (
    echo [✗] 验证失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo 修复完成！
echo ========================================
echo.
echo 下一步操作:
echo.
echo 1. 如果 Vite 服务器正在运行:
echo    - 按 Ctrl+C 停止服务器
echo    - 重新运行: npm run dev
echo.
echo 2. 如果 Vite 服务器未运行:
echo    - 运行: npm run dev
echo.
echo 3. 刷新浏览器页面 (F5)
echo.
echo 4. 重新点击"游戏化"菜单
echo.
pause
