import os
from fastapi import FastAPI, UploadFile, File
import uvicorn
from io import BytesIO

from PIL import Image
import numpy as np

import tensorflow as tf
app = FastAPI()
saved_model_path = "models/1"

# Check if the directory exists
if not os.path.exists(saved_model_path):
    raise FileNotFoundError(f"SavedModel directory '{saved_model_path}' does not exist.")

# Load the model
MODEL = tf.keras.models.load_model(saved_model_path)


CLASS_NAMES = ["Early Blight","Late Blight","Healthy"]
@app.get("/ping")
async def ping():
    return "Hello, I'm alive"
def read_file_as_image(data) ->np.ndarray:
    image = np.array(Image.open(BytesIO(data)))
    return image
    pass

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    image = read_file_as_image(await file.read())
    img_batch = np.expand_dims(image,0)
    predictions = MODEL.predict(img_batch)
    predicted_class = CLASS_NAMES[np.argmax(predictions)]
    confidence = np.max(predictions[0])
    print(predicted_class,confidence)
    return {
        "class":predicted_class,"confidence":float(confidence)
    }
    pass

if __name__ == "__main__":
    uvicorn.run(app, host='localhost', port=8000)
