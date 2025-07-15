@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
echo ========================================
echo   ZGCA剧本系统 - 快速修复工具
echo ========================================
echo.

echo 🔧 步骤1: 清理所有相关进程...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM electron.exe /T >nul 2>&1
taskkill /F /IM node.exe /T >nul 2>&1
echo ✅ 进程清理完成

echo.
echo 🔧 步骤2: 检查并释放端口...
netstat -ano | findstr :8899 >nul
if %errorlevel% equ 0 (
    echo ⚠️ 端口8899仍被占用，尝试强制释放...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8899') do (
        taskkill /F /PID %%a >nul 2>&1
    )
)

netstat -ano | findstr :8900 >nul
if %errorlevel% equ 0 (
    echo ⚠️ 端口8900仍被占用，尝试强制释放...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8900') do (
        taskkill /F /PID %%a >nul 2>&1
    )
)
echo ✅ 端口检查完成

echo.
echo 🔧 步骤3: 清理临时文件...
if exist "backg\__pycache__" (
    rmdir /s /q "backg\__pycache__"
    echo ✅ 已清理Python缓存
)

if exist "node_modules\.cache" (
    rmdir /s /q "node_modules\.cache"
    echo ✅ 已清理Node.js缓存
)

echo.
echo 🔧 步骤4: 重新安装依赖...
echo 正在安装Python依赖...
cd backg
pip install -r requirement.txt --upgrade --force-reinstall
if %errorlevel% neq 0 (
    echo ❌ Python依赖安装失败，尝试使用镜像源...
    pip install -r requirement.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
)
cd ..

echo.
echo 正在安装Node.js依赖...
npm install --force
if %errorlevel% neq 0 (
    echo ❌ Node.js依赖安装失败，尝试清理缓存...
    npm cache clean --force
    npm install
)

echo.
echo 🔧 步骤5: 检查配置文件...
if exist "backg\config.py" (
    echo ✅ 配置文件存在
) else (
    echo ❌ 配置文件不存在，请检查config.py
)

echo.
echo 🔧 步骤6: 测试连接...
echo 等待5秒后开始测试...
timeout /t 5 /nobreak >nul

echo 启动测试服务器...
start /B cmd /c "cd backg && python electron_bridge.py"
timeout /t 10 /nobreak >nul

echo 测试API连接...
python -c "import requests; print('API测试:', requests.get('http://localhost:8900/api/status', timeout=5).json())" 2>nul
if %errorlevel% equ 0 (
    echo ✅ API连接测试成功
) else (
    echo ❌ API连接测试失败
)

echo.
echo 🔧 修复完成！
echo 现在可以尝试运行以下命令启动应用：
echo   1. start.bat          (正常启动)
echo   2. start_debug.bat    (调试启动)
echo   3. npm start          (直接启动)
echo.
echo 如果问题仍然存在，请：
echo   1. 检查API密钥配置
echo   2. 确认网络连接正常
echo   3. 运行 python diagnose.py 进行详细诊断
echo.

pause 