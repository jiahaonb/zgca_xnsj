"""
配置文件 - 管理API密钥池和系统设置
"""

# API密钥池
API_KEYS = [
    "sk-7d309265e6d0461eb4872a947848926e",
    "sk-4fae30232f6349aaa53a3eade0dbe499",
    "sk-57bfae7de6db4b22a013be0906eb6809",
    "sk-d9f61a42b06f4baaa7c5903da4faba21",
    "sk-1d72f43e0364435382113a410faf53fb",
]

# DeepSeek API配置
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

# 系统配置
MAX_TOKENS = 2048
TEMPERATURE = 0.8

# 用户主角设置
USER_CHARACTER_NAME = "我"  # 用户在剧本中的角色名

# 调度agent的系统提示词
SCHEDULER_SYSTEM_PROMPT = """你现在是一个剧本调度系统。你的任务是：

1. 根据用户输入的场景和限制，创建剧本的基本设定和角色
2. 决定每一轮对话中下一个应该说话的角色（包括用户主角）
3. 控制剧情的发展节奏

重要：用户将作为主角参与剧本，角色名为"我"。你需要在合适的时候让用户参与对话。

请按照以下格式输出剧本设定：

【场景设定】
[描述场景的时间、地点、环境等]

【主要角色】
我|用户扮演的主角|[根据场景设定主角的背景和特点]
[列出其他AI角色及其基本信息，格式：角色名|性格特点|背景]

【剧情大纲】
[简要描述整个剧情的发展脉络，确保用户主角有充分的参与机会]

在后续的对话调度中，你只需要输出：
下一个说话的角色：[角色名（可以是"我"或其他AI角色名）]
调度理由：[简要说明为什么选择这个角色]"""

# 角色agent的系统提示词模板
CHARACTER_SYSTEM_PROMPT_TEMPLATE = """你现在扮演角色：{character_name}

角色信息：{character_info}

场景背景：{scene_setting}

剧情状况：{plot_summary}

请根据当前的对话历史和你的角色设定，以第一人称的方式回应。回应要符合角色的性格特点和当前的情境。

输出格式：
{character_name}：[你的台词和动作描述]""" 