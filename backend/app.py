from flask import Flask, request, jsonify, send_file, abort
from werkzeug.utils import secure_filename, safe_join
from flask_cors import CORS
import os
import io
import cv2
import base64
from PIL import Image
import traceback

import sys
sys.path.append("D:\PROGRAMMING\React Js\DIP\human-anime-app")

from app2 import base64_to_anime  # Assuming this function is defined in app.py

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
OUTPUT_FOLDER = os.path.join(os.getcwd(), 'outputs')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# ========== Route for Image (Base64) Processing ==========
@app.route("/predict", methods=["POST"])
def predict_image():
    try:
        data = request.json
        base64_img = data.get("image")
        # print("base64_img: ", base64_img[:100], sep="\n")
        if not base64_img:
            return jsonify({"error": "No image provided"}), 400
        
        encoded_img = base64_to_anime(base64_img)

        # image_data = base64.b64decode(base64_img.split(",")[1])
        # image = Image.open(io.BytesIO(image_data)).convert("RGB")
        # image = image.convert("L")  # Convert to grayscale

        # buffer = io.BytesIO()
        # image.save(buffer, format="PNG")
        # encoded_img = base64.b64encode(buffer.getvalue()).decode("utf-8")

        # print({ "result_image": f"data:image/png;base64,{encoded_img}" })
        return jsonify({ "result_image": f"data:image/png;base64,{encoded_img}" })

    except Exception as e:
        # print(f"Error processing image: {e}")
        print("traceback:", traceback.format_exc())
        return jsonify({ "error": str(e) }), 500


# ========== Route for Video Processing ==========
@app.route("/video-process", methods=["POST"])
def process_video():
    if 'video' not in request.files:
        return jsonify({"error": "No video file provided"}), 400

    video = request.files['video']
    filename = secure_filename(video.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    output_filename = f"processed_{filename}"
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)

    # Save the uploaded video
    video.save(input_path)

    try:
        # Cleanup old processed videos
        for f in os.listdir(OUTPUT_FOLDER):
            if f.startswith("processed_"):
                os.remove(os.path.join(OUTPUT_FOLDER, f))

        cap = cv2.VideoCapture(input_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS) or 15)

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray_3channel = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            out.write(gray_3channel)

        cap.release()
        out.release()

        print(f"✅ Processed video saved at: {output_path}")
        return jsonify({ "filename": output_filename })

    except Exception as e:
        return jsonify({ "error": str(e) }), 500


# ========== Route to Stream Processed Video ==========
@app.route("/video/<filename>")
def stream_video(filename):
    try:
        full_path = safe_join(OUTPUT_FOLDER, filename)
        if not os.path.isfile(full_path):
            print(f"⚠️ File not found: {full_path}")
            abort(404)

        print(f"✅ Streaming video from: {full_path}")
        return send_file(full_path, mimetype='video/mp4')

    except Exception as e:
        print(f"🚫 Error serving video: {e}")
        return jsonify({ "error": str(e) }), 500




# --------------------------- Yatrik------------------------------------


# import os
# import cv2
# import base64
# import numpy as np
# import onnxruntime as ort
# from io import BytesIO
# from deploy.test_by_onnx import process_image  # Assuming this function is implemented


# # Model configuration
# model_path = r"D:\\PROGRAMMING\\React Js\\DIP\\human-anime-app\\deploy\\AnimeGANv3_Hayao_STYLE_36.onnx"
# device = "gpu"  # or "cpu"

# def base64_to_cv2(base64_str):
#     print("entered base64_to_cv2")
#     img_bytes = base64.b64decode(base64_str)
#     print("img_bytes:", type(img_bytes), len(img_bytes))
#     img_array = np.frombuffer(img_bytes, dtype=np.uint8)
#     print(img_array.shape)
#     img_array = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
#     return cv2.imdecode(img_array, cv2.IMREAD_COLOR)

# def cv2_to_base64(cv2_img):
#     _, buffer = cv2.imencode('.jpg', cv2_img)
#     return base64.b64encode(buffer).decode('utf-8')

# def Convert_single_image_from_cv2(cv2_img, model_path, device="cpu"):
#     if ort.get_device() == 'GPU' and device == "gpu":
#         session = ort.InferenceSession(model_path, providers=['CUDAExecutionProvider','CPUExecutionProvider'])
#     else:
#         session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])

#     input_name = session.get_inputs()[0].name

#     original_shape = cv2_img.shape[:2][::-1]  # (width, height)
#     img = process_image(cv2_img, model_path)
#     img = np.expand_dims(img, axis=0)

#     # Run inference
#     output = session.run(None, {input_name: img})[0]

#     # Convert output back to image
#     output_img = (np.squeeze(output) + 1.) / 2 * 255
#     output_img = np.clip(output_img, 0, 255).astype(np.uint8)
#     output_img = cv2.resize(output_img, original_shape)
#     output_img = cv2.cvtColor(output_img, cv2.COLOR_RGB2BGR)

#     return output_img

# # === Main callable ===
# def base64_to_anime(base64_input_image):
#     print("entered")

#     input_img_cv2 = base64_to_cv2(base64_input_image)
#     if input_img_cv2 is None:
#         raise ValueError("Failed to decode base64 image to OpenCV format.")
#     else:
#         print("working input_img_cv2:", input_img_cv2.shape)

#     print("input_img_cv2:", input_img_cv2.shape)
    
#     # Decode input base64 to cv2
#     input_img_cv2 = base64_to_cv2(base64_input_image)
#     print("input_img_cv2:", input_img_cv2.shape)
    
#     # Apply transformation using ONNX model
#     output_img_cv2 = Convert_single_image_from_cv2(input_img_cv2, model_path, device)
#     print("output_img_cv2:", output_img_cv2.shape)
    
#     # Convert back to base64
#     output_base64 = cv2_to_base64(output_img_cv2)
#     print("output_base64:", output_base64)

#     with open("D:\PROGRAMMING\React Js\DIP\human-anime-app\output.jpg", "wb") as f:
#         f.write(base64.b64decode(output_base64))
        
#     return output_base64


if __name__ == "__main__":
    app.run()
