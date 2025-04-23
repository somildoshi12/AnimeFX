import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';

const transition = {
  initial: { opacity: 0, y: 30 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -30 },
  transition: { duration: 0.5 }
};

const VideoPage = () => {
  const [originalVideo, setOriginalVideo] = useState(null);
  const [videoId, setVideoId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [videoReady, setVideoReady] = useState(false);
  const [downloadPath, setDownloadPath] = useState(null);
  const intervalRef = useRef(null);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  // Effect for polling progress
  useEffect(() => {
    if (!loading || !videoId) return;

    const pollProgress = async () => {
      try {
        const res = await fetch(`http://localhost:5000/progress/${videoId}`);
        if (!res.ok) return;
        
        const data = await res.json();
        setProgress(Number(data.progress));
        
        if (data.progress >= 100) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
          setLoading(false);
          setVideoReady(true);
        }
      } catch (err) {
        console.error("Error polling progress:", err);
      }
    };

    // Start polling immediately then every second
    pollProgress();
    intervalRef.current = setInterval(pollProgress, 1000);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [loading, videoId]);

  const handleVideoChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Clear previous state
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    
    const localURL = URL.createObjectURL(file);
    setOriginalVideo(localURL);
    setVideoId(null);
    setError(null);
    setProgress(0);
    setVideoReady(false);
    setLoading(true);
    setDownloadPath(null);

    const formData = new FormData();
    formData.append("video", file);

    try {
      console.log('Uploading video to backend...');
      const res = await fetch("http://localhost:5000/video-process", {
        method: "POST",
        body: formData
      });
      
      if (!res.ok) {
        throw new Error(`Server responded with ${res.status}`);
      }
      
      const data = await res.json();
      console.log("Response from server:", data);
      
      if (data.video_id && data.video_path) {
        console.log(`Setting video ID: ${data.video_id}`);
        console.log(`Setting video path: ${data.video_path}`);
        setVideoId(data.video_id);
        setDownloadPath(data.video_path);
      } else {
        setLoading(false);
        setError("Invalid response from backend");
      }
    } catch (err) {
      setLoading(false);
      setError(`Error uploading video: ${err.message}`);
    }
  };

  // Create download URL
  const getDownloadUrl = () => {
    if (!downloadPath) return null;
    
    const fileName = downloadPath.split('\\').pop().split('/').pop();
    return `http://localhost:5000/download/${fileName}`;
  };

  return (
    <motion.div className="min-h-screen bg-gradient-to-b from-gray-900 via-gray-800 to-gray-700 text-white px-4 py-10" {...transition}>
      <div className="max-w-5xl mx-auto bg-white/10 backdrop-blur-lg border border-white/20 shadow-2xl rounded-2xl p-8">
        <h2 className="text-3xl font-bold text-center mb-6 text-white">🎥 Upload and Anime-Convert Your Video</h2>

        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-300 mb-2">Select a video file</label>
          <div className="flex items-center">
            <label className="cursor-pointer bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg">
              Choose File
              <input
                type="file"
                accept="video/*"
                onChange={handleVideoChange}
                className="hidden"
              />
            </label>
            {originalVideo && (
              <span className="ml-3 text-gray-300">
                {videoId || "Video selected"}
              </span>
            )}
          </div>
        </div>

        {error && (
          <div className="bg-red-500/20 p-4 rounded-lg text-center mb-6">
            <p>{error}</p>
          </div>
        )}

        {loading && (
          <div className="text-center text-blue-400 font-semibold mb-6">
            <div className="mb-2">Processing video... {progress}%</div>
            <div className="w-full bg-gray-700 rounded-full h-4 overflow-hidden">
              <div 
                className="bg-blue-500 h-full transition-all duration-300" 
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}

        <div className="grid md:grid-cols-2 gap-10 mt-8">
          {originalVideo && (
            <div className="bg-white/10 p-4 rounded-xl border border-white/20 shadow-md">
              <h3 className="text-xl font-semibold mb-2">Original Video</h3>
              <div className="aspect-video bg-black rounded-lg overflow-hidden">
                <video 
                  src={originalVideo} 
                  controls 
                  className="w-full h-full object-contain"
                />
              </div>
            </div>
          )}

          {videoReady && downloadPath && (
            <div className="bg-white/10 p-4 rounded-xl border border-white/20 shadow-md">
              <h3 className="text-xl font-semibold mb-2">Anime-Styled Output</h3>
              
              <div className="aspect-video bg-gray-900 rounded-lg flex items-center justify-center mb-4">
                <div className="text-center">
                  <p className="text-gray-400 mb-2">Your anime-styled video is ready!</p>
                  <p className="text-gray-500 text-sm mb-4">Click the button below to download</p>
                  
                  <a
                    href={getDownloadUrl()}
                    download
                    className="px-6 py-3 bg-green-600 rounded-lg hover:bg-green-700 transition inline-flex items-center gap-2"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                    Download Video
                  </a>
                </div>
              </div>
              
              <div className="text-center text-gray-400 text-sm">
                <p>Filename: {downloadPath.split('\\').pop().split('/').pop()}</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default VideoPage;