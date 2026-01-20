import React from 'react';
import { Link } from 'react-router-dom';
import { useLanguage } from '../context/LanguageContext';
import { translations } from '../utils/translations';
import { Facebook, Twitter, Instagram, Linkedin } from 'lucide-react';

const Footer = () => {
  const { language } = useLanguage();
  const t = translations[language];

  const footerLinks = [
    { label: t.aboutUs, path: '/about' },
    { label: t.contact, path: '/contact' },
    { label: language === 'en' ? 'Business' : language === 'ur' ? 'کاروبار' : 'الأعمال', path: '/business' },
    { label: language === 'en' ? 'Pricing' : language === 'ur' ? 'قیمتیں' : 'التسعير', path: '/pricing' },
    { label: t.faq, path: '/faq' }
  ];

  const socialLinks = [
    { icon: <Facebook size={20} />, url: '#' },
    { icon: <Twitter size={20} />, url: '#' },
    { icon: <Instagram size={20} />, url: '#' },
    { icon: <Linkedin size={20} />, url: '#' }
  ];

  return (
    <footer className="bg-gray-900 text-white py-12">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          {/* Brand */}
          <div>
            <h3 className="text-2xl font-bold bg-gradient-to-r from-yellow-400 to-amber-500 bg-clip-text text-transparent mb-4">
              {t.logo}
            </h3>
            <p className="text-gray-400 mb-4">
              Europe's Community of Trust. Connecting real shops with real shoppers.
            </p>
            <div className="flex space-x-4">
              {socialLinks.map((social, index) => (
                <a
                  key={index}
                  href={social.url}
                  className="w-10 h-10 rounded-full bg-gray-800 hover:bg-gradient-to-r hover:from-yellow-400 hover:to-amber-500 flex items-center justify-center transition-all duration-300"
                >
                  {social.icon}
                </a>
              ))}
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-lg font-semibold mb-4">Quick Links</h4>
            <ul className="space-y-2">
              {footerLinks.map((link, index) => (
                <li key={index}>
                  <Link
                    to={link.path}
                    className="text-gray-400 hover:text-yellow-400 transition-colors duration-300"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Newsletter */}
          <div>
            <h4 className="text-lg font-semibold mb-4">Stay Updated</h4>
            <p className="text-gray-400 mb-4 text-sm">
              Subscribe to our newsletter for the latest updates and offers.
            </p>
            <div className="flex">
              <input
                type="email"
                placeholder="Your email"
                className="flex-1 px-4 py-2 rounded-l-lg bg-gray-800 border border-gray-700 focus:outline-none focus:border-yellow-400"
              />
              <button className="px-6 py-2 bg-gradient-to-r from-yellow-400 to-amber-500 hover:from-yellow-500 hover:to-amber-600 text-black font-semibold rounded-r-lg transition-all duration-300">
                Subscribe
              </button>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-gray-800 pt-8 text-center">
          <p className="text-gray-400 text-sm">
            © 2025 TrustedShops Clone. All rights reserved. Built with trust and transparency.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;