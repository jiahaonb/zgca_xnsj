"""
调度智能体 - 负责剧本创建、角色管理和对话调度
"""

import re
from typing import List, Dict, Any, Optional
from openai import OpenAI
from character_agent import CharacterAgent
from api_pool import APIKeyPool
from config import (
    DEEPSEEK_BASE_URL, 
    DEEPSEEK_MODEL, 
    MAX_TOKENS, 
    TEMPERATURE,
    SCHEDULER_SYSTEM_PROMPT
)


class SchedulerAgent:
    def __init__(self, api_key: str):
        """
        初始化调度智能体
        
        Args:
            api_key: 调度agent的API密钥
        """
        self.api_key = api_key
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=DEEPSEEK_BASE_URL
        )
        
        self.api_pool = APIKeyPool()
        self.characters: Dict[str, CharacterAgent] = {}
        self.scene_setting = ""
        self.plot_summary = ""
        self.conversation_history = []
        
    def create_script_setting(self, user_input: str) -> Dict[str, Any]:
        """
        根据用户输入创建剧本设定
        
        Args:
            user_input: 用户输入的场景和限制
            
        Returns:
            剧本设定信息
        """
        try:
            response = self.client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=[
                    {"role": "system", "content": SCHEDULER_SYSTEM_PROMPT},
                    {"role": "user", "content": user_input}
                ],
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
                stream=False
            )
            
            script_setting = response.choices[0].message.content.strip()
            
            # 解析剧本设定
            parsed_setting = self._parse_script_setting(script_setting)
            
            # 保存场景和剧情信息
            self.scene_setting = parsed_setting.get("scene_setting", "")
            self.plot_summary = parsed_setting.get("plot_summary", "")
            
            return parsed_setting
            
        except Exception as e:
            return {"error": f"剧本设定创建失败: {str(e)}"}
    
    def _parse_script_setting(self, script_setting: str) -> Dict[str, Any]:
        """
        解析剧本设定文本
        
        Args:
            script_setting: 剧本设定文本
            
        Returns:
            解析后的设定信息
        """
        result = {
            "full_setting": script_setting,
            "scene_setting": "",
            "characters": [],
            "plot_summary": ""
        }
        
        # 提取场景设定
        scene_match = re.search(r'【场景设定】\s*\n(.*?)(?=【|$)', script_setting, re.DOTALL)
        if scene_match:
            result["scene_setting"] = scene_match.group(1).strip()
        
        # 提取主要角色
        characters_match = re.search(r'【主要角色】\s*\n(.*?)(?=【|$)', script_setting, re.DOTALL)
        if characters_match:
            characters_text = characters_match.group(1).strip()
            # 解析角色信息（格式：角色名|性格特点|背景）
            character_lines = [line.strip() for line in characters_text.split('\n') if line.strip()]
            for line in character_lines:
                if '|' in line:
                    parts = line.split('|')
                    if len(parts) >= 2:
                        character_name = parts[0].strip()
                        character_info = '|'.join(parts[1:]).strip()
                        result["characters"].append({
                            "name": character_name,
                            "info": character_info
                        })
        
        # 提取剧情大纲
        plot_match = re.search(r'【剧情大纲】\s*\n(.*?)(?=【|$)', script_setting, re.DOTALL)
        if plot_match:
            result["plot_summary"] = plot_match.group(1).strip()
        
        return result
    
    def create_characters(self, characters_info: List[Dict[str, str]]) -> bool:
        """
        创建角色智能体
        
        Args:
            characters_info: 角色信息列表
            
        Returns:
            是否创建成功
        """
        try:
            character_count = len(characters_info)
            if character_count == 0:
                return False
            
            # 从API池获取密钥
            api_keys = self.api_pool.get_keys(character_count)
            
            # 创建角色智能体
            for i, character_info in enumerate(characters_info):
                character_name = character_info["name"]
                character_detail = character_info["info"]
                api_key = api_keys[i]
                
                character_agent = CharacterAgent(character_name, character_detail, api_key)
                character_agent.set_scene_info(self.scene_setting, self.plot_summary)
                
                self.characters[character_name] = character_agent
            
            return True
            
        except Exception as e:
            print(f"❌ 角色创建失败: {str(e)}")
            return False
    
    def decide_next_speaker(self, current_situation: str = "") -> Optional[str]:
        """
        决定下一个说话的角色
        
        Args:
            current_situation: 当前情况描述
            
        Returns:
            下一个说话的角色名字
        """
        try:
            # 构建对话历史
            conversation_context = "\n".join(self.conversation_history[-10:])  # 最近10条对话
            
            # 构建可选角色列表
            character_list = ", ".join(self.characters.keys())
            
            user_input = f"""
当前场景：{self.scene_setting}

可选角色：{character_list}

最近对话历史：
{conversation_context}

当前情况：{current_situation}

请决定下一个应该说话的角色。
"""
            
            response = self.client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=[
                    {"role": "system", "content": SCHEDULER_SYSTEM_PROMPT},
                    {"role": "user", "content": user_input}
                ],
                temperature=TEMPERATURE,
                max_tokens=512,
                stream=False
            )
            
            decision_text = response.choices[0].message.content.strip()
            
            # 从回应中提取角色名
            next_speaker = self._extract_character_name(decision_text)
            
            return next_speaker
            
        except Exception as e:
            print(f"❌ 角色调度失败: {str(e)}")
            return None
    
    def _extract_character_name(self, decision_text: str) -> Optional[str]:
        """
        从调度决定中提取角色名
        
        Args:
            decision_text: 调度决定文本
            
        Returns:
            角色名字
        """
        # 尝试匹配 "下一个说话的角色：角色名" 格式
        match = re.search(r'下一个说话的角色：(.+)', decision_text)
        if match:
            character_name = match.group(1).strip()
            # 检查是否是有效的角色名
            for name in self.characters.keys():
                if name in character_name:
                    return name
        
        # 如果没有匹配到格式，尝试直接在文本中查找角色名
        for character_name in self.characters.keys():
            if character_name in decision_text:
                return character_name
        
        # 如果都没找到，返回第一个角色
        if self.characters:
            return list(self.characters.keys())[0]
        
        return None
    
    def add_to_history(self, message: str):
        """
        添加到对话历史
        
        Args:
            message: 对话内容
        """
        self.conversation_history.append(message)
        
        # 同时添加到所有角色的历史记录
        for character in self.characters.values():
            character.add_to_history(message)
    
    def get_character_agent(self, character_name: str) -> Optional[CharacterAgent]:
        """
        获取指定角色的智能体
        
        Args:
            character_name: 角色名字
            
        Returns:
            角色智能体
        """
        return self.characters.get(character_name)
    
    def get_characters_info(self) -> List[Dict[str, str]]:
        """
        获取所有角色信息
        
        Returns:
            角色信息列表
        """
        return [character.get_character_info() for character in self.characters.values()]
    
    def clear_all_history(self):
        """
        清空所有历史记录
        """
        self.conversation_history.clear()
        for character in self.characters.values():
            character.clear_history() 