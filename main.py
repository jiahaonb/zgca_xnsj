"""
多智能体剧本编辑系统主程序
基于调度agent和多个角色agents的架构
"""

from script_system import ScriptSystem


def print_welcome():
    """
    打印欢迎信息
    """
    print("🎭" + "=" * 58 + "🎭")
    print("    欢迎使用多智能体剧本编辑系统！")
    print("=" * 60)
    print("✨ 系统特点：")
    print("  - 👤 用户主角：您将作为主角参与剧本对话")
    print("  - 🤖 调度Agent：智能创建剧本设定和角色调度")
    print("  - 🎭 AI角色：其他角色使用独立的AI智能体")
    print("  - 🎬 实时对话：支持用户参与的对话模式")
    print("  - 📊 状态管理：实时监控系统和API使用状况")
    print("=" * 60)


def print_menu():
    """
    打印主菜单
    """
    print("\n📋 主菜单")
    print("-" * 30)
    print("1. 🎭 创建新剧本")
    print("2. 🎬 开始剧本对话")
    print("3. 🎮 交互式对话")
    print("4. 📊 查看系统状态")
    print("5. 🗑️  清空对话历史")
    print("6. 🚪 退出系统")
    print("-" * 30)


def create_new_script(script_system: ScriptSystem):
    """
    创建新剧本
    
    Args:
        script_system: 剧本系统实例
    """
    print("\n🎭 创建新剧本")
    print("=" * 50)
    print("请描述您想要的剧本场景和限制条件")
    print("💡 您将作为主角参与剧本，系统会自动创建其他AI角色")
    print("\n📝 场景描述示例：")
    print("  - 现代都市背景，朋友们在咖啡厅讨论创业计划")
    print("  - 古代武侠世界，我在客栈遇到了神秘的江湖人士")
    print("  - 科幻未来，我作为宇宙飞船的船员面临危机")
    print("  - 校园青春，我和同学在图书馆准备重要考试")
    print("-" * 50)
    
    user_input = input("📝 请输入场景描述: ").strip()
    
    if not user_input:
        print("❌ 场景描述不能为空")
        return
    
    if user_input.lower() in ['quit', 'exit', '退出', 'q']:
        return
    
    # 初始化剧本
    result = script_system.initialize_script(user_input)
    
    if "error" in result:
        print(f"❌ {result['error']}")
    else:
        ai_count = result['characters_count'] - 1  # 减去用户主角
        print(f"\n✅ 剧本创建成功！")
        print(f"👤 您是主角，另外创建了 {ai_count} 个AI角色")


def start_auto_conversation(script_system: ScriptSystem):
    """
    开始剧本对话
    
    Args:
        script_system: 剧本系统实例
    """
    if not script_system.is_initialized:
        print("❌ 请先创建剧本设定")
        return
    
    print("\n🎬 剧本对话模式")
    print("-" * 40)
    print("💡 优化的交互体验：")
    print("  - 当需要您说话时，直接输入台词，按回车跳过")
    print("  - 您说话后会直接调度AI角色，AI说话后才会再次询问您")
    print("🤖 流畅的对话节奏，减少不必要的重复询问")
    print("-" * 40)
    
    try:
        rounds_input = input("请输入对话轮数 (默认5轮): ").strip()
        if rounds_input and rounds_input.isdigit():
            rounds = int(rounds_input)
        else:
            rounds = 5
        
        if rounds > 50:
            print("⚠️ 对话轮数过多，已限制为50轮")
            rounds = 50
        
        script_system.start_conversation(rounds)
        
    except ValueError:
        print("❌ 请输入有效的数字")
    except KeyboardInterrupt:
        print("\n⏹️ 对话已中断")


def start_interactive_conversation(script_system: ScriptSystem):
    """
    开始交互式对话
    
    Args:
        script_system: 剧本系统实例
    """
    if not script_system.is_initialized:
        print("❌ 请先创建剧本设定")
        return
    
    script_system.interactive_conversation()


def main():
    """
    主函数
    """
    print_welcome()
    
    # 初始化剧本系统
    try:
        script_system = ScriptSystem()
    except ValueError as e:
        print(f"❌ 系统初始化失败: {str(e)}")
        print("请检查config.py中的API_KEYS配置")
        return
    except Exception as e:
        print(f"❌ 系统初始化失败: {str(e)}")
        return
    
    # 主循环
    while True:
        try:
            print_menu()
            choice = input("\n🎯 请选择操作 (1-6): ").strip()
            
            if choice == '1':
                create_new_script(script_system)
            
            elif choice == '2':
                start_auto_conversation(script_system)
            
            elif choice == '3':
                start_interactive_conversation(script_system)
            
            elif choice == '4':
                script_system.print_system_status()
            
            elif choice == '5':
                script_system.clear_history()
            
            elif choice == '6':
                print("👋 感谢使用多智能体剧本编辑系统，再见！")
                break
            
            else:
                print("❌ 无效选择，请输入1-6之间的数字")
        
        except KeyboardInterrupt:
            print("\n👋 感谢使用多智能体剧本编辑系统，再见！")
            break
        except Exception as e:
            print(f"❌ 发生未知错误: {str(e)}")
            print("系统将继续运行...")


if __name__ == "__main__":
    main()
