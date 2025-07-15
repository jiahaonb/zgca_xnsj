@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
echo ========================================
echo   ZGCA多智能体剧本编辑系统 调试启动器
echo ========================================
echo.

echo 🔍 运行系统诊断...
python diagnose.py
echo.

echo 🛠️ 正在清理可能的残留进程...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM electron.exe /T >nul 2>&1
taskkill /F /IM node.exe /T >nul 2>&1
echo 清理完成
echo.

echo 📦 检查Python环境...
python --version
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到Python环境，请安装Python 3.8+
    pause
    exit /b 1
)

echo 📦 检查Node.js环境...
node --version
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到Node.js环境，请安装Node.js
    pause
    exit /b 1
)

echo.
echo 🔧 安装Python依赖...
cd backg
pip install -r requirement.txt
if %errorlevel% neq 0 (
    echo ❌ 错误: Python依赖安装失败
    echo 尝试升级pip: python -m pip install --upgrade pip
    pause
    exit /b 1
)
cd ..

echo.
echo 🔧 安装Electron依赖...
npm install
if %errorlevel% neq 0 (
    echo ❌ 错误: Electron依赖安装失败
    echo 尝试清理npm缓存: npm cache clean --force
    pause
    exit /b 1
)

echo.
echo 🚀 启动应用程序...
echo 注意: 第一次启动可能需要较长时间
echo 如果界面无响应，请检查以下几点：
echo   1. API密钥是否正确配置
echo   2. 网络连接是否正常
echo   3. 是否有防火墙阻止连接
echo.

echo 🔄 3秒后开始启动...
timeout /t 3 /nobreak >nul

start /B npm start

echo.
echo 📱 应用程序已启动，请查看Electron窗口
echo 如果遇到问题，请：
echo   1. 检查控制台输出中的错误信息
echo   2. 按F12打开开发者工具查看错误
echo   3. 运行 python diagnose.py 进行诊断
echo.

echo 按任意键退出...
pause >nul 