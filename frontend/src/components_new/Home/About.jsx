import React from 'react'
import 'boxicons/css/boxicons.min.css'
import Header2 from './Header2'

function About() {
  return (
    <>
      <Header2 />
      <main className="flex flex-col items-center justify-center min-h-screen px-6 py-20 relative overflow-hidden">
      
      {/* Background gradient effects */}
      <div className="absolute inset-0 bg-gradient-to-br from-purple-900/20 via-transparent to-blue-900/20"></div>
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl"></div>
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl"></div>

      <div className="max-w-4xl mx-auto text-center z-10">
        
        {/* Tag box with gradient border */}
        <div className='relative w-48 h-10 bg-gradient-to-r from-[#656565] to-[#dbbdff] shadow-[0_0_15px_rgba(255,255,255,0.4)] rounded-full mx-auto mb-8'>
          <div className='absolute inset-[3px] bg-black rounded-full flex items-center justify-center gap-1'>
            <i className='bx bx-info-circle'></i> 
            ABOUT US
          </div>
        </div>

        {/* Main Heading */}
        <h1 className='text-4xl md:text-5xl lg:text-6xl font-semibold tracking-wider mb-8'>
          REVOLUTIONIZING
          <br />
          <span className="bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
            DIGITAL PAYMENTS
          </span>
        </h1>
        
        {/* Description */}
        <p className='text-lg md:text-xl tracking-wider text-gray-300 max-w-3xl mx-auto mb-12 leading-relaxed'>
          We’re building a smarter, hands-free payment experience where technology adapts to you — not the other way around. Fast, secure, and effortless, VPay makes transactions feel as natural as speaking.
        </p>
        <p className='text-lg md:text-xl tracking-wider text-gray-300 max-w-3xl mx-auto mb-12 leading-relaxed'>
          By removing the need for cards, taps, or swipes, VPay reduces checkout friction, speeds up transactions, and creates a more accessible payment option for everyone — from busy customers on the go to businesses seeking faster, smoother sales.
        </p>

        {/* Feature Cards */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          
          <div className="bg-gradient-to-br from-gray-900/50 to-gray-800/30 backdrop-blur-sm border border-gray-700/50 rounded-xl p-6 hover:border-purple-500/50 transition-all duration-300">
            <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-blue-500 rounded-lg flex items-center justify-center mb-4 mx-auto">
              <i className='bx bx-microphone text-xl text-white'></i>
            </div>
            <h3 className="text-xl font-semibold mb-3">Voice-First</h3>
            <p className="text-gray-400 text-sm leading-relaxed">
              Simply speak your payment commands. Our AI understands natural language and processes transactions instantly.
            </p>
          </div>

          <div className="bg-gradient-to-br from-gray-900/50 to-gray-800/30 backdrop-blur-sm border border-gray-700/50 rounded-xl p-6 hover:border-blue-500/50 transition-all duration-300">
            <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-teal-500 rounded-lg flex items-center justify-center mb-4 mx-auto">
                <i className='bxr bx-shield text-xl text-white'></i>
            </div>
            <h3 className="text-xl font-semibold mb-3">Secure</h3>
            <p className="text-gray-400 text-sm leading-relaxed">
            Encrypted and protected with biometric authentication, your transactions stay secure and private.

            </p>
          </div>

          <div className="bg-gradient-to-br from-gray-900/50 to-gray-800/30 backdrop-blur-sm border border-gray-700/50 rounded-xl p-6 hover:border-teal-500/50 transition-all duration-300">
            <div className="w-12 h-12 bg-gradient-to-r from-teal-500 to-green-500 rounded-lg flex items-center justify-center mb-4 mx-auto">
              <i className='bx bx-rocket text-xl text-white'></i>
            </div>
            <h3 className="text-xl font-semibold mb-3">Fast</h3>
            <p className="text-gray-400 text-sm leading-relaxed">
              Complete transactions in seconds. No more fumbling with cards or apps — just speak and pay.
            </p>
          </div>

        </div>

        {/* Mission Statement */}
        <div className="bg-gradient-to-r from-purple-900/20 to-blue-900/20 backdrop-blur-sm border border-gray-700/30 rounded-2xl p-8 max-w-2xl mx-auto">
          <h2 className="text-2xl font-semibold mb-4">Our Mission</h2>
          <p className="text-gray-300 leading-relaxed">
              Pay with your voice. VPay transforms digital payments into a natural, effortless experience, where technology adapts to you, not the other way around.
          </p>
        </div>

      </div>
    </main>
    </>
  );
}

export default About
