import os
import cv2
import base64
import numpy as np
import onnxruntime as ort
from io import BytesIO
from deploy.test_by_onnx import process_image
import tempfile
import re
import imghdr
from urllib.parse import unquote

# === Model Configuration ===
model_path = r"D:\\PROGRAMMING\\React Js\\DIP\\human-anime-app\\deploy\\AnimeGANv3_Hayao_STYLE_36.onnx"
device = "gpu"

# === ONNX Session Initialization (shared across image and video) ===
print("🧠 Initializing ONNX session...")
if ort.get_device() == 'GPU' and device == "gpu":
    ort_session = ort.InferenceSession(model_path, providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
    print("✅ Using GPU for inference")
else:
    ort_session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
    print("⚠️ Falling back to CPU")

# === Helpers ===
def save_and_open_base64_image(base64_string):
    try:
        base64_string = unquote(base64_string)

        if base64_string.startswith('data:'):
            pattern = r'data:([^;]+);base64,(.+)'
            match = re.match(pattern, base64_string)
            if not match:
                raise ValueError("Invalid base64 format")
            mime_type, base64_content = match.groups()
            extension = mime_type.split('/')[-1]
            if extension == 'jpeg':
                extension = 'jpg'
        else:
            base64_content = base64_string
            extension = 'png'

        image_data = base64.b64decode(base64_content)

        if not extension:
            extension = imghdr.what(None, h=image_data) or 'png'

        with tempfile.NamedTemporaryFile(suffix=f'.{extension}', delete=False) as temp_file:
            temp_file.write(image_data)
            temp_path = temp_file.name

        img = cv2.imread(temp_path)
        if img is None:
            raise ValueError("OpenCV couldn't decode the image")
        return img, temp_path

    except Exception as e:
        print(f"❌ Error decoding image: {e}")
        return None, None

def cleanup(temp_file_path):
    try:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
    except Exception as e:
        print(f"❌ Cleanup error: {e}")

def cv2_to_base64(cv2_img):
    _, buffer = cv2.imencode('.jpg', cv2_img)
    return base64.b64encode(buffer).decode('utf-8')

def Convert_single_image_from_cv2(cv2_img, session=None):
    if session is None:
        session = ort_session

    input_name = session.get_inputs()[0].name
    original_shape = cv2_img.shape[:2][::-1]
    img = process_image(cv2_img, model_path)
    img = np.expand_dims(img, axis=0)

    output = session.run(None, {input_name: img})[0]
    output_img = (np.squeeze(output) + 1.) / 2 * 255
    output_img = np.clip(output_img, 0, 255).astype(np.uint8)
    output_img = cv2.resize(output_img, original_shape)
    output_img = cv2.cvtColor(output_img, cv2.COLOR_RGB2BGR)
    return output_img

# === Image API (used in /predict) ===
def base64_to_anime(base64_input_image):
    print("📡 base64_to_anime() called")
    input_img_cv2, temp = save_and_open_base64_image(base64_input_image)
    cleanup(temp)

    if input_img_cv2 is None:
        raise ValueError("❌ Could not decode base64 input image")

    output_img_cv2 = Convert_single_image_from_cv2(input_img_cv2, ort_session)

    if output_img_cv2 is None:
        raise ValueError("❌ ONNX inference failed")

    print("✅ Anime-style image generated")
    return cv2_to_base64(output_img_cv2)

def image_to_anime(image):
    return Convert_single_image_from_cv2(image, ort_session)
