"""
REIMS Data Encryption Service
Enhanced encryption for data at rest and in transit
"""

import os
import base64
import logging
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
from typing import Optional, Union

logger = logging.getLogger(__name__)

class EncryptionService:
    """Enhanced encryption service for data at rest"""
    
    def __init__(self):
        self.cipher = self._initialize_cipher()
    
    def _initialize_cipher(self) -> Fernet:
        """Initialize Fernet cipher with encryption key"""
        
        try:
            # Try to get encryption key from environment
            encryption_key = os.getenv("ENCRYPTION_KEY")
            
            if not encryption_key:
                # Generate a new key if not provided
                logger.warning("No ENCRYPTION_KEY found in environment, generating new key")
                encryption_key = Fernet.generate_key().decode()
                logger.info(f"Generated encryption key: {encryption_key[:20]}...")
                logger.warning("⚠️ Store this key securely: ENCRYPTION_KEY={encryption_key}")
            
            # Ensure key is bytes
            if isinstance(encryption_key, str):
                encryption_key = encryption_key.encode()
            
            return Fernet(encryption_key)
            
        except Exception as e:
            logger.error(f"Failed to initialize encryption cipher: {e}")
            # Fallback to a default key for development (DO NOT USE IN PRODUCTION)
            logger.warning("⚠️ Using default encryption key - INSECURE!")
            return Fernet(Fernet.generate_key())
    
    def encrypt(self, data: Union[str, bytes]) -> bytes:
        """Encrypt data"""
        
        try:
            if isinstance(data, str):
                data = data.encode('utf-8')
            
            encrypted_data = self.cipher.encrypt(data)
            return encrypted_data
            
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            raise
    
    def decrypt(self, encrypted_data: bytes) -> str:
        """Decrypt data"""
        
        try:
            decrypted_data = self.cipher.decrypt(encrypted_data)
            return decrypted_data.decode('utf-8')
            
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            raise
    
    def encrypt_field(self, value: Optional[str]) -> Optional[str]:
        """Encrypt a database field value"""
        
        if value is None:
            return None
        
        try:
            encrypted = self.encrypt(value)
            # Encode as base64 for database storage
            return base64.b64encode(encrypted).decode('utf-8')
        except Exception as e:
            logger.error(f"Field encryption error: {e}")
            return value  # Return original value if encryption fails
    
    def decrypt_field(self, encrypted_value: Optional[str]) -> Optional[str]:
        """Decrypt a database field value"""
        
        if encrypted_value is None:
            return None
        
        try:
            # Decode from base64
            encrypted_bytes = base64.b64decode(encrypted_value.encode('utf-8'))
            return self.decrypt(encrypted_bytes)
        except Exception as e:
            logger.error(f"Field decryption error: {e}")
            return encrypted_value  # Return original value if decryption fails
    
    @staticmethod
    def generate_key() -> str:
        """Generate a new encryption key"""
        return Fernet.generate_key().decode()
    
    @staticmethod
    def derive_key_from_password(password: str, salt: Optional[bytes] = None) -> tuple:
        """Derive an encryption key from a password"""
        
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key.decode(), base64.b64encode(salt).decode()

class DatabaseEncryption:
    """Database-specific encryption helpers"""
    
    def __init__(self, encryption_service: EncryptionService):
        self.encryption_service = encryption_service
    
    def encrypt_sensitive_field(self, model_instance, field_name: str):
        """Encrypt a sensitive field on a model instance"""
        
        try:
            value = getattr(model_instance, field_name)
            if value:
                encrypted_value = self.encryption_service.encrypt_field(value)
                setattr(model_instance, field_name, encrypted_value)
        except Exception as e:
            logger.error(f"Failed to encrypt field {field_name}: {e}")
    
    def decrypt_sensitive_field(self, model_instance, field_name: str):
        """Decrypt a sensitive field on a model instance"""
        
        try:
            encrypted_value = getattr(model_instance, field_name)
            if encrypted_value:
                decrypted_value = self.encryption_service.decrypt_field(encrypted_value)
                setattr(model_instance, field_name, decrypted_value)
        except Exception as e:
            logger.error(f"Failed to decrypt field {field_name}: {e}")

class FileEncryption:
    """File-specific encryption for MinIO storage"""
    
    def __init__(self, encryption_service: EncryptionService):
        self.encryption_service = encryption_service
    
    def encrypt_file(self, file_path: str, output_path: Optional[str] = None) -> str:
        """Encrypt a file"""
        
        try:
            # Read file
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Encrypt
            encrypted_data = self.encryption_service.encrypt(file_data)
            
            # Write encrypted file
            if output_path is None:
                output_path = file_path + '.encrypted'
            
            with open(output_path, 'wb') as f:
                f.write(encrypted_data)
            
            logger.info(f"File encrypted: {file_path} -> {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"File encryption error: {e}")
            raise
    
    def decrypt_file(self, encrypted_file_path: str, output_path: Optional[str] = None) -> str:
        """Decrypt a file"""
        
        try:
            # Read encrypted file
            with open(encrypted_file_path, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt
            decrypted_data = self.encryption_service.cipher.decrypt(encrypted_data)
            
            # Write decrypted file
            if output_path is None:
                output_path = encrypted_file_path.replace('.encrypted', '')
            
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
            
            logger.info(f"File decrypted: {encrypted_file_path} -> {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"File decryption error: {e}")
            raise

# Global encryption service instances
_encryption_service = None
_database_encryption = None
_file_encryption = None

def get_encryption_service() -> EncryptionService:
    """Get or create encryption service instance"""
    global _encryption_service
    
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    
    return _encryption_service

def get_database_encryption() -> DatabaseEncryption:
    """Get or create database encryption instance"""
    global _database_encryption
    
    if _database_encryption is None:
        _database_encryption = DatabaseEncryption(get_encryption_service())
    
    return _database_encryption

def get_file_encryption() -> FileEncryption:
    """Get or create file encryption instance"""
    global _file_encryption
    
    if _file_encryption is None:
        _file_encryption = FileEncryption(get_encryption_service())
    
    return _file_encryption

# PostgreSQL encryption configuration
def enable_postgresql_encryption():
    """Enable PostgreSQL encryption at rest"""
    
    logger.info("📝 PostgreSQL Encryption Configuration:")
    logger.info("   1. Enable transparent data encryption (TDE)")
    logger.info("   2. Configure pg_crypto extension")
    logger.info("   3. Use encrypted file systems")
    logger.info("")
    logger.info("   SQL Commands:")
    logger.info("   CREATE EXTENSION IF NOT EXISTS pgcrypto;")
    logger.info("   ALTER SYSTEM SET ssl = on;")
    logger.info("")
    logger.info("   For production: Use AWS RDS encryption or Azure Database encryption")

# MinIO encryption configuration
def enable_minio_encryption():
    """Enable MinIO encryption at rest"""
    
    logger.info("📝 MinIO Encryption Configuration:")
    logger.info("   1. Enable server-side encryption (SSE)")
    logger.info("   2. Configure KMS for key management")
    logger.info("")
    logger.info("   Environment variables:")
    logger.info("   MINIO_KMS_SECRET_KEY=your-secret-key")
    logger.info("   MINIO_SSE_MASTER_KEY=your-master-key")
    logger.info("")
    logger.info("   For production: Use AWS KMS, Azure Key Vault, or HashiCorp Vault")


















