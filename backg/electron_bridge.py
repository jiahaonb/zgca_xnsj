"""
Electron Bridge - 连接Electron前端与Python后端的API桥梁
"""

import json
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from script_system import ScriptSystem
import threading
import time

# 配置日志 - 设置UTF-8编码
import sys
import os

# 设置控制台输出编码
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)

class ElectronBridge:
    def __init__(self, port=None):
        # 从环境变量读取端口，如果没有设置则使用默认端口8900
        if port is None:
            port = int(os.environ.get('FLASK_PORT', 8900))
        self.port = port
        self.app = Flask(__name__)
        CORS(self.app)  # 允许跨域请求
        
        # 初始化剧本系统
        try:
            self.script_system = ScriptSystem()
            logger.info("剧本系统初始化成功")
        except Exception as e:
            logger.error(f"剧本系统初始化失败: {e}")
            self.script_system = None
        
        self.setup_routes()
    
    def setup_routes(self):
        """设置API路由"""
        
        @self.app.route('/api/status', methods=['GET'])
        def get_status():
            """获取系统状态"""
            try:
                status = {
                    'success': True,
                    'status': 'running',
                    'port': self.port,
                    'script_system_available': self.script_system is not None,
                    'timestamp': time.time()
                }
                
                if self.script_system:
                    system_status = self.script_system.get_system_status()
                    status.update(system_status)
                
                return jsonify(status)
            except Exception as e:
                logger.error(f"获取状态失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/api/create-script', methods=['POST'])
        def create_script():
            """创建剧本"""
            try:
                data = request.get_json()
                scene_description = data.get('sceneDescription', '').strip()
                
                if not scene_description:
                    return jsonify({
                        'success': False,
                        'error': '场景描述不能为空'
                    }), 400
                
                if not self.script_system:
                    return jsonify({
                        'success': False,
                        'error': '剧本系统未初始化'
                    }), 500
                
                logger.info(f"创建剧本请求: {scene_description}")
                
                # 调用剧本系统创建剧本
                result = self.script_system.initialize_script(scene_description)
                
                if 'error' in result:
                    return jsonify({
                        'success': False,
                        'error': result['error']
                    }), 500
                
                # 获取角色信息
                characters_info = []
                if hasattr(self.script_system.scheduler, 'get_characters_info'):
                    characters_info = self.script_system.scheduler.get_characters_info()
                
                response_data = {
                    'success': True,
                    'message': '剧本创建成功',
                    'data': {
                        'scene': scene_description,
                        'characters': [char['name'] for char in characters_info],
                        'characters_detail': characters_info,
                        'characters_count': len(characters_info)
                    }
                }
                
                logger.info(f"剧本创建成功: {len(characters_info)} 个角色")
                return jsonify(response_data)
                
            except Exception as e:
                logger.error(f"创建剧本失败: {e}")
                return jsonify({
                    'success': False,
                    'error': f'创建剧本失败: {str(e)}'
                }), 500
        
        @self.app.route('/api/send-message', methods=['POST'])
        def send_message():
            """发送用户消息并获取AI回应"""
            try:
                data = request.get_json()
                message = data.get('message', '').strip()
                round_num = data.get('round', 1)
                
                if not message:
                    return jsonify({
                        'success': False,
                        'error': '消息内容不能为空'
                    }), 400
                
                if not self.script_system or not self.script_system.is_initialized:
                    return jsonify({
                        'success': False,
                        'error': '请先创建剧本设定'
                    }), 400
                
                logger.info(f"收到用户消息 (第{round_num}轮): {message}")
                
                # 添加用户消息到历史记录
                user_response = f"我：{message}"
                self.script_system.scheduler.add_to_history(user_response)
                
                # 决定下一个AI角色发言
                situation = f"用户刚刚说：{message}，这是第{round_num}轮对话"
                next_speaker = self.script_system.scheduler.decide_next_ai_speaker(situation)
                
                if not next_speaker:
                    return jsonify({
                        'success': False,
                        'error': '无法确定下一个发言角色'
                    }), 500
                
                # 获取AI角色回应
                character_agent = self.script_system.scheduler.get_character_agent(next_speaker)
                if not character_agent:
                    return jsonify({
                        'success': False,
                        'error': f'找不到角色 {next_speaker} 的智能体'
                    }), 500
                
                # 生成AI回应
                ai_response = character_agent.generate_response(situation)
                
                # 添加AI回应到历史记录
                self.script_system.scheduler.add_to_history(ai_response)
                
                response_data = {
                    'success': True,
                    'response': ai_response,
                    'speaker': next_speaker,
                    'round': round_num,
                    'situation': situation
                }
                
                logger.info(f"AI回应 ({next_speaker}): {ai_response[:100]}...")
                return jsonify(response_data)
                
            except Exception as e:
                logger.error(f"处理消息失败: {e}")
                return jsonify({
                    'success': False,
                    'error': f'处理消息失败: {str(e)}'
                }), 500
        
        @self.app.route('/api/start-conversation', methods=['POST'])
        def start_conversation():
            """开始自动对话"""
            try:
                data = request.get_json()
                rounds = data.get('rounds', 5)
                
                if not self.script_system or not self.script_system.is_initialized:
                    return jsonify({
                        'success': False,
                        'error': '请先创建剧本设定'
                    }), 400
                
                logger.info(f"开始自动对话: {rounds} 轮")
                
                # 在后台线程中执行对话
                def run_conversation():
                    try:
                        self.script_system.start_conversation(rounds)
                    except Exception as e:
                        logger.error(f"自动对话执行失败: {e}")
                
                conversation_thread = threading.Thread(target=run_conversation)
                conversation_thread.daemon = True
                conversation_thread.start()
                
                return jsonify({
                    'success': True,
                    'message': f'开始 {rounds} 轮自动对话',
                    'rounds': rounds
                })
                
            except Exception as e:
                logger.error(f"启动对话失败: {e}")
                return jsonify({
                    'success': False,
                    'error': f'启动对话失败: {str(e)}'
                }), 500
        
        @self.app.route('/api/clear-history', methods=['POST'])
        def clear_history():
            """清空对话历史"""
            try:
                if self.script_system:
                    self.script_system.clear_history()
                
                logger.info("对话历史已清空")
                return jsonify({
                    'success': True,
                    'message': '对话历史已清空'
                })
                
            except Exception as e:
                logger.error(f"清空历史失败: {e}")
                return jsonify({
                    'success': False,
                    'error': f'清空历史失败: {str(e)}'
                }), 500
        
        @self.app.route('/api/next-speaker', methods=['POST'])
        def get_next_speaker():
            """获取下一个说话的角色"""
            try:
                if not self.script_system or not self.script_system.is_initialized:
                    return jsonify({
                        'success': False,
                        'error': '请先创建剧本设定'
                    }), 400
                
                data = request.get_json()
                round_num = data.get('round', 1)
                situation = data.get('situation', f'这是第{round_num}轮对话')
                
                logger.info(f"获取下一个说话角色 (第{round_num}轮)")
                
                # 根据最后一个说话的人决定流程
                last_speaker = getattr(self.script_system, 'last_speaker', None)
                
                if last_speaker != "我":
                    # 上一个不是用户说话（或者是第一轮），应该询问用户
                    return jsonify({
                        'success': True,
                        'next_speaker': '我',
                        'speaker_type': 'user',
                        'action': 'ask_user',
                        'message': '现在轮到您说话了',
                        'round': round_num
                    })
                else:
                    # 用户刚说完，调度AI角色
                    next_speaker = self.script_system.scheduler.decide_next_ai_speaker(situation)
                    
                    if not next_speaker:
                        return jsonify({
                            'success': False,
                            'error': '无法确定下一个发言角色'
                        }), 500
                    
                    return jsonify({
                        'success': True,
                        'next_speaker': next_speaker,
                        'speaker_type': 'ai',
                        'action': 'ai_speak',
                        'message': f'下一个说话的是：{next_speaker}',
                        'round': round_num
                    })
                
            except Exception as e:
                logger.error(f"获取下一个说话角色失败: {e}")
                return jsonify({
                    'success': False,
                    'error': f'获取下一个说话角色失败: {str(e)}'
                }), 500
        
        @self.app.route('/api/user-speak', methods=['POST'])
        def user_speak():
            """用户说话"""
            try:
                if not self.script_system or not self.script_system.is_initialized:
                    return jsonify({
                        'success': False,
                        'error': '请先创建剧本设定'
                    }), 400
                
                data = request.get_json()
                message = data.get('message', '').strip()
                round_num = data.get('round', 1)
                action = data.get('action', 'speak')  # 'speak' 或 'skip'
                
                if action == 'skip':
                    # 用户选择跳过
                    logger.info(f"用户跳过发言 (第{round_num}轮)")
                    return jsonify({
                        'success': True,
                        'action': 'skip',
                        'message': '用户选择跳过',
                        'round': round_num
                    })
                
                if not message:
                    return jsonify({
                        'success': False,
                        'error': '消息内容不能为空'
                    }), 400
                
                logger.info(f"用户发言 (第{round_num}轮): {message}")
                
                # 添加用户消息到历史记录
                user_response = f"我：{message}"
                self.script_system.scheduler.add_to_history(user_response)
                self.script_system.last_speaker = "我"
                self.script_system.conversation_count += 1
                
                return jsonify({
                    'success': True,
                    'action': 'speak',
                    'message': message,
                    'formatted_message': user_response,
                    'round': round_num
                })
                
            except Exception as e:
                logger.error(f"用户发言失败: {e}")
                return jsonify({
                    'success': False,
                    'error': f'用户发言失败: {str(e)}'
                }), 500
        
        @self.app.route('/api/ai-speak', methods=['POST'])
        def ai_speak():
            """AI角色说话"""
            try:
                if not self.script_system or not self.script_system.is_initialized:
                    return jsonify({
                        'success': False,
                        'error': '请先创建剧本设定'
                    }), 400
                
                data = request.get_json()
                speaker = data.get('speaker', '').strip()
                round_num = data.get('round', 1)
                situation = data.get('situation', f'这是第{round_num}轮对话')
                
                if not speaker:
                    return jsonify({
                        'success': False,
                        'error': '说话角色不能为空'
                    }), 400
                
                logger.info(f"AI角色发言 (第{round_num}轮): {speaker}")
                
                # 获取AI角色智能体
                character_agent = self.script_system.scheduler.get_character_agent(speaker)
                if not character_agent:
                    return jsonify({
                        'success': False,
                        'error': f'找不到角色 {speaker} 的智能体'
                    }), 500
                
                # 生成AI回应
                ai_response = character_agent.generate_response(situation)
                
                # 添加AI回应到历史记录
                self.script_system.scheduler.add_to_history(ai_response)
                self.script_system.last_speaker = speaker
                self.script_system.conversation_count += 1
                
                return jsonify({
                    'success': True,
                    'speaker': speaker,
                    'message': ai_response,
                    'round': round_num
                })
                
            except Exception as e:
                logger.error(f"AI角色发言失败: {e}")
                return jsonify({
                    'success': False,
                    'error': f'AI角色发言失败: {str(e)}'
                }), 500
        
        @self.app.route('/api/get-history', methods=['GET'])
        def get_history():
            """获取对话历史"""
            try:
                if not self.script_system:
                    return jsonify({
                        'success': False,
                        'error': '剧本系统未初始化'
                    }), 500
                
                history = self.script_system.get_conversation_history()
                
                return jsonify({
                    'success': True,
                    'history': history,
                    'count': len(history)
                })
                
            except Exception as e:
                logger.error(f"获取历史失败: {e}")
                return jsonify({
                    'success': False,
                    'error': f'获取历史失败: {str(e)}'
                }), 500
        
        @self.app.route('/api/system-info', methods=['GET'])
        def get_system_info():
            """获取系统详细信息"""
            try:
                info = {
                    'success': True,
                    'bridge_status': 'running',
                    'port': self.port,
                    'script_system_available': self.script_system is not None
                }
                
                if self.script_system:
                    system_status = self.script_system.get_system_status()
                    info.update(system_status)
                    
                    # 获取角色信息
                    if hasattr(self.script_system.scheduler, 'get_characters_info'):
                        characters_info = self.script_system.scheduler.get_characters_info()
                        info['characters'] = characters_info
                
                return jsonify(info)
                
            except Exception as e:
                logger.error(f"获取系统信息失败: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e)
                }), 500
        
        @self.app.route('/', methods=['GET'])
        def root():
            """根路径 - 返回API信息"""
            return jsonify({
                'success': True,
                'service': 'ZGCA多智能体剧本编辑系统 - Electron Bridge',
                'version': '1.0.0',
                'status': 'running',
                'port': self.port,
                'endpoints': {
                    'status': '/api/status',
                    'system_info': '/api/system-info',
                    'create_script': '/api/create-script',
                    'send_message': '/api/send-message',
                    'start_conversation': '/api/start-conversation',
                    'clear_history': '/api/clear-history',
                    'get_history': '/api/get-history'
                }
            })
        
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({
                'success': False,
                'error': 'API endpoint not found',
                'message': '请使用正确的API端点，访问根路径 / 查看可用端点列表'
            }), 404
        
        @self.app.errorhandler(500)
        def internal_error(error):
            return jsonify({
                'success': False,
                'error': 'Internal server error'
            }), 500
    
    def run(self, debug=False):
        """启动Flask服务器"""
        try:
            logger.info(f"启动Electron Bridge服务器，端口: {self.port}")
            self.app.run(
                host='127.0.0.1',
                port=self.port,
                debug=debug,
                threaded=True,
                use_reloader=False  # 避免重复启动
            )
        except Exception as e:
            logger.error(f"启动服务器失败: {e}")
            raise

def main():
    """主函数"""
    bridge = ElectronBridge()  # 使用默认端口配置
    
    try:
        bridge.run(debug=False)
    except KeyboardInterrupt:
        logger.info("服务器已停止")
    except Exception as e:
        logger.error(f"服务器运行错误: {e}")

if __name__ == "__main__":
    main() 