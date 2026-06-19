@echo off
chcp 65001 >nul
echo ========================================
echo API 连接诊断工具
echo ========================================
echo.

echo [1/5] 检查后端服务器...
curl -s http://localhost:5000/health >nul 2>&1
if errorlevel 1 (
    echo [✗] 后端服务器未运行
    echo.
    echo 解决方案:
    echo 1. 打开新的命令行窗口
    echo 2. cd exam\backend
    echo 3. python run.py
    echo.
    echo 或者运行: exam\start_all.bat
    echo.
    goto :error
) else (
    echo [✓] 后端服务器运行正常
)

echo.
echo [2/5] 检查 API 服务...
curl -s http://localhost:5000/api >nul 2>&1
if errorlevel 1 (
    echo [✗] API 服务异常
    goto :error
) else (
    echo [✓] API 服务正常
)

echo.
echo [3/5] 检查积分 API...
curl -s http://localhost:5000/api/points >nul 2>&1
if errorlevel 1 (
    echo [✗] 积分 API 异常
    goto :error
) else (
    echo [✓] 积分 API 已注册
)

echo.
echo [4/5] 检查成就 API...
curl -s http://localhost:5000/api/achievements >nul 2>&1
if errorlevel 1 (
    echo [✗] 成就 API 异常
    goto :error
) else (
    echo [✓] 成就 API 已注册
)

echo.
echo [5/5] 检查每日任务 API...
curl -s http://localhost:5000/api/daily-tasks >nul 2>&1
if errorlevel 1 (
    echo [✗] 每日任务 API 异常
    goto :error
) else (
    echo [✓] 每日任务 API 已注册
)

echo.
echo ========================================
echo 诊断结果: 全部正常 ✓
echo ========================================
echo.
echo 如果前端仍然报错，请尝试:
echo 1. 刷新浏览器页面 (F5)
echo 2. 清除浏览器缓存 (Ctrl+Shift+Delete)
echo 3. 运行: cd ..\backend ^&^& python init_user_points.py
echo.
pause
exit /b 0

:error
echo.
echo ========================================
echo 诊断结果: 发现问题 ✗
echo ========================================
echo.
echo 请按照上述提示解决问题
echo 或查看: API_CONNECTION_GUIDE.md
echo.
pause
exit /b 1
