# SIT-IN Monitoring System - Enhanced Edition 🎓

**A comprehensive sit-in session monitoring and management system for University of Cebu's College of Computer Studies**

## ✨ Features Implemented

### Student Features
- ✅ **Sit-in Summary Dashboard** - View total sessions, average duration, longest session
- ✅ **Manual & Auto Tracking** - Start/end sessions manually or via auto-tracking
- ✅ **Session History** - Detailed record of all sit-in sessions with timestamps
- ✅ **AI Recommendations** - Personalized recommendations based on usage patterns
- ✅ **Software Availability** - View available software per lab
- ✅ **Reservation System** - Book lab time in advance
- ✅ **Dark Mode** - Toggle dark/light theme with persistence

### Admin Features
- ✅ **Analytics Dashboard** - Real-time analytics with charts
  - Peak hours analysis
  - Peak days tracking
  - Lab utilization rates
  - Student engagement metrics
- ✅ **Comprehensive Reports** - Export session data as CSV
  - Filter by date range, lab, student
  - Includes all session details
- ✅ **Software Management** - Upload and manage software applications
  - Track availability per lab
  - Add/edit/delete software entries
- ✅ **Student Records** - View all student sit-in history
- ✅ **Feedback/Testimonials** - Anonymous student feedback display

### Technical Features
- ✅ **Dark Mode** - Complete dark theme with CSS variables
- ✅ **Responsive Design** - Works on desktop, tablet, and mobile
- ✅ **Real-time Data** - Live session tracking and updates
- ✅ **Secure Authentication** - Session-based auth for students and admins
- ✅ **Automated Scheduling** - Background tasks for session management

---

## 📦 Project Structure

```
SIT-IN-Enhanced/
├── app.py                          # Main Flask application
├── ccs.db                          # SQLite database
├── requirements.txt                # Python dependencies
├── page/
│   ├── landingpage.html           # Home page
│   ├── dashboard-enhanced.html    # NEW: Student dashboard with summary
│   ├── dashboard.html             # Original dashboard
│   ├── history.html               # Session history
│   ├── reservation.html           # Lab reservation
│   ├── community.html             # Community pages
│   └── ...
├── admin/
│   ├── home.html                  # Admin home
│   ├── analytics.html             # NEW: Analytics & reports
│   ├── students.html              # Student management
│   ├── sitin.html                 # Sit-in records
│   └── ...
├── css/
│   ├── landing.css                # Main styles
│   └── darkmode.css               # NEW: Dark mode styles
├── js/
│   ├── darkmode.js                # NEW: Dark mode toggle
│   ├── script.js                  # Main JavaScript
│   ├── dashboard.js               # Dashboard functions
│   └── ...
└── images/                        # Static images
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)
- Git (optional, for cloning)

### Step 1: Clone or Extract Project
```bash
# If you have the ZIP file, extract it
unzip SIT-IN-Enhanced.zip
cd SIT-IN-Enhanced
```

### Step 2: Install Dependencies
```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### Step 3: Initialize Database
```bash
# The database will be created automatically when you run the app
# First run will initialize all tables
python app.py
```

### Step 4: Access the Application
```
Open browser and go to: http://127.0.0.1:5000
```

---

## 🔐 Default Admin Credentials

**Username:** `admin`  
**Password:** `admin123`

⚠️ **IMPORTANT:** Change these credentials in production!

---

## 📊 New API Endpoints

### Student Routes
- `GET /api/student/sit-in-summary` - Get sit-in statistics
- `POST /api/student/sitin/start` - Start new session
- `POST /api/student/sitin/<id>/end` - End session
- `GET /api/student/history` - Get all sessions
- `GET /api/student/recommendations` - Get AI recommendations

### Software Routes
- `GET /api/software/available` - Get available software per lab
- `GET /api/admin/software` - List all software (admin)
- `POST /api/admin/software` - Add software (admin)
- `PUT /api/admin/software/<id>` - Update software (admin)
- `DELETE /api/admin/software/<id>` - Delete software (admin)

### Analytics Routes
- `GET /api/admin/analytics` - Get analytics data
- `POST /api/admin/reports/generate` - Generate CSV report
- `GET /api/admin/reports/list` - List all reports

---

## 💾 Database Schema

### New/Updated Tables

**sitin table** (Enhanced with new columns):
```sql
ALTER TABLE sitin ADD COLUMN time_in DATETIME;
ALTER TABLE sitin ADD COLUMN time_out DATETIME;
ALTER TABLE sitin ADD COLUMN duration_minutes INTEGER;
ALTER TABLE sitin ADD COLUMN pc_number TEXT;
ALTER TABLE sitin ADD COLUMN remarks TEXT;
ALTER TABLE sitin ADD COLUMN is_manual INTEGER DEFAULT 1;
```

**software_apps table** (New):
```sql
CREATE TABLE software_apps (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    lab_id TEXT,
    version TEXT,
    availability TEXT DEFAULT 'available',
    uploaded_by INTEGER,
    created DATETIME,
    FOREIGN KEY(uploaded_by) REFERENCES admins(id)
);
```

