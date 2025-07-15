// 应用状态管理
class AppState {
    constructor() {
        this.isScriptCreated = false;
        this.isConversationActive = false;
        this.currentRound = 0;
        this.messageCount = 0;
        this.characters = [];
        this.conversationHistory = [];
        this.systemStatus = 'disconnected';
    }

    updateStatus(status) {
        this.systemStatus = status;
        this.updateStatusDisplay();
    }

    updateStatusDisplay() {
        const statusDot = document.getElementById('statusDot');
        const statusText = document.getElementById('statusText');
        const connectionStatus = document.getElementById('connectionStatus');

        if (this.systemStatus === 'connected') {
            statusDot.classList.add('online');
            statusText.textContent = '系统就绪';
            connectionStatus.classList.add('connected');
            connectionStatus.innerHTML = '<i class="fas fa-circle"></i> 已连接';
        } else {
            statusDot.classList.remove('online');
            statusText.textContent = '等待连接';
            connectionStatus.classList.remove('connected');
            connectionStatus.innerHTML = '<i class="fas fa-circle"></i> 未连接';
        }
    }

    enableConversationControls() {
        const startBtn = document.getElementById('startConversationBtn');
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        const skipBtn = document.getElementById('skipBtn');

        startBtn.disabled = false;
        messageInput.disabled = false;
        sendBtn.disabled = false;
        skipBtn.disabled = false;
    }

    disableConversationControls() {
        const startBtn = document.getElementById('startConversationBtn');
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        const skipBtn = document.getElementById('skipBtn');

        startBtn.disabled = true;
        messageInput.disabled = true;
        sendBtn.disabled = true;
        skipBtn.disabled = true;
    }
}

// 全局应用状态
const appState = new AppState();

// 应用主类
class ScriptEditorApp {
    constructor() {
        this.initializeApp();
        this.bindEvents();
        this.updateTimeDisplay();
        this.checkSystemStatus();
    }

    async initializeApp() {
        console.log('初始化ZGCA剧本编辑系统...');
        
        // 检查ElectronAPI是否可用
        if (typeof window.electronAPI !== 'undefined') {
            console.log('ElectronAPI已加载');
            await this.testConnection();
        } else {
            console.warn('ElectronAPI未找到，可能在浏览器环境中运行');
        }

        // 显示欢迎动画
        this.showWelcomeAnimation();
    }

    showWelcomeAnimation() {
        const welcomeContent = document.querySelector('.welcome-content');
        if (welcomeContent) {
            welcomeContent.style.animation = 'slideIn 0.6s ease-out';
        }
    }

    async testConnection() {
        try {
            if (window.electronAPI && window.electronAPI.request) {
                const response = await window.electronAPI.request.getStatus();
                if (response.success) {
                    appState.updateStatus('connected');
                    this.showNotification('系统连接成功', 'success');
                } else {
                    throw new Error('连接测试失败');
                }
            }
        } catch (error) {
            console.error('连接测试失败:', error);
            this.showNotification('系统连接失败，请检查配置', 'error');
        }
    }

