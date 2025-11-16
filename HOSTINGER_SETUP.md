# Running Stock Alert Script on Hostinger

## ⚠️ Important: Selenium vs Simple Script

### ❌ **Selenium Script (stock_alert_selenium.py) - NOT Recommended for Shared Hosting**
- **Requires:** Chrome browser binary, ChromeDriver, Xvfb (for headless)
- **Shared Hosting:** Usually **NOT SUPPORTED** - Hostinger shared hosting doesn't allow installing Chrome
- **VPS:** Can work on Hostinger VPS, but needs setup
- **Resource Heavy:** Uses more CPU/RAM

### ✅ **Simple Script (stock_alert_simple.py) - RECOMMENDED**
- **No Browser Needed:** Uses only requests + BeautifulSoup
- **Shared Hosting Compatible:** Works on most shared hosting
- **Lightweight:** Minimal resources
- **Same Features:** Delivery checking + Telegram notifications included

---

## 🚀 Recommended: Use stock_alert_simple.py on Hostinger

### Setup on Hostinger Shared Hosting:

1. **Upload Files:**
   ```bash
   - stock_alert_simple.py
   - items.json
   - requirements.txt (or install manually)
   ```

2. **SSH Access (if available) or use Python App:**
   ```bash
   # Check Python version
   python3 --version
   
   # Install dependencies
   pip3 install requests beautifulsoup4 schedule --user
   ```

3. **Run with nohup (keeps running after SSH disconnect):**
   ```bash
   nohup python3 stock_alert_simple.py > output.log 2>&1 &
   ```

4. **Or use screen/tmux for persistent session:**
   ```bash
   screen -S stockmonitor
   python3 stock_alert_simple.py
   # Press Ctrl+A then D to detach
   ```

---

## 🖥️ If You Want to Use Selenium (VPS Only)

### Requirements for Selenium on Hostinger VPS:

#### 1. **System Dependencies (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install -y \
    wget \
    curl \
    unzip \
    xvfb \
    libxss1 \
    libappindicator1 \
    libindicator7 \
    fonts-liberation \
    libasound2 \
    libnspr4 \
    libnss3 \
    libxrandr2 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libgdk-pixbuf2.0-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxrandr2 \
    libxss1 \
    libxtst6 \
    lsb-release \
    xdg-utils
```

#### 2. **Install Google Chrome:**
```bash
# Download Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

# Install
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-get install -f -y

# Verify
google-chrome --version
```

#### 3. **Install ChromeDriver:**
```bash
# Get Chrome version
CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d. -f1)

# Download matching ChromeDriver
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION}")
wget -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip"

# Extract and install
unzip /tmp/chromedriver.zip -d /tmp/
sudo mv /tmp/chromedriver /usr/local/bin/chromedriver
sudo chmod +x /usr/local/bin/chromedriver

# Verify
chromedriver --version
```

#### 4. **Update Selenium Script for Server:**
The script already has `--no-sandbox` which is needed for servers.

#### 5. **Run with Xvfb (virtual display):**
```bash
# Install Xvfb if not already installed
sudo apt-get install xvfb -y

# Run script with virtual display
xvfb-run -a python3 stock_alert_selenium.py
```

Or run as background service:
```bash
nohup xvfb-run -a python3 stock_alert_selenium.py > selenium.log 2>&1 &
```

---

## 📋 Quick Comparison

| Feature | stock_alert_simple.py | stock_alert_selenium.py |
|---------|----------------------|-------------------------|
| **Works on Shared Hosting** | ✅ Yes | ❌ No (needs VPS) |
| **Setup Complexity** | 🟢 Easy | 🟡 Medium |
| **Resource Usage** | 🟢 Low | 🟡 High |
| **Speed** | 🟢 Fast | 🟡 Slower |
| **JS Rendering** | ❌ No | ✅ Yes |
| **For Croma** | ✅ Works | ✅ Works |

---

## 💡 Recommendation

**For Hostinger: Use `stock_alert_simple.py`**

- ✅ Works on shared hosting
- ✅ Same delivery checking features
- ✅ Same Telegram notifications
- ✅ Easier to set up
- ✅ Less resource usage
- ✅ Faster checks

Most websites (including Croma) work fine with `stock_alert_simple.py` because the stock status is usually in the initial HTML response.

---

## 🔧 Hostinger Specific Notes

### If you have SSH access:
```bash
# Check Python version
python3 --version

# Install packages to user directory (no sudo needed)
pip3 install --user requests beautifulsoup4 schedule

# Run script
python3 stock_alert_simple.py
```

### If using Hostinger Python App:
1. Upload files via File Manager
2. Configure Python app to run `stock_alert_simple.py`
3. Set environment variables if needed

### Keep Script Running:
```bash
# Option 1: Use screen
screen -S stock
python3 stock_alert_simple.py

# Option 2: Use nohup
nohup python3 stock_alert_simple.py &

# Option 3: Use systemd service (VPS only)
# Create /etc/systemd/system/stock-monitor.service
```

---

## ❓ Troubleshooting

**"Permission denied" errors:**
- Use `pip3 install --user` instead of `pip3 install`

**"Command not found: python3":**
- Try `python` instead of `python3`
- Check if Python is installed: `which python`

**"Module not found":**
- Install packages: `pip3 install --user requests beautifulsoup4 schedule`

**Script stops after SSH disconnect:**
- Use `screen`, `tmux`, or `nohup`

---

## 📞 Need Help?

- Check Hostinger's Python documentation
- Ensure SSH access is enabled
- For VPS, check if root/sudo access is available
- Most issues are solved by using `stock_alert_simple.py` instead

