import React from 'react'

export default function FeaturesSection() {
  return (
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
  )
}
