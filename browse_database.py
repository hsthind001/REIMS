"""
Interactive SQLite Database Browser
Simple script to explore your REIMS database
"""
import sqlite3
import sys
from datetime import datetime

# ANSI color codes for Windows
try:
    import colorama
    colorama.init()
    GREEN = '\033[92m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
except:
    GREEN = CYAN = YELLOW = RESET = BOLD = ''

def print_header(text):
    print(f"\n{CYAN}{BOLD}{'='*70}")
    print(f"{text:^70}")
    print(f"{'='*70}{RESET}\n")

def print_section(text):
    print(f"\n{YELLOW}▶ {text}{RESET}")

def show_tables(conn):
    """Show all tables in the database"""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    print_section("Available Tables:")
    for i, (table,) in enumerate(tables, 1):
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"   {i}. {GREEN}{table}{RESET} ({count} records)")
    
    return [t[0] for t in tables]

def show_table_structure(conn, table_name):
    """Show table structure"""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    print_section(f"Table Structure: {table_name}")
    print(f"\n   {'Column':<25} {'Type':<15} {'Not Null':<10} {'Default'}")
    print(f"   {'-'*70}")
    for col in columns:
        col_name = col[1]
        col_type = col[2]
        not_null = "YES" if col[3] else "NO"
        default = col[4] if col[4] else ""
        print(f"   {col_name:<25} {col_type:<15} {not_null:<10} {default}")

def show_recent_records(conn, table_name, limit=10):
    """Show recent records from a table"""
    cursor = conn.cursor()
    
    # Get column names
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cursor.fetchall()]
    
    # Get recent records
    try:
        # Try to order by common date columns
        if 'upload_date' in columns:
            order_col = 'upload_date'
        elif 'created_at' in columns:
            order_col = 'created_at'
        elif 'id' in columns:
            order_col = 'id'
        else:
            order_col = columns[0]
        
        cursor.execute(f"SELECT * FROM {table_name} ORDER BY {order_col} DESC LIMIT {limit}")
        records = cursor.fetchall()
        
        if not records:
            print(f"   {YELLOW}No records found in {table_name}{RESET}")
            return
        
        print_section(f"Recent Records from {table_name} (showing {len(records)} of {limit}):")
        print()
        
        # Display each record
        for i, record in enumerate(records, 1):
            print(f"   {CYAN}Record {i}:{RESET}")
            for col_name, value in zip(columns, record):
                # Truncate long values
                str_value = str(value)
                if len(str_value) > 60:
                    str_value = str_value[:57] + "..."
                print(f"      {col_name:<20}: {str_value}")
            print()
    
    except Exception as e:
        print(f"   {YELLOW}Error reading records: {e}{RESET}")

def custom_query(conn):
    """Execute a custom SQL query"""
    print_section("Custom SQL Query")
    print("   Enter your SQL query (or 'back' to return):")
    print("   Example: SELECT * FROM financial_documents WHERE status='completed'")
    print()
    
    query = input("   SQL> ").strip()
    
    if query.lower() == 'back':
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        
        if query.strip().upper().startswith('SELECT'):
            results = cursor.fetchall()
            if results:
                # Get column names
                col_names = [description[0] for description in cursor.description]
                
                print(f"\n   {GREEN}Query Results:{RESET}")
                print(f"   {' | '.join(col_names)}")
                print(f"   {'-'*70}")
                
                for row in results:
                    print(f"   {' | '.join(str(val)[:30] for val in row)}")
                print(f"\n   {CYAN}({len(results)} rows returned){RESET}")
            else:
                print(f"   {YELLOW}Query returned no results{RESET}")
        else:
            conn.commit()
            print(f"   {GREEN}Query executed successfully{RESET}")
    
    except Exception as e:
        print(f"   {YELLOW}Error executing query: {e}{RESET}")

