import React from 'react'
import MicRecorder from "../MicRecorder"

export default function Prototype() {
  return (
    <section className="px-6 py-20 text-center">
      <h3 className="text-3xl font-bold mb-6">Prototype Demo</h3>
      <p className="text-lg text-gray-300 mb-8">
        This is a placeholder for the backend integration.  
        When the backend is ready, this page will connect directly to VPay’s voice payment system.
      </p>

      <div className="max-w-md mx-auto bg-purple-900/50 p-6 rounded-lg shadow">
        <h4 className="text-xl font-semibold mb-4">Try a Demo Payment</h4>
            <MicRecorder/>
      </div>
    </section>
  )
}
