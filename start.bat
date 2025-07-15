@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
echo ========================================
echo   ZGCA多智能体剧本编辑系统 启动器
echo ========================================
echo.

echo 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python环境，请安装Python 3.8+
    pause
    exit /b 1
)

echo 检查Node.js环境...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Node.js环境，请安装Node.js
    pause
    exit /b 1
)

echo.
echo 安装Python依赖...
cd backg
pip install -r requirement.txt
if %errorlevel% neq 0 (
    echo 错误: Python依赖安装失败
    pause
    exit /b 1
)
cd ..

echo.
echo 安装Electron依赖...
npm install
if %errorlevel% neq 0 (
    echo 错误: Electron依赖安装失败
    pause
    exit /b 1
)

echo.
echo 启动应用程序...
echo 注意: 第一次启动可能需要较长时间
echo.

npm start

echo.
echo 应用程序已退出
pause 