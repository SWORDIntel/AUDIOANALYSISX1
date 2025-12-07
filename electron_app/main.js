/**
 * FVOAS Electron Main Process
 * ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 * Electron wrapper for FVOAS web interface
 * 
 * Classification: SECRET
 * Device: 9 (Audio) | Layer: 3 | Clearance: 0x03030303
 */

const { app, BrowserWindow, Menu, ipcMain, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs');

let mainWindow = null;
let backendProcess = null;
let backendPort = null;

// Find free port
function findFreePort(startPort = 8000, endPort = 9000) {
  return new Promise((resolve) => {
    const net = require('net');
    const port = Math.floor(Math.random() * (endPort - startPort + 1)) + startPort;
    const server = net.createServer();
    
    server.listen(port, () => {
      server.once('close', () => resolve(port));
      server.close();
    });
    
    server.on('error', () => {
      // Port in use, try next
      findFreePort(startPort, endPort).then(resolve);
    });
  });
}

// Start backend server
async function startBackendServer() {
  const port = await findFreePort(8000, 9000);
  backendPort = port;
  
  // Find Python executable
  const pythonExe = process.platform === 'win32' ? 'python.exe' : 'python3';
  
  // Find run_fvoas_interface.py
  const scriptPath = path.join(__dirname, '..', 'run_fvoas_interface.py');
  
  // Start backend
  backendProcess = spawn(pythonExe, [
    scriptPath,
    '--web',
    '--port', port.toString(),
    '--host', '127.0.0.1'
  ], {
    cwd: path.join(__dirname, '..'),
    stdio: 'pipe'
  });
  
  backendProcess.stdout.on('data', (data) => {
    console.log(`Backend: ${data}`);
  });
  
  backendProcess.stderr.on('data', (data) => {
    console.error(`Backend Error: ${data}`);
  });
  
  backendProcess.on('close', (code) => {
    console.log(`Backend process exited with code ${code}`);
    if (mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.webContents.send('backend-error', 'Backend server stopped');
    }
  });
  
  // Wait for server to be ready
  return new Promise((resolve) => {
    const checkServer = setInterval(() => {
      const http = require('http');
      const req = http.get(`http://127.0.0.1:${port}/api/modules`, (res) => {
        clearInterval(checkServer);
        resolve(port);
      });
      req.on('error', () => {
        // Server not ready yet
      });
    }, 500);
    
    // Timeout after 30 seconds
    setTimeout(() => {
      clearInterval(checkServer);
      resolve(port);
    }, 30000);
  });
}

function createWindow() {
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1000,
    minHeight: 700,
    icon: path.join(__dirname, 'assets', 'fvoas_logo.png'),
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      sandbox: true
    },
    backgroundColor: '#1a1a1a', // FVOAS dark theme
    titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
    show: false // Don't show until ready
  });

  // Load the app once backend is ready
  startBackendServer().then((port) => {
    const url = `http://127.0.0.1:${port}`;
    console.log(`Loading FVOAS interface at ${url}`);
    mainWindow.loadURL(url);
    
    // Show window when ready
    mainWindow.once('ready-to-show', () => {
      mainWindow.show();
      
      // Focus window
      if (process.platform === 'darwin') {
        app.dock.show();
      }
    });
  });

  // Handle window closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Handle external links
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  // Create application menu
  createMenu();
}

function createMenu() {
  const template = [
    {
      label: 'FVOAS',
      submenu: [
        {
          label: 'About FVOAS',
          click: () => {
            const { dialog } = require('electron');
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'About FVOAS',
              message: 'Federal Voice Obfuscation and Analysis Suite',
              detail: 'Version 1.0.0\n\nClassification: SECRET\nDevice: 9 (Audio) | Layer: 3\n\n⚠️ Compliant but Not Audited/Certified',
              buttons: ['OK']
            });
          }
        },
        { type: 'separator' },
        {
          label: 'Quit',
          accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
          click: () => {
            app.quit();
          }
        }
      ]
    },
    {
      label: 'View',
      submenu: [
        { role: 'reload', label: 'Reload' },
        { role: 'forceReload', label: 'Force Reload' },
        { role: 'toggleDevTools', label: 'Toggle Developer Tools' },
        { type: 'separator' },
        { role: 'resetZoom', label: 'Actual Size' },
        { role: 'zoomIn', label: 'Zoom In' },
        { role: 'zoomOut', label: 'Zoom Out' },
        { type: 'separator' },
        { role: 'togglefullscreen', label: 'Toggle Fullscreen' }
      ]
    },
    {
      label: 'Window',
      submenu: [
        { role: 'minimize', label: 'Minimize' },
        { role: 'close', label: 'Close' }
      ]
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'FVOAS Documentation',
          click: () => {
            shell.openExternal('https://github.com/SWORDIntel/AUDIOANALYSISX1');
          }
        },
        {
          label: 'Compliance Information',
          click: () => {
            const { dialog } = require('electron');
            dialog.showMessageBox(mainWindow, {
              type: 'warning',
              title: 'Compliance Notice',
              message: 'Federal Compliance Status',
              detail: 'This system is COMPLIANT with federal specifications but NOT AUDITED/CERTIFIED.\n\nFor production deployments, formal audit may be required.',
              buttons: ['OK']
            });
          }
        }
      ]
    }
  ];

  // macOS specific menu adjustments
  if (process.platform === 'darwin') {
    template[0].submenu = [
      { role: 'about', label: 'About FVOAS' },
      { type: 'separator' },
      { role: 'services', label: 'Services' },
      { type: 'separator' },
      { role: 'hide', label: 'Hide FVOAS' },
      { role: 'hideOthers', label: 'Hide Others' },
      { role: 'unhide', label: 'Show All' },
      { type: 'separator' },
      { role: 'quit', label: 'Quit FVOAS' }
    ];
    
    template[3].submenu = [
      { role: 'close', label: 'Close' },
      { role: 'minimize', label: 'Minimize' },
      { role: 'zoom', label: 'Zoom' },
      { type: 'separator' },
      { role: 'front', label: 'Bring All to Front' }
    ];
  }

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// App event handlers
app.whenReady().then(() => {
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  // Stop backend server
  if (backendProcess) {
    backendProcess.kill();
    backendProcess = null;
  }
  
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('before-quit', () => {
  // Ensure backend is stopped
  if (backendProcess) {
    backendProcess.kill();
    backendProcess = null;
  }
});

// IPC handlers
ipcMain.handle('get-backend-port', () => {
  return backendPort;
});

ipcMain.handle('get-app-version', () => {
  return app.getVersion();
});

ipcMain.handle('get-platform', () => {
  return process.platform;
});
