"""Supabase Storage helper for file uploads"""
from supabase import create_client, Client
from typing import BinaryIO, Optional
import os
from datetime import datetime
import hashlib

class SupabaseStorageClient:
    """Helper class for Supabase Storage operations"""
    
    def __init__(self):
        self.supabase_url = (os.getenv("SUPABASE_URL") or "").strip()
        # SERVICE_ROLE_KEY is required for storage uploads (bypasses RLS)
        # ANON_KEY will fail with "new row violates row-level security policy"
        self.supabase_key = (os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY") or "").strip()
        
        if not os.getenv("SUPABASE_SERVICE_ROLE_KEY"):
            print("⚠️  WARNING: SUPABASE_SERVICE_ROLE_KEY not set! File uploads will fail due to RLS.")
            print("   Get it from: Supabase Dashboard → Settings → API → service_role key")
            print("   Add to .env: SUPABASE_SERVICE_ROLE_KEY=your_key_here")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in environment")
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        self.bucket_name = "session-materials"
    
    async def ensure_bucket_exists(self):
        """Bucket 'session-materials' should be created manually in Supabase Dashboard"""
        # Bucket already exists in Supabase, no need to create
        pass
    
    def _generate_unique_filename(self, original_filename: str, session_id: int) -> str:
        """Generate unique filename to avoid collisions"""
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        # Create hash from original filename + timestamp
        hash_input = f"{original_filename}{timestamp}".encode()
        file_hash = hashlib.md5(hash_input).hexdigest()[:8]
        
        # Extract extension
        ext = ""
        if "." in original_filename:
            ext = original_filename.rsplit(".", 1)[1]
            original_name = original_filename.rsplit(".", 1)[0]
        else:
            original_name = original_filename
        
        # Format: session_{id}/{timestamp}_{hash}_{name}.{ext}
        safe_name = original_name.replace(" ", "_")[:50]  # Limit length
        unique_name = f"{timestamp}_{file_hash}_{safe_name}"
        if ext:
            unique_name += f".{ext}"
        
        return f"session_{session_id}/{unique_name}"
    
    async def upload_file(
        self,
        file_data: bytes,
        filename: str,
        session_id: int,
        content_type: str = "application/octet-stream"
    ) -> str:
        """
        Upload file to Supabase Storage
        
        Args:
            file_data: Binary file data
            filename: Original filename
            session_id: Session ID for organizing files
            content_type: MIME type of the file
        
        Returns:
            Public URL of uploaded file
        """
        await self.ensure_bucket_exists()
        
        # Generate unique path
        storage_path = self._generate_unique_filename(filename, session_id)
        
        try:
            # Upload to Supabase Storage
            print(f"🔄 Uploading to Supabase Storage: {storage_path}")
            response = self.client.storage.from_(self.bucket_name).upload(
                path=storage_path,
                file=file_data,
                file_options={"content-type": content_type, "upsert": "false"}
            )
            
            print(f"✅ Upload response: {response}")
            
            # Get public URL
            public_url = self.client.storage.from_(self.bucket_name).get_public_url(storage_path)
            
            print(f"🔗 Public URL: {public_url}")
            
            return public_url
            
        except Exception as e:
            print(f"❌ Upload error: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Failed to upload file to Supabase Storage: {str(e)}")
    
    async def delete_file(self, file_url: str) -> bool:
        """
        Delete file from Supabase Storage
        
        Args:
            file_url: Full public URL of the file
        
        Returns:
            True if successful
        """
        try:
            # Extract storage path from URL
            # URL format: https://{project}.supabase.co/storage/v1/object/public/{bucket}/{path}
            url_parts = file_url.split(f"/storage/v1/object/public/{self.bucket_name}/")
            if len(url_parts) < 2:
                raise ValueError(f"Invalid Supabase Storage URL: {file_url}")
            
            storage_path = url_parts[1]
            
            # Delete from storage
            self.client.storage.from_(self.bucket_name).remove([storage_path])
            
            return True
            
        except Exception as e:
            print(f"Failed to delete file from Supabase Storage: {str(e)}")
            return False

# Singleton instance
_storage_client: Optional[SupabaseStorageClient] = None

def get_storage_client() -> SupabaseStorageClient:
    """Get or create singleton storage client"""
    global _storage_client
    if _storage_client is None:
        _storage_client = SupabaseStorageClient()
    return _storage_client
