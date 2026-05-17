# 📖 DETAILED INSTALLATION GUIDE

## System Requirements

- **Operating System:** Windows, macOS, or Linux
- **Python:** 3.7 or higher
- **RAM:** Minimum 512MB (1GB recommended)
- **Disk Space:** ~50MB for application + database
- **Browser:** Any modern browser (Chrome, Firefox, Safari, Edge)

## Installation Methods

### Method 1: Automatic (Recommended) ⭐

#### Windows:
1. Extract the ZIP file to your desired location
2. Double-click `start_server.bat`
3. Wait for setup to complete automatically
4. Browser should open to `http://127.0.0.1:5000`

#### macOS/Linux:
```bash
# Extract ZIP
unzip SIT-IN-Enhanced.zip
cd SIT-IN-Enhanced

# Make script executable
chmod +x start_server.sh

# Run
./start_server.sh
```

---

### Method 2: Manual Installation

#### Step 1: Install Python
- Visit https://www.python.org/downloads/
- Download Python 3.7 or higher
- **IMPORTANT:** Check "Add Python to PATH" during installation

#### Step 2: Extract Project
- Extract the ZIP file to a folder of your choice
- Remember the folder path (you'll need it)

#### Step 3: Open Terminal/Command Prompt
- **Windows:** Right-click in folder → "Open PowerShell here" or "Command Prompt here"
- **macOS/Linux:** Right-click in Finder → "New Terminal at Folder" or use `cd` command

#### Step 4: Create Virtual Environment
```bash
# Windows:
python -m venv venv
venv\Scripts\activate

# macOS/Linux:
python3 -m venv venv
source venv/bin/activate
```

#### Step 5: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 6: Run the Application
```bash
python app.py
```

#### Step 7: Access in Browser
```
Open: http://127.0.0.1:5000
```

---

## Troubleshooting Installation

### Problem: "Python is not recognized"
**Solution:**
- Python is not in your PATH
- Reinstall Python and check "Add Python to PATH"
- Or use full path: `C:\Python311\python.exe app.py` (Windows)

### Problem: "ModuleNotFoundError: No module named 'flask'"
**Solution:**
```bash
# Make sure virtual environment is activated
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Then reinstall:
pip install -r requirements.txt
```

### Problem: "Port 5000 already in use"
**Solution 1 - Change port:**
- Edit `app.py` (last line)
- Change `app.run(debug=True)` to `app.run(debug=True, port=5001)`

**Solution 2 - Free port:**
```bash
# Windows - Find process using port 5000:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -i :5000
kill -9 <PID>
```

### Problem: "Permission denied" on macOS/Linux
**Solution:**
```bash
chmod +x start_server.sh
./start_server.sh
```

### Problem: Database errors
**Solution:**
```bash
# Delete and recreate database
rm ccs.db
python app.py
```

---

## Post-Installation Verification

After successful installation, verify:

1. **Server Running:**
   - Terminal shows: "Running on http://127.0.0.1:5000"
   - No error messages

2. **Browser Access:**
   - Opens http://127.0.0.1:5000
   - Landing page displays correctly

3. **Navigation:**
   - Can click on all navbar links
   - Pages load without errors

4. **Login:**
   - Can access login page
   - Can access admin login page

5. **Database:**
   - File `ccs.db` exists in project folder
   - No database errors in terminal

---

## Configuration (Optional)

### Change Admin Credentials
Edit `app.py` line ~196:
```python
('admin', hashlib.sha256('your_new_password'.encode()).hexdigest())
```

### Change Port
Edit `app.py` last line:
```python
app.run(debug=True, port=8000)  # Change to desired port
```

### Change CORS Origins
Edit `app.py` lines 8-11:
```python
CORS(app, supports_credentials=True, origins=[
    'http://yourdomain.com',  # Add your domain
    'http://127.0.0.1:5000'
])
```

---

## Running in Production

### Important Changes:

1. **Disable Debug Mode:**
   ```python
   app.debug = False  # In __main__ section
   ```

2. **Use Environment Variables:**
   ```python
   SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-key')
   ```

3. **Use Production Server:**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

4. **Update CORS:**
   ```python
   CORS(app, origins=['yourdomain.com'])
   ```

5. **Enable HTTPS:**
   - Use nginx/Apache reverse proxy
   - Install SSL certificate

---

## Deployment Options

### Option 1: Simple Server (Good for Small Teams)
```bash
# Keep running in background (Linux/macOS):
nohup python app.py &

# Or use screen:
screen python app.py  # Press Ctrl+A then D to detach
```

### Option 2: Docker (Recommended)
Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
```

Build and run:
```bash
docker build -t sit-in .
docker run -p 5000:5000 sit-in
```

### Option 3: Cloud Deployment
- **Heroku:** Add Procfile with `web: gunicorn app:app`
- **AWS:** Use Elastic Beanstalk or EC2
- **DigitalOcean:** VPS with Python and Gunicorn
- **Replit:** Paste code directly, click Run

---

## Backup & Restore

### Backup Database:
```bash
# Simple copy
cp ccs.db ccs.db.backup

# Or scheduled backup (Linux):
0 2 * * * cp /path/to/ccs.db /path/to/backup/ccs.db.$(date +\%Y\%m\%d)
```

### Restore Database:
```bash
cp ccs.db.backup ccs.db
```

---

## Uninstallation

### Complete Removal:
```bash
# Windows:
# 1. Delete the project folder
# 2. Restart computer

# macOS/Linux:
rm -rf SIT-IN-Enhanced
```

### Remove Virtual Environment Only:
```bash
rm -rf venv
```

---

## Getting Help

1. **Check QUICKSTART.md** - Fast setup guide
2. **Check README.md** - Full documentation
3. **Browser Console Errors** - Press F12 in browser
4. **Terminal Output** - Check for error messages
5. **Verify Python:** `python --version`
6. **Verify Git:** `git --version` (optional)

---

## System Information (For Support)

When reporting issues, include:
```
Python version: [python --version]
OS: [Windows/macOS/Linux]
Browser: [Chrome/Firefox/Safari/Edge]
Error message: [Full error text]
Steps to reproduce: [List of steps]
```

---

## Next Steps After Installation

1. ✅ Verify server is running
2. ✅ Access http://127.0.0.1:5000
3. ✅ Read QUICKSTART.md
4. ✅ Login as admin (admin/admin123)
5. ✅ Create student account
6. ✅ Test all features
7. ✅ Change admin password
8. ✅ Start using the system!

---

## Performance Optimization

For better performance:

1. **Increase Worker Processes:**
   ```bash
   gunicorn -w 8 app:app
   ```

2. **Enable Caching:**
   ```python
   CACHING_TIMEOUT = 300  # 5 minutes
   ```

3. **Database Optimization:**
   ```python
   # Add indexes to frequently queried columns
   CREATE INDEX idx_user_id ON sitin(user_id);
   ```

4. **Monitor Resources:**
   ```bash
   # Linux:
   top
   df -h
   
   # macOS:
   Activity Monitor
   ```

---

## Version Information

- **Current Version:** 2.0 Enhanced
- **Release Date:** May 2026
- **Python Minimum:** 3.7
- **Status:** Production Ready ✅

---

**Installation Complete!** 🎉

You're ready to use the SIT-IN Monitoring System. Enjoy!
