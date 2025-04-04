import React, { useState } from 'react';
import { motion } from 'framer-motion';

const transition = {
  initial: { opacity: 0, y: 30 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -30 },
  transition: { duration: 0.5 }
};

const ImagePage = () => {
  const [, setImageFile] = useState(null);
  const [base64Image, setBase64Image] = useState('');
  const [processedImage, setProcessedImage] = useState(null);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setImageFile(file);

    const reader = new FileReader();
    reader.onloadend = () => {
      const base64 = reader.result;
      setBase64Image(base64);
      sendToBackend(base64);
    };
    reader.readAsDataURL(file);
  };

  const sendToBackend = async (base64Image) => {
    try {
      const res = await fetch("http://localhost:5000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: base64Image })
      });

      const data = await res.json();
      if (data.result_image) {
        setProcessedImage(data.result_image);
      } else {
        setProcessedImage(null);
      }
    } catch (error) {
      console.error("Backend error:", error);
      setProcessedImage(null);
    }
  };

  return (
    <motion.div
      className="min-h-screen bg-gradient-to-b from-gray-900 via-gray-800 to-gray-700 text-white px-4 py-10"
      {...transition}
    >
      <div className="max-w-5xl mx-auto bg-white/10 backdrop-blur-lg border border-white/20 shadow-2xl rounded-2xl p-8">
        <h2 className="text-3xl font-bold text-center mb-6 text-white">🖼️ Upload Your Image</h2>

        <input
          type="file"
          accept="image/*"
          onChange={handleImageChange}
          className="block w-full mb-8 text-sm text-white
          file:mr-4 file:py-2 file:px-6
          file:rounded-full file:border-0
          file:text-sm file:font-semibold
          file:bg-blue-600 file:text-white
          hover:file:bg-blue-700"
        />

        {base64Image && (
          <div className="grid md:grid-cols-2 gap-10">
            {/* Preview Box */}
            <div className="bg-white/10 p-4 rounded-xl border border-white/20 shadow-md">
              <h3 className="text-xl font-semibold mb-2">Original Image</h3>
              <div className="w-[400px] h-[300px] rounded-lg overflow-hidden bg-gray-900 flex items-center justify-center border border-white/10">
                <img src={base64Image} alt="Preview" className="object-contain max-w-full max-h-full" />
              </div>
            </div>

            {/* Model Output Image */}
            <div className="bg-white/10 p-4 rounded-xl border border-white/20 shadow-md">
              <h3 className="text-xl font-semibold mb-2">Model Output</h3>
              <div className="w-[400px] h-[300px] rounded-lg bg-gray-900 flex items-center justify-center border border-white/10">
                {processedImage ? (
                  <img src={processedImage} alt="Processed" className="object-contain max-w-full max-h-full" />
                ) : (
                  <p className="text-gray-500">Waiting for output...</p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default ImagePage;
