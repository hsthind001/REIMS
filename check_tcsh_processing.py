import sqlite3

try:
    conn = sqlite3.connect('reims.db', timeout=5)
    cursor = conn.cursor()
    
    # Check TCSH documents status
    cursor.execute('SELECT document_id, original_filename, status FROM documents WHERE original_filename LIKE "%TCSH%"')
    docs = cursor.fetchall()
    
    print('TCSH Documents Status:')
    for doc in docs:
        print(f'  {doc[1]} - {doc[2]}')
    
    # Check processing jobs
    print('\nProcessing Jobs for TCSH Documents:')
    for doc in docs:
        cursor.execute('SELECT job_id, status, created_at, completed_at FROM processing_jobs WHERE document_id = ?', (doc[0],))
        job = cursor.fetchone()
        if job:
            print(f'  {doc[1]} - Job: {job[1]}, Created: {job[2]}, Completed: {job[3]}')
    
    # Check extracted data
    print('\nTCSH Documents with Extracted Data:')
    for doc in docs:
        cursor.execute('SELECT COUNT(*) FROM extracted_data WHERE document_id = ?', (doc[0],))
        count = cursor.fetchone()[0]
        if count > 0:
            print(f'  {doc[1]} - {count} data records')
        else:
            print(f'  {doc[1]} - No extracted data')
    
    conn.close()
    
except Exception as e:
    print(f'Error: {e}')


