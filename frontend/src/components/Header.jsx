import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Search, User, Globe, Menu, X } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';
import { useAuth } from '../context/AuthContext';
import { translations } from '../utils/translations';
import { Button } from './ui/button';
import { Input } from './ui/input';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from './ui/dropdown-menu';

const Header = () => {
  const { language, changeLanguage } = useLanguage();
  const t = translations[language];
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const languages = [
    { code: 'en', name: 'English' },
    { code: 'ur', name: 'اردو' },
    { code: 'ar', name: 'العربية' }
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="text-2xl font-bold bg-gradient-to-r from-yellow-400 to-amber-500 bg-clip-text text-transparent">
              {t.logo}
            </div>
          </Link>

          {/* Search Bar */}
          <div className="hidden md:flex flex-1 max-w-md mx-4">
            <form 
              onSubmit={(e) => {
                e.preventDefault();
                if (searchQuery.trim()) {
                  navigate(`/shops?q=${encodeURIComponent(searchQuery)}`);
                } else {
                  navigate('/shops');
                }
              }}
              className="relative w-full"
            >
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
              <Input
                type="text"
                placeholder={language === 'en' ? 'Search shops...' : language === 'ur' ? 'دکانیں تلاش کریں...' : 'البحث عن المتاجر...'}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 pr-4"
              />
            </form>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-6">
            {/* Navigation Links */}
            <nav className="flex items-center space-x-6">
              <Link to="/shops" className="text-gray-700 hover:text-yellow-600 font-medium transition-colors">
                {language === 'en' ? 'Shops' : language === 'ur' ? 'دکانیں' : 'المتاجر'}
              </Link>
              <Link to="/fake-shops" className="text-gray-700 hover:text-yellow-600 font-medium transition-colors">
                {language === 'en' ? 'Fake Shop Check' : language === 'ur' ? 'جعلی دکان چیک' : 'فحص المتجر المزيف'}
              </Link>
              <Link to="/business" className="text-gray-700 hover:text-yellow-600 font-medium transition-colors">
                {language === 'en' ? 'For Business' : language === 'ur' ? 'کاروبار کے لیے' : 'للأعمال'}
              </Link>
              <Link to="/pricing" className="text-gray-700 hover:text-yellow-600 font-medium transition-colors">
                {language === 'en' ? 'Pricing' : language === 'ur' ? 'قیمتیں' : 'التسعير'}
              </Link>
              <Link to="/about" className="text-gray-700 hover:text-yellow-600 font-medium transition-colors">
                {t.aboutUs}
              </Link>
            </nav>

            {/* Language Selector */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm" className="flex items-center space-x-1">
                  <Globe size={18} />
                  <span>{languages.find(l => l.code === language)?.name}</span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                {languages.map((lang) => (
                  <DropdownMenuItem
                    key={lang.code}
                    onClick={() => changeLanguage(lang.code)}
                    className={language === lang.code ? 'bg-yellow-50' : ''}
                  >
                    {lang.name}
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>

            {/* User Menu */}
            {user ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="sm" className="flex items-center space-x-1">
                    <User size={18} />
                    <span>{user.full_name || t.myAccount}</span>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem asChild>
                    <Link to="/profile">{t.myAccount}</Link>
                  </DropdownMenuItem>
                  {user.role === 'admin' && (
                    <DropdownMenuItem asChild>
                      <Link to="/admin" className="text-red-600 font-semibold">Admin Panel</Link>
                    </DropdownMenuItem>
                  )}
                  <DropdownMenuItem onClick={logout}>
                    {t.logout}
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <div className="flex items-center space-x-3">
                <Link to="/signin">
                  <Button variant="ghost">{t.signIn}</Button>
                </Link>
                <Link to="/signup/business">
                  <Button variant="outline" className="hidden sm:flex">
                    Für Shops
                  </Button>
                </Link>
                <Link to="/signup">
                  <Button className="bg-gradient-to-r from-yellow-400 to-amber-500 hover:from-yellow-500 hover:to-amber-600 text-black">
                    {t.signUp}
                  </Button>
                </Link>
              </div>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="md:hidden p-2 rounded-lg hover:bg-gray-100"
          >
            {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden py-4 border-t">
            <div className="flex flex-col space-y-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                <input
                  type="text"
                  placeholder={t.search}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-400"
                />
              </div>
              
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Language:</span>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="outline" size="sm">
                      <Globe size={16} className="mr-2" />
                      {languages.find(l => l.code === language)?.name}
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent>
                    {languages.map((lang) => (
                      <DropdownMenuItem
                        key={lang.code}
                        onClick={() => changeLanguage(lang.code)}
                      >
                        {lang.name}
                      </DropdownMenuItem>
                    ))}
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>

              {!user && (
                <div className="flex flex-col space-y-2">
                  <Link to="/signin">
                    <Button variant="outline" className="w-full">{t.signIn}</Button>
                  </Link>
                  <Link to="/signup">
                    <Button className="w-full bg-gradient-to-r from-yellow-400 to-amber-500 hover:from-yellow-500 hover:to-amber-600 text-black">
                      {t.signUp}
                    </Button>
                  </Link>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;