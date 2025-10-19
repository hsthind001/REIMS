# ============================================================================
# REIMS SQLite Database Backup Script
# ============================================================================
# This script backs up the SQLite database with timestamp
# Run this script weekly or set up as a scheduled task
# ============================================================================

param(
    [string]$DatabasePath = "C:\REIMS\reims.db",
    [string]$BackupDir = "C:\REIMS\backups",
    [int]$KeepDays = 30  # Keep backups for 30 days
)

Write-Host "`n╔══════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          REIMS SQLite Database Backup Utility                    ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Create backup directory if it doesn't exist
if (!(Test-Path $BackupDir)) {
    Write-Host "📁 Creating backup directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
    Write-Host "✅ Backup directory created: $BackupDir" -ForegroundColor Green
}

# Check if database exists
if (!(Test-Path $DatabasePath)) {
    Write-Host "❌ Error: Database not found at $DatabasePath" -ForegroundColor Red
    exit 1
}

# Get database info
$dbInfo = Get-Item $DatabasePath
$dbSize = [math]::Round($dbInfo.Length / 1KB, 2)
$timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$backupFileName = "reims_backup_$timestamp.db"
$backupPath = Join-Path $BackupDir $backupFileName

Write-Host "📊 Database Information:" -ForegroundColor Cyan
Write-Host "   Source: $DatabasePath" -ForegroundColor White
Write-Host "   Size: $dbSize KB" -ForegroundColor White
Write-Host "   Last Modified: $($dbInfo.LastWriteTime)" -ForegroundColor White

# Check document count
try {
    $docCount = python -c "import sqlite3; conn = sqlite3.connect('$DatabasePath'); count = conn.execute('SELECT COUNT(*) FROM financial_documents').fetchone()[0]; print(count); conn.close()" 2>$null
    Write-Host "   Documents: $docCount records" -ForegroundColor White
} catch {
    Write-Host "   Documents: Unable to count" -ForegroundColor Gray
}

Write-Host "`n💾 Creating backup..." -ForegroundColor Yellow
Write-Host "   Destination: $backupFileName" -ForegroundColor Gray

try {
    # Copy database file
    Copy-Item -Path $DatabasePath -Destination $backupPath -Force
    
    # Verify backup
    $backupInfo = Get-Item $backupPath
    $backupSize = [math]::Round($backupInfo.Length / 1KB, 2)
    
    if ($backupInfo.Length -eq $dbInfo.Length) {
        Write-Host "✅ Backup created successfully!" -ForegroundColor Green
        Write-Host "   File: $backupFileName" -ForegroundColor White
        Write-Host "   Size: $backupSize KB" -ForegroundColor White
        Write-Host "   Location: $BackupDir" -ForegroundColor White
    } else {
        Write-Host "⚠️  Backup created but size mismatch!" -ForegroundColor Yellow
        Write-Host "   Original: $dbSize KB" -ForegroundColor Gray
        Write-Host "   Backup: $backupSize KB" -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ Backup failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Clean up old backups
Write-Host "`n🧹 Cleaning up old backups..." -ForegroundColor Yellow
$cutoffDate = (Get-Date).AddDays(-$KeepDays)
$oldBackups = Get-ChildItem -Path $BackupDir -Filter "reims_backup_*.db" | Where-Object { $_.LastWriteTime -lt $cutoffDate }

if ($oldBackups.Count -gt 0) {
    Write-Host "   Found $($oldBackups.Count) old backup(s) (older than $KeepDays days)" -ForegroundColor Gray
    foreach ($backup in $oldBackups) {
        Remove-Item $backup.FullName -Force
        Write-Host "   ✅ Deleted: $($backup.Name)" -ForegroundColor Gray
    }
} else {
    Write-Host "   No old backups to delete" -ForegroundColor Gray
}

# List recent backups
Write-Host "`n📚 Recent Backups:" -ForegroundColor Cyan
$recentBackups = Get-ChildItem -Path $BackupDir -Filter "reims_backup_*.db" | Sort-Object LastWriteTime -Descending | Select-Object -First 5
foreach ($backup in $recentBackups) {
    $age = (Get-Date) - $backup.LastWriteTime
    $ageStr = if ($age.Days -gt 0) { "$($age.Days) days ago" } elseif ($age.Hours -gt 0) { "$($age.Hours) hours ago" } else { "$($age.Minutes) minutes ago" }
    $sizeKB = [math]::Round($backup.Length / 1KB, 2)
    Write-Host "   • $($backup.Name)" -ForegroundColor White
    Write-Host "     Size: $sizeKB KB | Created: $ageStr" -ForegroundColor Gray
}

$totalBackups = (Get-ChildItem -Path $BackupDir -Filter "reims_backup_*.db").Count
$totalBackupSize = [math]::Round((Get-ChildItem -Path $BackupDir -Filter "reims_backup_*.db" | Measure-Object -Property Length -Sum).Sum / 1MB, 2)

Write-Host "`n📊 Backup Summary:" -ForegroundColor Cyan
Write-Host "   Total backups: $totalBackups files" -ForegroundColor White
Write-Host "   Total size: $totalBackupSize MB" -ForegroundColor White
Write-Host "   Retention: $KeepDays days" -ForegroundColor White

Write-Host "`n✅ Backup process completed successfully!" -ForegroundColor Green
Write-Host "`n💡 To restore a backup:" -ForegroundColor Yellow
Write-Host "   1. Stop the backend" -ForegroundColor White
Write-Host "   2. Copy backup file to $DatabasePath" -ForegroundColor White
Write-Host "   3. Restart the backend" -ForegroundColor White
Write-Host "`n═══════════════════════════════════════════════════════════════════`n" -ForegroundColor Gray

