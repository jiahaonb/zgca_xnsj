@echo off
chcp 65001 >nul
echo ========================================
echo   ZGCA 系统诊断工具
echo ========================================
echo.

echo 检查Node.js环境...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Node.js环境，请安装Node.js
    pause
    exit /b 1
)

echo Node.js 版本:
node --version

echo.
echo 检查Electron依赖...
if not exist "node_modules" (
    echo 正在安装依赖...
    npm install
    if %errorlevel% neq 0 (
        echo 错误: 依赖安装失败
        pause
        exit /b 1
    )
)

echo.
echo 启动测试模式 (仅前端，不启动Python后端)...
echo 如果出现黑屏，请查看控制台错误信息
echo.

npm start

echo.
echo 测试结束
pause 