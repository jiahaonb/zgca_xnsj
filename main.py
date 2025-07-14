import os
from typing import Dict, Any
from openai import OpenAI

class ScriptEditingSystem:
    def __init__(self, api_key: str = None):
        """
        初始化剧本编辑系统
        
        Args:
            api_key: DeepSeek API密钥，如果不提供则从环境变量读取
        """
        self.api_key = "sk-b5d99239cf204027ba552eee5c7573ba"
        
        # 初始化deepseek客户端
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")
        else:
            self.client = None
        
        # 系统提示词
        self.system_prompt = """你现在是一个剧本编辑系统。用户输入了场景及简单的限制之后，你可以根据输入创建一个简单的剧本，包括角色、剧情等。你担任调度员的角色，调度之后角色的反应。你的任务是基于用户的输入，构思一个剧本的开端，包括背景、角色和初始情境。在剧本进行中，你需要阅读完整的对话历史，然后决定下一个应该说话的角色是谁。你的输出必须清晰地指明下一个角色的名字。

        请按照以下格式输出剧本：

        【场景设定】
        [描述场景的时间、地点、环境等]

        【主要角色】
        [列出主要角色及其基本信息]

        【剧情大纲】
        [简要描述整个剧情的发展脉络]

        【详细剧本】
        [包含对话、动作、场景描述等的完整剧本内容]

        【角色反应调度】
        [作为调度员，分析各角色在关键情节点的心理状态和可能反应]

        请确保剧本内容丰富、角色性格鲜明、情节发展合理。"""

    def call_deepseek_api(self, user_input: str):
        """
        调用DeepSeek API
        
        Args:
            user_input: 用户输入的场景和限制
            
        Returns:
            API响应结果
        """
        if not self.client:
            return {"error": "请设置DeepSeek API密钥"}
            
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt
                    },
                    {
                        "role": "user", 
                        "content": user_input
                    }
                ],
                temperature=0.8,
                max_tokens=2048,
                stream=False
            )
            return response
            
        except Exception as e:
            return {"error": f"API调用失败: {str(e)}"}

    def generate_script(self, user_input: str) -> str:
        """
        生成剧本
        
        Args:
            user_input: 用户输入的场景和限制
            
        Returns:
            生成的剧本内容
        """
        result = self.call_deepseek_api(user_input)
        
        # 检查是否有错误
        if isinstance(result, dict) and "error" in result:
            return f"❌ {result['error']}"
        
        try:
            script_content = result.choices[0].message.content
            return script_content
        except (AttributeError, IndexError) as e:
            return f"❌ 解析API响应失败: {str(e)}"

    def run(self):
        """
        运行主程序
        """
        print("🎭 欢迎使用剧本编辑系统！")
        print("=" * 50)
        
        user_input = input("\n📝 请输入场景和限制: ").strip()
        if user_input.lower() in ['quit', 'exit', '退出', 'q']:
            print("👋 感谢使用剧本编辑系统，再见！")
            return
        
        print("\n🤖 正在生成剧本，请稍候...")
        print("-" * 50)

        script = self.generate_script(user_input)
        print(script)
        
def main():
    """
    主函数
    """
    
    system = ScriptEditingSystem()
    system.run()


if __name__ == "__main__":
    main()
