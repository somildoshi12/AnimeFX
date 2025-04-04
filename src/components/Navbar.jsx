import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Menu, X } from 'lucide-react'; // Make sure this works after npm install

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className="fixed top-0 left-0 w-full z-50 bg-white/10 backdrop-blur-lg border-b border-white/20 text-white shadow-md px-6 py-4">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        <h1 className="text-2xl md:text-3xl font-bold tracking-tight">Base64 Media Processor</h1>

        {/* Desktop Menu */}
        <div className="hidden md:flex space-x-8 text-lg font-medium">
          <Link to="/" className="hover:text-blue-400">Home</Link>
          <Link to="/image" className="hover:text-blue-400">Image</Link>
          <Link to="/video" className="hover:text-blue-400">Video</Link>
          <Link to="/about" className="hover:text-blue-400">About</Link>
        </div>

        {/* Mobile Hamburger */}
        <button onClick={() => setIsOpen(!isOpen)} className="md:hidden focus:outline-none">
          {isOpen ? <X size={28} /> : <Menu size={28} />}
        </button>
      </div>

      {/* Mobile Dropdown */}
      {isOpen && (
        <div className="md:hidden mt-4 space-y-4 text-lg font-medium flex flex-col items-start pl-6">
          <Link to="/" onClick={() => setIsOpen(false)} className="hover:text-blue-400">Home</Link>
          <Link to="/image" onClick={() => setIsOpen(false)} className="hover:text-blue-400">Image</Link>
          <Link to="/video" onClick={() => setIsOpen(false)} className="hover:text-blue-400">Video</Link>
          <Link to="/about" onClick={() => setIsOpen(false)} className="hover:text-blue-400">About</Link>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
