import 'boxicons/css/boxicons.min.css';

const Header2 = () => {
    // simple function to toggle the mobile menu
    const toggleMobileMenu = () => {
        // get the mobile menu element 
        const mobileMenu = document.getElementById('mobileMenu')

        //if it has the hidden class, remove it. otherwise add it
        if(mobileMenu.classList.contains('hidden')) {
            mobileMenu.classList.remove('hidden');
        } else {
            mobileMenu.classList.add('hidden');
        }
    }
  return (
    <header className="flex justify-between items-center py-4 px-4 lg:px-20">
        <h1 className="text-3x1 md:text-4x1 lg:text-5xl font-light m-0">
            VPay
        
        </h1>

        {/*Desktop navigation*/}

        <nav className="hidden md:flex items-center gap-12">
            <a className="text-base tracking-wider transition-colors hover:text-gray-300 z-50" href="#">
                Home
            </a>

            <a className="text-base tracking-wider transition-colors hover:text-gray-300 z-50" href="#">
                About
            </a>

            <a className="text-base tracking-wider transition-colors hover:text-gray-300 z-50" href="#">
                Payment
            </a>
            <a className="text-base tracking-wider transition-colors hover:text-gray-300 z-50" href="#">
                Profile
            </a>
        </nav>

        <button className="hidden md:block bg-[#a7a7a7] text-black py-3 px-8 rounded-full border-none font-medium transition-all duration-500 hover:bg-white cursor-pointer z-50">
            Prototype
        </button>

        {/*Mobile meny button - visible only on mobile*/}
        <button onClick={toggleMobileMenu} 
        className='md:hidden text-3xl p-2 z-50'>
            <i class='bx bx-menu'></i>
        </button>

        {/*Mobile meny button - hidden by defaulte*/}
        <div id='mobileMenu' className=' hidden fixed top-16 bottom-0 right-0 left-0 p-5 md:hidden z-40 bg-black bg-opacity-70 backdrop-blue- md'>
            <nav className='flex flex-col gap-6 items-center'>
            <a className="text-base tracking-wider transition-colors hover:text-gray-300 z-50" href="#">
                Home
            </a>

            <a className="text-base tracking-wider transition-colors hover:text-gray-300 z-50" href="#">
                About
            </a>

            <a className="text-base tracking-wider transition-colors hover:text-gray-300 z-50" href="#">
                Payment
            </a>
            <a className="text-base tracking-wider transition-colors hover:text-gray-300 z-50" href="#">
                Profile
            </a>
            </nav>
        </div>


    </header>
  )
}

export default Header2