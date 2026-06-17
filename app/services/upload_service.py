import os
import shutil
import uuid
from fastapi import UploadFile, HTTPException

UPLOAD_DIR = "static/banners"

class UploadService:
    @staticmethod
    def save_image(file: UploadFile) -> str:
        if not os.path.exists(UPLOAD_DIR):
            os.makedirs(UPLOAD_DIR)

        file_extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        try:
            with open(file_path, "wb+") as file_object:
                shutil.copyfileobj(file.file, file_object)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")

        return f"http://localhost:8000/{file_path}"

upload_service = UploadService()