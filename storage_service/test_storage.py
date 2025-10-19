import asyncio
import os
from client import minio_client
from operations import storage_ops

async def test_storage():
    """Test basic storage operations"""
    try:
        # Test bucket initialization
        print("1. Testing bucket initialization...")
        assert minio_client.client.bucket_exists(minio_client.bucket_name), "Bucket should exist"
        print("✓ Bucket initialization successful")

        # Create a test file
        print("\n2. Creating test file...")
        test_file_path = "test_document.txt"
        with open(test_file_path, "w") as f:
            f.write("This is a test document for REIMS storage service.")

        # Test file upload
        print("\n3. Testing file upload...")
        class MockUploadFile:
            async def read(self):
                with open(test_file_path, "rb") as f:
                    return f.read()
            
            async def close(self):
                pass
            
            @property
            def filename(self):
                return "test_document.txt"
            
            @property
            def content_type(self):
                return "text/plain"

        mock_file = MockUploadFile()
        metadata = {"test_key": "test_value"}
        
        result = await storage_ops.store_document(mock_file, metadata)
        print("Upload result:", result)
        assert result["filename"] == "test_document.txt", "Filename should match"
        document_id = result["document_id"]
        
        # Test metadata retrieval
        print("\n4. Testing metadata retrieval...")
        metadata = storage_ops.get_document_metadata(document_id)
        print("Retrieved metadata:", metadata)
        assert metadata is not None, "Metadata should exist"
        assert metadata["document_id"] == document_id, "Document ID should match"
        
        # Test document deletion
        print("\n5. Testing document deletion...")
        deleted = storage_ops.delete_document(document_id)
        assert deleted, "Document should be deleted"
        print("✓ Document deleted successfully")
        
        # Clean up test file
        os.remove(test_file_path)
        print("\nAll tests completed successfully!")
        
    except Exception as e:
        print(f"Test failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(test_storage())