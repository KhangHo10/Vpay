import Header2 from "./components_new/Header2";
import Hero from "./components_new/Hero";

export default function App() {
  return (
    <main>
      {/*Gradient img*/}
      <img className="absolute top-0 right-0 opacity-60 -z-1" src="/gradient.png" alt="gradient-img"/>

      {/*Blur effect*/}
      <div className="h-0 w-[40rem] absolute top-[20%] 
      right-[-5%] shadow-[0_0_900px_20px_#ac7de3] -rotate-[30deg] -z-10"></div>

      <Header2/>
      <Hero />

    </main>
  )
}