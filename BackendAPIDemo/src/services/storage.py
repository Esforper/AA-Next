# ================================
# src/services/storage.py - File Management
# ================================

"""
Storage Service - Dosya yönetimi
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
import shutil
import uuid

from ..models.storage import StorageFile, FileType
from ..config import settings

class StorageService:
    """File storage service"""
    
    def __init__(self):
        self.base_path = Path(settings.storage_base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    async def save_file(self, 
                       file_content: bytes, 
                       filename: str,
                       file_type: FileType = FileType.OTHER,
                       public: bool = False) -> Optional[StorageFile]:
        """Dosya kaydet"""
        try:
            # Unique filename oluştur
            file_id = str(uuid.uuid4())
            file_extension = Path(filename).suffix
            stored_filename = f"{file_id}{file_extension}"
            stored_path = self.base_path / stored_filename
            
            # Dosyayı kaydet
            with open(stored_path, 'wb') as f:
                f.write(file_content)
            
            # StorageFile oluştur
            storage_file = StorageFile(
                file_id=file_id,
                original_name=filename,
                stored_path=str(stored_path),
                file_size=len(file_content),
                mime_type=self._get_mime_type(filename),
                file_type=file_type,
                public=public,
                provider="local"
            )
            
            print(f"✅ File saved: {filename} -> {stored_filename}")
            return storage_file
            
        except Exception as e:
            print(f"❌ Save file error: {e}")
            return None
    
    async def get_file(self, file_id: str) -> Optional[bytes]:
        """Dosya al"""
        try:
            # Dosyayı bul
            for file_path in self.base_path.glob(f"{file_id}.*"):
                with open(file_path, 'rb') as f:
                    return f.read()
            
            print(f"❌ File not found: {file_id}")
            return None
            
        except Exception as e:
            print(f"❌ Get file error: {e}")
            return None
    
    async def delete_file(self, file_id: str) -> bool:
        """Dosya sil"""
        try:
            # Dosyayı bul ve sil
            for file_path in self.base_path.glob(f"{file_id}.*"):
                file_path.unlink()
                print(f"✅ File deleted: {file_path.name}")
                return True
            
            print(f"❌ File not found for deletion: {file_id}")
            return False
            
        except Exception as e:
            print(f"❌ Delete file error: {e}")
            return False
    
    async def list_files(self, file_type: Optional[FileType] = None) -> List[StorageFile]:
        """Dosyaları listele"""
        try:
            files = []
            for file_path in self.base_path.iterdir():
                if file_path.is_file():
                    stat = file_path.stat()
                    
                    # File type check
                    detected_type = self._detect_file_type(file_path.name)
                    if file_type and detected_type != file_type:
                        continue
                    
                    storage_file = StorageFile(
                        file_id=file_path.stem,
                        original_name=file_path.name,
                        stored_path=str(file_path),
                        file_size=stat.st_size,
                        mime_type=self._get_mime_type(file_path.name),
                        file_type=detected_type,
                        provider="local"
                    )
                    
                    files.append(storage_file)
            
            return files
            
        except Exception as e:
            print(f"❌ List files error: {e}")
            return []
    
    def _get_mime_type(self, filename: str) -> str:
        """MIME type tespit et"""
        extension = Path(filename).suffix.lower()
        mime_types = {
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.mp4': 'video/mp4',
            '.avi': 'video/avi',
            '.txt': 'text/plain',
            '.json': 'application/json',
            '.pdf': 'application/pdf'
        }
        return mime_types.get(extension, 'application/octet-stream')
    
    def _detect_file_type(self, filename: str) -> FileType:
        """File type tespit et"""
        extension = Path(filename).suffix.lower()
        
        if extension in ['.mp3', '.wav', '.ogg', '.m4a']:
            return FileType.AUDIO
        elif extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            return FileType.IMAGE
        elif extension in ['.mp4', '.avi', '.mov', '.mkv']:
            return FileType.VIDEO
        elif extension in ['.txt', '.pdf', '.doc', '.docx']:
            return FileType.DOCUMENT
        else:
            return FileType.OTHER

# Global instance
storage_service = StorageService()