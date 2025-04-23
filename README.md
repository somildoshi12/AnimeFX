
# Human Anime App 🎨📹

This project transforms human images and videos into anime-style visuals using a React frontend and Flask backend with an ONNX model.

## 📁 Project Structure

```
human-anime-app/
│
├── backend/             # Flask API for processing
│   ├── app.py
│   └── test_ny_onnx.py
│
├── human-anime-app/     # React frontend
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── ...
│
├── outputs/             # Folder to store processed output files
└── README.md
```

---

## 🚀 Features

- Upload and transform human images and videos to anime-style
- Real-time preview of uploaded media
- Backend preprocessing using ONNX model
- React frontend with animations and dark mode

---

## 🧑‍💻 Prerequisites

- **Node.js** (v16+ recommended)
- **Python** (3.8+)
- **pip**
- **virtualenv** (optional but recommended)

---

## 🔧 Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/somildoshi12/human-anime-dip.git
cd human-anime-app
```

### 2. Setup the Flask Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Use venv\Scripts\activate on Windows

pip install -r requirements.txt  # Make sure this file exists or install manually
```

> 🔹 If there's no `requirements.txt`, install dependencies like this:
```bash
pip install flask flask-cors opencv-python onnxruntime numpy
```

### 3. Start the Flask Server

```bash
python app.py
```

It will run on: `http://localhost:5000`

---

### 4. Setup the React Frontend

```bash
cd ../human-anime-app
npm install
```

### 5. Start the React App

```bash
npm start
```

It will run on: `http://localhost:3000`

---

## 🖼 Usage

1. Navigate to `http://localhost:3000`
2. Upload an image or video.
3. Wait for it to be processed.
4. View the output right below the original file.

---

## 🗂 Output

- All processed files will be stored in the `outputs/` folder.
- For videos, a `.mp4` version of the anime-style output is generated.

---

## 📌 Notes

- Make sure the backend is running before uploading files from the frontend.
- Check console logs for progress updates or any error messages.

---

## 📬 Contact

Maintainer: Somil Doshi
