# PostgreSQL Password Setup Guide

## Current Configuration
✓ **SQLite is configured by default** - NO password required, NO authentication errors!

## If You Want to Use PostgreSQL

### Option 1: Find Your Current PostgreSQL Password
1. Check if you saved it during PostgreSQL installation
2. Look in your password manager
3. Check installation notes

### Option 2: Reset PostgreSQL Password

#### Method 1: Using pgAdmin (Easiest)
1. Open pgAdmin 4
2. Connect to your PostgreSQL server (it may prompt for password)
3. Right-click on "postgres" user → Properties
4. Go to "Definition" tab
5. Set a new password
6. Click "Save"

#### Method 2: Using Command Line
```powershell
# Find PostgreSQL installation
$pgPath = "C:\Program Files\PostgreSQL\18\bin"

# Set new password (replace 'newpassword' with your desired password)
& "$pgPath\psql.exe" -U postgres -c "ALTER USER postgres PASSWORD 'newpassword';"
```

#### Method 3: Edit pg_hba.conf (Temporary - for password reset)
1. Find pg_hba.conf file (usually in `C:\Program Files\PostgreSQL\18\data\`)
2. Find the line with: `host all all 127.0.0.1/32 scram-sha-256`
3. Change to: `host all all 127.0.0.1/32 trust`
4. Restart PostgreSQL service:
   ```powershell
   Restart-Service postgresql-x64-18
   ```
5. Connect without password and set new one:
   ```powershell
   psql -U postgres -c "ALTER USER postgres PASSWORD 'newpassword';"
   ```
6. Change pg_hba.conf back to `scram-sha-256`
7. Restart PostgreSQL service again

### Step 3: Update .env File
Once you have the password, edit `.env` file:

```bash
# Comment out SQLite:
# DATABASE_URL=sqlite:///./reims.db

# Uncomment and update PostgreSQL:
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD_HERE@localhost:5432/reims
```

### Step 4: Create REIMS Database
```powershell
# Using psql
psql -U postgres -c "CREATE DATABASE reims;"

# Or using pgAdmin - right-click "Databases" → Create → Database → Name: "reims"
```

## Testing Connection
Run the test script:
```powershell
python test_postgres_password.py
```

## Recommendation
✓ **For development: Use SQLite (already configured)**
- No password hassles
- No authentication errors  
- Works instantly
- Perfect for local development

✓ **For production: Use PostgreSQL**
- Better performance with large datasets
- Better concurrency
- Required for enterprise deployments

















