import React, { useState, useEffect } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { translations } from '../utils/translations';
import { statisticsAPI } from '../services/api';
import { TrendingUp, Store, CreditCard } from 'lucide-react';

const Hero = () => {
  const { language } = useLanguage();
  const t = translations[language];
  const [statistics, setStatistics] = useState({
    shoppers: '45 Million',
    shops: '32,000',
    dailyTransactions: '1 Million'
  });

  useEffect(() => {
    fetchStatistics();
  }, []);

  const fetchStatistics = async () => {
    try {
      const response = await statisticsAPI.getStatistics();
      setStatistics(response.data);
    } catch (error) {
      console.error('Error fetching statistics:', error);
      // Keep default values on error
    }
  };

  const stats = [
    {
      icon: <TrendingUp className="w-8 h-8" />,
      value: statistics.shoppers,
      label: t.shoppers
    },
    {
      icon: <Store className="w-8 h-8" />,
      value: statistics.shops,
      label: t.shops
    },
    {
      icon: <CreditCard className="w-8 h-8" />,
      value: statistics.dailyTransactions,
      label: t.transactionsPerDay
    }
  ];

  return (
    <section className="relative bg-gradient-to-br from-yellow-50 via-amber-50 to-white py-20 overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-yellow-200 rounded-full opacity-20 blur-3xl"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-amber-200 rounded-full opacity-20 blur-3xl"></div>
      </div>

      <div className="container mx-auto px-4 relative z-10">
        <div className="text-center max-w-4xl mx-auto">
          {/* Main Heading */}
          <h1 className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-gray-900 via-gray-800 to-gray-900 bg-clip-text text-transparent">
            {t.heroTitle}
          </h1>
          
          {/* Subtitle */}
          <p className="text-xl md:text-2xl text-gray-600 mb-12 font-medium">
            {t.heroSubtitle}
          </p>

          {/* Statistics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-16">
            {stats.map((stat, index) => (
              <div
                key={index}
                className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1"
              >
                <div className="flex flex-col items-center space-y-4">
                  <div className="p-4 bg-gradient-to-br from-yellow-400 to-amber-500 rounded-full text-white">
                    {stat.icon}
                  </div>
                  <div className="text-4xl font-bold bg-gradient-to-r from-yellow-500 to-amber-600 bg-clip-text text-transparent">
                    {stat.value}
                  </div>
                  <div className="text-gray-600 font-medium text-center">
                    {stat.label}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;