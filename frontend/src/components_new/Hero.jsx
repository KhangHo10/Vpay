import 'boxicons/css/boxicons.min.css';
import Spline from '@splinetool/react-spline';


const Hero = () => {
  return (
    <main className="flex lg:mt-20 flex-col lg:flex-row items-center justify-between min-h-[calc(90vh-6rem)]">

        <div className ="max-w-xl ml-[5%] z-10 mt-[90%] md:mt-[60%] lg:mt-0">
            {/*tag box-with gradient border*/}
            <div className='relative w-[95%] sm:w-48 h-10 bg-gradient-to-r from-[#656565] to-[#dbbdff] shadow-[0_0_15px_rgba(255,255,255,0.4)] rounded-full'>
                <div className='absolute inset-[3px] bg-black rounded-full flex items-center justify-center gap-1'>
                    <i class='bx bx-microphone'></i> 
                    INTRODUCING
                </div>
            </div>

            {/* Main Heading */}
            <h1 className='text-3xl sm:text-4xl md:text4xl lg:text-5xl font-semibold tracking-wider my-8'>
                VPAY:
                <br />
                PAY BY VOICE
            </h1>
            {/* Description */}
            <p class='text-base sm:text-lg tracking-wider text-gray-400 max-w-[25rem] lg:max-w-[30rem]'>
                Vpay is like Google Pay or Apple Pay - but smarter. Instead of tapping
                or swiping, just say what you want to pay, and let VPay handle the rest.
            </p>

            {/* BUTTONOSNFOSDJFlk */}
            <div className='flex gap-4 mt-12'>
                <a className='border border-[#2a2a2a] py-1 sm:py-3 px-16 sm:px-5 rounded-full sm:text-lg text-sm 
                font-semibold tracking-wider transition-all duration-300 
                hover:bg[#1a1a1a]' href="#">
                    Documentation <i class = 'bx bx-link-external'></i>
                </a>
                <a className='border border-[#2a2a2a] py-2 sm:py-3 px-8 sm:px-10 rounded-full sm:text-lg text-sm 
                font-semibold tracking-wider transition-all duration-300 
                hover:bg[#1a1a1a] bg-gray-300 text-black hover:text-white' href="#">
                    Get Started <i class = 'bx bx-link-external'></i>
                </a>
            </div>

        </div>
        {/* 3d bot */}
        <Spline className='absolute lg:top-0 top-[-20%] bottom-0 lg:left-[25%] sm:left-[-2%] h-full' scene="https://prod.spline.design/lbx2sTvagxoPcglg/scene.splinecode" />

    </main>
  )
}

export default Hero