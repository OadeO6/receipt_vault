from enum import Enum
from pydantic import BaseModel


class FileType(str, Enum):
    PDF = "application/pdf"
    JPEG = "image/jpeg"
    PNG = "image/png"
    TXT = "text/plain"
    CSV = "text/csv"
