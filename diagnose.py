#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZGCA多智能体剧本编辑系统 - 诊断工具
用于检查系统状态和排除故障
"""

import sys
import os
import json
import time
import requests
import subprocess
from pathlib import Path

def print_header(title):
    """打印标题"""
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")

def print_status(item, status, details=""):
    """打印状态信息"""
    status_icon = "✅" if status else "❌"
    print(f"{status_icon} {item}: {details}")

def check_python_environment():
    """检查Python环境"""
    print_header("Python环境检查")
    
    # 检查Python版本
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print_status("Python版本", True, f"Python {python_version}")
    
    # 检查依赖包
    required_packages = [
        "flask", "flask_cors", "openai", "requests", "numpy", "sounddevice"
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            print_status(f"依赖包 {package}", True, "已安装")
        except ImportError:
            print_status(f"依赖包 {package}", False, "未安装")
    
    return True

def check_config_file():
    """检查配置文件"""
    print_header("配置文件检查")
    
    config_path = Path("backg/config.py")
    if not config_path.exists():
        print_status("配置文件", False, "config.py不存在")
        return False
    
    try:
        sys.path.insert(0, str(config_path.parent))
        import config
        
        # 检查API密钥
        if hasattr(config, 'API_KEYS') and config.API_KEYS:
            print_status("API密钥配置", True, f"找到{len(config.API_KEYS)}个密钥")
            
            # 检查密钥格式
            for i, key in enumerate(config.API_KEYS):
                if key.startswith('sk-') and len(key) > 20:
                    print_status(f"API密钥 {i+1}", True, f"格式正确 (sk-...{key[-4:]})")
                else:
                    print_status(f"API密钥 {i+1}", False, "格式可能有问题")
        else:
            print_status("API密钥配置", False, "未找到API密钥")
        
        # 检查其他配置
        if hasattr(config, 'DEEPSEEK_BASE_URL'):
            print_status("DeepSeek API地址", True, config.DEEPSEEK_BASE_URL)
        
        return True
        
    except Exception as e:
        print_status("配置文件", False, f"加载失败: {str(e)}")
        return False

def check_port_availability():
    """检查端口可用性"""
    print_header("端口状态检查")
    
    ports = [8899, 8900]
    for port in ports:
        try:
            response = requests.get(f"http://localhost:{port}/api/status", timeout=5)
            if response.status_code == 200:
                print_status(f"端口 {port}", True, "服务正在运行")
            else:
                print_status(f"端口 {port}", False, f"状态码: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print_status(f"端口 {port}", False, "连接被拒绝")
        except requests.exceptions.Timeout:
            print_status(f"端口 {port}", False, "连接超时")
        except Exception as e:
            print_status(f"端口 {port}", False, f"错误: {str(e)}")

def check_backend_service():
    """检查后端服务"""
    print_header("后端服务检查")
    
    try:
        # 检查Python后端
        response = requests.get("http://localhost:8900/api/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_status("Python后端", True, "正在运行")
            print_status("脚本系统", data.get('script_system_available', False), 
                        "可用" if data.get('script_system_available') else "不可用")
        else:
            print_status("Python后端", False, f"状态码: {response.status_code}")
    except Exception as e:
        print_status("Python后端", False, f"错误: {str(e)}")
    
    try:
        # 检查Express代理
        response = requests.get("http://localhost:8899/api/status", timeout=10)
        if response.status_code == 200:
            print_status("Express代理", True, "正在运行")
        else:
            print_status("Express代理", False, f"状态码: {response.status_code}")
    except Exception as e:
        print_status("Express代理", False, f"错误: {str(e)}")

def check_system_processes():
    """检查系统进程"""
    print_header("系统进程检查")
    
    processes = ['python.exe', 'electron.exe', 'node.exe']
    for process in processes:
        try:
            result = subprocess.run(['tasklist', '/FI', f'IMAGENAME eq {process}'], 
                                  capture_output=True, text=True, shell=True)
            if process in result.stdout:
                lines = [line for line in result.stdout.split('\n') if process in line]
                print_status(f"{process}进程", True, f"发现{len(lines)}个进程")
            else:
                print_status(f"{process}进程", False, "未发现运行的进程")
        except Exception as e:
            print_status(f"{process}进程", False, f"检查失败: {str(e)}")

def test_api_connection():
    """测试API连接"""
    print_header("API连接测试")
    
    try:
        # 测试创建剧本API
        test_data = {
            "sceneDescription": "测试场景：两个朋友在咖啡厅聊天"
        }
        
        response = requests.post("http://localhost:8899/api/create-script", 
                               json=test_data, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print_status("API创建剧本", True, "测试成功")
                print_status("角色创建", True, f"创建了{data.get('data', {}).get('characters_count', 0)}个角色")
            else:
                print_status("API创建剧本", False, f"业务错误: {data.get('error', '未知错误')}")
        else:
            print_status("API创建剧本", False, f"HTTP错误: {response.status_code}")
    except Exception as e:
        print_status("API创建剧本", False, f"连接错误: {str(e)}")

def provide_solutions():
    """提供解决方案"""
    print_header("常见问题解决方案")
    
    solutions = [
        ("如果Python后端未响应", [
            "1. 检查API密钥是否正确",
            "2. 确认DeepSeek API服务可用",
            "3. 重启后端服务: cd backg && python electron_bridge.py"
        ]),
        ("如果端口被占用", [
            "1. 找到占用进程: netstat -ano | findstr :8899",
            "2. 终止进程: taskkill /F /PID <进程ID>",
            "3. 重新启动应用"
        ]),
        ("如果依赖包缺失", [
            "1. 安装Python依赖: pip install -r backg/requirement.txt",
            "2. 安装Node.js依赖: npm install",
            "3. 重新启动应用"
        ]),
        ("如果Electron界面无响应", [
            "1. 检查开发者工具中的错误信息",
            "2. 确认前后端连接正常",
            "3. 重启整个应用: start.bat"
        ])
    ]
    
    for problem, steps in solutions:
        print(f"\n🔧 {problem}:")
        for step in steps:
            print(f"   {step}")

def main():
    """主函数"""
    print("🎭 ZGCA多智能体剧本编辑系统 - 系统诊断工具")
    print("=" * 60)
    
    # 设置工作目录
    os.chdir(Path(__file__).parent)
    
    # 执行各项检查
    check_python_environment()
    check_config_file()
    check_port_availability()
    check_backend_service()
    check_system_processes()
    test_api_connection()
    provide_solutions()
    
    print_header("诊断完成")
    print("💡 如需更多帮助，请查看README.md或联系开发者")
    print("🔄 建议先尝试重启应用: start.bat")

if __name__ == "__main__":
    main() 