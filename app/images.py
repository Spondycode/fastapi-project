# Image processing utilities
import os
import shutil
import tempfile
from dotenv import load_dotenv
from imagekitio import ImageKit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
from fastapi import UploadFile

# Load environment variables
load_dotenv()

# ImageKit configuration
IMAGEKIT_PRIVATE_KEY = os.getenv("IMAGEKIT_PRIVATE_KEY")
IMAGEKIT_PUBLIC_KEY = os.getenv("IMAGEKIT_PUBLIC_KEY")
IMAGEKIT_URL_ENDPOINT = os.getenv("IMAGEKIT_URL_ENDPOINT")

# Initialize ImageKit
imagekit = ImageKit(
    private_key=IMAGEKIT_PRIVATE_KEY,
    public_key=IMAGEKIT_PUBLIC_KEY,
    url_endpoint=IMAGEKIT_URL_ENDPOINT
)


async def upload_to_imagekit(file: UploadFile):
    """Upload a file to ImageKit using a temporary file with the same suffix."""
    # Create a temporary file with the same suffix as the uploaded file
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
        temp_file_path = temp_file.name
        shutil.copyfileobj(file.file, temp_file)
    
    try:
        # Upload to ImageKit
        upload_result = imagekit.upload_file(
            file=open(temp_file_path, "rb"),
            file_name=file.filename,
            options=UploadFileRequestOptions(
                use_unique_file_name=True,
                tags=["backend-upload"]
            )
        )
        return upload_result
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
