const { contextBridge, ipcRenderer } = require('electron');

// 暴露受保护的方法给渲染器进程
contextBridge.exposeInMainWorld('electronAPI', {
  // IPC通信方法
  showMessageBox: (options) => ipcRenderer.invoke('show-message-box', options),
  getAppInfo: () => ipcRenderer.invoke('get-app-info'),
  restartApp: () => ipcRenderer.invoke('restart-app'),

  // HTTP请求封装
  request: {
    // 创建剧本
    createScript: async (sceneDescription) => {
      try {
        const response = await fetch('http://localhost:8899/api/create-script', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ sceneDescription })
        });
        return await response.json();
      } catch (error) {
        console.error('创建剧本请求失败:', error);
        return { success: false, error: error.message };
      }
    },

    // 发送消息
    sendMessage: async (message, round = 1) => {
      try {
        const response = await fetch('http://localhost:8899/api/send-message', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ message, round })
        });
        return await response.json();
      } catch (error) {
        console.error('发送消息请求失败:', error);
        return { success: false, error: error.message };
      }
    },

    // 获取状态
    getStatus: async () => {
      try {
        const response = await fetch('http://localhost:8899/api/status');
        return await response.json();
      } catch (error) {
        console.error('获取状态请求失败:', error);
        return { success: false, error: error.message };
      }
    },

    // 获取下一个说话的角色
    getNextSpeaker: async (round = 1, situation = '') => {
      try {
        const response = await fetch('http://localhost:8899/api/next-speaker', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ round, situation })
        });
        return await response.json();
      } catch (error) {
        console.error('获取下一个说话角色请求失败:', error);
        return { success: false, error: error.message };
      }
    },

    // 用户说话
    userSpeak: async (message, round = 1, action = 'speak') => {
      try {
        const response = await fetch('http://localhost:8899/api/user-speak', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ message, round, action })
        });
        return await response.json();
      } catch (error) {
        console.error('用户说话请求失败:', error);
        return { success: false, error: error.message };
      }
    },

    // AI角色说话
    aiSpeak: async (speaker, round = 1, situation = '') => {
      try {
        const response = await fetch('http://localhost:8899/api/ai-speak', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ speaker, round, situation })
        });
        return await response.json();
      } catch (error) {
        console.error('AI角色说话请求失败:', error);
        return { success: false, error: error.message };
      }
    },

    // 获取对话历史
    getHistory: async () => {
      try {
        const response = await fetch('http://localhost:8899/api/get-history');
        return await response.json();
      } catch (error) {
        console.error('获取对话历史请求失败:', error);
        return { success: false, error: error.message };
      }
    },

    // 清空对话历史
    clearHistory: async () => {
      try {
        const response = await fetch('http://localhost:8899/api/clear-history', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          }
        });
        return await response.json();
      } catch (error) {
        console.error('清空对话历史请求失败:', error);
        return { success: false, error: error.message };
      }
    }
  },

  // 工具方法
  utils: {
    // 生成唯一ID
    generateId: () => {
      return Math.random().toString(36).substr(2, 9);
    },

    // 格式化时间
    formatTime: (timestamp) => {
      const date = new Date(timestamp);
      return date.toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
    },

    // 延迟函数
    delay: (ms) => {
      return new Promise(resolve => setTimeout(resolve, ms));
    },

    // 复制到剪贴板
    copyToClipboard: async (text) => {
      try {
        await navigator.clipboard.writeText(text);
        return true;
      } catch (error) {
        console.error('复制失败:', error);
        return false;
      }
    }
  },

  // 事件监听
  events: {
    // 监听窗口事件
    onWindowEvent: (event, callback) => {
      window.addEventListener(event, callback);
      return () => window.removeEventListener(event, callback);
    },

    // 监听键盘事件
    onKeydown: (callback) => {
      const handler = (event) => callback(event);
      window.addEventListener('keydown', handler);
      return () => window.removeEventListener('keydown', handler);
    },

    // 监听窗口大小变化
    onResize: (callback) => {
      const handler = () => callback({
        width: window.innerWidth,
        height: window.innerHeight
      });
      window.addEventListener('resize', handler);
      return () => window.removeEventListener('resize', handler);
    }
  }
});

// 调试信息
console.log('Preload script loaded successfully');
console.log('ElectronAPI exposed to renderer process'); 