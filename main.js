const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const express = require('express');
const cors = require('cors');
const axios = require('axios');

class ElectronApp {
  constructor() {
    this.mainWindow = null;
    this.pythonProcess = null;
    this.expressApp = null;
    this.server = null;
    this.port = 8899;
    this.pythonPort = 8900;  // Python后端端口
    this.pythonBackendReady = false;
    this.readyCheckInterval = null;
  }

  createWindow() {
    // 创建浏览器窗口
    this.mainWindow = new BrowserWindow({
      width: 1200,
      height: 800,
      minWidth: 800,
      minHeight: 600,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        enableRemoteModule: false,
        preload: path.join(__dirname, 'preload.js')
      },
      frame: true,
      titleBarStyle: 'default',
      backgroundColor: '#1a1a1a',
      show: false,
      icon: path.join(__dirname, 'assets', 'icon.png')
    });

    // 加载前端页面
    const testPath = path.join(__dirname, 'renderer', 'index.html');
    console.log('Loading page from:', testPath);
    this.mainWindow.loadFile(testPath);

    // 当窗口准备好时显示
    this.mainWindow.once('ready-to-show', () => {
      console.log('Window is ready to show');
      this.mainWindow.show();
    });

    // 添加错误处理
    this.mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
      console.error('Failed to load page:', errorCode, errorDescription);
    });

    this.mainWindow.webContents.on('crashed', () => {
      console.error('Renderer process crashed');
    });

    // 当窗口被关闭时发出的事件
    this.mainWindow.on('closed', () => {
      this.mainWindow = null;
      this.cleanup();
    });

    // 开发模式下打开开发者工具
    if (process.argv.includes('--dev')) {
      this.mainWindow.webContents.openDevTools();
    }
  }

  async checkPythonBackendReady() {
    try {
      const response = await axios.get(`http://127.0.0.1:${this.pythonPort}/api/status`, {
        timeout: 5000
      });
      
      if (response.status === 200) {
        console.log('Python后端就绪检查成功');
        this.pythonBackendReady = true;
        
        // 清除定时检查
        if (this.readyCheckInterval) {
          clearInterval(this.readyCheckInterval);
          this.readyCheckInterval = null;
        }
        
        return true;
      }
    } catch (error) {
      console.log(`Python后端就绪检查失败: ${error.message}`);
      this.pythonBackendReady = false;
      return false;
    }
  }

  setupExpressServer() {
    // 创建Express服务器作为API代理
    this.expressApp = express();
    this.expressApp.use(cors());
    this.expressApp.use(express.json());

    // 通用代理函数
    const proxyToPython = async (req, res, apiPath) => {
      if (!this.pythonBackendReady) {
        console.log('Python后端未就绪，返回503错误');
        return res.status(503).json({
          success: false,
          error: 'Python后端未就绪，请稍后再试'
        });
      }

      try {
        const pythonUrl = `http://127.0.0.1:${this.pythonPort}${apiPath}`;
        console.log(`代理请求到Python后端: ${req.method} ${pythonUrl}`);
        
        const response = await axios({
          method: req.method,
          url: pythonUrl,
          data: req.body,
          headers: {
            'Content-Type': 'application/json'
          },
          timeout: 30000
        });

        res.json(response.data);
      } catch (error) {
        console.error(`代理请求失败: ${error.message}`);
        
        if (error.response) {
          // Python后端返回的错误
          res.status(error.response.status).json(error.response.data);
        } else if (error.code === 'ECONNREFUSED') {
          // 连接拒绝错误
          res.status(503).json({
            success: false,
            error: 'Python后端连接失败'
          });
        } else {
          // 其他错误
          res.status(500).json({
            success: false,
            error: `代理请求失败: ${error.message}`
          });
        }
      }
    };

    // API路由 - 代理到Python后端
    this.expressApp.post('/api/create-script', (req, res) => {
      proxyToPython(req, res, '/api/create-script');
    });

    this.expressApp.post('/api/send-message', (req, res) => {
      proxyToPython(req, res, '/api/send-message');
    });

    this.expressApp.post('/api/start-conversation', (req, res) => {
      proxyToPython(req, res, '/api/start-conversation');
    });

    this.expressApp.post('/api/clear-history', (req, res) => {
      proxyToPython(req, res, '/api/clear-history');
    });

    this.expressApp.get('/api/get-history', (req, res) => {
      proxyToPython(req, res, '/api/get-history');
    });

    this.expressApp.get('/api/system-info', (req, res) => {
      proxyToPython(req, res, '/api/system-info');
    });

    this.expressApp.get('/api/status', (req, res) => {
      proxyToPython(req, res, '/api/status');
    });

    // 添加根路径处理
    this.expressApp.get('/', (req, res) => {
      res.json({
        success: true,
        service: 'ZGCA Express代理服务器',
        version: '1.0.0',
        status: 'running',
        port: this.port,
        pythonBackendReady: this.pythonBackendReady,
        pythonPort: this.pythonPort,
        message: '这是Electron Express代理服务器'
      });
    });

    // 启动Express服务器
    this.server = this.expressApp.listen(this.port, () => {
      console.log(`Express代理服务器运行在端口 ${this.port}`);
    });

    // 添加错误处理
    this.server.on('error', (error) => {
      console.error(`Express服务器错误: ${error.message}`);
    });
  }

  async startPythonBackend() {
    // 首先检查Python后端是否已经在运行
    console.log('检查Python后端是否已在运行...');
    const alreadyRunning = await this.checkPythonBackendReady();
    
    if (alreadyRunning) {
      console.log('Python后端已在运行，无需重新启动');
      return;
    }

    // 启动Python后端
    try {
      const pythonScript = path.join(__dirname, 'backg', 'electron_bridge.py');
      console.log(`启动Python后端: ${pythonScript}`);
      
      this.pythonProcess = spawn('python', [pythonScript], {
        cwd: path.join(__dirname, 'backg'),
        stdio: 'pipe',
        env: {
          ...process.env,
          FLASK_PORT: this.pythonPort.toString()
        }
      });

      this.pythonProcess.stdout.on('data', (data) => {
        const output = data.toString();
        console.log(`Python后端输出: ${output}`);
        
        // 检测Python后端是否启动成功
        if (output.includes('启动Electron Bridge服务器') || 
            output.includes('Running on') ||
            output.includes('Press CTRL+C to quit')) {
          console.log('Python后端启动成功，开始就绪检查');
          // 延迟2秒后开始检查
          setTimeout(() => {
            this.checkPythonBackendReady();
          }, 2000);
        }
      });

      this.pythonProcess.stderr.on('data', (data) => {
        console.error(`Python后端错误: ${data}`);
      });

      this.pythonProcess.on('close', (code) => {
        console.log(`Python后端进程退出，代码: ${code}`);
        this.pythonProcess = null;
        this.pythonBackendReady = false;
      });

      this.pythonProcess.on('error', (error) => {
        console.error('Python后端启动失败:', error);
        this.pythonBackendReady = false;
      });

      console.log('Python后端启动中...');
      
      // 启动定时检查，每5秒检查一次Python后端是否就绪
      this.readyCheckInterval = setInterval(() => {
        if (!this.pythonBackendReady) {
          console.log('定时检查Python后端状态...');
          this.checkPythonBackendReady();
        }
      }, 5000);
      
    } catch (error) {
      console.error('启动Python后端失败:', error);
      this.pythonBackendReady = false;
    }
  }

  cleanup() {
    // 清理资源
    if (this.readyCheckInterval) {
      clearInterval(this.readyCheckInterval);
      this.readyCheckInterval = null;
    }
    
    if (this.pythonProcess) {
      console.log('终止Python后端进程');
      this.pythonProcess.kill();
      this.pythonProcess = null;
    }
    
    if (this.server) {
      console.log('关闭Express服务器');
      this.server.close();
      this.server = null;
    }
    
    this.pythonBackendReady = false;
  }

  init() {
    // 当Electron初始化完成并准备创建浏览器窗口时触发
    app.whenReady().then(async () => {
      console.log('Electron应用已就绪');
      
      this.setupExpressServer();
      await this.startPythonBackend();
      this.createWindow();
      
      // 在macOS上，当点击dock图标且没有其他窗口打开时，
      // 通常会重新创建窗口
      app.on('activate', () => {
        if (BrowserWindow.getAllWindows().length === 0) {
          this.createWindow();
        }
      });
    });

    // 当所有窗口关闭时退出
    app.on('window-all-closed', () => {
      if (process.platform !== 'darwin') {
        this.cleanup();
        app.quit();
      }
    });

    // 在应用即将退出时清理
    app.on('before-quit', () => {
      this.cleanup();
    });

    // IPC通信处理
    this.setupIPC();
  }

  setupIPC() {
    // 显示消息对话框
    ipcMain.handle('show-message-box', async (event, options) => {
      const result = await dialog.showMessageBox(this.mainWindow, options);
      return result;
    });

    // 获取应用信息
    ipcMain.handle('get-app-info', () => {
      return {
        version: app.getVersion(),
        name: app.getName()
      };
    });

    // 重启应用
    ipcMain.handle('restart-app', () => {
      app.relaunch();
      app.exit();
    });

    // 获取Python后端状态
    ipcMain.handle('get-python-backend-status', () => {
      return {
        ready: this.pythonBackendReady,
        port: this.pythonPort
      };
    });
  }
}

// 创建应用实例并初始化
const electronApp = new ElectronApp();
electronApp.init(); 