# REIMS Backup Script
# Creates a complete backup of all persistent storage

param(
    [string]$BackupDir = "backups"
)

$ErrorActionPreference = "Stop"

Write-Host "`n╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║          REIMS BACKUP SCRIPT                            ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Create backup directory with timestamp
$timestamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$backupPath = Join-Path $BackupDir "reims_backup_$timestamp"

Write-Host "📁 Creating backup directory: $backupPath" -ForegroundColor Yellow
New-Item -ItemType Directory -Path $backupPath -Force | Out-Null

# Items to backup
$itemsToBackup = @(
    @{
        Name = "Database"
        Source = "reims.db"
        Essential = $true
        Description = "Main SQLite database with all data"
    },
    @{
        Name = "Database WAL"
        Source = "reims.db-wal"
        Essential = $false
        Description = "Write-Ahead Log (if exists)"
    },
    @{
        Name = "Database SHM"
        Source = "reims.db-shm"
        Essential = $false
        Description = "Shared memory file (if exists)"
    },
    @{
        Name = "MinIO Data"
        Source = "minio-data"
        Essential = $true
        Description = "Object storage data"
    },
    @{
        Name = "Environment Config"
        Source = ".env"
        Essential = $true
        Description = "Configuration and credentials"
    },
    @{
        Name = "Uploads"
        Source = "uploads"
        Essential = $false
        Description = "Uploaded files directory"
    },
    @{
        Name = "Storage"
        Source = "storage"
        Essential = $false
        Description = "Processed files storage"
    },
    @{
        Name = "Redis Dump"
        Source = "dump.rdb"
        Essential = $false
        Description = "Redis persistence file"
    }
)

$backupStats = @{
    Total = 0
    Success = 0
    Failed = 0
    Skipped = 0
    TotalSize = 0
}

foreach ($item in $itemsToBackup) {
    $backupStats.Total++
    
    Write-Host "`n📦 Backing up: $($item.Name)" -ForegroundColor White
    Write-Host "   Source: $($item.Source)" -ForegroundColor Gray
    Write-Host "   $($item.Description)" -ForegroundColor Gray
    
    if (Test-Path $item.Source) {
        try {
            $destination = Join-Path $backupPath (Split-Path $item.Source -Leaf)
            
            if (Test-Path $item.Source -PathType Container) {
                # Directory - copy recursively
                Copy-Item -Path $item.Source -Destination $destination -Recurse -Force
                $size = (Get-ChildItem -Path $destination -Recurse | Measure-Object -Property Length -Sum).Sum
            } else {
                # File - copy directly
                Copy-Item -Path $item.Source -Destination $destination -Force
                $size = (Get-Item $destination).Length
            }
            
            $sizeMB = [math]::Round($size / 1MB, 2)
            $backupStats.TotalSize += $size
            $backupStats.Success++
            
            Write-Host "   ✅ Backed up successfully ($sizeMB MB)" -ForegroundColor Green
        }
        catch {
            $backupStats.Failed++
            Write-Host "   ✗ Backup failed: $_" -ForegroundColor Red
            
            if ($item.Essential) {
                Write-Host "`n⚠️ CRITICAL: Failed to backup essential item!" -ForegroundColor Red
                throw
            }
        }
    }
    else {
        $backupStats.Skipped++
        if ($item.Essential) {
            Write-Host "   ⚠️ NOT FOUND (Essential item missing!)" -ForegroundColor Yellow
        } else {
            Write-Host "   ⏭️ Skipped (not found)" -ForegroundColor Gray
        }
    }
}

# Create backup manifest
$manifest = @{
    Timestamp = $timestamp
    BackupDate = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    System = @{
        OS = "$env:OS"
        ComputerName = $env:COMPUTERNAME
        UserName = $env:USERNAME
    }
    Statistics = $backupStats
    Items = $itemsToBackup
}

$manifestPath = Join-Path $backupPath "backup_manifest.json"
$manifest | ConvertTo-Json -Depth 5 | Out-File $manifestPath -Encoding UTF8

Write-Host "`n═══════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "                    BACKUP SUMMARY" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════════════" -ForegroundColor Cyan

Write-Host "`n📊 Statistics:" -ForegroundColor White
Write-Host "   Total items:    $($backupStats.Total)" -ForegroundColor Gray
Write-Host "   ✅ Successful:  $($backupStats.Success)" -ForegroundColor Green
Write-Host "   ✗ Failed:       $($backupStats.Failed)" -ForegroundColor $(if ($backupStats.Failed -gt 0) { "Red" } else { "Gray" })
Write-Host "   ⏭️ Skipped:      $($backupStats.Skipped)" -ForegroundColor Gray
Write-Host "   📦 Total size:   $([math]::Round($backupStats.TotalSize / 1MB, 2)) MB" -ForegroundColor Cyan

Write-Host "`n💾 Backup location:" -ForegroundColor White
Write-Host "   $backupPath" -ForegroundColor Cyan

if ($backupStats.Failed -eq 0) {
    Write-Host "`n✅ BACKUP COMPLETED SUCCESSFULLY!" -ForegroundColor Green
    Write-Host "═══════════════════════════════════════════════════════════`n" -ForegroundColor Cyan
    exit 0
} else {
    Write-Host "`n⚠️ BACKUP COMPLETED WITH ERRORS!" -ForegroundColor Yellow
    Write-Host "═══════════════════════════════════════════════════════════`n" -ForegroundColor Cyan
    exit 1
}

















