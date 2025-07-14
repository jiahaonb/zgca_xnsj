"""
剧本系统核心逻辑 - 整合调度agent和角色agents的交互流程
"""

from typing import Optional, Dict, Any
from scheduler_agent import SchedulerAgent
from api_pool import APIKeyPool
from config import API_KEYS


class ScriptSystem:
    def __init__(self):
        """
        初始化剧本系统
        """
        # 确保有可用的API密钥
        if not API_KEYS:
            raise ValueError("请在config.py中设置API_KEYS")
        
        # 使用第一个API密钥作为调度agent的密钥
        scheduler_api_key = API_KEYS[0]
        self.scheduler = SchedulerAgent(scheduler_api_key)
        
        self.is_initialized = False
        self.conversation_count = 0
        
    def initialize_script(self, user_input: str) -> Dict[str, Any]:
        """
        初始化剧本设定和角色
        
        Args:
            user_input: 用户输入的场景和限制
            
        Returns:
            初始化结果
        """
        print("🎭 正在创建剧本设定...")
        
        # 创建剧本设定
        script_setting = self.scheduler.create_script_setting(user_input)
        
        if "error" in script_setting:
            return script_setting
        
        print("📝 剧本设定创建完成！")
        print("-" * 50)
        print(script_setting["full_setting"])
        print("-" * 50)
        
        # 创建角色智能体
        characters_info = script_setting.get("characters", [])
        if not characters_info:
            return {"error": "未能从剧本设定中提取到角色信息"}
        
        print(f"🤖 正在创建 {len(characters_info)} 个角色智能体...")
        
        success = self.scheduler.create_characters(characters_info)
        if not success:
            return {"error": "角色智能体创建失败"}
        
        self.is_initialized = True
        
        print("✅ 角色智能体创建完成！")
        print("\n🎯 创建的角色：")
        for character_info in self.scheduler.get_characters_info():
            print(f"  - {character_info['name']}: {character_info['info']}")
        
        return {
            "success": True,
            "characters_count": len(characters_info),
            "characters": characters_info
        }
    
    def start_conversation(self, rounds: int = 10) -> None:
        """
        开始多轮对话
        
        Args:
            rounds: 对话轮数
        """
        if not self.is_initialized:
            print("❌ 请先初始化剧本设定")
            return
        
        print(f"\n🎬 开始 {rounds} 轮对话...")
        print("=" * 60)
        
        for round_num in range(1, rounds + 1):
            print(f"\n【第 {round_num} 轮对话】")
            print("-" * 30)
            
            # 调度agent决定下一个说话的角色
            current_situation = f"这是第{round_num}轮对话"
            next_speaker = self.scheduler.decide_next_speaker(current_situation)
            
            if not next_speaker:
                print("❌ 调度失败，无法确定下一个说话的角色")
                continue
            
            print(f"🎯 调度结果：{next_speaker} 说话")
            
            # 获取角色agent并生成回应
            character_agent = self.scheduler.get_character_agent(next_speaker)
            if not character_agent:
                print(f"❌ 未找到角色 {next_speaker} 的智能体")
                continue
            
            # 生成角色回应
            character_response = character_agent.generate_response(current_situation)
            
            # 输出回应
            print(f"💬 {character_response}")
            
            # 添加到历史记录
            self.scheduler.add_to_history(character_response)
            
            self.conversation_count += 1
            
            # 在每轮之间添加分隔
            if round_num < rounds:
                print()
    
    def interactive_conversation(self) -> None:
        """
        交互式对话模式
        """
        if not self.is_initialized:
            print("❌ 请先初始化剧本设定")
            return
        
        print("\n🎬 进入交互式对话模式")
        print("输入 'quit' 或 'exit' 退出，输入 'auto [数字]' 进行自动对话")
        print("=" * 60)
        
        while True:
            try:
                user_input = input("\n🎮 请输入指令或情境描述: ").strip()
                
                if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                    print("👋 退出交互式对话模式")
                    break
                
                if user_input.lower().startswith('auto'):
                    # 自动对话模式
                    parts = user_input.split()
                    rounds = 5  # 默认5轮
                    if len(parts) > 1 and parts[1].isdigit():
                        rounds = int(parts[1])
                    self.start_conversation(rounds)
                    continue
                
                # 手动指定情境
                current_situation = user_input if user_input else "继续对话"
                
                # 调度决定下一个说话的角色
                next_speaker = self.scheduler.decide_next_speaker(current_situation)
                
                if not next_speaker:
                    print("❌ 调度失败，无法确定下一个说话的角色")
                    continue
                
                print(f"🎯 调度结果：{next_speaker} 说话")
                
                # 获取角色agent并生成回应
                character_agent = self.scheduler.get_character_agent(next_speaker)
                if not character_agent:
                    print(f"❌ 未找到角色 {next_speaker} 的智能体")
                    continue
                
                # 生成角色回应
                character_response = character_agent.generate_response(current_situation)
                
                # 输出回应
                print(f"💬 {character_response}")
                
                # 添加到历史记录
                self.scheduler.add_to_history(character_response)
                
                self.conversation_count += 1
                
            except KeyboardInterrupt:
                print("\n👋 退出交互式对话模式")
                break
            except Exception as e:
                print(f"❌ 发生错误: {str(e)}")
    
    def get_conversation_history(self) -> list:
        """
        获取对话历史
        
        Returns:
            对话历史列表
        """
        return self.scheduler.conversation_history.copy()
    
    def clear_history(self) -> None:
        """
        清空对话历史
        """
        self.scheduler.clear_all_history()
        self.conversation_count = 0
        print("✅ 对话历史已清空")
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        获取系统状态
        
        Returns:
            系统状态信息
        """
        status = {
            "initialized": self.is_initialized,
            "conversation_count": self.conversation_count,
            "characters_count": len(self.scheduler.characters),
            "api_pool_available": self.scheduler.api_pool.get_available_count(),
            "api_pool_total": self.scheduler.api_pool.get_total_count()
        }
        
        if self.is_initialized:
            status["characters"] = self.scheduler.get_characters_info()
        
        return status
    
    def print_system_status(self) -> None:
        """
        打印系统状态
        """
        status = self.get_system_status()
        
        print("\n📊 系统状态")
        print("-" * 30)
        print(f"初始化状态: {'✅ 已初始化' if status['initialized'] else '❌ 未初始化'}")
        print(f"对话轮数: {status['conversation_count']}")
        print(f"角色数量: {status['characters_count']}")
        print(f"API池状态: {status['api_pool_available']}/{status['api_pool_total']} 可用")
        
        if status['initialized'] and status['characters_count'] > 0:
            print("\n🎭 角色列表:")
            for character in status['characters']:
                print(f"  - {character['name']}") 