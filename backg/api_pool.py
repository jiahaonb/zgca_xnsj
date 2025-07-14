"""
API密钥池管理 - 负责分配和管理API密钥
"""

import random
from typing import List, Optional
from config import API_KEYS


class APIKeyPool:
    def __init__(self):
        """
        初始化API密钥池
        """
        self.available_keys = API_KEYS.copy()
        self.used_keys = []
        
    def get_keys(self, count: int) -> List[str]:
        """
        获取指定数量的API密钥
        
        Args:
            count: 需要的密钥数量
            
        Returns:
            API密钥列表
        """
        if count > len(self.available_keys):
            # 如果需要的数量超过可用密钥数，重复使用密钥
            keys = []
            for i in range(count):
                key_index = i % len(API_KEYS)
                keys.append(API_KEYS[key_index])
            return keys
        
        # 随机选择密钥
        selected_keys = random.sample(self.available_keys, count)
        
        # 将选中的密钥移到已使用列表
        for key in selected_keys:
            self.available_keys.remove(key)
            self.used_keys.append(key)
            
        return selected_keys
    
    def release_key(self, api_key: str) -> None:
        """
        释放API密钥，使其重新可用
        
        Args:
            api_key: 要释放的API密钥
        """
        if api_key in self.used_keys:
            self.used_keys.remove(api_key)
            self.available_keys.append(api_key)
    
    def release_all_keys(self) -> None:
        """
        释放所有已使用的API密钥
        """
        self.available_keys.extend(self.used_keys)
        self.used_keys.clear()
    
    def get_available_count(self) -> int:
        """
        获取可用密钥数量
        
        Returns:
            可用密钥数量
        """
        return len(self.available_keys)
    
    def get_total_count(self) -> int:
        """
        获取总密钥数量
        
        Returns:
            总密钥数量
        """
        return len(API_KEYS) 