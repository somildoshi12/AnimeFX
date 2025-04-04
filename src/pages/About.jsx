import React from 'react';
import { motion } from 'framer-motion';

const transition = {
  initial: { opacity: 0, y: 30 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -30 },
  transition: { duration: 0.5 }
};

const About = () => {
  return (
    <motion.div
      className="min-h-screen bg-gradient-to-b from-gray-900 via-gray-800 to-gray-700 text-white px-4 py-10 flex items-center justify-center"
      {...transition}
    >
      <div className="max-w-3xl bg-white/10 backdrop-blur-lg border border-white/20 shadow-2xl rounded-2xl p-10">
        <h2 className="text-3xl font-bold text-blue-400 mb-4">About This Project</h2>
        <p className="text-lg text-gray-300 leading-relaxed">
          This web application allows users to upload images and videos and convert them to base64 format.
          A deep learning backend model (coming soon) will process these files and return meaningful output shown just below the preview.
          Built using React, Tailwind CSS, and designed with a clean, modern UI in mind.
        </p>
      </div>
    </motion.div>
  );
};

export default About;
