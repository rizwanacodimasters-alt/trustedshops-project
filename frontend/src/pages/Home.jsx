import React, { useState, useRef, useEffect } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { translations } from '../utils/translations';
import { shopAPI, reviewAPI } from '../services/api';
import Hero from '../components/Hero';
import ShopCard from '../components/ShopCard';
import ReviewCard from '../components/ReviewCard';
import { Shield, CheckCircle, Award, ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Link } from 'react-router-dom';

const Home = () => {
  const { language } = useLanguage();
  const t = translations[language];
  const [currentReviewIndex, setCurrentReviewIndex] = useState(0);
  const [shops, setShops] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const shopsRef = useRef(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [shopsResponse, reviewsResponse] = await Promise.all([
        shopAPI.getShops({ limit: 20 }),
        reviewAPI.getReviews({ limit: 20 })
      ]);
      
      setShops(shopsResponse.data.data || []);
      setReviews(reviewsResponse.data.data || []);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const features = [
    {
      icon: <CheckCircle className="w-12 h-12" />,
      title: t.verifiedShops,
      description: t.verifiedShopsDesc
    },
    {
      icon: <Award className="w-12 h-12" />,
      title: t.realReviews,
      description: t.realReviewsDesc
    },
    {
      icon: <Shield className="w-12 h-12" />,
      title: t.buyerProtection,
      description: t.buyerProtectionDesc
    }
  ];

  const scrollShops = (direction) => {
    if (shopsRef.current) {
      const scrollAmount = 400;
      shopsRef.current.scrollBy({
        left: direction === 'left' ? -scrollAmount : scrollAmount,
        behavior: 'smooth'
      });
    }
  };

  const visibleReviews = reviews.slice(currentReviewIndex, currentReviewIndex + 3);

  const nextReviews = () => {
    if (currentReviewIndex + 3 < reviews.length) {
      setCurrentReviewIndex(currentReviewIndex + 3);
    }
  };

  const prevReviews = () => {
    if (currentReviewIndex - 3 >= 0) {
      setCurrentReviewIndex(currentReviewIndex - 3);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-500"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <Hero />

      {/* Safe Shopping Section */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-4xl font-bold mb-6 text-gray-900">
                {t.safeShoppingTitle}
              </h2>
              <p className="text-gray-600 text-lg leading-relaxed mb-8">
                {t.safeShoppingDesc}
              </p>
              <Link to="/signup">
                <Button size="lg" className="bg-gradient-to-r from-yellow-400 to-amber-500 hover:from-yellow-500 hover:to-amber-600 text-black font-semibold">
                  {t.becomePartOf}
                </Button>
              </Link>
              <p className="text-sm text-gray-500 mt-3">{t.noPaymentRequired}</p>
            </div>
            <div className="relative">
              <img
                src="https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=600&h=400&fit=crop"
                alt="Safe Shopping"
                className="rounded-2xl shadow-2xl"
              />
              <div className="absolute -bottom-6 -left-6 w-32 h-32 bg-yellow-400 rounded-full opacity-20 blur-2xl"></div>
              <div className="absolute -top-6 -right-6 w-32 h-32 bg-amber-400 rounded-full opacity-20 blur-2xl"></div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-gradient-to-br from-gray-50 to-yellow-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4 text-gray-900">
              {t.realShopsTitle}
            </h2>
            <p className="text-gray-600 text-lg max-w-2xl mx-auto">
              {t.realShopsDesc}
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className="bg-white p-8 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2 text-center"
              >
                <div className="inline-flex p-4 bg-gradient-to-br from-yellow-400 to-amber-500 rounded-full text-white mb-6">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-bold mb-3 text-gray-900">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Featured Shops Section */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between mb-12">
            <h2 className="text-4xl font-bold text-gray-900">{t.realShopsTitle}</h2>
            <div className="flex space-x-2">
              <Button
                variant="outline"
                size="icon"
                onClick={() => scrollShops('left')}
                className="rounded-full"
              >
                <ChevronLeft />
              </Button>
              <Button
                variant="outline"
                size="icon"
                onClick={() => scrollShops('right')}
                className="rounded-full"
              >
                <ChevronRight />
              </Button>
            </div>
          </div>

          <div
            ref={shopsRef}
            className="flex overflow-x-auto space-x-6 pb-4 scrollbar-hide"
            style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}
          >
            {shops.length > 0 ? (
              shops.map((shop) => (
                <div key={shop.id} className="flex-shrink-0 w-80">
                  <ShopCard shop={shop} />
                </div>
              ))
            ) : (
              <div className="text-center w-full py-12">
                <p className="text-gray-500">No shops available yet.</p>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* Reviews Section */}
      <section className="py-20 bg-gradient-to-br from-yellow-50 to-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4 text-gray-900">
              {t.reviewsTitle}
            </h2>
            <p className="text-gray-600 text-lg max-w-3xl mx-auto">
              {t.reviewsDesc}
            </p>
          </div>

          {reviews.length > 0 ? (
            <>
              <div className="grid md:grid-cols-3 gap-6 mb-8">
                {visibleReviews.map((review) => (
                  <ReviewCard key={review.id} review={review} />
                ))}
              </div>

              <div className="flex justify-center space-x-4">
                <Button
                  variant="outline"
                  onClick={prevReviews}
                  disabled={currentReviewIndex === 0}
                >
                  <ChevronLeft className="mr-2" /> Previous
                </Button>
                <Button
                  variant="outline"
                  onClick={nextReviews}
                  disabled={currentReviewIndex + 3 >= reviews.length}
                >
                  Next <ChevronRight className="ml-2" />
                </Button>
              </div>
            </>
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-500">No reviews available yet.</p>
            </div>
          )}
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-yellow-400 via-amber-500 to-yellow-400">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl md:text-5xl font-bold text-black mb-6">
            {t.becomePartOf}
          </h2>
          <p className="text-black/80 text-xl mb-8">{t.noPaymentRequired}</p>
          <Link to="/signup">
            <Button
              size="lg"
              className="bg-black text-white hover:bg-gray-900 text-lg px-8 py-6"
            >
              {t.startNow}
            </Button>
          </Link>
        </div>
      </section>
    </div>
  );
};

export default Home;