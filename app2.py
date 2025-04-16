import os
import cv2
import base64
import numpy as np
import onnxruntime as ort
from io import BytesIO
from deploy.test_by_onnx import process_image  # Assuming this function is implemented
import tempfile, traceback

# Model configuration
model_path = r"D:\\PROGRAMMING\\React Js\\DIP\\human-anime-app\\deploy\\AnimeGANv3_Hayao_STYLE_36.onnx"
device = "gpu"  # or "cpu"

# def base64_to_cv2(base64_str):
#     # print("Base64 to CV2: ", base64_str)
#     img_bytes = base64.b64decode(base64_str)
#     img_array = np.frombuffer(img_bytes, dtype=np.uint8)
#     return cv2.imdecode(img_array, cv2.IMREAD_COLOR)

# WORKING
# def base64_to_cv2(base64_str):
#     if ',' in base64_str:
#         base64_str = base64_str.split(",")[1]
#     img_bytes = base64.b64decode(base64_str)
#     img_array = np.frombuffer(img_bytes, dtype=np.uint8)
#     return cv2.imdecode(img_array, cv2.IMREAD_COLOR)

import base64
import re
import tempfile
import os
import cv2
import imghdr
from urllib.parse import unquote

def save_and_open_base64_image(base64_string):
    """
    Takes a base64 string of an image (with or without the data URI prefix),
    saves it to a temporary file with the appropriate extension,
    and opens it using OpenCV.
    
    Args:
        base64_string (str): Base64 encoded image, potentially with data URI prefix
        
    Returns:
        tuple: (image as numpy array, temp_file_path)
    """
    try:
        # Handle URL encoded strings
        base64_string = unquote(base64_string)
        
        # Extract the actual base64 content and mimetype if data URI format is used
        if base64_string.startswith('data:'):
            # Extract mimetype and base64 content
            pattern = r'data:([^;]+);base64,(.+)'
            match = re.match(pattern, base64_string)
            
            if not match:
                raise ValueError("Invalid base64 data URI format")
                
            mime_type, base64_content = match.groups()
            
            # Determine file extension from mime type
            extension = mime_type.split('/')[-1]
            # Handle special cases
            if extension == 'jpeg':
                extension = 'jpg'
            elif extension == 'svg+xml':
                extension = 'svg'
        else:
            # If no data URI format, just use the raw base64 content
            base64_content = base64_string
            extension = None  # We'll determine extension after decoding
        
        # Decode the base64 content
        image_data = base64.b64decode(base64_content)
        
        # If extension wasn't determined from mime type, try to detect it
        if not extension:
            extension = imghdr.what(None, h=image_data)
            if not extension:
                # Default to png if detection fails
                extension = 'png'
        
        # Create a temporary file with the correct extension
        with tempfile.NamedTemporaryFile(suffix=f'.{extension}', delete=False) as temp_file:
            temp_file.write(image_data)
            temp_file_path = temp_file.name
        
        # Open the image with OpenCV
        img = cv2.imread(temp_file_path)
        
        if img is None:
            # Handle special formats not supported by cv2.imread
            # For example SVG, WEBP, HEIC, etc.
            raise ValueError(f"OpenCV couldn't read the image format: {extension}")
            
        return img, temp_file_path
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return None, None
    
def cleanup(temp_file_path):
    """
    Removes the temporary file
    
    Args:
        temp_file_path (str): Path to the temporary file
    """
    try:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
    except Exception as e:
        print(f"Error cleaning up temporary file: {str(e)}")

def cv2_to_base64(cv2_img):
    _, buffer = cv2.imencode('.jpg', cv2_img)
    return base64.b64encode(buffer).decode('utf-8')

def Convert_single_image_from_cv2(cv2_img, model_path, device="cpu"):
    if ort.get_device() == 'GPU' and device == "gpu":
        session = ort.InferenceSession(model_path, providers=['CUDAExecutionProvider','CPUExecutionProvider'])
    else:
        session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])

    input_name = session.get_inputs()[0].name

    original_shape = cv2_img.shape[:2][::-1]  # (width, height)
    img = process_image(cv2_img, model_path)
    img = np.expand_dims(img, axis=0)

    # Run inference
    output = session.run(None, {input_name: img})[0]

    # Convert output back to image
    output_img = (np.squeeze(output) + 1.) / 2 * 255
    output_img = np.clip(output_img, 0, 255).astype(np.uint8)
    output_img = cv2.resize(output_img, original_shape)
    output_img = cv2.cvtColor(output_img, cv2.COLOR_RGB2BGR)

    return output_img

# === Main callable ===
def base64_to_anime(base64_input_image):
    # print("Processing image...")
    # Decode input base64 to cv2
    # input_img_cv2 = base64_to_cv2(base64_input_image)
    input_img_cv2, temp = save_and_open_base64_image(base64_input_image)
    # print("\n\ntemp: ", temp)
    cleanup(temp)  # Clean up the temporary file after use
    # print("Input image shape:", input_img_cv2.shape)    
    # Apply transformation using ONNX model
    output_img_cv2 = Convert_single_image_from_cv2(input_img_cv2, model_path, device)
    # print("Output image shape:", output_img_cv2.shape)
    
    # Convert back to base64
    output_base64 = cv2_to_base64(output_img_cv2)
    # print("Conversion to base64 completed.")
    
    return output_base64

# === Example usage for testing ===
if __name__ == "__main__":
    # Read image from disk for testing only
    with open("D:\PROGRAMMING\React Js\DIP\human-anime-app\img1.jpg", "rb") as f:
        input_base64 = base64.b64encode(f.read()).decode('utf-8')

    output_base64 = base64_to_anime(input_base64)

    # Save result for verification
    with open("D:\PROGRAMMING\React Js\DIP\human-anime-app\output.jpg", "wb") as f:
        f.write(base64.b64decode(output_base64))
