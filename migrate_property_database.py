#!/usr/bin/env python3
"""
REIMS Property Management Database Migration
Creates all property management tables and indexes
"""

import sqlite3
import os
from datetime import datetime


def create_property_tables(db_path):
    """Create all property management tables"""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print(f"🏗️  Creating property management tables in {db_path}")
        
        # Properties table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS properties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_code TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                address TEXT NOT NULL,
                city TEXT NOT NULL,
                state TEXT NOT NULL,
                zip_code TEXT NOT NULL,
                country TEXT DEFAULT 'USA',
                property_type TEXT NOT NULL,
                status TEXT DEFAULT 'available',
                square_footage DECIMAL(10,2),
                bedrooms INTEGER,
                bathrooms DECIMAL(3,1),
                parking_spaces INTEGER DEFAULT 0,
                purchase_price DECIMAL(12,2),
                current_market_value DECIMAL(12,2),
                monthly_rent DECIMAL(10,2),
                property_taxes DECIMAL(10,2),
                insurance_cost DECIMAL(10,2),
                description TEXT,
                amenities TEXT,
                year_built INTEGER,
                last_renovation DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tenants table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tenants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tenant_code TEXT UNIQUE NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                phone TEXT,
                emergency_contact_name TEXT,
                emergency_contact_phone TEXT,
                emergency_contact_relationship TEXT,
                employer TEXT,
                monthly_income DECIMAL(10,2),
                credit_score INTEGER,
                background_check_status TEXT,
                date_of_birth DATETIME,
                ssn_last_four TEXT,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Leases table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lease_number TEXT UNIQUE NOT NULL,
                property_id INTEGER NOT NULL,
                tenant_id INTEGER NOT NULL,
                start_date DATETIME NOT NULL,
                end_date DATETIME NOT NULL,
                monthly_rent DECIMAL(10,2) NOT NULL,
                security_deposit DECIMAL(10,2) NOT NULL,
                late_fee DECIMAL(8,2) DEFAULT 0,
                pet_deposit DECIMAL(8,2) DEFAULT 0,
                status TEXT DEFAULT 'pending',
                lease_type TEXT DEFAULT 'fixed_term',
                auto_renewal INTEGER DEFAULT 0,
                notice_period_days INTEGER DEFAULT 30,
                rent_due_day INTEGER DEFAULT 1,
                utilities_included TEXT,
                additional_fees TEXT,
                terms_and_conditions TEXT,
                special_provisions TEXT,
                signed_date DATETIME,
                move_in_date DATETIME,
                move_out_date DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (property_id) REFERENCES properties (id),
                FOREIGN KEY (tenant_id) REFERENCES tenants (id)
            )
        """)
        
        # Rent payments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rent_payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lease_id INTEGER NOT NULL,
                payment_date DATETIME NOT NULL,
                due_date DATETIME NOT NULL,
                amount_due DECIMAL(10,2) NOT NULL,
                amount_paid DECIMAL(10,2) NOT NULL,
                payment_method TEXT,
                transaction_id TEXT,
                late_fee DECIMAL(8,2) DEFAULT 0,
                is_late INTEGER DEFAULT 0,
                is_partial INTEGER DEFAULT 0,
                notes TEXT,
                processed_by TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lease_id) REFERENCES leases (id)
            )
        """)
        
        # Maintenance requests table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS maintenance_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_number TEXT UNIQUE NOT NULL,
                property_id INTEGER NOT NULL,
                tenant_id INTEGER,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT,
                priority TEXT DEFAULT 'medium',
                status TEXT DEFAULT 'pending',
                assigned_to TEXT,
                contractor_contact TEXT,
                scheduled_date DATETIME,
                estimated_cost DECIMAL(10,2),
                actual_cost DECIMAL(10,2),
                reported_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                started_date DATETIME,
                completed_date DATETIME,
                resolution_notes TEXT,
                tenant_satisfaction INTEGER,
                warranty_until DATETIME,
                photos TEXT,
                receipts TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (property_id) REFERENCES properties (id),
                FOREIGN KEY (tenant_id) REFERENCES tenants (id)
            )
        """)
        
        # Financial transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS financial_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_number TEXT UNIQUE NOT NULL,
                property_id INTEGER NOT NULL,
                transaction_type TEXT NOT NULL,
                category TEXT NOT NULL,
                amount DECIMAL(12,2) NOT NULL,
                description TEXT NOT NULL,
                payment_method TEXT,
                vendor TEXT,
                invoice_number TEXT,
                reference_number TEXT,
                transaction_date DATETIME NOT NULL,
                due_date DATETIME,
                paid_date DATETIME,
                is_recurring INTEGER DEFAULT 0,
                recurring_frequency TEXT,
                tax_deductible INTEGER DEFAULT 0,
                notes TEXT,
                receipt_url TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (property_id) REFERENCES properties (id)
            )
        """)
        
        # Property documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS property_documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                property_id INTEGER,
                tenant_id INTEGER,
                lease_id INTEGER,
                maintenance_request_id INTEGER,
                document_type TEXT NOT NULL,
                filename TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                file_size INTEGER,
                mime_type TEXT,
                storage_path TEXT NOT NULL,
                document_id TEXT,
                title TEXT,
                description TEXT,
                tags TEXT,
                is_confidential INTEGER DEFAULT 0,
                uploaded_by TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (property_id) REFERENCES properties (id),
                FOREIGN KEY (tenant_id) REFERENCES tenants (id),
                FOREIGN KEY (lease_id) REFERENCES leases (id),
                FOREIGN KEY (maintenance_request_id) REFERENCES maintenance_requests (id)
            )
        """)
        
        # Create indexes for better performance
        print("📈 Creating indexes...")
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_properties_status ON properties(status)",
            "CREATE INDEX IF NOT EXISTS idx_properties_type ON properties(property_type)",
            "CREATE INDEX IF NOT EXISTS idx_properties_city ON properties(city)",
            "CREATE INDEX IF NOT EXISTS idx_tenants_email ON tenants(email)",
            "CREATE INDEX IF NOT EXISTS idx_leases_property ON leases(property_id)",
            "CREATE INDEX IF NOT EXISTS idx_leases_tenant ON leases(tenant_id)",
            "CREATE INDEX IF NOT EXISTS idx_leases_status ON leases(status)",
            "CREATE INDEX IF NOT EXISTS idx_leases_dates ON leases(start_date, end_date)",
            "CREATE INDEX IF NOT EXISTS idx_maintenance_property ON maintenance_requests(property_id)",
            "CREATE INDEX IF NOT EXISTS idx_maintenance_status ON maintenance_requests(status)",
            "CREATE INDEX IF NOT EXISTS idx_maintenance_priority ON maintenance_requests(priority)",
            "CREATE INDEX IF NOT EXISTS idx_financial_property ON financial_transactions(property_id)",
            "CREATE INDEX IF NOT EXISTS idx_financial_type ON financial_transactions(transaction_type)",
            "CREATE INDEX IF NOT EXISTS idx_financial_date ON financial_transactions(transaction_date)",
            "CREATE INDEX IF NOT EXISTS idx_rent_payments_lease ON rent_payments(lease_id)",
            "CREATE INDEX IF NOT EXISTS idx_rent_payments_due ON rent_payments(due_date)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        # Insert sample data
        print("📋 Inserting sample data...")
        
        # Sample properties
        sample_properties = [
            ('PROP001', 'Sunset Apartments Unit 1A', '123 Main Street', 'Springfield', 'IL', '62701', 'USA', 'residential', 'available', 850.0, 2, 1.0, 1, 150000.0, 175000.0, 1200.0, 2400.0, 800.0, 'Modern 2-bedroom apartment with updated kitchen', '["parking", "laundry", "balcony"]', 2015, None),
            ('PROP002', 'Downtown Office Suite', '456 Business Ave', 'Springfield', 'IL', '62702', 'USA', 'commercial', 'occupied', 1200.0, None, 2.0, 3, 300000.0, 350000.0, 2500.0, 5000.0, 1200.0, 'Prime commercial office space in downtown area', '["elevator", "parking", "conference_room"]', 2010, None),
            ('PROP003', 'Garden View Townhouse', '789 Oak Street', 'Springfield', 'IL', '62703', 'USA', 'residential', 'occupied', 1100.0, 3, 2.5, 2, 200000.0, 225000.0, 1500.0, 3000.0, 900.0, 'Spacious townhouse with garden view', '["garage", "patio", "garden"]', 2018, None)
        ]
        
        cursor.executemany("""
            INSERT OR IGNORE INTO properties 
            (property_code, name, address, city, state, zip_code, country, property_type, status, 
             square_footage, bedrooms, bathrooms, parking_spaces, purchase_price, current_market_value, 
             monthly_rent, property_taxes, insurance_cost, description, amenities, year_built, last_renovation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_properties)
        
        # Sample tenants
        sample_tenants = [
            ('TEN001', 'John', 'Smith', 'john.smith@email.com', '555-0101', 'Jane Smith', '555-0102', 'Spouse', 'Tech Corp', 5000.0, 750, 'approved', '1985-03-15', '1234', 'Reliable tenant, no issues'),
            ('TEN002', 'Sarah', 'Johnson', 'sarah.johnson@email.com', '555-0201', 'Mike Johnson', '555-0202', 'Brother', 'Design Studio', 4500.0, 720, 'approved', '1990-07-22', '5678', 'Great communication, prompt payments')
        ]
        
        cursor.executemany("""
            INSERT OR IGNORE INTO tenants 
            (tenant_code, first_name, last_name, email, phone, emergency_contact_name, 
             emergency_contact_phone, emergency_contact_relationship, employer, monthly_income, 
             credit_score, background_check_status, date_of_birth, ssn_last_four, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_tenants)
        
        # Sample leases
        sample_leases = [
            ('LEASE001', 2, 1, '2024-01-01', '2024-12-31', 2500.0, 5000.0, 100.0, 0.0, 'active', 'fixed_term', 0, 30, 1, '["water", "sewer"]', '[]', 'Standard lease terms apply', 'No pets allowed', '2023-12-15', '2024-01-01', None),
            ('LEASE002', 3, 2, '2024-02-01', '2025-01-31', 1500.0, 3000.0, 75.0, 200.0, 'active', 'fixed_term', 1, 30, 1, '["heat"]', '[]', 'Standard lease terms apply', 'One small pet allowed', '2024-01-20', '2024-02-01', None)
        ]
        
        cursor.executemany("""
            INSERT OR IGNORE INTO leases 
            (lease_number, property_id, tenant_id, start_date, end_date, monthly_rent, security_deposit, 
             late_fee, pet_deposit, status, lease_type, auto_renewal, notice_period_days, rent_due_day, 
             utilities_included, additional_fees, terms_and_conditions, special_provisions, 
             signed_date, move_in_date, move_out_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_leases)
        
        # Sample maintenance requests
        sample_maintenance = [
            ('MAINT001', 1, 1, 'Leaky Faucet in Kitchen', 'Kitchen faucet is dripping constantly', 'plumbing', 'medium', 'pending', None, None, None, 150.0, None, '2024-01-15 10:00:00', None, None, None, None, None, '[]', '[]'),
            ('MAINT002', 3, 2, 'HVAC Not Working', 'Heating system not responding to thermostat', 'hvac', 'high', 'pending', 'HVAC Pro Services', '555-HVAC', '2024-01-20 14:00:00', 300.0, None, '2024-01-18 09:30:00', None, None, None, None, None, '[]', '[]')
        ]
        
        cursor.executemany("""
            INSERT OR IGNORE INTO maintenance_requests 
            (request_number, property_id, tenant_id, title, description, category, priority, status, 
             assigned_to, contractor_contact, scheduled_date, estimated_cost, actual_cost, 
             reported_date, started_date, completed_date, resolution_notes, tenant_satisfaction, 
             warranty_until, photos, receipts)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_maintenance)
        
        # Sample financial transactions
        sample_transactions = [
            ('FIN001', 2, 'income', 'rent', 2500.0, 'Monthly rent payment - January 2024', 'bank_transfer', 'John Smith', None, 'RENT-JAN-2024', '2024-01-01', '2024-01-01', '2024-01-01', 0, None, 0, 'On-time payment', None),
            ('FIN002', 1, 'expense', 'maintenance', 125.0, 'Plumbing repair - kitchen faucet', 'check', 'ABC Plumbing', 'INV-001', 'EXP-JAN-001', '2024-01-16', '2024-01-16', '2024-01-16', 0, None, 1, 'Emergency repair', None),
            ('FIN003', 3, 'income', 'rent', 1500.0, 'Monthly rent payment - February 2024', 'online', 'Sarah Johnson', None, 'RENT-FEB-2024', '2024-02-01', '2024-02-01', '2024-02-01', 0, None, 0, 'On-time payment', None)
        ]
        
        cursor.executemany("""
            INSERT OR IGNORE INTO financial_transactions 
            (transaction_number, property_id, transaction_type, category, amount, description, 
             payment_method, vendor, invoice_number, reference_number, transaction_date, 
             due_date, paid_date, is_recurring, recurring_frequency, tax_deductible, notes, receipt_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_transactions)
        
        conn.commit()
        
        # Verify tables were created
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name = 'properties' OR name = 'tenants' OR name = 'leases' OR name = 'maintenance_requests' OR name = 'financial_transactions' OR name = 'property_documents' OR name = 'rent_payments')")
        tables = cursor.fetchall()
        
        print(f"✅ Successfully created {len(tables)} property management tables:")
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
                count = cursor.fetchone()[0]
                print(f"   - {table[0]}: {count} records")
            except Exception as e:
                print(f"   - {table[0]}: table created (count error: {e})")
        
        print(f"\n🎯 Property management database setup complete!")
        print(f"   Database: {db_path}")
        print(f"   Tables: Properties, Tenants, Leases, Maintenance, Financial Transactions")
        print(f"   Sample data: Loaded for testing")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up property management database: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()


def main():
    """Main function to run database migration"""
    
    # Get the database path
    db_path = os.path.join(os.getcwd(), "reims.db")
    
    print("🏗️  REIMS Property Management Database Migration")
    print("=" * 50)
    print(f"Target database: {db_path}")
    print(f"Migration started: {datetime.now()}")
    print()
    
    # Create tables
    success = create_property_tables(db_path)
    
    if success:
        print("\n✅ Migration completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Start the REIMS backend server")
        print("   2. Access property management at /api/property/")
        print("   3. View analytics at frontend property management tab")
    else:
        print("\n❌ Migration failed!")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())