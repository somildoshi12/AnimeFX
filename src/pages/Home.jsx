import React from 'react';
import { motion } from 'framer-motion';

const transition = {
  initial: { opacity: 0, y: 30 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -30 },
  transition: { duration: 0.5 }
};

const Home = () => {
  return (
    <motion.div
      className="min-h-screen bg-gradient-to-b from-gray-900 via-gray-800 to-gray-700 text-white px-4 py-10 flex items-center justify-center"
      {...transition}
    >
      <div className="max-w-3xl bg-white/10 backdrop-blur-lg border border-white/20 shadow-2xl rounded-2xl p-10 text-center">
        <h1 className="text-4xl md:text-5xl font-bold text-blue-400 mb-6">Welcome to AnimeFX</h1>
        <p className="text-lg text-gray-300 leading-relaxed">
        Turn real moments into anime magic — powered by AI.<br />
        </p>
      </div>
    </motion.div>
  );
};

export default Home;
