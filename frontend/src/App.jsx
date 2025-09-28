import Home from "./components_new/Home/Home";
import { BrowserRouter as Router, Routes, Route, Link, useNavigate } from "react-router-dom";
import Prototype from "./components_new/Home/Prototype";
import About from "./components_new/Home/About";
import Profile from "./components_new/Home/Profile";
import Payment from "./components_new/Home/Payment";

export default function App() {
  return (
    <Router>
      {/*Gradient img*/}
      <img className="absolute top-0 right-0 opacity-60 -z-1" src="/gradient.png" alt="gradient-img"/>

      {/*Blur effect*/}
      <div className="h-0 w-[40rem] absolute top-[20%] 
      right-[-5%] shadow-[0_0_900px_20px_#ac7de3] -rotate-[30deg] -z-10"></div>

      <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/prototype" element={<Prototype />} />
          <Route path="/about" element={<About />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/payment" element={<Payment />} />
      </Routes>

    </Router>
  )
}