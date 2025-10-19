# REIMS Quick Reference Card

## 📱 Mobile Responsive (NEW!)

**Automatic:** Adapts to screen size (< 768px)

Mobile Features:
- Single column card layout
- Collapsible hamburger menu
- Bottom tab navigation (4 tabs)
- Full-screen property views
- Swipeable chart navigation
- 44x44px touch targets
- Horizontal scroll tables

**Bottom Tabs:**
- 🏠 Dashboard
- 🏢 Properties
- 🔔 Alerts
- 📄 Documents

**Mobile Menu:**
- Tap hamburger (☰) to open
- All 10 navigation options
- Slide-in from left
- Auto-close on selection

## ⌨️ Command Palette

**Activation:** Press `⌘K` (Mac) or `Ctrl+K` (Windows)

Quick access to:
- Navigate to any feature
- Upload documents
- Run analysis
- Generate reports
- Export data
- Search documents
- Recent actions

**Usage:**
1. Press ⌘K / Ctrl+K
2. Type command or use keyboard shortcuts
3. Arrow keys to navigate
4. Enter to execute

**Popular Shortcuts:**
- `G P` - Go to Portfolio
- `U D` - Upload Document
- `A P` - Run Analysis
- `R M` - Generate Report
- `E C` - Export CSV

## 🚀 Start Application

```powershell
# Terminal 1: Backend
python start_optimized_server.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

## ✅ Check Status

```powershell
.\check_reims_status.ps1
```

## 🌐 Access Points

| Service | URL |
|---------|-----|
| **Main App** | http://localhost:3000 |
| **API Docs** | http://localhost:8000/docs |
| **Health Check** | http://localhost:8000/health |

## 📱 Application Features

| Tab | Feature | Description |
|-----|---------|-------------|
| 🏢 Portfolio | Property View | Property portfolio dashboard |
| 📊 KPIs | Metrics | Key performance indicators |
| 📤 Upload | Documents | Upload documents |
| ⚙️ Processing | Status | Processing pipeline |
| 📈 Charts | Analytics | Financial charts |
| 🎯 Exit | Strategy | Exit strategy comparison |
| 📡 Monitor | Real-time | Live monitoring |
| 🚨 Alerts | Notifications | Alert center |
| 📍 **Location** | **Intelligence** | **Market analysis** |
| 🤖 **AI Tenants** | **Recommendations** | **AI tenant matching (NEW!)** |

## 🎯 Location Analysis Feature

Access: Click **📍 Location** tab

### 4 Intelligence Cards:

1. **👥 Demographics**
   - Population trends
   - Median income
   - Age distribution

2. **💼 Employment**
   - Unemployment rate
   - Labor force
   - Major employers

3. **🏗️ New Developments**
   - Active projects
   - Total investment
   - Recent developments

4. **📋 Political & Zoning**
   - Recent changes
   - Policy updates
   - Impact ratings

## 🤖 AI Tenant Recommendations Feature

Access: Click **🤖 AI Tenants** tab

### Overview:
- **Available space metrics** with vacancy rate
- **Tenant mix pie chart** (interactive)
- **5 AI-powered recommendations**

### Each Recommendation Shows:
1. **Business Type** - With icon and space needs
2. **Synergy Score** - 0-100 with progress bar
3. **Rent Range** - Typical price per sqft
4. **Success Factors** - 4 reasons they'll succeed
5. **Demographics** - Target customer profile
6. **Add Button** - Add to prospects list

### Example Recommendations:
- 💪 Premium Fitness Studio (92 synergy)
- ☕ Coffee & Co-Working (88 synergy)
- 🍽️ Fast-Casual Restaurant (85 synergy)
- 🛍️ Boutique Retail (82 synergy)
- 💼 Professional Services (78 synergy)

## 🔧 Troubleshooting

### Backend Not Starting
```powershell
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill process (replace PID)
Stop-Process -Id [PID] -Force

# Restart
python start_optimized_server.py
```

### Frontend Not Starting
```powershell
# Check if port 3000 is in use
netstat -ano | findstr :3000

# Kill process (replace PID)
Stop-Process -Id [PID] -Force

# Restart
cd frontend
npm run dev
```

### PowerShell Curl Issues
❌ **Don't use:** `curl -UseBasicParsing`  
✅ **Use:** `.\check_reims_status.ps1`

## 📚 Documentation

| Topic | File |
|-------|------|
| Startup | `STARTUP_GUIDE.md` |
| Location Feature | `LOCATION_ANALYSIS_GUIDE.md` |
| PowerShell Fix | `POWERSHELL_CURL_FIX.md` |
| Complete Summary | `SESSION_COMPLETE_SUMMARY.md` |

## 💡 Tips

- Always use `check_reims_status.ps1` to verify services
- Access Location Analysis via 📍 Location tab
- Check API docs at http://localhost:8000/docs
- Hot reload is active - changes appear immediately
- All features work offline (uses SQLite)

---

**Status:** ✅ All Systems Operational  
**Version:** REIMS v2.0  
**Last Updated:** October 12, 2025

