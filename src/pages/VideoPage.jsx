import React, { useState } from 'react';
import { motion } from 'framer-motion';

const transition = {
  initial: { opacity: 0, y: 30 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -30 },
  transition: { duration: 0.5 }
};

const VideoPage = () => {
  const [originalVideo, setOriginalVideo] = useState(null);
  const [processedFilename, setProcessedFilename] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleVideoChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const localURL = URL.createObjectURL(file);
    setOriginalVideo(localURL);
    setProcessedFilename(null);
    setLoading(true);

    const formData = new FormData();
    formData.append("video", file);

    try {
      const res = await fetch("http://localhost:5000/video-process", {
        method: "POST",
        body: formData,
      });

      const data = await res.json();
      if (data.filename) {
        // Add delay to ensure file is fully written
        setTimeout(() => {
          setProcessedFilename(data.filename);
          setLoading(false);
        }, 1500);
      } else {
        setLoading(false);
      }
    } catch (err) {
      console.error("Video processing failed:", err);
      setLoading(false);
    }
  };

  return (
    <motion.div
      className="min-h-screen bg-gradient-to-b from-gray-900 via-gray-800 to-gray-700 text-white px-4 py-10"
      {...transition}
    >
      <div className="max-w-5xl mx-auto bg-white/10 backdrop-blur-lg border border-white/20 shadow-2xl rounded-2xl p-8">
        <h2 className="text-3xl font-bold text-center mb-6 text-white">🎥 Upload and Process Video</h2>

        <input
          type="file"
          accept="video/*"
          onChange={handleVideoChange}
          className="block w-full mb-6 text-sm text-white file:mr-4 file:py-2 file:px-6 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700"
        />

        {loading && (
          <div className="text-center text-blue-400 font-semibold mb-4 animate-pulse">
            Processing video... Please wait ⏳
          </div>
        )}

        <div className="grid md:grid-cols-2 gap-10">
          {originalVideo && (
            <div className="bg-white/10 p-4 rounded-xl border border-white/20 shadow-md">
              <h3 className="text-xl font-semibold mb-2">Original Video</h3>
              <video src={originalVideo} controls className="w-full rounded-lg" />
            </div>
          )}

          {processedFilename && !loading && (
            <div className="bg-white/10 p-4 rounded-xl border border-white/20 shadow-md">
              <h3 className="text-xl font-semibold mb-2">Grayscale Output</h3>
              <video
                src={`http://localhost:5000/video/${processedFilename}`}
                controls
                className="w-full rounded-lg"
              />
              <div className="mt-4 text-center">
                <a
                  href={`http://localhost:5000/video/${processedFilename}`}
                  download={processedFilename}
                  className="text-blue-400 underline hover:text-blue-300 transition"
                >
                  ⬇️ Download Processed Video
                </a>
              </div>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default VideoPage;
