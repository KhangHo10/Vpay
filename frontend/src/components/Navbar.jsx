import React from 'react'
import { Link } from "react-router-dom";

export default function Navbar() {
  return (
    <header className="flex justify-between items-center px-8 py-4">
        <h1 className="text-2xl font-bold">VPay</h1>
        <nav className="space-x-6">
            <Link to="/" className="hover:text-purple-300">Home</Link>
            <Link to="/about" className="hover:text-purple-300">About</Link>
            <Link to="/prototype" className="hover:text-purple-300">Prototype</Link>
        </nav>
    </header>
  )
}
