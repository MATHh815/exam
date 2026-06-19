@echo off
chcp 65001 >nul
echo ============================================================
echo 安装 UI 美化依赖
echo ============================================================
echo.

echo [1/3] 安装图表库 (ECharts)...
call npm install echarts vue-echarts

echo.
echo [2/3] 安装动画库 (GSAP)...
call npm install gsap

echo.
echo [3/3] 安装工具库...
call npm install @vueuse/core dayjs

echo.
echo ============================================================
echo ✅ 依赖安装完成！
echo ============================================================
echo.
pause
