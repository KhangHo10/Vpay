import React from "react";
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from "react-router-dom";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import Home from "./components/Home/Home";
import Prototype from "./components/Prototype";
import About from "./components/Home/About"
import FeaturesSection from "./components/Home/FeaturesSection"


function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-purple-800 to-indigo-900 text-white">
        {/* Navbar */}
        <Navbar/>
        {/* Page Routes */}
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/prototype" element={<Prototype />} />
          <Route path="/about" element={<About />} />
          <Route path="/featuresSection" element={<FeaturesSection />} />
        </Routes>

        {/* Footer */}
        <Footer/>
      </div>
    </Router>
  );
}

export default App;
