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

# Add your app path
sys.path.append("D:\\PROGRAMMING\\React Js\\DIP\\human-anime-app")
from app2 import base64_to_anime, image_to_anime  # Assuming these are correctly defined

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

        encoded_img = base64_to_anime(base64_img)
        return jsonify({"result_image": f"data:image/png;base64,{encoded_img}"})

    except Exception as e:
        print("traceback:", traceback.format_exc())
        return jsonify({"error": str(e)}), 500


# ========== Route for Video Processing ==========
@app.route("/video-process", methods=["POST"])
def process_video():
    try:
        print("video-process()")
        if 'video' not in request.files:
            return jsonify({"error": "No video file provided"}), 400

        video = request.files['video']
        filename = secure_filename(video.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        output_filename = f"processed_{filename}"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)

        # Save the uploaded video
        video.save(input_path)

        process_video_with_anime_filter(input_path, output_path, base64_to_anime, target_fps=1)

        print(f"✅ Processed video saved at: {output_path}")
        return jsonify({"filename": output_filename})

    except Exception as e:
        print(f"🚫 Error processing video: {e}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500


# ========== Route to Stream Processed Video ==========
@app.route("/video/<filename>")
def stream_video(filename):
    try:
        print("🚀 Serving video...")
        full_path = safe_join(OUTPUT_FOLDER, filename)

        if not os.path.isfile(full_path):
            print(f"⚠️ File not found: {full_path}")
            abort(404)

        print(f"✅ Streaming video from: {full_path}")
        return send_file(full_path, mimetype='video/mp4')

    except Exception as e:
        print(f"🚫 Error serving video: {e}")
        return jsonify({"error": str(e)}), 500


# # ========== Anime Video Processing Function ==========
# def process_video_with_anime_filter(input_path, output_path, base64_to_anime, target_fps=15, jpeg_quality=85):
#     cap = cv2.VideoCapture(input_path)
#     if not cap.isOpened():
#         raise IOError(f"Cannot open video file at {input_path}")

#     original_fps = cap.get(cv2.CAP_PROP_FPS)
#     frame_interval = int(original_fps // target_fps) if original_fps > target_fps else 1

#     width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#     height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

#     fourcc = cv2.VideoWriter_fourcc(*'mp4v')
#     out = cv2.VideoWriter(output_path, fourcc, target_fps, (width, height))

#     frame_idx = 0
#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break

#         if frame_idx % frame_interval == 0:
#             print(f"Processed frame {frame_idx} of {cap.get(cv2.CAP_PROP_FRAME_COUNT) // frame_interval}")

#                         # Apply anime transformation
#             anime_frame = image_to_anime(frame)
#             cv2.imwrite(os.path.join(OUTPUT_FOLDER, f"frame_{frame_idx}.jpg"), anime_frame, [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality])

#             # Ensure result is in the correct format
#             if anime_frame.shape[1] != width or anime_frame.shape[0] != height:
#                 anime_frame = cv2.resize(anime_frame, (width, height))

#             out.write(anime_frame)

#         frame_idx += 1


#         #     # encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality]
#         #     # result, encimg = cv2.imencode('.jpg', frame, encode_param)
#         #     if result:
#         #         # compressed_frame = cv2.imdecode(encimg, cv2.IMREAD_COLOR)
#         #         anime_frame = image_to_anime(frame)

#         #         if anime_frame.shape[1] != width or anime_frame.shape[0] != height:
#         #             anime_frame = cv2.resize(anime_frame, (width, height))

#         #         out.write(anime_frame)

#         # frame_idx += 1

#     cap.release()
#     out.release()
#     print(f"Compressed anime video saved at {output_path}")

def process_video_with_anime_filter(input_path, output_path, base64_to_anime, target_fps=15, jpeg_quality=85):
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        raise IOError(f"Cannot open video file at {input_path}")

    original_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_interval = int(original_fps // target_fps) if original_fps > target_fps else 1

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, target_fps, (width, height))

    frame_idx = 0
    processed_frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Skip frames to achieve target FPS
        if frame_idx % frame_interval != 0:
            frame_idx += 1
            continue

        print(f"🎬 Processing frame {processed_frame_count + 1} of ~{total_frames // frame_interval}")

        # Apply anime transformation
        anime_frame = image_to_anime(frame)

        # Save each frame optionally as compressed image (optional, for debugging or audit)
        frame_filename = os.path.join(OUTPUT_FOLDER, f"frame_{processed_frame_count}.jpg")
        print(f"💾 Saving frame {processed_frame_count + 1} as {frame_filename}")
        cv2.imwrite(frame_filename, anime_frame, [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality])

        # Ensure the processed frame has correct dimensions
        if anime_frame.shape[:2] != (height, width):
            anime_frame = cv2.resize(anime_frame, (width, height))

        # Write frame to video
        out.write(anime_frame)

        frame_idx += 1
        processed_frame_count += 1

    cap.release()
    out.release()
    print(f"✅ Compressed anime video saved at: {output_path}")


# ========== Run App ==========
if __name__ == "__main__":
    app.run()
