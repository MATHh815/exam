@echo off
chcp 65001 >nul
echo ============================================================
echo 收藏功能修复脚本
echo ============================================================
echo.

echo [1/3] 更新数据库表结构...
echo ------------------------------------------------------------
cd backend
python migrate_add_bookmark_notes.py
if %errorlevel% neq 0 (
    echo.
    echo ✗ 数据库迁移失败
    echo 请检查错误信息并手动修复
    pause
    exit /b 1
)

echo.
echo [2/3] 检查后端服务...
echo ------------------------------------------------------------
echo 请确保后端服务正在运行
echo 如果没有运行，请在新窗口执行: cd exam\backend ^&^& python run.py
echo.
pause

echo.
echo [3/3] 检查前端服务...
echo ------------------------------------------------------------
echo 请确保前端服务正在运行
echo 如果没有运行，请在新窗口执行: cd exam\frontend ^&^& npm run dev
echo.
pause

echo.
echo ============================================================
echo 修复完成！
echo ============================================================
echo.
echo 下一步:
echo   1. 访问 http://localhost:5173
echo   2. 登录系统
echo   3. 点击"我的收藏"菜单
echo   4. 测试收藏功能
echo.
echo 如果还有问题，请查看 BOOKMARKS_FIX.md 文档
echo.
pause
