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
  const [processedVideoUrl, setProcessedVideoUrl] = useState(null);
  const [videoId, setVideoId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [videoReady, setVideoReady] = useState(false);
  const intervalRef = useRef(null);
  const videoRef = useRef(null);

  const [videoPath, setVideoPath] = useState(null);


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
          
          // Add a slight delay before trying to load the video
          setTimeout(() => {
            tryLoadVideo();
          }, 1000);
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

  // Try to load the video
  const tryLoadVideo = () => {
    if (!processedVideoUrl || !videoRef.current) return;
    
    console.log("Trying to load video from:", processedVideoUrl);
    
    // Force the video element to reload
    videoRef.current.load();
  };

  // Create a fake HTML video element just for testing
  const createTestVideo = () => {
    if (!processedVideoUrl) return;
    
    // Add a random number to prevent caching
    const cacheBuster = Date.now();
    const testUrl = `${processedVideoUrl}&test=${cacheBuster}`;
    
    // Create a video element
    const video = document.createElement('video');
    video.src = testUrl;
    video.style.display = 'none';
    video.setAttribute('playsinline', '');
    video.setAttribute('controls', '');
    
    // Add event listeners
    video.onloadeddata = () => {
      console.log("Test video loaded successfully!");
      alert("Test video loaded successfully!");
      document.body.removeChild(video);
    };
    
    video.onerror = (e) => {
      console.error("Test video error:", e);
      alert(`Test video error: ${e.target.error?.message || 'Unknown error'}`);
      document.body.removeChild(video);
    };
    
    // Add to body and attempt to load
    document.body.appendChild(video);
    video.load();
  };

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
    setProcessedVideoUrl(null);
    setVideoId(null);
    setError(null);
    setProgress(0);
    setVideoReady(false);
    setLoading(true);

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
      
      if (data.video_id && data.video_url) {
        console.log(`Setting video ID: ${data.video_id}`);
        console.log(`Setting video URL: ${data.video_url}`);
        setVideoId(data.video_id);
        setProcessedVideoUrl(data.video_url);
      } else {
        setLoading(false);
        setError("Invalid response from backend");
      }
    } catch (err) {
      setLoading(false);
      setError(`Error uploading video: ${err.message}`);
    }
  };

  return (
    <motion.div className="min-h-screen bg-gradient-to-b from-gray-900 via-gray-800 to-gray-700 text-white px-4 py-10" {...transition}>
      <div className="max-w-5xl mx-auto bg-white/10 backdrop-blur-lg border border-white/20 shadow-2xl rounded-2xl p-8">
        <h2 className="text-3xl font-bold text-center mb-6 text-white">🎥 Upload and Anime-Convert Your Video</h2>

        <input
          type="file"
          accept="video/*"
          onChange={handleVideoChange}
          className="block w-full mb-6 text-sm text-white file:mr-4 file:py-2 file:px-6 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700"
        />

        {error && (
          <div className="bg-red-500/20 p-4 rounded-lg text-center mb-6">
            <p>{error}</p>
          </div>
        )}

        {loading && (
          <div className="text-center text-blue-400 font-semibold mb-4">
            <div>Processing video... {progress}%</div>
            <div className="mt-2 w-full bg-gray-600 rounded-full h-4 overflow-hidden">
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
              <video src={originalVideo} controls className="w-full rounded-lg" />
            </div>
          )}

          {videoReady && processedVideoUrl && (
            <div className="bg-white/10 p-4 rounded-xl border border-white/20 shadow-md">
              {/* <h3 className="text-xl font-semibold mb-2">Anime-Styled Output</h3> */}
              
              {/* Embedded video player */}
              {/* <div className="mb-4">
                <video 
                  ref={videoRef}
                  controls 
                  className="w-full rounded-lg"
                  crossOrigin="anonymous"
                >
                  <source src={processedVideoUrl} type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
              </div> */}

              {videoReady && processedVideoUrl && (
                <div className="bg-white/10 p-4 rounded-xl border border-white/20 shadow-md">
                  <h3 className="text-xl font-semibold mb-2">Anime-Styled Output</h3>
              
                  <div className="bg-gray-800 p-4 rounded-lg text-sm text-blue-300 break-words text-center border border-blue-500">
                    Output Video Path:
                    <div className="mt-2 text-white font-mono break-words">{processedVideoUrl}</div>
                  </div>
                </div>
              )}


              
              {/* Video player controls */}
              {/* <div className="flex justify-center gap-2 mb-4">
                <button
                  onClick={tryLoadVideo}
                  className="px-3 py-1 bg-blue-500 hover:bg-blue-600 rounded-md text-sm"
                >
                  Reload Video
                </button>
                
                <button
                  onClick={createTestVideo}
                  className="px-3 py-1 bg-purple-500 hover:bg-purple-600 rounded-md text-sm"
                >
                  Test Video Loading
                </button>
              </div> */}
              
              {/* Direct access links */}
              {/* <div className="flex flex-wrap justify-center gap-2 mt-4">
                <a
                  href={processedVideoUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-4 py-2 bg-blue-600 rounded-lg hover:bg-blue-700 transition inline-block"
                >
                  Open in New Tab
                </a>
                
                <a
                  href={processedVideoUrl}
                  download
                  className="px-4 py-2 bg-green-600 rounded-lg hover:bg-green-700 transition inline-block"
                >
                  ⬇️ Download Video
                </a>
              </div>
              
              <div className="mt-4 text-sm text-center text-gray-400">
                <p>If the video doesn't play, please use "Open in New Tab" or "Download" buttons.</p>
              </div> */}
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default VideoPage;