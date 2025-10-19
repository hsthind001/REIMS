#!/usr/bin/env python3
"""
Quick fix script for stuck documents
Updates documents that have been processed but still show as 'queued'
"""

import sqlite3
from datetime import datetime

def update_stuck_documents():
    """Update documents that have been processed but status not updated"""
    try:
        conn = sqlite3.connect('reims.db')
        cursor = conn.cursor()
        
        print("=== UPDATING STUCK DOCUMENTS ===")
        print()
        
        # Find documents that have extracted data but are still marked as queued
        cursor.execute("""
            SELECT d.document_id, d.original_filename, d.status
            FROM documents d
            WHERE d.status = 'queued'
            AND EXISTS (
                SELECT 1 FROM extracted_data ed 
                WHERE ed.document_id = d.document_id
            )
        """)
        
        stuck_docs = cursor.fetchall()
        
        print(f"Found {len(stuck_docs)} stuck documents:")
        
        for doc_id, filename, status in stuck_docs:
            print(f"  {filename} - Current status: {status}")
        
        if stuck_docs:
            # Update stuck documents to completed
            cursor.execute("""
                UPDATE documents 
                SET status = 'completed' 
                WHERE document_id IN (
                    SELECT DISTINCT d.document_id 
                    FROM documents d
                    WHERE d.status = 'queued'
                    AND EXISTS (
                        SELECT 1 FROM extracted_data ed 
                        WHERE ed.document_id = d.document_id
                    )
                )
            """)
            
            affected = cursor.rowcount
            print(f"\n✅ Updated {affected} stuck documents to 'completed'")
            
            # Also update processing jobs
            cursor.execute("""
                UPDATE processing_jobs 
                SET status = 'completed', completed_at = datetime('now')
                WHERE document_id IN (
                    SELECT DISTINCT d.document_id 
                    FROM documents d
                    WHERE d.status = 'completed'
                    AND EXISTS (
                        SELECT 1 FROM extracted_data ed 
                        WHERE ed.document_id = d.document_id
                    )
                )
                AND status = 'queued'
            """)
            
            jobs_updated = cursor.rowcount
            print(f"✅ Updated {jobs_updated} processing jobs to 'completed'")
        else:
            print("No stuck documents found.")
        
        # Show summary
        cursor.execute("SELECT status, COUNT(*) FROM documents GROUP BY status")
        status_summary = cursor.fetchall()
        
        print("\n📊 Document Status Summary:")
        for status, count in status_summary:
            print(f"  {status}: {count}")
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating stuck documents: {e}")
        return False

if __name__ == "__main__":
    success = update_stuck_documents()
    if success:
        print("\n🎉 Stuck documents update completed!")
    else:
        print("\n❌ Failed to update stuck documents!")

