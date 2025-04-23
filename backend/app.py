from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
from flask_cors import CORS
import os
import traceback
import cv2
import sys
import threading
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Enable real-time print flushing
sys.stdout.reconfigure(line_buffering=True)

from app2 import base64_to_anime, image_to_anime, ort_session

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
OUTPUT_FOLDER = os.path.join(os.getcwd(), 'outputs')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

progress_dict = {}

# ========== Image Upload ==========
@app.route("/predict", methods=["POST"])
def predict_image():
    try:
        data = request.json
        base64_img = data.get("image")
        if not base64_img:
            return jsonify({"error": "No image provided"}), 400

        print("📥 Received image for /predict")

        start_time = time.time()
        encoded_img = base64_to_anime(base64_img)
        end_time = time.time()
        
        elapsed = round(end_time - start_time, 3)
        print(f"🕒 Image processed in {elapsed} seconds")
        
        return jsonify({
            "result_image": f"data:image/png;base64,{encoded_img}",
            "processing_time": f"{elapsed} seconds"
        })

    except Exception as e:
        print("❌ Error in /predict:", traceback.format_exc(), flush=True)
        return jsonify({"error": str(e)}), 500

# ========== Video Process Route ==========
@app.route("/video-process", methods=["POST"])
def process_video():
    try:
        if 'video' not in request.files:
            return jsonify({"error": "No video file provided"}), 400

        video = request.files['video']
        original_filename = secure_filename(video.filename)
        input_path = os.path.join(UPLOAD_FOLDER, original_filename)
        output_filename = f"processed_{original_filename}"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)

        video.save(input_path)
        progress_dict[original_filename] = 0

        print(f"🎬 Processing video: {original_filename}")
        
        # Start processing in a background thread
        def process_in_background():
            try:
                process_video_with_anime_filter(input_path, output_path, ort_session, original_filename)
                print(f"✅ Output saved: {output_path}")
            except Exception as e:
                print(f"❌ Error in background processing: {str(e)}")
                progress_dict[original_filename] = -1  # Mark as error
        
        thread = threading.Thread(target=process_in_background)
        thread.daemon = True
        thread.start()

        return jsonify({
            "filename": output_filename,
            "video_id": original_filename,
            "video_path": output_path
        })

    except Exception as e:
        print("❌ Error in /video-process:", traceback.format_exc(), flush=True)
        return jsonify({"error": str(e)}), 500

# ========== Simple Download Route ==========
@app.route("/download/<filename>")
def download_file(filename):
    try:
        file_path = os.path.join(OUTPUT_FOLDER, filename)
        
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return jsonify({"error": "File not found"}), 404
        
        print(f"📥 Serving download for: {filename}")
        
        # Simple send_file with as_attachment=True to force download
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,  # For Flask 2.0+
            # attachment_filename=filename  # For Flask < 2.0
        )
        
    except Exception as e:
        print(f"❌ Error in download route: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

# ========== Progress Polling ==========
@app.route("/progress/<video_id>")
def get_progress(video_id):
    percent = progress_dict.get(video_id, 0)
    print(f"📊 Progress for video {video_id}: {percent}%", flush=True)
    return jsonify({"progress": percent})

# ========== Video Processing ==========
def process_video_with_anime_filter(input_path, output_path, model_session, video_id, target_fps=15):
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise IOError(f"Cannot open video file: {input_path}")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"🎞️ {total_frames} frames @ {width}x{height}")

    # Use mp4v codec
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, target_fps, (width, height))

    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        percent = int((frame_idx / total_frames) * 100)
        progress_dict[video_id] = min(percent, 99)
        print(f"🌀 Frame {frame_idx + 1}/{total_frames} ({percent}%)")

        # Process the frame
        resized = cv2.resize(frame, (720, 720))
        anime_frame = image_to_anime(resized)
        final_frame = cv2.resize(anime_frame, (width, height))

        out.write(final_frame)
        frame_idx += 1

    cap.release()
    out.release()
    cv2.destroyAllWindows()
    progress_dict[video_id] = 100
    print(f"✅ Done processing: {video_id}")

# ========== Run App ==========
if __name__ == "__main__":
    print("🚀 Flask server running on http://localhost:5000", flush=True)
    app.run(debug=True)