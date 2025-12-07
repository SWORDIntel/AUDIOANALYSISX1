/**
 * FVOAS Electron Preload Script
 * ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 * Secure bridge between renderer and main process
 */

const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  getBackendPort: () => ipcRenderer.invoke('get-backend-port'),
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  getPlatform: () => ipcRenderer.invoke('get-platform'),
  
  // Listen for backend events
  onBackendError: (callback) => {
    ipcRenderer.on('backend-error', (event, message) => callback(message));
  },
  
  // Remove listeners
  removeAllListeners: (channel) => {
    ipcRenderer.removeAllListeners(channel);
  }
});

// Inject FVOAS theme CSS
window.addEventListener('DOMContentLoaded', () => {
  const style = document.createElement('style');
  style.textContent = `
    /* FVOAS Electron Theme */
    :root {
      --fvoas-primary: #00ffff;
      --fvoas-secondary: #0088ff;
      --fvoas-accent: #0000ff;
      --fvoas-bg: #1a1a1a;
      --fvoas-surface: #2a2a2a;
      --fvoas-text: #e0e0e0;
      --fvoas-border: #00ffff;
    }
    
    body {
      background: var(--fvoas-bg);
      color: var(--fvoas-text);
      font-family: 'Courier New', monospace;
      margin: 0;
      padding: 0;
    }
    
    /* Electron-specific styles */
    .electron-titlebar {
      -webkit-app-region: drag;
      height: 30px;
      background: var(--fvoas-surface);
      border-bottom: 1px solid var(--fvoas-border);
    }
  `;
  document.head.appendChild(style);
});
