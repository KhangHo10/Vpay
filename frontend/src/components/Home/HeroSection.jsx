import React from 'react'
import { useNavigate } from "react-router-dom"


export default function HeroSection() {
    const navigate = useNavigate();

    return (
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
    )
}
