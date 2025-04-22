from flask import Flask, request, jsonify, send_file, abort, make_response, send_from_directory
from werkzeug.utils import secure_filename
from flask_cors import CORS
import os
import traceback
import cv2
import sys
import threading
import random
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Enable real-time print flushing
sys.stdout.reconfigure(line_buffering=True)

from app2 import base64_to_anime, image_to_anime, ort_session

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

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
        encoded_img = base64_to_anime(base64_img)
        return jsonify({"result_image": f"data:image/png;base64,{encoded_img}"})

    except Exception as e:
        print("❌ Error in /predict:", traceback.format_exc(), flush=True)
        return jsonify({"error": str(e)}), 500

# ========== Video Upload ==========
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

        # Return the video URL with a cache-busting parameter
        random_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=8))
        return jsonify({
            "filename": output_filename,
            "video_id": original_filename,
            "video_url": f"http://localhost:5000/videos/{output_filename}?nocache={random_id}"
        })

    except Exception as e:
        print("❌ Error in /video-process:", traceback.format_exc(), flush=True)
        return jsonify({"error": str(e)}), 500

# ========== Serve Videos ==========
@app.route("/videos/<filename>")
def serve_video(filename):
    """Serve video files directly with forced headers for local development."""
    print(f"🎬 Serving video: {filename} from outputs directory")
    try:
        # Get the full path to the file
        file_path = os.path.join(OUTPUT_FOLDER, filename)
        
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return jsonify({"error": "File not found"}), 404
            
        # Read the file directly to bypass any automatic content handling
        with open(file_path, 'rb') as video_file:
            video_data = video_file.read()
        
        # Create a response with the file data - FORCE 200 OK
        response = make_response(video_data)
        
        # Force status code to 200 OK instead of 206 Partial Content
        response.status_code = 200
        
        # Force content type and disable caching
        response.headers.set('Content-Type', 'video/mp4')
        response.headers.set('Content-Length', str(os.path.getsize(file_path)))
        
        # Allow all CORS
        response.headers.set('Access-Control-Allow-Origin', '*')
        response.headers.set('Access-Control-Allow-Methods', 'GET, OPTIONS')
        response.headers.set('Access-Control-Allow-Headers', '*')
        
        # Force no caching
        response.headers.set('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        response.headers.set('Pragma', 'no-cache')
        response.headers.set('Expires', '0')
        
        # Add additional headers to help with video streaming but still force 200 OK
        response.headers.set('Accept-Ranges', 'none')  # Disable range requests to force 200 OK
        
        print(f"✅ Successfully serving video: {filename} with size {os.path.getsize(file_path)} bytes")
        print(f"✅ Status code explicitly set to: 200 OK")
        return response
        
    except Exception as e:
        print(f"❌ Error serving video: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

# ========== Legacy Download Route (for compatibility) ==========
@app.route("/download/<video_id>")
def download_video(video_id):
    print(f"📥 Download request for video: {video_id}")
    try:
        if not video_id.startswith("processed_"):
            video_id = f"processed_{video_id}"

        # Redirect to the new videos endpoint
        return serve_video(video_id)

    except Exception as e:
        print("❌ Error in /download route:", traceback.format_exc())
        return jsonify({"error": str(e)}), 500

# ========== Progress Polling ==========
@app.route("/progress/<video_id>")
def get_progress(video_id):
    percent = progress_dict.get(video_id, 0)
    print(f"📊 Progress for video {video_id}: {percent}%", flush=True)
    
    # Add CORS headers
    response = jsonify({"progress": percent})
    response.headers.set('Access-Control-Allow-Origin', '*')
    response.headers.set('Access-Control-Allow-Methods', 'GET, OPTIONS')
    return response

# ========== Video Processing ==========
def process_video_with_anime_filter(input_path, output_path, model_session, video_id, target_fps=15):
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise IOError(f"Cannot open video file: {input_path}")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"🎞️ {total_frames} frames @ {width}x{height}")

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

        # ↓ Resize for inference speed
        resized = cv2.resize(frame, (720, 720))
        anime_frame = image_to_anime(resized)

        # ↑ Resize back to original
        final_frame = cv2.resize(anime_frame, (width, height))
        # flipped_frame = cv2.flip(final_frame, -1)

        # out.write(flipped_frame)
        out.write(final_frame)
        frame_idx += 1

    cap.release()
    out.release()
    progress_dict[video_id] = 100
    print(f"✅ Done processing: {video_id}")

# ========== Run App ==========
if __name__ == "__main__":
    print("🚀 Flask server running on http://localhost:5000", flush=True)
    app.run(debug=True)