const { app, BrowserWindow } = require("electron");

/** Must match Flask port in backend/app.py. Start Flask before Electron. */
const FRONTEND_URL = "http://127.0.0.1:5001/";

function createWindow() {
  const win = new BrowserWindow({
    width: 1000,
    height: 700,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  // Bust stale cached HTML while iterating on the UI
  win.loadURL(`${FRONTEND_URL}?_=${Date.now()}`);
}

app.whenReady().then(() => {
  createWindow();

  app.on("activate", () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});