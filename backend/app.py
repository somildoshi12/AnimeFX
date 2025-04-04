from flask import Flask, request, jsonify, send_file, abort
from werkzeug.utils import secure_filename, safe_join
from flask_cors import CORS
import os
import io
import cv2
import base64
from PIL import Image

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
        if not base64_img:
            return jsonify({"error": "No image provided"}), 400

        image_data = base64.b64decode(base64_img.split(",")[1])
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        image = image.convert("L")  # Convert to grayscale

        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        encoded_img = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return jsonify({ "result_image": f"data:image/png;base64,{encoded_img}" })

    except Exception as e:
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


if __name__ == "__main__":
    app.run(debug=True)
