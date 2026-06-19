@echo off
chcp 65001 >nul
echo ========================================
echo GitHub 仓库初始化脚本
echo ========================================
echo.

REM 检查是否已经是git仓库
if exist ".git" (
    echo [提示] 已经是Git仓库
    echo.
) else (
    echo [1/5] 初始化Git仓库...
    git init
    echo.
)

echo [2/5] 添加所有文件...
git add .
echo.

echo [3/5] 创建初始提交...
git commit -m "Initial commit: 考公考研考编智能学习系统

- 完整的用户认证系统
- 智能练习功能
- 模拟考试系统
- 错题本管理
- 学习统计分析
- AI智能分析
- 考研院校查询
- 响应式UI设计
- 完整的API文档
- Docker支持"
echo.

echo [4/5] 设置默认分支为main...
git branch -M main
echo.

echo ========================================
echo 初始化完成！
echo ========================================
echo.
echo 下一步：
echo.
echo 1. 在GitHub上创建新仓库
echo    访问: https://github.com/new
echo.
echo 2. 仓库名称建议: exam-system
echo    描述: 考公考研考编智能学习系统
echo.
echo 3. 不要勾选 "Initialize with README"
echo.
echo 4. 创建后，运行以下命令关联远程仓库:
echo.
echo    git remote add origin https://github.com/YOUR_USERNAME/exam-system.git
echo    git push -u origin main
echo.
echo 或者使用GitHub Desktop更简单！
echo.
pause
