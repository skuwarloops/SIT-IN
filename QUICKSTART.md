# 🚀 QUICK START GUIDE - SIT-IN Monitoring System

## In 3 Easy Steps:

### Step 1: Run the Server

**Windows Users:**
```
Double-click: start_server.bat
```

**Mac/Linux Users:**
```bash
chmod +x start_server.sh
./start_server.sh
```

### Step 2: Open Your Browser
```
Go to: http://127.0.0.1:5000
```

### Step 3: Login

#### Student Login
- Go to "Login" on the home page
- Create a new account or use existing credentials
- Access the dashboard

#### Admin Login  
- Go to "Admin Login" (bottom of login page)
- Username: `admin`
- Password: `admin123`
- Access admin dashboard at `/admin/home.html`

---

## 🎯 What's New?

✨ **New Features:**
- 📊 Student sit-in summary with statistics
- 🤖 AI-powered recommendations
- 📈 Admin analytics dashboard
- 📥 CSV report generation
- 💾 Software management system
- 🌙 Dark mode toggle
- ⏱️ Manual & auto session tracking

---

## 📍 Important URLs

| Page | URL |
|------|-----|
| Home | `http://127.0.0.1:5000/` |
| Student Dashboard | `http://127.0.0.1:5000/page/dashboard-enhanced.html` |
| Student Login | `http://127.0.0.1:5000/login-register/index.html` |
| Admin Panel | `http://127.0.0.1:5000/admin/home.html` |
| Admin Login | `http://127.0.0.1:5000/login-register/admin-login.html` |
| Analytics | `http://127.0.0.1:5000/admin/analytics.html` |
| History | `http://127.0.0.1:5000/page/history.html` |
| Reservation | `http://127.0.0.1:5000/page/reservation.html` |

---

## 🔑 Default Credentials

### Admin
- **Username:** `admin`
- **Password:** `admin123`

### Student Sample Account
- **Create a new account** during registration

---

## 🎓 Student Tutorial

1. **Register:** Create account with your information
2. **Login:** Use your credentials
3. **Start Sit-in:** Click "Start New Sit-in" on dashboard
4. **View Summary:** See total sessions, average duration, longest session
5. **Get Recommendations:** Click "View Recommendations" for AI suggestions
6. **Check History:** View all past sit-in sessions
7. **Make Reservation:** Book lab time in advance

---

## 👨‍💼 Admin Tutorial

1. **Login:** Use admin credentials
2. **View Analytics:** Go to Analytics tab
   - See peak hours and days
   - Check lab utilization
   - View student statistics
3. **Generate Reports:** Go to Reports tab
   - Select date range
   - Choose lab (optional)
   - Download CSV file
4. **Manage Software:** Go to Software Management
   - Add new software
   - Update availability status
   - Delete obsolete software
5. **View Records:** Check all student sit-in records
6. **Monitor Feedback:** View anonymous student testimonials

---

## 🌙 Dark Mode

**Toggle anytime:**
- Click the moon (🌙) or sun (☀️) icon in the top navbar
- Your preference is automatically saved
- Works on all pages

---

## 🗄️ Database

The system uses **SQLite** (automatically created):
- Database file: `ccs.db`
- No setup needed - created on first run
- No external database required

---

## 🛠️ Troubleshooting

### Issue: "Port 5000 is already in use"
**Solution:**
1. Find and close the other process using port 5000
2. Or modify port in `app.py` line 887:
   ```python
   app.run(debug=True, port=5001)
   ```

### Issue: "ModuleNotFoundError"
**Solution:**
```bash
# Make sure virtual environment is activated
pip install -r requirements.txt
```

### Issue: Database errors
**Solution:**
```bash
# Delete database and recreate
rm ccs.db
python app.py
```

### Issue: Blank pages or 404 errors
**Solution:**
1. Clear browser cache (Ctrl+Shift+Delete)
2. Hard refresh (Ctrl+F5)
3. Restart server

---

## 📊 API Endpoints (For Developers)

### Student APIs
- `GET /api/student/sit-in-summary` - Get statistics
- `POST /api/student/sitin/start` - Start session
- `POST /api/student/sitin/{id}/end` - End session
- `GET /api/student/history` - Get all sessions
- `GET /api/student/recommendations` - Get AI recommendations

### Admin APIs
- `GET /api/admin/analytics` - Get analytics data
- `POST /api/admin/reports/generate` - Generate report
- `GET /api/admin/software` - List software
- `POST /api/admin/software` - Add software
- `PUT /api/admin/software/{id}` - Update software
- `DELETE /api/admin/software/{id}` - Delete software

---

## 📞 Need Help?

1. **Read the full README.md** - Complete documentation
2. **Check the browser console** - For JavaScript errors (F12)
3. **Check app logs** - In the terminal running the server
4. **Verify Python version** - Must be 3.7 or higher

---

## ✅ Verification Checklist

After starting the server, verify:
- [ ] Browser opens to http://127.0.0.1:5000
- [ ] Landing page loads without errors
- [ ] Login page accessible
- [ ] Can create student account
- [ ] Dashboard loads after login
- [ ] Dark mode toggle works
- [ ] Admin analytics page loads
- [ ] Reports can be generated

---

## 🎉 You're All Set!

The SIT-IN Monitoring System is now ready to use. Enjoy the enhanced features!

**Questions?** Check README.md for detailed documentation.

---

**Version:** 2.0 Enhanced  
**Updated:** May 2026  
**Status:** ✅ Ready to Use
