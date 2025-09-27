import React from "react";
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from "react-router-dom";

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-purple-800 to-indigo-900 text-white">
        {/* Navbar */}
        <header className="flex justify-between items-center px-8 py-4">
          <h1 className="text-2xl font-bold">VPay</h1>
          <nav className="space-x-6">
            <Link to="/" className="hover:text-purple-300">Home</Link>
            <Link to="/about" className="hover:text-purple-300">About</Link>
            <Link to="/prototype" className="hover:text-purple-300">Prototype</Link>
          </nav>
        </header>

        {/* Page Routes */}
        <Routes>
          {/* Home */}
          <Route path="/" element={<Home />} />

          {/* About */}
          <Route
            path="/about"
            element={
              <section className="px-6 py-20">
                <h3 className="text-3xl font-bold mb-6 text-center">About VPay</h3>
                <p className="max-w-3xl mx-auto text-center text-gray-300 text-lg">
                  VPay was built with one mission: to make payments easier, faster, and more secure.
                  By combining voice recognition and financial technology, we’re creating a future
                  where you can pay for anything without even reaching for your wallet.
                </p>
              </section>
            }
          />

          {/* Prototype */}
          <Route path="/prototype" element={<Prototype />} />
        </Routes>

        {/* Footer */}
        <footer className="px-6 py-8 text-center text-gray-400">
          © {new Date().getFullYear()} VPay. All rights reserved.
        </footer>
      </div>
    </Router>
  );
}

/* ---------- Home Page ---------- */
function Home() {
  const navigate = useNavigate();

  return (
    <>
      {/* Hero Section */}
      <main className="flex flex-col items-center text-center px-6 py-20">
        <h2 className="text-5xl md:text-6xl font-extrabold mb-6">
          Pay with just your <span className="text-purple-300">Voice</span>
        </h2>
        <p className="max-w-2xl text-lg md:text-xl text-gray-300 mb-8">
          VPay is like Google Pay or Apple Pay — but smarter. Instead of tapping or swiping,
          just say what you want to pay, and let VPay handle the rest.
        </p>
        <button
          onClick={() => navigate("/prototype")}
          className="px-6 py-3 bg-purple-600 rounded-lg shadow-lg hover:bg-purple-500 transition"
        >
          Get Started
        </button>
      </main>

      {/* Features Section */}
      <section className="px-6 py-16 bg-purple-900/50">
        <h3 className="text-3xl font-bold mb-10 text-center">Features</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="p-6 bg-purple-800 rounded-xl shadow hover:scale-105 transition">
            <h4 className="text-xl font-semibold mb-2">Voice Payments</h4>
            <p>Pay instantly using only your voice, with built-in security.</p>
          </div>
          <div className="p-6 bg-purple-800 rounded-xl shadow hover:scale-105 transition">
            <h4 className="text-xl font-semibold mb-2">Fast & Secure</h4>
            <p>Transactions happen in seconds with encryption protection.</p>
          </div>
          <div className="p-6 bg-purple-800 rounded-xl shadow hover:scale-105 transition">
            <h4 className="text-xl font-semibold mb-2">Global Support</h4>
            <p>Works across multiple countries and currencies.</p>
          </div>
        </div>
      </section>
    </>
  );
}

/* ---------- Prototype Page ---------- */
function Prototype() {
  return (
    <section className="px-6 py-20 text-center">
      <h3 className="text-3xl font-bold mb-6">Prototype Demo</h3>
      <p className="text-lg text-gray-300 mb-8">
        This is a placeholder for the backend integration.  
        When the backend is ready, this page will connect directly to VPay’s voice payment system.
      </p>

      <div className="max-w-md mx-auto bg-purple-900/50 p-6 rounded-lg shadow">
        <h4 className="text-xl font-semibold mb-4">Try a Demo Payment</h4>
        <input
          type="text"
          placeholder="Say or type amount (e.g. $25)"
          className="w-full p-3 mb-4 rounded bg-purple-800 text-white focus:outline-none"
        />
        <button className="w-full p-3 bg-purple-600 rounded-lg shadow hover:bg-purple-500 transition">
          Simulate Payment
        </button>
      </div>
    </section>
  );
}

export default App;