def main():
    """Main interactive menu"""
    db_path = 'reims.db'
    
    print_header("🗄️  REIMS SQLite Database Browser")
    
    try:
        conn = sqlite3.connect(db_path)
        print(f"{GREEN}✅ Connected to: {db_path}{RESET}")
        
        # Get database info
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        table_count = cursor.fetchone()[0]
        
        print(f"{CYAN}📊 Database contains {table_count} tables{RESET}")
        
        while True:
            print(f"\n{BOLD}{'─'*70}{RESET}")
            print(f"{BOLD}Main Menu:{RESET}")
            print("   1. Show all tables")
            print("   2. View table structure")
            print("   3. Browse table data")
            print("   4. View uploaded documents")
            print("   5. Run custom SQL query")
            print("   6. Database statistics")
            print("   0. Exit")
            print(f"{BOLD}{'─'*70}{RESET}")
            
            choice = input(f"\n{CYAN}Enter your choice (0-6):{RESET} ").strip()
            
            if choice == '0':
                print(f"\n{GREEN}👋 Goodbye!{RESET}\n")
                break
            
            elif choice == '1':
                tables = show_tables(conn)
            
            elif choice == '2':
                tables = show_tables(conn)
                table_num = input(f"\n{CYAN}Enter table number:{RESET} ").strip()
                try:
                    idx = int(table_num) - 1
                    if 0 <= idx < len(tables):
                        show_table_structure(conn, tables[idx])
                    else:
                        print(f"{YELLOW}Invalid table number{RESET}")
                except ValueError:
                    print(f"{YELLOW}Please enter a valid number{RESET}")
            
            elif choice == '3':
                tables = show_tables(conn)
                table_num = input(f"\n{CYAN}Enter table number:{RESET} ").strip()
                try:
                    idx = int(table_num) - 1
                    if 0 <= idx < len(tables):
                        limit = input(f"{CYAN}How many records to show? (default 10):{RESET} ").strip()
                        limit = int(limit) if limit else 10
                        show_recent_records(conn, tables[idx], limit)
                    else:
                        print(f"{YELLOW}Invalid table number{RESET}")
                except ValueError:
                    print(f"{YELLOW}Please enter a valid number{RESET}")
            
            elif choice == '4':
                # Quick view of uploaded documents
                print_section("📄 Uploaded Documents")
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, file_name, document_type, status, upload_date 
                    FROM financial_documents 
                    ORDER BY upload_date DESC 
                    LIMIT 20
                """)
                docs = cursor.fetchall()
                
                if docs:
                    print(f"\n   {'ID':<5} {'File Name':<30} {'Type':<15} {'Status':<10} {'Upload Date'}")
                    print(f"   {'-'*90}")
                    for doc in docs:
                        doc_id = str(doc[0])[:4]
                        file_name = str(doc[1])[:28] if doc[1] else "N/A"
                        doc_type = str(doc[2])[:13] if doc[2] else "N/A"
                        status = str(doc[3])[:8] if doc[3] else "N/A"
                        upload_date = str(doc[4])[:19] if doc[4] else "N/A"
                        print(f"   {doc_id:<5} {file_name:<30} {doc_type:<15} {status:<10} {upload_date}")
                    print(f"\n   {CYAN}Total: {len(docs)} documents shown{RESET}")
                else:
                    print(f"   {YELLOW}No documents found{RESET}")
            
            elif choice == '5':
                custom_query(conn)
            
            elif choice == '6':
                print_section("📊 Database Statistics")
                
                # Get file size
                import os
                size_bytes = os.path.getsize(db_path)
                size_kb = size_bytes / 1024
                size_mb = size_kb / 1024
                
                print(f"   Database file: {db_path}")
                print(f"   Size: {size_kb:.2f} KB ({size_mb:.2f} MB)")
                
                # Get table stats
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' 
                    ORDER BY name
                """)
                tables = cursor.fetchall()
                
                print(f"\n   Table Statistics:")
                print(f"   {'-'*40}")
                for (table,) in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"   {table:<30} {count:>8} rows")
            
            else:
                print(f"{YELLOW}Invalid choice. Please enter 0-6.{RESET}")
    
    except sqlite3.Error as e:
        print(f"\n{YELLOW}❌ Database error: {e}{RESET}")
        sys.exit(1)
    
    except FileNotFoundError:
        print(f"\n{YELLOW}❌ Database file not found: {db_path}{RESET}")
        sys.exit(1)
    
    except KeyboardInterrupt:
        print(f"\n\n{GREEN}👋 Interrupted by user. Goodbye!{RESET}\n")
    
    finally:
        if 'conn' in locals():
            conn.close()
            print(f"{GREEN}✅ Database connection closed{RESET}\n")

if __name__ == "__main__":
    main()