    bindEvents() {
        // 创建剧本按钮
        document.getElementById('createScriptBtn').addEventListener('click', () => {
            this.createScript();
        });

        // 开始对话按钮
        document.getElementById('startConversationBtn').addEventListener('click', () => {
            this.startConversation();
        });

        // 清空历史按钮
        document.getElementById('clearHistoryBtn').addEventListener('click', () => {
            this.clearHistory();
        });

        // 发送消息按钮
        document.getElementById('sendBtn').addEventListener('click', () => {
            this.sendMessage();
        });

        // 跳过按钮
        document.getElementById('skipBtn').addEventListener('click', () => {
            this.skipRound();
        });

        // 输入框回车发送
        document.getElementById('messageInput').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // 场景输入框回车创建
        document.getElementById('sceneInput').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && e.ctrlKey) {
                e.preventDefault();
                this.createScript();
            }
        });

        // 模态框关闭
        document.getElementById('modalCloseBtn').addEventListener('click', () => {
            this.hideModal();
        });

        // 点击overlay关闭模态框
        document.getElementById('modalOverlay').addEventListener('click', (e) => {
            if (e.target === e.currentTarget) {
                this.hideModal();
            }
        });

        // 系统状态按钮
        document.getElementById('statusBtn').addEventListener('click', () => {
            this.showSystemInfo();
        });

        // 设置按钮
        document.getElementById('settingsBtn').addEventListener('click', () => {
            this.showSettings();
        });

        // 导出对话按钮
        document.getElementById('exportBtn').addEventListener('click', () => {
            this.exportConversation();
        });

        // 全屏按钮
        document.getElementById('fullscreenBtn').addEventListener('click', () => {
            this.toggleFullscreen();
        });

        // 键盘快捷键
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardShortcuts(e);
        });
    }

    async createScript() {
        const sceneInput = document.getElementById('sceneInput');
        const sceneDescription = sceneInput.value.trim();

        if (!sceneDescription) {
            this.showNotification('请输入场景描述', 'warning');
            sceneInput.focus();
            return;
        }

        this.showLoading('正在创建剧本设定...');

        try {
            if (window.electronAPI && window.electronAPI.request) {
                const response = await window.electronAPI.request.createScript(sceneDescription);
                
                if (response.success) {
                    appState.isScriptCreated = true;
                    appState.characters = response.data.characters || [];
                    
                    this.showNotification('剧本创建成功！', 'success');
                    this.displayScriptInfo(response.data);
                    appState.enableConversationControls();
                    
                    // 清空输入框
                    sceneInput.value = '';
                } else {
                    throw new Error(response.error || '创建剧本失败');
                }
            } else {
                // 模拟响应（开发测试用）
                await this.simulateScriptCreation(sceneDescription);
            }
        } catch (error) {
            console.error('创建剧本失败:', error);
            this.showNotification(`创建剧本失败: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }

    async simulateScriptCreation(sceneDescription) {
        // 模拟网络延迟
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        appState.isScriptCreated = true;
        appState.characters = ['我', 'AI角色1', 'AI角色2'];
        
        this.showNotification('剧本创建成功！（模拟模式）', 'success');
        this.displayScriptInfo({
            scene: sceneDescription,
            characters: appState.characters
        });
        appState.enableConversationControls();
    }

    displayScriptInfo(data) {
        // 移除欢迎消息
        const welcomeMessage = document.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }

        // 添加剧本信息消息
        const chatMessages = document.getElementById('chatMessages');
        const scriptInfoHtml = `
            <div class="message system">
                <div class="message-header">
                    <span class="message-author">系统</span>
                    <span class="message-time">${this.getCurrentTime()}</span>
                </div>
                <div class="message-content">
                    <h4>🎭 剧本创建成功！</h4>
                    <p><strong>场景：</strong>${data.scene}</p>
                    <p><strong>角色：</strong>${data.characters.join(', ')}</p>
                    <p>现在可以开始对话了！</p>
                </div>
            </div>
        `;
        
        chatMessages.innerHTML = scriptInfoHtml;
        this.scrollToBottom();
    }

    async startConversation() {
        if (!appState.isScriptCreated) {
            this.showNotification('请先创建剧本设定', 'warning');
            return;
        }

        const roundsInput = document.getElementById('roundsInput');
        const rounds = parseInt(roundsInput.value) || 5;

        appState.isConversationActive = true;
        appState.currentRound = 0;

        this.addSystemMessage(`开始 ${rounds} 轮对话...`);
        this.addSystemMessage('💡 系统会询问您是否需要说话，您可以输入台词或选择跳过');

        try {
            // 真正的对话流程
            for (let i = 1; i <= rounds; i++) {
                if (!appState.isConversationActive) break;

                appState.currentRound = i;
                this.addSystemMessage(`第 ${i} 轮对话`);
                
                await this.executeConversationRound(i);
                
                // 每轮之间的延迟
                if (i < rounds) {
                    await this.delay(1000);
                }
            }

            appState.isConversationActive = false;
            this.addSystemMessage('对话结束');
            
        } catch (error) {
            console.error('对话过程中发生错误:', error);
            this.showNotification(`对话错误: ${error.message}`, 'error');
            appState.isConversationActive = false;
        }
    }

    async executeConversationRound(round) {
        if (!window.electronAPI || !window.electronAPI.request) {
            this.addSystemMessage('❌ API不可用，使用模拟模式');
            await this.simulateConversationRound(round);
            return;
        }

        try {
            // 获取下一个说话的角色
            const nextSpeakerResponse = await window.electronAPI.request.getNextSpeaker(round);
            
            if (!nextSpeakerResponse.success) {
                throw new Error(nextSpeakerResponse.error);
            }

            const { next_speaker, speaker_type, action } = nextSpeakerResponse;

            if (speaker_type === 'user') {
                // 轮到用户说话
                this.addSystemMessage(`🎭 现在轮到您说话了 (第${round}轮)`);
                
                // 启用用户输入
                this.enableUserInput(round);
                
                // 等待用户输入
                const userResponse = await this.waitForUserInput(round);
                
                if (userResponse.action === 'speak') {
                    // 用户说话
                    this.addUserMessage(userResponse.message);
                    
                    // 调用用户说话API
                    const userSpeakResponse = await window.electronAPI.request.userSpeak(
                        userResponse.message, round, 'speak'
                    );
                    
                    if (!userSpeakResponse.success) {
                        throw new Error(userSpeakResponse.error);
                    }
                } else {
                    // 用户跳过
                    this.addSystemMessage('您选择跳过本轮发言');
                    
                    // 调用用户跳过API
                    await window.electronAPI.request.userSpeak('', round, 'skip');
                }
                
                // 用户说话或跳过后，继续获取AI角色
                await this.delay(500);
                const aiSpeakerResponse = await window.electronAPI.request.getNextSpeaker(round);
                
                if (aiSpeakerResponse.success && aiSpeakerResponse.speaker_type === 'ai') {
                    await this.executeAISpeech(aiSpeakerResponse.next_speaker, round);
                }
                
            } else if (speaker_type === 'ai') {
                // 轮到AI说话
                await this.executeAISpeech(next_speaker, round);
            }
            
        } catch (error) {
            console.error(`第${round}轮对话失败:`, error);
            this.addSystemMessage(`❌ 第${round}轮对话失败: ${error.message}`);
        }
    }

    async executeAISpeech(speaker, round) {
        this.addSystemMessage(`🎯 ${speaker} 正在思考...`);
        this.showLoading(`${speaker} 正在生成回应...`);
        
        try {
            const aiSpeakResponse = await window.electronAPI.request.aiSpeak(
                speaker, round, `这是第${round}轮对话`
            );
            
            if (!aiSpeakResponse.success) {
                throw new Error(aiSpeakResponse.error);
            }
            
            // 显示AI回应
            this.addAIMessage(speaker, aiSpeakResponse.message);
            
        } catch (error) {
            console.error(`AI角色${speaker}发言失败:`, error);
            this.addSystemMessage(`❌ ${speaker}发言失败: ${error.message}`);
        } finally {
            this.hideLoading();
        }
    }

    enableUserInput(round) {
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        const skipBtn = document.getElementById('skipBtn');
        
        messageInput.disabled = false;
        sendBtn.disabled = false;
        skipBtn.disabled = false;
        
        // 设置占位符
        messageInput.placeholder = `请输入您的台词 (第${round}轮)...`;
        messageInput.focus();
        
        // 滚动到输入区域
        messageInput.scrollIntoView({ behavior: 'smooth' });
    }

    disableUserInput() {
        const messageInput = document.getElementById('messageInput');
        const sendBtn = document.getElementById('sendBtn');
        const skipBtn = document.getElementById('skipBtn');
        
        messageInput.disabled = true;
        sendBtn.disabled = true;
        skipBtn.disabled = true;
        messageInput.placeholder = '输入您的台词...';
    }

    waitForUserInput(round) {
        return new Promise((resolve) => {
            // 存储当前的resolve函数
            this.currentUserInputResolve = resolve;
            this.currentRound = round;
            
            // 设置超时（可选）
            setTimeout(() => {
                if (this.currentUserInputResolve) {
                    this.currentUserInputResolve({ action: 'skip', message: '' });
                    this.currentUserInputResolve = null;
                }
            }, 60000); // 60秒超时
        });
    }

    async simulateConversationRound(round) {
        this.addSystemMessage(`第 ${round} 轮对话 (模拟模式)`);
        
        // 模拟AI角色发言
        await this.delay(1500);
        this.addAIMessage(`AI角色${round}`, `这是第${round}轮对话的AI回应。`);
        
        return new Promise(resolve => {
            setTimeout(resolve, 500);
        });
    }

    async sendMessage() {
        const messageInput = document.getElementById('messageInput');
        const message = messageInput.value.trim();

        if (!appState.isScriptCreated) {
            this.showNotification('请先创建剧本设定', 'warning');
            return;
        }

        // 检查是否在对话轮次中
        if (appState.isConversationActive && this.currentUserInputResolve) {
            // 在对话轮次中，处理用户输入
            if (!message) {
                this.showNotification('请输入消息内容', 'warning');
                messageInput.focus();
                return;
            }
            
            // 清空输入框
            messageInput.value = '';
            
            // 禁用输入
            this.disableUserInput();
            
            // 解析用户输入
            this.currentUserInputResolve({ action: 'speak', message: message });
            this.currentUserInputResolve = null;
            
            return;
        }

        // 不在对话轮次中，直接发送消息
        if (!message) {
            this.showNotification('请输入消息内容', 'warning');
            messageInput.focus();
            return;
        }

        // 添加用户消息
        this.addUserMessage(message);
        messageInput.value = '';

        // 发送到后端处理
        try {
            if (window.electronAPI && window.electronAPI.request) {
                const response = await window.electronAPI.request.sendMessage(message, appState.currentRound + 1);
                
                if (response.success) {
                    this.addAIMessage(response.speaker || 'AI助手', response.response);
                } else {
                    throw new Error(response.error || '发送消息失败');
                }
            } else {
                // 模拟AI回应
                await this.delay(1000);
                this.addAIMessage('AI助手', `收到您的消息："${message}"，这是模拟回应。`);
            }
        } catch (error) {
            console.error('发送消息失败:', error);
            this.showNotification(`发送失败: ${error.message}`, 'error');
        }
    }

    skipRound() {
        // 检查是否在对话轮次中
        if (appState.isConversationActive && this.currentUserInputResolve) {
            // 在对话轮次中，处理用户跳过
            const messageInput = document.getElementById('messageInput');
            messageInput.value = '';
            
            // 禁用输入
            this.disableUserInput();
            
            // 解析用户跳过
            this.currentUserInputResolve({ action: 'skip', message: '' });
            this.currentUserInputResolve = null;
        } else {
            this.showNotification('当前不在对话轮次中', 'warning');
        }
    }

    async clearHistory() {
        if (appState.conversationHistory.length === 0) {
            this.showNotification('没有对话历史可清空', 'info');
            return;
        }

        try {
            // 调用后端API清空历史
            if (window.electronAPI && window.electronAPI.request) {
                const response = await window.electronAPI.request.clearHistory();
                
                if (!response.success) {
                    throw new Error(response.error || '清空历史失败');
                }
            }
            
            // 清空前端界面
            const chatMessages = document.getElementById('chatMessages');
            chatMessages.innerHTML = `
                <div class="welcome-message">
                    <div class="welcome-content">
                        <i class="fas fa-theater-masks"></i>
                        <h3>对话历史已清空</h3>
                        <p>可以开始新的对话了！</p>
                    </div>
                </div>
            `;

            // 重置状态
            appState.conversationHistory = [];
            appState.messageCount = 0;
            appState.currentRound = 0;
            appState.isConversationActive = false;
            
            this.updateMessageCount();
            this.showNotification('对话历史已清空', 'success');
            
        } catch (error) {
            console.error('清空历史失败:', error);
            this.showNotification(`清空历史失败: ${error.message}`, 'error');
        }
    }



    addUserMessage(content) {
        this.addMessage('我', content, 'user');
    }

    addAIMessage(character, content) {
        this.addMessage(character, content, 'ai');
    }

    addSystemMessage(content) {
        this.addMessage('系统', content, 'system');
    }

    addMessage(author, content, type) {
        const chatMessages = document.getElementById('chatMessages');
        const messageId = window.electronAPI ? window.electronAPI.utils.generateId() : Math.random().toString(36).substr(2, 9);
        
        // 移除欢迎消息（如果存在）
        const welcomeMessage = chatMessages.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }

        const messageHtml = `
            <div class="message ${type}" data-message-id="${messageId}">
                <div class="message-header">
                    <span class="message-author">${author}</span>
                    <span class="message-time">${this.getCurrentTime()}</span>
                </div>
                <div class="message-content">${this.formatMessageContent(content)}</div>
            </div>
        `;

        chatMessages.insertAdjacentHTML('beforeend', messageHtml);
        
        // 保存到历史记录
        appState.conversationHistory.push({
            id: messageId,
            author,
            content,
            type,
            timestamp: Date.now()
        });

        appState.messageCount++;
        this.updateMessageCount();
        this.scrollToBottom();
    }

    formatMessageContent(content) {
        // 简单的文本格式化
        return content
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>');
    }

    updateMessageCount() {
        const messageCountElement = document.getElementById('messageCount');
        if (messageCountElement) {
            messageCountElement.textContent = `消息: ${appState.messageCount}`;
        }
    }

    scrollToBottom() {
        const chatMessages = document.getElementById('chatMessages');
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    getCurrentTime() {
        if (window.electronAPI && window.electronAPI.utils) {
            return window.electronAPI.utils.formatTime(Date.now());
        }
        return new Date().toLocaleTimeString('zh-CN', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    }

    updateTimeDisplay() {
        const currentTimeElement = document.getElementById('currentTime');
        if (currentTimeElement) {
            currentTimeElement.textContent = this.getCurrentTime();
        }
        
        // 每秒更新时间
        setTimeout(() => this.updateTimeDisplay(), 1000);
    }

    async checkSystemStatus() {
        // 定期检查系统状态
        setInterval(async () => {
            try {
                if (window.electronAPI && window.electronAPI.request) {
                    const response = await window.electronAPI.request.getStatus();
                    if (response.success && appState.systemStatus !== 'connected') {
                        appState.updateStatus('connected');
                    }
                }
            } catch (error) {
                if (appState.systemStatus !== 'disconnected') {
                    appState.updateStatus('disconnected');
                }
            }
        }, 10000); // 每10秒检查一次
    }

    showLoading(message = '正在处理...') {
        const loadingOverlay = document.getElementById('loadingOverlay');
        const loadingText = loadingOverlay.querySelector('p');
        if (loadingText) {
            loadingText.textContent = message;
        }
        loadingOverlay.style.display = 'flex';
    }

    hideLoading() {
        const loadingOverlay = document.getElementById('loadingOverlay');
        loadingOverlay.style.display = 'none';
    }

    showModal(title, content) {
        const modal = document.getElementById('modal');
        const modalTitle = document.getElementById('modalTitle');
        const modalContent = document.getElementById('modalContent');
        const modalOverlay = document.getElementById('modalOverlay');

        modalTitle.textContent = title;
        modalContent.innerHTML = content;
        modalOverlay.style.display = 'flex';

        // 添加打开动画
        modal.style.animation = 'slideIn 0.3s ease-out';
    }

    hideModal() {
        const modalOverlay = document.getElementById('modalOverlay');
        modalOverlay.style.display = 'none';
    }

    showNotification(message, type = 'info') {
        const notification = document.getElementById('notification');
        const notificationMessage = notification.querySelector('.notification-message');
        const notificationIcon = notification.querySelector('.notification-icon');

        // 设置图标
        const icons = {
            success: 'fas fa-check',
            error: 'fas fa-exclamation-triangle',
            warning: 'fas fa-exclamation-circle',
            info: 'fas fa-info-circle'
        };

        notificationIcon.className = `notification-icon ${icons[type] || icons.info}`;
        notificationMessage.textContent = message;
        
        // 设置样式类
        notification.className = `notification ${type}`;
        
        // 显示通知
        notification.classList.add('show');

        // 3秒后自动隐藏
        setTimeout(() => {
            notification.classList.remove('show');
        }, 3000);
    }

    showSystemInfo() {
        const systemInfo = `
            <div class="system-info">
                <h4>系统信息</h4>
                <p><strong>状态：</strong>${appState.systemStatus === 'connected' ? '已连接' : '未连接'}</p>
                <p><strong>剧本状态：</strong>${appState.isScriptCreated ? '已创建' : '未创建'}</p>
                <p><strong>对话状态：</strong>${appState.isConversationActive ? '进行中' : '未开始'}</p>
                <p><strong>当前轮数：</strong>${appState.currentRound}</p>
                <p><strong>消息数量：</strong>${appState.messageCount}</p>
                <p><strong>角色数量：</strong>${appState.characters.length}</p>
            </div>
        `;
        this.showModal('系统状态', systemInfo);
    }

    showSettings() {
        const settingsContent = `
            <div class="settings">
                <h4>应用设置</h4>
                <p>设置功能正在开发中...</p>
                <div class="setting-item">
                    <label>主题模式：</label>
                    <select disabled>
                        <option>深色模式</option>
                        <option>浅色模式</option>
                    </select>
                </div>
                <div class="setting-item">
                    <label>自动保存：</label>
                    <input type="checkbox" checked disabled>
                </div>
            </div>
        `;
        this.showModal('设置', settingsContent);
    }

    exportConversation() {
        if (appState.conversationHistory.length === 0) {
            this.showNotification('没有对话可导出', 'warning');
            return;
        }

        const conversations = appState.conversationHistory
            .map(msg => `[${new Date(msg.timestamp).toLocaleString()}] ${msg.author}: ${msg.content}`)
            .join('\n');

        if (window.electronAPI && window.electronAPI.utils) {
            window.electronAPI.utils.copyToClipboard(conversations)
                .then(success => {
                    if (success) {
                        this.showNotification('对话已复制到剪贴板', 'success');
                    } else {
                        this.showNotification('复制失败', 'error');
                    }
                });
        } else {
            // 浏览器环境下的处理
            navigator.clipboard.writeText(conversations)
                .then(() => this.showNotification('对话已复制到剪贴板', 'success'))
                .catch(() => this.showNotification('复制失败', 'error'));
        }
    }

    toggleFullscreen() {
        const chatContainer = document.querySelector('.chat-container');
        chatContainer.classList.toggle('fullscreen');
        
        const icon = document.querySelector('#fullscreenBtn i');
        if (chatContainer.classList.contains('fullscreen')) {
            icon.className = 'fas fa-compress';
        } else {
            icon.className = 'fas fa-expand';
        }
    }

    handleKeyboardShortcuts(e) {
        // Ctrl/Cmd + Enter: 创建剧本
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            if (document.activeElement === document.getElementById('sceneInput')) {
                this.createScript();
            }
        }

        // Escape: 关闭模态框
        if (e.key === 'Escape') {
            this.hideModal();
        }

        // Ctrl/Cmd + K: 清空历史
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            this.clearHistory();
        }
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// 当DOM加载完成后初始化应用
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing app...');
    new ScriptEditorApp();
});

// 全局错误处理
window.addEventListener('error', (e) => {
    console.error('全局错误:', e.error);
});

window.addEventListener('unhandledrejection', (e) => {
    console.error('未处理的Promise拒绝:', e.reason);
}); 