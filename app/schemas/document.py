from pydantic import BaseModel
from typing import Optional

class DocumentUploadResponse(BaseModel):
    document_id: str
    status: str
