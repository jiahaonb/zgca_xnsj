#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速API测试脚本
"""

import requests
import json

def test_endpoint(url, description):
    """测试单个API端点"""
    print(f"\n🔍 {description}")
    print(f"   URL: {url}")
    try:
        response = requests.get(url, timeout=5)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
            return True
        else:
            print(f"   错误响应: {response.text}")
            return False
    except Exception as e:
        print(f"   错误: {e}")
        return False

def main():
    print("🎭 ZGCA系统 - 快速API测试")
    print("=" * 50)
    
    # 测试关键端点
    results = []
    
    # 1. 测试根路径（之前返回404错误）
    results.append(test_endpoint('http://localhost:8900/', '根路径测试'))
    
    # 2. 测试状态API
    results.append(test_endpoint('http://localhost:8900/api/status', '状态API测试'))
    
    # 3. 测试Express代理
    results.append(test_endpoint('http://localhost:8899/api/status', 'Express代理测试'))
    
    print("\n" + "=" * 50)
    print("📊 测试结果:")
    passed = sum(results)
    total = len(results)
    print(f"   通过: {passed}/{total}")
    
    if passed == total:
        print("✅ 所有测试通过！API端点正常工作")
    else:
        print("❌ 部分测试失败，请检查服务器状态")

if __name__ == "__main__":
    main() 