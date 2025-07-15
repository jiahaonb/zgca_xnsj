 # ZGCA多智能体剧本编辑系统 - Electron前端

一个基于Electron的现代化前端界面，为ZGCA多智能体剧本编辑系统提供美观的用户界面。

## ✨ 特性

- 🎨 **现代化UI设计** - 使用毛玻璃效果和渐变背景
- 🔄 **实时对话** - 与AI角色进行实时互动
- 💫 **流畅动画** - 优雅的过渡效果和动画
- 📱 **响应式设计** - 适配不同屏幕尺寸
- 🌙 **深色主题** - 护眼的深色界面
- ⚡ **高性能** - 基于Electron的原生应用

## 🛠️ 技术栈

- **前端框架**: Electron
- **UI技术**: HTML5 + CSS3 + JavaScript ES6+
- **后端通信**: Python Flask API
- **样式特效**: CSS毛玻璃效果、渐变、动画
- **图标库**: Font Awesome

## 📋 系统要求

- Node.js 16.0+ 
- Python 3.8+
- Windows 10/11, macOS 10.14+, 或 Linux

## 🚀 快速开始

### 方法一：使用启动脚本（推荐）

1. **双击运行启动脚本**
   ```bash
   # Windows
   start.bat
   
   # macOS/Linux (待创建)
   ./start.sh
   ```

### 方法二：手动安装

1. **安装Python依赖**
   ```bash
   cd backg
   pip install -r requirement.txt
   cd ..
   ```

2. **安装Node.js依赖**
   ```bash
   npm install
   ```

3. **启动应用**
   ```bash
   npm start
   ```

## 📁 项目结构

```
zgca_xnsj/
├── main.js                 # Electron主进程
├── preload.js             # 预加载脚本
├── package.json           # 项目配置
├── start.bat             # Windows启动脚本
├── renderer/             # 渲染进程文件
│   ├── index.html        # 主界面HTML
│   ├── styles.css        # 样式文件
│   └── script.js         # 前端逻辑
├── assets/               # 资源文件
│   └── a.svg            # 背景图片
└── backg/               # Python后端
    ├── main.py          # 原始后端入口
    ├── electron_bridge.py # Electron桥梁API
    ├── script_system.py # 剧本系统
    ├── scheduler_agent.py # 调度智能体
    ├── character_agent.py # 角色智能体
    ├── api_pool.py      # API密钥池
    ├── config.py        # 配置文件
    └── requirement.txt  # Python依赖
```

## 🎮 使用说明

### 1. 创建剧本
- 在左侧控制面板的"场景描述"框中输入你想要的剧本场景
- 点击"创建剧本"按钮
- 系统将自动创建角色和设定

### 2. 开始对话
- 剧本创建成功后，对话控制按钮将被激活
- 可以选择自动对话或手动输入消息
- 支持跳过回合功能

### 3. 界面功能
- **系统状态**: 右上角显示连接状态
- **对话历史**: 右侧显示完整对话记录
- **导出功能**: 可以导出对话记录
- **全屏模式**: 支持对话区域全屏显示

### 4. 快捷键
- `Ctrl + Enter`: 在场景输入框中创建剧本
- `Enter`: 在消息输入框中发送消息
- `Ctrl + K`: 清空对话历史
- `Escape`: 关闭模态对话框

## 🔧 配置说明

### Python后端配置
编辑 `backg/config.py` 文件：
```python
# API密钥池
API_KEYS = [
    "your-api-key-1",
    "your-api-key-2",
    # 添加更多密钥
]

# 其他配置
MAX_TOKENS = 2048
TEMPERATURE = 0.8
```

### Electron配置
在 `package.json` 中可以修改：
- 应用名称和版本
- 构建配置
- 依赖版本

## 🐛 故障排除

### 常见问题

**Q: 应用启动失败**
A: 检查Node.js和Python环境是否正确安装

**Q: 后端连接失败**
A: 确保Python依赖已安装，特别是flask和flask-cors

**Q: API调用失败**
A: 检查config.py中的API密钥配置是否正确

**Q: 界面显示异常**
A: 尝试清除浏览器缓存或重启应用

### 调试模式
开发模式下启动：
```bash
npm run dev
```
这将打开开发者工具用于调试。

## 🔄 开发说明

### 前端开发
- 修改 `renderer/` 目录下的文件
- 使用现代JavaScript ES6+语法
- CSS使用Grid和Flexbox布局

### 后端开发
- Python后端位于 `backg/` 目录
- 使用Flask提供REST API
- 支持CORS跨域请求

### 构建发布
```bash
npm run build
```

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 🙏 致谢

- Electron团队提供的优秀框架
- Font Awesome提供的图标库
- 所有贡献者的努力

---

**享受您的AI剧本创作之旅！** 🎭✨