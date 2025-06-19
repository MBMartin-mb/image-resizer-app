from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import base64
from io import BytesIO
from dotenv import load_dotenv
import os
import logging

# Nastavení logování
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def detect_main_content(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        return x, y, w, h
    return 0, 0, image.shape[1], image.shape[0]

def resize_and_crop(image, target_width, target_height, aspect_ratio):
    x, y, w, h = detect_main_content(image)
    current_aspect = w / h
    target_aspect = target_width / target_height

    if current_aspect > target_aspect:
        new_width = int(h * target_aspect)
        crop_x = x + (w - new_width) // 2
        crop_y = y
        crop_w = new_width
        crop_h = h
    else:
        crop_h = int(w / target_aspect)
        crop_x = x
        crop_y = y + (h - crop_h) // 2
        crop_w = w

    cropped = image[max(0, crop_y):crop_y + crop_h, max(0, crop_x):crop_x + crop_w]
    resized = cv2.resize(cropped, (target_width, target_height), interpolation=cv2.INTER_AREA)
    return resized

def image_to_base64(image):
    _, buffer = cv2.imencode('.png', image)
    return f"data:image/png;base64,{base64.b64encode(buffer).decode('utf-8')}"

@app.get("/")
async def read_root():
    return {"message": "Welcome to Image Resizer Backend. Use /process-image for image processing."}

@app.post("/process-image")
async def process_image(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        if not contents:
            raise HTTPException(status_code=400, detail="No file content provided.")
        
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image file.")

        formats = [
            {"width": 1080, "height": 1080, "key": "social_media"},  # 1:1
            {"width": 1920, "height": 1080, "key": "carousel"},      # 16:9
            {"width": 300, "height": 250, "key": "banner"},          # Static banner
        ]

        result = {}
        for fmt in formats:
            resized_image = resize_and_crop(image, fmt["width"], fmt["height"], fmt["width"] / fmt["height"])
            result[fmt["key"]] = image_to_base64(resized_image)

        logger.info("Image processed successfully.")
        return JSONResponse(content=result)
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
