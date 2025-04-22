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
      <div className="max-w-3xl bg-white/10 backdrop-blur-lg border border-white/20 shadow-2xl rounded-2xl p-10 text-center" >
        <h2 className="text-3xl font-bold text-blue-400 mb-4 text-center">About This Project</h2>
        <p className="text-lg text-gray-300 leading-relaxed txt-center">
        AnimeFX is an AI-powered web app that transforms images and videos into anime-style visuals using deep learning models.<br /> 
        Built with React and Flask, it offers real-time progress tracking and a sleek, modern UI styled with Tailwind CSS.
        </p>
        <br />
        <hr className="border-gray-600 my-8 mt-4 mb-4" />

        <h3 className="text-xl font-semibold text-blue-300 mt-6 mb-2">Team Members:</h3>
        <div className="space-y-1 text-gray-300 text-center">
          <p>Somil Doshi – 2380129</p>
          <p>Yatrikkumar Shah</p>
          <p>Arka Dey</p>
          <p>Shreya</p>
          <p>Kiarah Patel</p>
        </div>


      </div>
    </motion.div>
  );
};

export default About;
