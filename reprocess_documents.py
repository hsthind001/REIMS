#!/usr/bin/env python3
"""
Reprocess existing documents to extract data
For documents already in database but without extracted data
"""

import os
import sys
import uuid
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from minio import Minio
import PyPDF2
import pandas as pd

# MinIO configuration
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"

# Database configuration
DB_PATH = "reims.db"

# Temporary download directory
TEMP_DIR = "temp_reprocessing"
os.makedirs(TEMP_DIR, exist_ok=True)

def extract_pdf_data(file_path, document_id):
    """Extract data from PDF file"""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)
            
            # Extract text from all pages
            full_text = ""
            for page in pdf_reader.pages:
                full_text += page.extract_text() + "\n"
            
            word_count = len(full_text.split())
            
            extracted_data = {
                'document_type': 'pdf',
                'page_count': num_pages,
                'word_count': word_count,
                'text_preview': full_text[:500],
                'full_text': full_text,
                'file_name': Path(file_path).name
            }
            
            return {
                'status': 'success',
                'data': extracted_data,
                'metrics': {
                    'pages': num_pages,
                    'words': word_count
                }
            }
            
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def reprocess_documents():
    """Reprocess documents that don't have extracted data"""
    print("\n╔══════════════════════════════════════════════════════════════════════╗")
    print("║          🔄 REPROCESSING DOCUMENTS FOR DATA EXTRACTION 🔄           ║")
    print("╚══════════════════════════════════════════════════════════════════════╝\n")
    
    # Connect to database and MinIO
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    minio_client = Minio(
        MINIO_ENDPOINT,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )
    
    # Find documents without extracted data
    cursor.execute("""
        SELECT d.document_id, d.original_filename, d.minio_bucket, d.minio_object_name, d.content_type
        FROM documents d
        LEFT JOIN extracted_data e ON d.document_id = e.document_id
        WHERE e.id IS NULL
    """)
    
    documents = cursor.fetchall()
    
    if not documents:
        print("✅ All documents have been processed!\n")
        conn.close()
        return
    
    print(f"📋 Found {len(documents)} documents to reprocess\n")
    print("="*70 + "\n")
    
    processed = 0
    failed = 0
    
    for doc_id, filename, bucket, object_name, content_type in documents:
        print(f"📄 Processing: {filename}")
        print(f"   Document ID: {doc_id}")
        
        try:
            # Download file from MinIO
            local_path = os.path.join(TEMP_DIR, Path(object_name).name)
            minio_client.fget_object(bucket, object_name, local_path)
            print(f"   ✓ Downloaded from MinIO")
            
            # Extract data based on content type
            if 'pdf' in content_type.lower():
                result = extract_pdf_data(local_path, doc_id)
            else:
                result = {'status': 'unsupported', 'message': f'Content type {content_type} not supported'}
            
            if result['status'] == 'success':
                # Store extracted data
                data = result['data']
                metrics = result.get('metrics', {})
                
                cursor.execute("""
                    INSERT INTO extracted_data (
                        id, document_id, data_type, extracted_content,
                        page_count, word_count, extraction_timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(uuid.uuid4()),
                    doc_id,
                    data.get('document_type', 'pdf'),
                    json.dumps(data),
                    metrics.get('pages'),
                    metrics.get('words'),
                    datetime.utcnow()
                ))
                
                # Update processing job
                cursor.execute("""
                    UPDATE processing_jobs 
                    SET status = 'completed',
                        completed_at = ?,
                        processing_result = ?
                    WHERE document_id = ?
                """, (
                    datetime.utcnow(),
                    json.dumps({'extraction_metrics': metrics}),
                    doc_id
                ))
                
                # Update document status
                cursor.execute("""
                    UPDATE documents 
                    SET status = 'processed'
                    WHERE document_id = ?
                """, (doc_id,))
                
                conn.commit()
                print(f"   ✓ Extracted {metrics.get('pages', 0)} pages, {metrics.get('words', 0)} words")
                print(f"   ✓ Data stored in database\n")
                processed += 1
            else:
                print(f"   ❌ Extraction failed: {result.get('message', 'Unknown error')}\n")
                failed += 1
                
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
            failed += 1
            conn.rollback()
    
    # Verification
    print("="*70)
    print("📊 VERIFICATION")
    print("="*70 + "\n")
    
    cursor.execute("SELECT COUNT(*) FROM documents")
    doc_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM extracted_data")
    extracted_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM processing_jobs WHERE status = 'completed'")
    completed_jobs = cursor.fetchone()[0]
    
    print(f"  Documents in database: {doc_count}")
    print(f"  Extracted data records: {extracted_count}")
    print(f"  Completed processing jobs: {completed_jobs}")
    
    print("\n" + "="*70)
    print("✅ REPROCESSING COMPLETE")
    print("="*70)
    print(f"\n  Successfully processed: {processed}/{len(documents)}")
    print(f"  Failed: {failed}/{len(documents)}\n")
    
    conn.close()
    
    # Cleanup
    import shutil
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)

if __name__ == "__main__":
    reprocess_documents()

