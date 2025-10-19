"""
REIMS Database Migration Runner

Run SQL migrations using the database connection module.

Usage:
    python backend/db/migrations/run_migration.py 001_create_properties.sql
    python backend/db/migrations/run_migration.py --all
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime


# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from backend.db import init_db, close_db, execute, fetch_all, fetch_val


async def read_migration_file(filename: str) -> str:
    """Read SQL migration file"""
    migrations_dir = Path(__file__).parent
    file_path = migrations_dir / filename
    
    if not file_path.exists():
        raise FileNotFoundError(f"Migration file not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


async def create_migrations_table():
    """Create migrations tracking table if it doesn't exist"""
    await execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id SERIAL PRIMARY KEY,
            migration_name VARCHAR(255) UNIQUE NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            success BOOLEAN DEFAULT true,
            error_message TEXT
        )
    """)
    print("✅ Migrations tracking table ready")


async def is_migration_applied(migration_name: str) -> bool:
    """Check if migration has already been applied"""
    result = await fetch_val(
        "SELECT COUNT(*) FROM schema_migrations WHERE migration_name = $1 AND success = true",
        migration_name
    )
    return result > 0


async def record_migration(migration_name: str, success: bool = True, error: str = None):
    """Record migration in tracking table"""
    await execute(
        """
        INSERT INTO schema_migrations (migration_name, success, error_message)
        VALUES ($1, $2, $3)
        ON CONFLICT (migration_name) 
        DO UPDATE SET 
            applied_at = CURRENT_TIMESTAMP,
            success = EXCLUDED.success,
            error_message = EXCLUDED.error_message
        """,
        migration_name, success, error
    )


async def run_migration(filename: str, force: bool = False):
    """Run a single migration file"""
    print(f"\n{'='*70}")
    print(f"Migration: {filename}")
    print('='*70)
    
    # Check if already applied
    if not force and await is_migration_applied(filename):
        print(f"⏭️  Migration '{filename}' already applied. Use --force to reapply.")
        return True
    
    try:
        # Read migration SQL
        print(f"📖 Reading migration file...")
        sql = await read_migration_file(filename)
        
        # Execute migration
        print(f"🔄 Executing migration...")
        start_time = datetime.now()
        
        # Split SQL into individual statements (simple approach)
        # Note: This won't handle all complex SQL, but works for most migrations
        statements = [s.strip() for s in sql.split(';') if s.strip() and not s.strip().startswith('--')]
        
        for i, statement in enumerate(statements, 1):
            if statement:
                try:
                    await execute(statement)
                    print(f"   ✓ Statement {i}/{len(statements)} executed")
                except Exception as e:
                    # Some statements might fail if objects already exist, which is OK
                    if "already exists" in str(e).lower():
                        print(f"   ⚠️  Statement {i}/{len(statements)}: {str(e)[:100]}")
                    else:
                        raise
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        # Record success
        await record_migration(filename, success=True)
        
        print(f"\n✅ Migration completed successfully in {elapsed:.2f}s")
        print(f"📝 Recorded in schema_migrations table")
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        await record_migration(filename, success=False, error=str(e))
        return False


async def list_migrations():
    """List all available migrations"""
    migrations_dir = Path(__file__).parent
    migration_files = sorted(migrations_dir.glob('*.sql'))
    
    if not migration_files:
        print("No migration files found")
        return []
    
    print(f"\n{'='*70}")
    print("Available Migrations")
    print('='*70)
    
    for i, migration_file in enumerate(migration_files, 1):
        is_applied = await is_migration_applied(migration_file.name)
        status = "✅ Applied" if is_applied else "⏳ Pending"
        print(f"{i}. {migration_file.name:40s} {status}")
    
    return [f.name for f in migration_files]


async def show_migration_history():
    """Show migration history from database"""
    try:
        migrations = await fetch_all("""
            SELECT 
                migration_name,
                applied_at,
                success,
                error_message
            FROM schema_migrations
            ORDER BY applied_at DESC
        """)
        
        if not migrations:
            print("\n📊 No migrations recorded yet")
            return
        
        print(f"\n{'='*70}")
        print("Migration History")
        print('='*70)
        
        for m in migrations:
            status = "✅" if m['success'] else "❌"
            print(f"{status} {m['migration_name']:40s} {m['applied_at']}")
            if not m['success'] and m['error_message']:
                print(f"   Error: {m['error_message'][:100]}")
        
    except Exception as e:
        print(f"⚠️  Could not retrieve migration history: {str(e)}")


async def run_all_migrations(force: bool = False):
    """Run all pending migrations"""
    migrations = await list_migrations()
    
    if not migrations:
        print("No migrations to run")
        return
    
    print(f"\n{'='*70}")
    print(f"Running All Migrations (force={force})")
    print('='*70)
    
    success_count = 0
    failed_count = 0
    
    for migration in migrations:
        success = await run_migration(migration, force=force)
        if success:
            success_count += 1
        else:
            failed_count += 1
    
    print(f"\n{'='*70}")
    print("Summary")
    print('='*70)
    print(f"✅ Successful: {success_count}")
    print(f"❌ Failed: {failed_count}")


async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="REIMS Database Migration Runner")
    parser.add_argument(
        'migration',
        nargs='?',
        help='Migration file to run (e.g., 001_create_properties.sql)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Run all pending migrations'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force reapply migration even if already applied'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available migrations'
    )
    parser.add_argument(
        '--history',
        action='store_true',
        help='Show migration history'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("REIMS Database Migration Runner")
    print("="*70)
    
    try:
        # Initialize database connection
        print("\n🔌 Connecting to database...")
        await init_db()
        print("✅ Connected to database")
        
        # Create migrations tracking table
        await create_migrations_table()
        
        # Execute command
        if args.history:
            await show_migration_history()
        
        elif args.list or (not args.migration and not args.all):
            await list_migrations()
            await show_migration_history()
        
        elif args.all:
            await run_all_migrations(force=args.force)
        
        elif args.migration:
            await run_migration(args.migration, force=args.force)
        
        print("\n" + "="*70)
        print("✅ Migration runner completed")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        # Close database connection
        await close_db()


if __name__ == "__main__":
    asyncio.run(main())
















