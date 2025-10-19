# SQLite Database Backup Guide for REIMS

## 📋 Overview

Your REIMS application now uses SQLite exclusively. This guide shows you how to backup your database to protect your data.

---

## 🎯 Quick Backup Methods

### Method 1: Double-Click Backup (Easiest)

**Simply double-click:** `BACKUP_NOW.bat`

This will:
- ✅ Create a timestamped backup in `C:\REIMS\backups\`
- ✅ Show you backup information
- ✅ Clean up old backups (older than 30 days)
- ✅ Take 2-3 seconds

**Example backup name:** `reims_backup_2025-10-13_084102.db`

---

### Method 2: PowerShell Script (More Control)

**Run in PowerShell:**
```powershell
.\backup_sqlite_database.ps1
```

**Advanced options:**
```powershell
# Backup to different location
.\backup_sqlite_database.ps1 -BackupDir "D:\REIMS_Backups"

# Keep backups for 90 days instead of 30
.\backup_sqlite_database.ps1 -KeepDays 90

# Both options
.\backup_sqlite_database.ps1 -BackupDir "D:\Backups" -KeepDays 90
```

---

### Method 3: Manual Copy (Quick and Simple)

**Just copy the file:**
```powershell
copy C:\REIMS\reims.db C:\REIMS\backups\reims_manual_backup.db
```

**That's it!** SQLite is just a file, so copying it = backup.

---

## ⏰ Automated Scheduled Backups

### Setup Weekly Automatic Backups

**Create a scheduled task that runs weekly:**

1. **Open Task Scheduler**
   - Press `Win + R`
   - Type: `taskschd.msc`
   - Press Enter

2. **Create New Task**
   - Click "Create Basic Task"
   - Name: `REIMS Database Backup`
   - Description: `Weekly backup of REIMS SQLite database`

3. **Set Trigger**
   - Select: `Weekly`
   - Day: `Sunday` (or your preference)
   - Time: `2:00 AM` (when REIMS is not in use)
   - Click Next

4. **Set Action**
   - Select: `Start a program`
   - Program: `powershell.exe`
   - Arguments: `-ExecutionPolicy Bypass -File "C:\REIMS\backup_sqlite_database.ps1"`
   - Start in: `C:\REIMS`
   - Click Next

5. **Finish**
   - Check "Open Properties" before finish
   - In Properties:
     - ✅ Check "Run whether user is logged on or not"
     - ✅ Check "Run with highest privileges"
   - Click OK

**Done!** Your database will now backup automatically every Sunday at 2 AM.

---

### Quick Setup Script

Or run this PowerShell command to create the scheduled task:

```powershell
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File C:\REIMS\backup_sqlite_database.ps1" -WorkingDirectory "C:\REIMS"
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 2am
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName "REIMS Database Backup" -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description "Weekly backup of REIMS SQLite database"
```

---

## 📂 Backup Location

**Default backup directory:**
```
C:\REIMS\backups\
```

**Backup files:**
- `reims_backup_2025-10-13_084102.db`
- `reims_backup_2025-10-14_084102.db`
- `reims_backup_2025-10-15_084102.db`
- ... (keeps last 30 days)

**Backup retention:**
- Backups older than 30 days are automatically deleted
- You can change this with `-KeepDays` parameter

---

## 🔄 How to Restore a Backup

### If Something Goes Wrong

**Steps to restore:**

1. **Stop the backend**
   ```powershell
   Get-NetTCPConnection -LocalPort 8001 | Select-Object -ExpandProperty OwningProcess | ForEach-Object { Stop-Process -Id $_ -Force }
   ```

2. **Backup current database** (just in case)
   ```powershell
   copy C:\REIMS\reims.db C:\REIMS\reims_before_restore.db
   ```

3. **Restore the backup**
   ```powershell
   # Find the backup you want
   dir C:\REIMS\backups\reims_backup_*.db
   
   # Copy it to replace current database
   copy C:\REIMS\backups\reims_backup_2025-10-13_084102.db C:\REIMS\reims.db
   ```

4. **Restart the backend**
   ```powershell
   python run_backend.py
   ```

**Done!** Your database is restored.

---

## 💾 Backup Best Practices

### Recommended Backup Strategy

1. **Automated Weekly Backups** (set and forget)
   - Runs every Sunday at 2 AM
   - Keeps 30 days of history

2. **Manual Backup Before Major Changes**
   - Before updating REIMS
   - Before bulk data changes
   - Before system maintenance
   - Just double-click `BACKUP_NOW.bat`

3. **Off-site Backup Monthly** (optional but recommended)
   - Copy `C:\REIMS\backups\` to cloud storage
   - Or copy to external drive
   - Protects against hardware failure

### What Gets Backed Up

**The `reims.db` file contains:**
- ✅ All uploaded documents metadata (29 documents)
- ✅ All property records (127 properties)
- ✅ All user accounts (3 users)
- ✅ All processing jobs
- ✅ All extracted data
- ✅ All relationships and settings

**Note:** The backup does NOT include:
- ❌ Actual files in MinIO (separate backup needed)
- ❌ Configuration files (.env)
- ❌ Application code

---

## 📊 Backup Size

**Current database:**
- Size: ~352 KB (very small!)
- Documents: 29 records
- Growth: ~10-20 KB per 100 documents

**Estimated future sizes:**
- 100 documents: ~1 MB
- 1,000 documents: ~5 MB
- 10,000 documents: ~50 MB

**Storage needed for 30 days of backups:**
- Current: ~10 MB (30 backups × 352 KB)
- At 1,000 docs: ~150 MB

**Very manageable!** You won't run out of space.

---

## 🔧 Troubleshooting

### Backup Script Not Working?

**Check PowerShell execution policy:**
```powershell
Get-ExecutionPolicy
```

If it's `Restricted`, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Can't Find Backup Files?

**Check backup directory:**
```powershell
dir C:\REIMS\backups\
```

**If empty:**
- Run `BACKUP_NOW.bat` manually
- Check for error messages

### Scheduled Task Not Running?

**Test manually first:**
```powershell
.\backup_sqlite_database.ps1
```

**Check task scheduler:**
- Open Task Scheduler
- Find "REIMS Database Backup"
- Check "Last Run Result" (should be "0x0" for success)

---

## ✅ Quick Reference

| Task | Command |
|------|---------|
| **Quick backup** | Double-click `BACKUP_NOW.bat` |
| **Manual backup** | `copy reims.db backups\backup.db` |
| **PowerShell backup** | `.\backup_sqlite_database.ps1` |
| **List backups** | `dir C:\REIMS\backups\` |
| **Restore backup** | `copy backups\reims_backup_*.db reims.db` |
| **Check size** | `(Get-Item reims.db).Length / 1KB` |

---

## 🎯 Summary

**Your SQLite database is easy to backup:**

1. ✅ **Manual:** Just copy the file
2. ✅ **Semi-automated:** Double-click `BACKUP_NOW.bat`
3. ✅ **Fully automated:** Set up scheduled task (runs weekly)

**Recommended setup:**
- Set up weekly scheduled backup (one-time setup)
- Run `BACKUP_NOW.bat` before major changes
- Sleep peacefully knowing your data is safe! 😊

**Current status:**
- Database: 352 KB
- Documents: 29 records
- First backup: Created ✅
- Location: `C:\REIMS\backups\`

Your data is now protected! 🎉

