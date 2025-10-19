#!/usr/bin/env python3
"""
Process MinIO Files and Extract Data to Database
Retroactive processing for files uploaded to MinIO without database records
"""

import os
import sys
import uuid
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from minio import Minio
import io

# PDF processing
try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️  PyPDF2 not available - PDF processing will be limited")

# Excel processing
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("⚠️  pandas not available - Excel/CSV processing will be limited")

# MinIO configuration
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"

# Database configuration
DB_PATH = "reims.db"

# Temporary download directory
TEMP_DIR = "temp_processing"
os.makedirs(TEMP_DIR, exist_ok=True)

class MinIOFileProcessor:
    def __init__(self):
        self.minio_client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=False
        )
        self.db_conn = sqlite3.connect(DB_PATH)
        self.db_cursor = self.db_conn.cursor()
        
    def scan_minio_files(self):
        """Scan all MinIO buckets for uploaded files"""
        print("\n" + "="*70)
        print("📦 SCANNING MINIO BUCKETS")
        print("="*70 + "\n")
        
        all_files = []
        buckets = self.minio_client.list_buckets()
        
        for bucket in buckets:
            objects = list(self.minio_client.list_objects(bucket.name, recursive=True))
            
            if objects:
                print(f"📂 Bucket: {bucket.name}")
                for obj in objects:
                    # Skip test/temporary files
                    if 'persistence_test' in obj.object_name or 'test' in obj.object_name.lower():
                        continue
                        
                    file_info = {
                        'bucket': bucket.name,
                        'object_name': obj.object_name,
                        'size': obj.size,
                        'last_modified': obj.last_modified,
                        'etag': obj.etag
                    }
                    all_files.append(file_info)
                    print(f"  ✓ {obj.object_name} ({obj.size} bytes)")
                print()
        
        print(f"📊 Total files found: {len(all_files)}\n")
        return all_files
    
    def create_database_records(self, file_info):
        """Create database records for a file"""
        document_id = str(uuid.uuid4())
        
        # Determine content type from file extension
        file_ext = Path(file_info['object_name']).suffix.lower()
        content_type_map = {
            '.pdf': 'application/pdf',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.xls': 'application/vnd.ms-excel',
            '.csv': 'text/csv'
        }
        content_type = content_type_map.get(file_ext, 'application/octet-stream')
        
        # Extract property info from path (e.g., properties/1/)
        property_id = "1"  # Default
        if 'properties/' in file_info['object_name']:
            parts = file_info['object_name'].split('/')
            if len(parts) > 1:
                property_id = parts[1]
        
        # Create documents record
        try:
            self.db_cursor.execute("""
                INSERT INTO documents (
                    id, document_id, original_filename, stored_filename,
                    property_id, file_size, content_type, file_path,
                    upload_timestamp, status, minio_bucket, minio_object_name,
                    storage_type, minio_upload_timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                document_id,
                Path(file_info['object_name']).name,
                file_info['object_name'],
                property_id,
                file_info['size'],
                content_type,
                file_info['object_name'],
                datetime.utcnow(),
                'uploaded',
                file_info['bucket'],
                file_info['object_name'],
                'minio',
                file_info['last_modified']
            ))
            
            # Create processing job
            job_id = str(uuid.uuid4())
            self.db_cursor.execute("""
                INSERT INTO processing_jobs (
                    id, job_id, document_id, status, created_at
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                job_id,
                document_id,
                'queued',
                datetime.utcnow()
            ))
            
            self.db_conn.commit()
            return document_id, job_id
            
        except Exception as e:
            self.db_conn.rollback()
            print(f"  ❌ Database error: {e}")
            return None, None
    
    def download_and_extract(self, file_info, document_id):
        """Download file from MinIO and extract data"""
        try:
            # Download file
            local_path = os.path.join(TEMP_DIR, Path(file_info['object_name']).name)
            self.minio_client.fget_object(
                file_info['bucket'],
                file_info['object_name'],
                local_path
            )
            
            # Detect file type and extract
            file_ext = Path(file_info['object_name']).suffix.lower()
            
            if file_ext == '.pdf' and PDF_AVAILABLE:
                return self.extract_pdf_data(local_path, document_id)
            elif file_ext in ['.xlsx', '.xls', '.csv'] and PANDAS_AVAILABLE:
                return self.extract_tabular_data(local_path, document_id, file_ext)
            else:
                return {'status': 'unsupported', 'message': f'File type {file_ext} not supported'}
                
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def extract_pdf_data(self, file_path, document_id):
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
                    'text_preview': full_text[:500],  # First 500 chars
                    'full_text': full_text
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
    
    def extract_tabular_data(self, file_path, document_id, file_ext):
        """Extract data from Excel/CSV file"""
        try:
            # Read file based on type
            if file_ext == '.csv':
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            
            # Extract basic metrics
            row_count = len(df)
            column_count = len(df.columns)
            columns = df.columns.tolist()
            
            # Convert to dict for storage
            data_dict = df.to_dict(orient='records')
            
            # Get summary statistics for numeric columns
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            stats = {}
            for col in numeric_cols:
                stats[col] = {
                    'mean': float(df[col].mean()) if not df[col].isna().all() else None,
                    'sum': float(df[col].sum()) if not df[col].isna().all() else None,
                    'min': float(df[col].min()) if not df[col].isna().all() else None,
                    'max': float(df[col].max()) if not df[col].isna().all() else None
                }
            
            extracted_data = {
                'document_type': file_ext[1:],  # Remove dot
                'row_count': row_count,
                'column_count': column_count,
                'columns': columns,
                'data': data_dict[:100],  # First 100 rows
                'statistics': stats,
                'has_numeric_data': len(numeric_cols) > 0
            }
            
            return {
                'status': 'success',
                'data': extracted_data,
                'metrics': {
                    'rows': row_count,
                    'columns': column_count,
                    'numeric_columns': len(numeric_cols)
                }
            }
            
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def store_extracted_data(self, document_id, extraction_result):
        """Store extracted data in database"""
        try:
            if extraction_result['status'] != 'success':
                return False
            
            data = extraction_result['data']
            metrics = extraction_result.get('metrics', {})
            
            # Store in extracted_data table
            self.db_cursor.execute("""
                INSERT INTO extracted_data (
                    id, document_id, data_type, extracted_content,
                    row_count, column_count, page_count, word_count,
                    extraction_timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                str(uuid.uuid4()),
                document_id,
                data.get('document_type', 'unknown'),
                json.dumps(data),
                metrics.get('rows'),
                metrics.get('columns'),
                metrics.get('pages'),
                metrics.get('words'),
                datetime.utcnow()
            ))
            
            # Update processing job status
            self.db_cursor.execute("""
                UPDATE processing_jobs 
                SET status = 'completed',
                    completed_at = ?,
                    result_data = ?
                WHERE document_id = ?
            """, (
                datetime.utcnow(),
                json.dumps({'extraction_metrics': metrics}),
                document_id
            ))
            
            # Update document status
            self.db_cursor.execute("""
                UPDATE documents 
                SET status = 'processed'
                WHERE document_id = ?
            """, (document_id,))
            
            self.db_conn.commit()
            return True
            
        except Exception as e:
            self.db_conn.rollback()
            print(f"  ❌ Error storing data: {e}")
            return False
    
    def process_all_files(self):
        """Main processing workflow"""
        print("\n╔══════════════════════════════════════════════════════════════════════╗")
        print("║          📄 PROCESSING MINIO FILES TO DATABASE 📄                   ║")
        print("╚══════════════════════════════════════════════════════════════════════╝\n")
        
        # Step 1: Scan MinIO
        files = self.scan_minio_files()
        
        if not files:
            print("⚠️  No files found to process")
            return
        
        # Step 2-5: Process each file
        print("="*70)
        print("🔄 PROCESSING FILES")
        print("="*70 + "\n")
        
        processed_count = 0
        failed_count = 0
        
        for i, file_info in enumerate(files, 1):
            print(f"\n📄 Processing file {i}/{len(files)}: {file_info['object_name']}")
            
            # Create database records
            document_id, job_id = self.create_database_records(file_info)
            if not document_id:
                print("  ❌ Failed to create database records")
                failed_count += 1
                continue
            print(f"  ✓ Created database records (doc_id: {document_id[:8]}...)")
            
            # Download and extract
            print("  ⏳ Extracting data...")
            extraction_result = self.download_and_extract(file_info, document_id)
            
            if extraction_result['status'] == 'success':
                print(f"  ✓ Extraction successful")
                print(f"     Metrics: {extraction_result.get('metrics', {})}")
                
                # Store extracted data
                if self.store_extracted_data(document_id, extraction_result):
                    print("  ✓ Data stored in database")
                    processed_count += 1
                else:
                    print("  ❌ Failed to store data")
                    failed_count += 1
            else:
                print(f"  ⚠️  Extraction failed: {extraction_result.get('message', 'Unknown error')}")
                failed_count += 1
        
        # Step 5: Verify
        print("\n" + "="*70)
        print("📊 VERIFICATION")
        print("="*70 + "\n")
        
        self.db_cursor.execute("SELECT COUNT(*) FROM documents")
        doc_count = self.db_cursor.fetchone()[0]
        
        self.db_cursor.execute("SELECT COUNT(*) FROM extracted_data")
        extracted_count = self.db_cursor.fetchone()[0]
        
        self.db_cursor.execute("SELECT COUNT(*) FROM processing_jobs WHERE status = 'completed'")
        completed_jobs = self.db_cursor.fetchone()[0]
        
        print(f"  Documents in database: {doc_count}")
        print(f"  Extracted data records: {extracted_count}")
        print(f"  Completed processing jobs: {completed_jobs}")
        
        print("\n" + "="*70)
        print("✅ PROCESSING COMPLETE")
        print("="*70)
        print(f"\n  Successfully processed: {processed_count}/{len(files)}")
        print(f"  Failed: {failed_count}/{len(files)}\n")
        
    def close(self):
        """Cleanup resources"""
        self.db_conn.close()
        # Clean up temp files
        import shutil
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)


if __name__ == "__main__":
    processor = MinIOFileProcessor()
    try:
        processor.process_all_files()
    finally:
        processor.close()

