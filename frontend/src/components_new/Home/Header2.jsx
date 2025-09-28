import 'boxicons/css/boxicons.min.css';
import { Link, useNavigate } from 'react-router-dom';

const Header2 = () => {
    const navigate = useNavigate();

    // Simple function to toggle the mobile menu
    const toggleMobileMenu = () => {
        // Get the mobile menu element 
        const mobileMenu = document.getElementById('mobileMenu');

        // If it has the hidden class, remove it. Otherwise add it
        if(mobileMenu.classList.contains('hidden')) {
            mobileMenu.classList.remove('hidden');
        } else {
            mobileMenu.classList.add('hidden');
        }
    };

    // Handle prototype button click
    const handlePrototypeClick = () => {
        navigate('/prototype');
    };

    return (
        <header className="flex justify-between items-center py-4 px-4 lg:px-20">
            <Link to="/" className="text-3xl md:text-4xl lg:text-5xl font-light m-0">
                VPay
            </Link>

            {/* Desktop navigation */}
            <nav className="hidden md:flex items-center gap-12">
                <Link 
                    to="/" 
                    className="text-base tracking-wider transition-colors hover:text-gray-300 z-50"
                >
                    Home
                </Link>

                <Link 
                    to="/about" 
                    className="text-base tracking-wider transition-colors hover:text-gray-300 z-50"
                >
                    About
                </Link>

                <Link 
                    to="/payment" 
                    className="text-base tracking-wider transition-colors hover:text-gray-300 z-50"
                >
                    Payment
                </Link>

                <Link 
                    to="/profile" 
                    className="text-base tracking-wider transition-colors hover:text-gray-300 z-50"
                >
                    Profile
                </Link>
            </nav>

            <button 
                onClick={handlePrototypeClick}
                className="hidden md:block bg-[#a7a7a7] text-black py-3 px-8 rounded-full border-none font-medium transition-all duration-500 hover:bg-white cursor-pointer z-50"
            >
                Prototype
            </button>

            {/* Mobile menu button - visible only on mobile */}
            <button 
                onClick={toggleMobileMenu} 
                className='md:hidden text-3xl p-2 z-50'
            >
                <i className='bx bx-menu'></i>
            </button>

            {/* Mobile menu - hidden by default */}
            <div id='mobileMenu' className='hidden fixed top-16 bottom-0 right-0 left-0 p-5 md:hidden z-40 bg-black bg-opacity-70 backdrop-blur-md'>
                <nav className='flex flex-col gap-6 items-center'>
                    <Link 
                        to="/" 
                        className="text-base tracking-wider transition-colors hover:text-gray-300 z-50"
                        onClick={toggleMobileMenu}
                    >
                        Home
                    </Link>

                    <Link 
                        to="/about" 
                        className="text-base tracking-wider transition-colors hover:text-gray-300 z-50"
                        onClick={toggleMobileMenu}
                    >
                        About
                    </Link>

                    <Link 
                        to="/payment" 
                        className="text-base tracking-wider transition-colors hover:text-gray-300 z-50"
                        onClick={toggleMobileMenu}
                    >
                        Payment
                    </Link>

                    <Link 
                        to="/profile" 
                        className="text-base tracking-wider transition-colors hover:text-gray-300 z-50"
                        onClick={toggleMobileMenu}
                    >
                        Profile
                    </Link>
                </nav>
            </div>
        </header>
    );
};

export default Header2;