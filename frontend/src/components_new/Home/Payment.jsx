import React from 'react'
import 'boxicons/css/boxicons.min.css'
import Header2 from './Header2'

function Payment() {
  return (
    <>
      <Header2 />
      <main className="flex flex-col items-center justify-center min-h-screen px-6 py-20 relative overflow-hidden">
        
        {/* Background gradient effects */}
        <div className="absolute inset-0 bg-gradient-to-br from-green-900/20 via-transparent to-blue-900/20"></div>
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-green-500/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl"></div>

        <div className="max-w-4xl mx-auto text-center z-10">
          
          {/* Tag box with gradient border */}
          <div className='relative w-48 h-10 bg-gradient-to-r from-[#656565] to-[#dbbdff] shadow-[0_0_15px_rgba(255,255,255,0.4)] rounded-full mx-auto mb-8'>
            <div className='absolute inset-[3px] bg-black rounded-full flex items-center justify-center gap-1'>
              <i className='bx bx-credit-card'></i> 
              PAYMENT
            </div>
          </div>

          {/* Main Heading */}
          <h1 className='text-4xl md:text-5xl lg:text-6xl font-semibold tracking-wider mb-8'>
            SEAMLESS
            <br />
            <span className="bg-gradient-to-r from-green-400 to-blue-400 bg-clip-text text-transparent">
              VOICE PAYMENTS
            </span>
          </h1>
          
          {/* Description */}
          <p className='text-lg md:text-xl tracking-wider text-gray-300 max-w-3xl mx-auto mb-12 leading-relaxed'>
            Experience the future of payments with VPay. Simply speak your payment intent 
            and let our AI handle the rest. Fast, secure, and incredibly intuitive.
          </p>

          {/* Payment Methods */}
          <div className="grid md:grid-cols-2 gap-8 mb-16">
            
            <div className="bg-gradient-to-br from-gray-900/50 to-gray-800/30 backdrop-blur-sm border border-gray-700/50 rounded-xl p-8 hover:border-green-500/50 transition-all duration-300">
              <div className="w-16 h-16 bg-gradient-to-r from-green-500 to-emerald-500 rounded-lg flex items-center justify-center mb-6 mx-auto">
                <i className='bx bx-microphone text-2xl text-white'></i>
              </div>
              <h3 className="text-2xl font-semibold mb-4">Voice Commands</h3>
              <p className="text-gray-400 leading-relaxed mb-6">
                "Pay John $50 for dinner" or "Send $20 to Mom" - our AI understands natural language 
                and processes payments instantly with voice recognition.
              </p>
              <div className="flex items-center justify-center gap-2 text-green-400 text-sm">
                <i className='bx bx-check-circle'></i>
                <span>Natural Language Processing</span>
              </div>
            </div>

            <div className="bg-gradient-to-br from-gray-900/50 to-gray-800/30 backdrop-blur-sm border border-gray-700/50 rounded-xl p-8 hover:border-blue-500/50 transition-all duration-300">
              <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center mb-6 mx-auto">
                <i className='bxr bx-shield-quarter text-2xl text-white'></i>
              </div>
              <h3 className="text-2xl font-semibold mb-4">Secure Processing</h3>
              <p className="text-gray-400 leading-relaxed mb-6">
                Every transaction is protected with encryption, biometric authentication, 
                and real-time fraud detection for complete peace of mind.
              </p>
              <div className="flex items-center justify-center gap-2 text-blue-400 text-sm">
                <i className='bx bx-check-circle'></i>
                <span>256-bit Encryption</span>
              </div>
            </div>

          </div>

          {/* How it Works */}
          <div className="bg-gradient-to-r from-green-900/20 to-blue-900/20 backdrop-blur-sm border border-gray-700/30 rounded-2xl p-8 max-w-3xl mx-auto mb-12">
            <h2 className="text-3xl font-semibold mb-8">How It Works</h2>
            
            <div className="grid md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="w-12 h-12 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-white font-bold">1</span>
                </div>
                <h4 className="font-semibold mb-2">Speak</h4>
                <p className="text-gray-400 text-sm">Say your payment intent naturally</p>
              </div>
              
              <div className="text-center">
                <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-white font-bold">2</span>
                </div>
                <h4 className="font-semibold mb-2">Process</h4>
                <p className="text-gray-400 text-sm">AI analyzes and confirms details</p>
              </div>
              
              <div className="text-center">
                <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-white font-bold">3</span>
                </div>
                <h4 className="font-semibold mb-2">Complete</h4>
                <p className="text-gray-400 text-sm">Transaction completed securely</p>
              </div>
            </div>
          </div>

          {/* CTA Button */}
          <div className="flex justify-center">
            <button className="bg-gradient-to-r from-green-500 to-blue-500 hover:from-green-600 hover:to-blue-600 text-white font-semibold py-4 px-12 rounded-full text-lg transition-all duration-300 transform hover:scale-105 shadow-lg">
              Try Voice Payment
              <i className='bx bx-microphone ml-2'></i>
            </button>
          </div>

        </div>
      </main>
    </>
  );
}

export default Payment