from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import base64
import logging

# Inicializace FastAPI
app = FastAPI()

# CORS – pro komunikaci s frontendem
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/")
async def read_root():
    return {"message": "Welcome to Image Resizer Backend. Use /process-image for image processing."}

def resize_and_crop(image, target_width, target_height, aspect_ratio):
    height, width, _ = image.shape
    current_aspect = width / height
    target_aspect = target_width / target_height

    if current_aspect > target_aspect:
        # Ořežeme po stranách (obraz je moc široký)
        new_width = int(height * target_aspect)
        x1 = (width - new_width) // 2
        cropped = image[:, x1:x1 + new_width]
    else:
        # Ořežeme shora a zdola (obraz je moc vysoký)
        new_height = int(width / target_aspect)
        y1 = (height - new_height) // 2
        cropped = image[y1:y1 + new_height, :]

    resized = cv2.resize(cropped, (target_width, target_height), interpolation=cv2.INTER_AREA)
    return resized

def image_to_base64(image):
    _, buffer = cv2.imencode('.png', image)
    return f"data:image/png;base64,{base64.b64encode(buffer).decode('utf-8')}"

@app.post("/process-image")
async def process_image(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image format")

        formats = [
            {"width": 1080, "height": 1080, "key": "social_media"},
            {"width": 1920, "height": 1080, "key": "carousel"},
            {"width": 300, "height": 250, "key": "banner"},
        ]

        result = {}
        for fmt in formats:
            resized_image = resize_and_crop(
                image,
                fmt["width"],
                fmt["height"],
                fmt["width"] / fmt["height"]
            )
            result[fmt["key"]] = image_to_base64(resized_image)

        return JSONResponse(content=result)

    except Exception as e:
        logger.error(f"Error processing image: {e}")
        raise HTTPException(status_code=500, detail="Image processing failed")
