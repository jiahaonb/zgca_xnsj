#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API测试脚本 - 测试所有可用的API端点
"""

import requests
import json
import time

def test_api_endpoint(method, url, data=None, description=""):
    """测试API端点"""
    try:
        if method.upper() == 'GET':
            response = requests.get(url, timeout=10)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, timeout=10)
        
        print(f"{'='*60}")
        print(f"🔍 {description}")
        print(f"   方法: {method.upper()}")
        print(f"   URL: {url}")
        if data:
            print(f"   数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        print(f"   状态码: {response.status_code}")
        
        try:
            result = response.json()
            print(f"   响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
        except:
            print(f"   响应: {response.text}")
        
        return response.status_code == 200
        
    except requests.exceptions.ConnectionError:
        print(f"❌ 连接错误: 无法连接到 {url}")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ 超时错误: {url}")
        return False
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return False

def main():
    """主函数"""
    print("🎭 ZGCA多智能体剧本编辑系统 - API测试")
    print("=" * 60)
    
    # 测试8900端口（Python后端）
    print("\n📡 测试Python后端API (端口8900)")
    
    # 1. 测试状态API
    test_api_endpoint('GET', 'http://localhost:8900/api/status', 
                     description="获取系统状态")
    
    # 2. 测试系统信息API
    test_api_endpoint('GET', 'http://localhost:8900/api/system-info', 
                     description="获取系统详细信息")
    
    # 3. 测试获取历史API
    test_api_endpoint('GET', 'http://localhost:8900/api/get-history', 
                     description="获取对话历史")
    
    # 4. 测试创建剧本API
    test_data = {
        "sceneDescription": "现代都市背景，两个朋友在咖啡厅讨论创业计划"
    }
    test_api_endpoint('POST', 'http://localhost:8900/api/create-script', 
                     data=test_data, description="创建剧本")
    
    # 5. 测试发送消息API
    test_data = {
        "message": "大家好，我是新来的！",
        "round": 1
    }
    test_api_endpoint('POST', 'http://localhost:8900/api/send-message', 
                     data=test_data, description="发送消息")
    
    # 6. 测试清空历史API
    test_api_endpoint('POST', 'http://localhost:8900/api/clear-history', 
                     description="清空对话历史")
    
    # 7. 测试不存在的端点
    test_api_endpoint('GET', 'http://localhost:8900/', 
                     description="测试根路径（应该返回404）")
    
    test_api_endpoint('GET', 'http://localhost:8900/api/nonexistent', 
                     description="测试不存在的端点（应该返回404）")
    
    print("\n" + "="*60)
    print("📡 测试Express代理API (端口8899)")
    
    # 测试Express代理的相同端点
    test_api_endpoint('GET', 'http://localhost:8899/api/status', 
                     description="Express代理 - 获取系统状态")
    
    test_api_endpoint('POST', 'http://localhost:8899/api/create-script', 
                     data={"sceneDescription": "测试场景"}, 
                     description="Express代理 - 创建剧本")
    
    print("\n" + "="*60)
    print("📋 可用的API端点列表:")
    print("   GET  /api/status           - 获取系统状态")
    print("   GET  /api/system-info      - 获取系统详细信息")
    print("   GET  /api/get-history      - 获取对话历史")
    print("   POST /api/create-script    - 创建剧本")
    print("   POST /api/send-message     - 发送消息")
    print("   POST /api/start-conversation - 开始自动对话")
    print("   POST /api/clear-history    - 清空对话历史")
    print("\n💡 注意：访问根路径(/)或其他不存在的端点会返回404错误")

if __name__ == "__main__":
    main() 