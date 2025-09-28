import React from 'react'
import 'boxicons/css/boxicons.min.css'
import Header2 from './Header2'

function Profile() {
  return (
    <>
      <Header2 />
      <main className="flex flex-col items-center justify-center min-h-screen px-6 py-20 relative overflow-hidden">
        
        {/* Background gradient effects */}
        <div className="absolute inset-0 bg-gradient-to-br from-indigo-900/20 via-transparent to-purple-900/20"></div>
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl"></div>

        <div className="max-w-6xl mx-auto text-center z-10">
          
          {/* Tag box with gradient border */}
          <div className='relative w-48 h-10 bg-gradient-to-r from-[#656565] to-[#dbbdff] shadow-[0_0_15px_rgba(255,255,255,0.4)] rounded-full mx-auto mb-8'>
            <div className='absolute inset-[3px] bg-black rounded-full flex items-center justify-center gap-1'>
              <i className='bx bx-team'></i> 
              TEAM
            </div>
          </div>

          {/* Main Heading */}
          <h1 className='text-4xl md:text-5xl lg:text-6xl font-semibold tracking-wider mb-8'>
            MEET OUR
            <br />
            <span className="bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
              TEAM
            </span>
          </h1>
          
          {/* Description */}
          <p className='text-lg md:text-xl tracking-wider text-gray-300 max-w-3xl mx-auto mb-12 leading-relaxed'>
            Get to know the passionate team behind VPay, working to revolutionize 
            voice-powered payments and create the future of financial technology.
          </p>

          {/* Team Members Section */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            
            {/* Team Member 1 */}
            <div className="bg-gradient-to-br from-gray-900/50 to-gray-800/30 backdrop-blur-sm border border-gray-700/50 rounded-xl p-6 hover:border-indigo-500/50 transition-all duration-300 group">
              <div className="w-24 h-24 bg-gradient-to-r from-indigo-500/20 to-purple-500/20 rounded-full border-2 border-dashed border-indigo-400/30 flex items-center justify-center mb-4 mx-auto group-hover:border-indigo-400/60 transition-colors duration-300">
              <img className="w-full h-full object-cover rounded-full" src="/miguel2.PNG" alt="profile" />
              </div>
              <h3 className="text-xl font-semibold mb-2 text-gray-200">Miguel Avila</h3>
              <p className="text-indigo-400 text-sm font-medium mb-3">Backend Developer</p>
              <p className="text-gray-400 text-sm leading-relaxed">
                  Built secure backend APIs, transaction flows, and implemented Google’s ADK and A2A protocol to power smart, agent-driven payments.              </p>
            </div>

            {/* Team Member 2 */}
            <div className="bg-gradient-to-br from-gray-900/50 to-gray-800/30 backdrop-blur-sm border border-gray-700/50 rounded-xl p-6 hover:border-purple-500/50 transition-all duration-300 group">
              <div className="w-24 h-24 bg-gradient-to-r from-purple-500/20 to-pink-500/20 rounded-full border-2 border-dashed border-purple-400/30 flex items-center justify-center mb-4 mx-auto group-hover:border-purple-400/60 transition-colors duration-300">
                  <img className="w-full h-full object-cover rounded-full" src="/zara.JPG" alt="profile" />
              </div>
              <h3 className="text-xl font-semibold mb-2 text-gray-200">Zara Maraj</h3>
              <p className="text-purple-400 text-sm font-medium mb-3">Frontend Developer</p>
              <p className="text-gray-400 text-sm leading-relaxed">
              Designed and implemented the VPay user interface, ensuring a responsive, interactive, and visually engaging experience.
              </p>
            </div>

            {/* Team Member 3 */}
            <div className="bg-gradient-to-br from-gray-900/50 to-gray-800/30 backdrop-blur-sm border border-gray-700/50 rounded-xl p-6 hover:border-blue-500/50 transition-all duration-300 group">
              <div className="w-24 h-24 bg-gradient-to-r from-blue-500/20 to-cyan-500/20 rounded-full border-2 border-dashed border-blue-400/30 flex items-center justify-center mb-4 mx-auto group-hover:border-blue-400/60 transition-colors duration-300">
                  <img className="w-full h-full object-cover rounded-full" src="/khang2.PNG" alt="profile" />
              </div>
              <h3 className="text-xl font-semibold mb-2 text-gray-200">Khang Ho</h3>
              <p className="text-blue-400 text-sm font-medium mb-3">Backend Developer</p>
              <p className="text-gray-400 text-sm leading-relaxed">
              Developed and maintained server-side logic, payment processing, and database integration for VPay.
              </p>
            </div>

            {/* Team Member 4 */}
            <div className="bg-gradient-to-br from-gray-900/50 to-gray-800/30 backdrop-blur-sm border border-gray-700/50 rounded-xl p-6 hover:border-green-500/50 transition-all duration-300 group">
              <div className="w-24 h-24 bg-gradient-to-r from-green-500/20 to-emerald-500/20 rounded-full border-2 border-dashed border-green-400/30 flex items-center justify-center mb-4 mx-auto group-hover:border-green-400/60 transition-colors duration-300">
                  <img className="w-full h-full object-cover rounded-full" src="/haru2.PNG" alt="profile" />
              </div>
              <h3 className="text-xl font-semibold mb-2 text-gray-200">Haruki Horiuchi</h3>
              <p className="text-green-400 text-sm font-medium mb-3">Full Stack Developer</p>
              <p className="text-gray-400 text-sm leading-relaxed">
              Bridged frontend and backend, integrating UI components with backend logic and helping deploy the full VPay system.
              </p>
            </div>

          </div>

        </div>
      </main>
    </>
  );
}

export default Profile