@echo off
chcp 65001 >nul
echo.
echo ========================================
echo 🔧 考试系统认证问题完整修复工具
echo ========================================
echo.

echo 📋 修复内容:
echo 1. 修复JWT "Subject must be a string" 错误
echo 2. 初始化数据库和用户
echo 3. 重启后端服务
echo 4. 测试认证功能
echo.

pause

echo.
echo 🗄️ 步骤1: 初始化数据库...
echo.

REM 检查Python是否可用
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python未安装或不在PATH中
    echo 请安装Python或将其添加到PATH
    pause
    exit /b 1
)

REM 安装必要的依赖
echo 📦 安装bcrypt依赖...
pip install bcrypt >nul 2>&1

REM 运行数据库初始化
echo 🚀 运行数据库初始化...
python init_database.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ 数据库初始化失败！
    pause
    exit /b 1
)

echo.
echo ✅ 数据库初始化完成！
echo.

echo 🔄 步骤2: 重启服务 (重要!)
echo.

REM 提示用户重启服务
echo ⚠️ 重要: 必须重启后端服务以使JWT修复生效!
echo.
echo 请手动重启后端和前端服务:
echo.
echo 后端 (新终端):
echo   cd backend
echo   python run.py
echo.
echo 前端 (新终端):
echo   cd frontend  
echo   npm run dev
echo.

echo 📝 步骤3: 测试修复效果...
echo.
echo 服务重启后，请:
echo 1. 打开 test_jwt_fix.html 测试JWT修复
echo 2. 或者打开浏览器访问前端地址
echo 3. 使用以下账户登录测试:
echo    管理员: admin / 123456
echo    测试用户: testuser / 123456
echo.

echo 🎯 关键修复说明:
echo - 修复了JWT token的"Subject must be a string"错误
echo - 延长了token过期时间到1小时
echo - 添加了自动token刷新机制
echo - 创建了正确的用户数据
echo.

echo 🎉 修复完成！
echo.
echo 如果仍有问题，请检查:
echo - 后端服务是否已重启 (必须重启!)
echo - 前端服务是否正常运行
echo - 浏览器控制台是否还有错误信息
echo.

pause