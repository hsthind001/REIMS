from minio import Minio
from minio.error import S3Error
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class MinioClient:
    def __init__(self):
        try:
            self.client = Minio(
                endpoint=os.getenv("MINIO_ENDPOINT", "localhost:9000"),
                access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
                secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
                secure=os.getenv("MINIO_USE_SSL", "false").lower() == "true"
            )
            self.bucket_name = os.getenv("MINIO_BUCKET_NAME", "reims-documents")
            self._ensure_bucket_exists()
            self.available = True
        except Exception as e:
            print(f"Warning: Failed to connect to MinIO: {e}")
            print("Storage service will run in offline mode")
            self.client = None
            self.bucket_name = None
            self.available = False

    def _ensure_bucket_exists(self):
        """Ensure the configured bucket exists, create if it doesn't"""
        try:
            if self.client and not self.client.bucket_exists(self.bucket_name):
                self.client.make_bucket(self.bucket_name)
        except Exception as e:
            print(f"Warning: Failed to initialize MinIO bucket: {str(e)}")

    def get_presigned_url(self, object_name: str, expires: int = 3600) -> str:
        """Generate a presigned URL for object download"""
        if not self.available:
            raise Exception("MinIO service not available")
        try:
            from datetime import timedelta
            return self.client.presigned_get_object(
                self.bucket_name, object_name, expires=timedelta(seconds=expires)
            )
        except S3Error as e:
            raise Exception(f"Failed to generate presigned URL: {str(e)}")

    def is_available(self):
        """Check if MinIO client is available"""
        return self.available

# Create a singleton instance
minio_client = MinioClient()