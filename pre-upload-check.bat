@echo off
chcp 65001 >nul
echo ========================================
echo GitHub 上传前检查
echo ========================================
echo.

set ERROR_COUNT=0

echo [检查1] 检查.gitignore文件...
if exist ".gitignore" (
    echo ✓ .gitignore 存在
) else (
    echo ✗ .gitignore 不存在
    set /a ERROR_COUNT+=1
)
echo.

echo [检查2] 检查LICENSE文件...
if exist "LICENSE" (
    echo ✓ LICENSE 存在
) else (
    echo ✗ LICENSE 不存在
    set /a ERROR_COUNT+=1
)
echo.

echo [检查3] 检查README.md文件...
if exist "README.md" (
    echo ✓ README.md 存在
) else (
    echo ✗ README.md 不存在
    set /a ERROR_COUNT+=1
)
echo.

echo [检查4] 检查敏感文件是否被忽略...
findstr /C:".env" .gitignore >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ .env 已在 .gitignore 中
) else (
    echo ✗ .env 未在 .gitignore 中
    set /a ERROR_COUNT+=1
)

findstr /C:"*.db" .gitignore >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ *.db 已在 .gitignore 中
) else (
    echo ✗ *.db 未在 .gitignore 中
    set /a ERROR_COUNT+=1
)

findstr /C:"node_modules" .gitignore >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ node_modules 已在 .gitignore 中
) else (
    echo ✗ node_modules 未在 .gitignore 中
    set /a ERROR_COUNT+=1
)

findstr /C:"venv" .gitignore >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ venv 已在 .gitignore 中
) else (
    echo ✗ venv 未在 .gitignore 中
    set /a ERROR_COUNT+=1
)
echo.

echo [检查5] 检查敏感文件是否存在...
if exist "backend\.env" (
    echo ⚠ backend\.env 存在（确保已在.gitignore中）
) else (
    echo ✓ backend\.env 不存在
)

if exist "backend\instance\*.db" (
    echo ⚠ 数据库文件存在（确保已在.gitignore中）
) else (
    echo ✓ 数据库文件不存在或已忽略
)

if exist "backend\venv" (
    echo ⚠ backend\venv 存在（确保已在.gitignore中）
) else (
    echo ✓ backend\venv 不存在
)

if exist "frontend\node_modules" (
    echo ⚠ frontend\node_modules 存在（确保已在.gitignore中）
) else (
    echo ✓ frontend\node_modules 不存在
)
echo.

echo ========================================
if %ERROR_COUNT% equ 0 (
    echo ✓ 所有检查通过！可以安全上传到GitHub
    echo.
    echo 下一步：
    echo 1. 运行 github-init.bat 初始化Git仓库
    echo 2. 在GitHub上创建新仓库
    echo 3. 关联并推送代码
) else (
    echo ✗ 发现 %ERROR_COUNT% 个问题，请先修复
)
echo ========================================
echo.
pause
