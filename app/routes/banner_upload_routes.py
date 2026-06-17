from fastapi import APIRouter, UploadFile, File
from app.services.upload_service import upload_service

router = APIRouter(tags=["Uploads"])

@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    file_url = upload_service.save_image(file)
    return {"image_url": file_url}