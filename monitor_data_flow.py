#!/usr/bin/env python3
"""
Real-time monitoring for MinIO to Database data flow
Shows live status of uploads and data consistency
"""

import sqlite3
import time
import json
from datetime import datetime, timedelta
from pathlib import Path

class DataFlowMonitor:
    def __init__(self):
        self.db_path = "reims.db"
        self.last_check = datetime.now()
        
    def get_recent_uploads(self, minutes=10):
        """Get uploads from the last N minutes"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            since_time = datetime.now() - timedelta(minutes=minutes)
            
            cursor.execute("""
                SELECT document_id, original_filename, property_id, 
                       storage_type, minio_bucket, minio_object_name, 
                       upload_timestamp, minio_upload_timestamp
                FROM documents 
                WHERE upload_timestamp > ?
                ORDER BY upload_timestamp DESC
            """, (since_time,))
            
            recent_uploads = cursor.fetchall()
            conn.close()
            
            return recent_uploads
            
        except Exception as e:
            print(f"❌ Database error: {e}")
            return []
    
    def check_minio_objects(self):
        """Get current MinIO objects"""
        try:
            from minio import Minio
            client = Minio("localhost:9000", "minioadmin", "minioadmin", secure=False)
            objects = list(client.list_objects("reims-documents", recursive=True))
            return {obj.object_name: obj for obj in objects}
        except Exception as e:
            print(f"❌ MinIO error: {e}")
            return {}
    
    def analyze_consistency(self):
        """Analyze current data consistency"""
        # Get all database MinIO records
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT document_id, original_filename, property_id, 
                       storage_type, minio_object_name, upload_timestamp
                FROM documents 
                WHERE storage_type IN ('minio', 'local_and_minio')
                ORDER BY upload_timestamp DESC
            """)
            
            db_records = cursor.fetchall()
            conn.close()
            
            # Get MinIO objects
            minio_objects = self.check_minio_objects()
            
            # Analyze
            db_object_names = {record[4] for record in db_records if record[4]}
            minio_object_names = set(minio_objects.keys())
            
            matching = db_object_names.intersection(minio_object_names)
            db_only = db_object_names - minio_object_names
            minio_only = minio_object_names - db_object_names
            
            return {
                'db_records': len(db_records),
                'minio_objects': len(minio_objects),
                'matching': len(matching),
                'db_only': len(db_only),
                'minio_only': len(minio_only),
                'consistency_rate': (len(matching) / max(len(db_object_names.union(minio_object_names)), 1)) * 100
            }
            
        except Exception as e:
            print(f"❌ Analysis error: {e}")
            return None
    
    def show_status(self):
        """Show current status"""
        print(f"\n🔍 Data Flow Status - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Recent uploads
        recent = self.get_recent_uploads(60)  # Last hour
        print(f"📊 Recent uploads (last 60 minutes): {len(recent)}")
        
        if recent:
            print("   Recent files:")
            for record in recent[:5]:  # Show latest 5
                doc_id, filename, prop_id, storage_type, bucket, obj_name, upload_time, minio_time = record
                status_icon = "✅" if storage_type in ['minio', 'local_and_minio'] else "⚠️"
                print(f"   {status_icon} {filename} (Property: {prop_id})")
                print(f"      Storage: {storage_type}, Upload: {upload_time}")
        
        # Consistency analysis
        analysis = self.analyze_consistency()
        if analysis:
            print(f"\n🎯 Data Consistency:")
            print(f"   Database records: {analysis['db_records']}")
            print(f"   MinIO objects: {analysis['minio_objects']}")
            print(f"   Matching: {analysis['matching']}")
            print(f"   Consistency rate: {analysis['consistency_rate']:.1f}%")
            
            if analysis['consistency_rate'] >= 90:
                print("   Status: ✅ EXCELLENT")
            elif analysis['consistency_rate'] >= 70:
                print("   Status: 🟡 GOOD")
            else:
                print("   Status: ❌ NEEDS ATTENTION")
        
        return analysis
    
    def monitor_loop(self, check_interval=30):
        """Run continuous monitoring"""
        print("🚀 Starting continuous data flow monitoring...")
        print(f"⏱️ Check interval: {check_interval} seconds")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                self.show_status()
                print(f"\n⏳ Next check in {check_interval} seconds...")
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped by user")

def show_troubleshooting_guide():
    """Show troubleshooting guide for data flow issues"""
    print("\n" + "=" * 60)
    print("🔧 TROUBLESHOOTING GUIDE: MinIO to Database Data Flow")
    print("=" * 60)
    
    print("\n📋 Common Issues and Solutions:")
    
    print("\n1. ❌ Files uploaded via frontend not appearing in database:")
    print("   Causes:")
    print("   • Backend not running with database integration")
    print("   • Database connection issues")
    print("   • Upload endpoint not calling database storage")
    print("   Solutions:")
    print("   • Restart backend: python simple_backend.py")
    print("   • Check backend logs for database errors")
    print("   • Verify database schema: python verify_database.py")
    
    print("\n2. ❌ Files in MinIO but not in database:")
    print("   Causes:")
    print("   • Files uploaded before database integration")
    print("   • Database write failures during upload")
    print("   • Manual MinIO uploads outside the system")
    print("   Solutions:")
    print("   • Check upload logs for database errors")
    print("   • Re-upload files through frontend")
    print("   • Create database migration script")
    
    print("\n3. ❌ Files in database but not in MinIO:")
    print("   Causes:")
    print("   • MinIO upload failures")
    print("   • MinIO service was down during upload")
    print("   • Test records created without actual files")
    print("   Solutions:")
    print("   • Check MinIO service status")
    print("   • Re-upload affected files")
    print("   • Clean up orphaned database records")
    
    print("\n4. ✅ How to ensure data reaches database from MinIO uploads:")
    print("   1. Start backend with: python simple_backend.py")
    print("   2. Verify backend shows: '✅ Database integration available'")
    print("   3. Upload via frontend at: http://localhost:5173")
    print("   4. Check upload response shows: 'Database storage: stored_in_database'")
    print("   5. Monitor with: python verify_data_flow.py")
    
    print("\n📊 Monitoring Commands:")
    print("   • python verify_data_flow.py - Check current consistency")
    print("   • python verify_database.py - Check database schema")
    print("   • python test_minio_connection.py - Test MinIO connection")

def main():
    """Main function with options"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "monitor":
        # Continuous monitoring mode
        monitor = DataFlowMonitor()
        monitor.monitor_loop()
    elif len(sys.argv) > 1 and sys.argv[1] == "help":
        show_troubleshooting_guide()
    else:
        # Single check mode
        monitor = DataFlowMonitor()
        analysis = monitor.show_status()
        
        print("\n💡 Usage:")
        print("   python monitor_data_flow.py         - Single status check")
        print("   python monitor_data_flow.py monitor - Continuous monitoring")
        print("   python monitor_data_flow.py help    - Show troubleshooting guide")
        
        if analysis and analysis['consistency_rate'] < 70:
            print("\n⚠️ Data consistency issues detected!")
            print("   Run: python monitor_data_flow.py help")

if __name__ == "__main__":
    main()