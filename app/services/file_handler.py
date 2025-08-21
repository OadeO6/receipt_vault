from typing import Annotated
from pathlib import Path
from uuid import uuid4
from app.exceptions import WrongFileTypeError
from app.schemas import FileType
import magic
import mimetypes
from fastapi import UploadFile

from app.core.logger import CustomLogger


logger = CustomLogger(__name__)



class FileHandlerService:
    def __init__(self, base_dir: str, allowed_file_types: Annotated[list[str], list[FileType]]):
        self.base_dir = Path(base_dir)
        self.allowed_file_types = allowed_file_types

    # NOTE: Maybe limit the file size
    def _validate_file_(self, file: bytes) -> bool:
        file_type = magic.from_buffer(file, mime=True)
        logger.info(f"Detected file type: {file_type}")
        logger.info(f"Allowed file types: {self.allowed_file_types}")

        if file_type not in self.allowed_file_types:
            raise WrongFileTypeError(
                f"File type '{file_type}' not in allowed types: {self.allowed_file_types}",
                logger=logger
            )
        return True

    def store_file(self, file: UploadFile) -> str:
        # TODO: Use a image store with caching
        data: bytes = file.file.read()
        self._validate_file_(data)
        # TODO: validate file name
        id = str(uuid4())
        try:
            file_name = self.base_dir / id
            print(file_name)
            if file_name.exists():
                logger.warning(f"File {id} already exists, overwriting it...")
            with open(file_name, "wb") as f:
                f.write(data)
        except Exception:
            logger.error(f"Error saving file {id}")
            raise
        finally:
            file.file.seek(0)


        logger.info(f"File {id} saved successfuly")
        return id



    def get_file(self, id: str) -> UploadFile:
        file_name = self.base_dir / id
        pass

    def get_file_url(self, id):
        return ""