**reports table** (New):
```sql
CREATE TABLE reports (
    id INTEGER PRIMARY KEY,
    admin_id INTEGER,
    report_type TEXT,
    date_from TEXT,
    date_to TEXT,
    file_path TEXT,
    created DATETIME,
    FOREIGN KEY(admin_id) REFERENCES admins(id)
);
```

**ai_recommendations table** (New):
```sql
CREATE TABLE ai_recommendations (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    recommended_time TEXT,
    recommended_lab TEXT,
    reason TEXT,
    confidence REAL,
    created DATETIME,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
```

---

## 🎨 Dark Mode Usage

**Enable/Disable Dark Mode:**
- Click the moon/sun icon in the navbar to toggle
- Preference is automatically saved to browser storage
- Dark mode respects system preferences if not manually set

---

## 📈 Analytics Features

### Available Metrics
1. **Total Sessions** - Count of all sit-in sessions
2. **Active Students** - Number of unique students
3. **Average Duration** - Mean session duration in minutes
4. **Peak Hours** - Hours with most sit-ins (top 5)
5. **Peak Days** - Days with most sit-ins
6. **Lab Utilization** - Sessions per lab

### Report Generation
- Select date range
- Filter by lab (optional)
- Export as CSV file
- Includes comprehensive session details

---

## 🤖 AI Recommendations

The system analyzes each student's sit-in history to provide:
- **Optimal Time** - Best time based on personal history
- **Quiet Time** - Less crowded time suggestions
- **Preferred Lab** - Most frequently used lab
- **Confidence Score** - Reliability of recommendation

Requires at least one sit-in session in history to generate recommendations.

---

## 🔧 Troubleshooting

### Port Already in Use
```bash
# Change port in app.py line 887:
app.run(debug=True, port=5001)  # Change 5001 to another port
```

### Database Errors
```bash
# Reset database (WARNING: This will delete all data)
rm ccs.db
python app.py  # Will create fresh database
```

### Module Not Found
```bash
# Ensure virtual environment is activated
# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

### CORS Issues
- Ensure CORS origins are correct in app.py lines 8-10
- Add your development URL if needed

---

## 📝 Usage Guide

### For Students

1. **Register/Login**
   - Go to login page and create account
   - Fill in all required information

2. **Start Sit-in Session**
   - Click "Start New Sit-in" on dashboard
   - Select lab, enter PC number, add purpose
   - Click "Start Session"

3. **View Summary**
   - Dashboard shows total sessions, avg duration, longest session
   - Recent sessions table displays all recent activity

4. **Get Recommendations**
   - Click "View Recommendations" button
   - AI will suggest optimal sit-in times based on history

5. **Download History**
   - Go to History page
   - Click "Export" to download session data

### For Admins

1. **Login**
   - Use admin credentials
   - Access `/admin/home.html`

2. **View Analytics**
   - Go to Analytics tab
   - Select date range
   - View charts and statistics
   - Filter by different time periods

3. **Generate Reports**
   - Go to Reports tab
   - Select date range and lab (optional)
   - Click "Generate CSV Report"
   - File downloads automatically

4. **Manage Software**
   - Go to Software Management tab
   - Click "+ Add Software"
   - Fill in details and submit
   - Update availability status as needed
   - Delete software if no longer available

5. **View Student Records**
   - Go to Student Records
   - View all sit-in records
   - Filter and search as needed

---

## 🔐 Security Considerations

### Development Mode
- Debug mode is ON (good for development, NOT for production)
- Secret key is hardcoded (should be environment variable)
- CORS allows local origins only

### For Production:
```python
# Change in app.py:
app.debug = False
app.secret_key = os.environ.get('SECRET_KEY')  # Use env variable
# Restrict CORS origins
CORS(app, origins=['yourdomain.com'])
```

---

## 📞 Support

For issues or feature requests:
1. Check the troubleshooting section
2. Review API documentation in app.py comments
3. Check browser console for JavaScript errors
4. Verify database connectivity

---

## 📄 License

© 2026 University of Cebu — College of Computer Studies

---

## 🎉 Summary of New Features

| Feature | Status | Location |
|---------|--------|----------|
| Sit-in Summary | ✅ Complete | `page/dashboard-enhanced.html` |
| AI Recommendations | ✅ Complete | `/api/student/recommendations` |
| Analytics Dashboard | ✅ Complete | `admin/analytics.html` |
| CSV Report Generation | ✅ Complete | `/api/admin/reports/generate` |
| Software Management | ✅ Complete | `/api/admin/software` |
| Dark Mode | ✅ Complete | `css/darkmode.css`, `js/darkmode.js` |
| Session Duration Tracking | ✅ Complete | Database + API |
| Lab Utilization Charts | ✅ Complete | `admin/analytics.html` |
| Peak Hours/Days Analysis | ✅ Complete | `/api/admin/analytics` |
| Anonymous Testimonials | ✅ Existing | `admin/feedback.html` |

---

## 🚀 Next Steps

1. Change admin credentials
2. Customize lab names/numbers if needed
3. Test all features thoroughly
4. Deploy to production server
5. Monitor and collect feedback from users

---

**Last Updated:** May 2026  
**Version:** 2.0 (Enhanced Edition)  
**Status:** Production Ready ✅
