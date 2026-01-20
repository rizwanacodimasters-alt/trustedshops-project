import React from 'react';
import { Link } from 'react-router-dom';
import { useLanguage } from '../context/LanguageContext';
import { translations } from '../utils/translations';
import { Button } from '../components/ui/button';
import { Card, CardContent } from '../components/ui/card';
import { TrendingUp, Users, Shield, Star, CheckCircle, Zap } from 'lucide-react';

const Business = () => {
  const { language } = useLanguage();
  const t = translations[language];

  const benefits = [
    {
      icon: <TrendingUp className="w-12 h-12" />,
      title: language === 'en' ? 'Increase Traffic' : language === 'ur' ? 'ٹریفک بڑھائیں' : 'حركة المرور الزيادة',
      description: language === 'en' ? 'Boost your click-through rates by up to 17% with authentic customer reviews' : language === 'ur' ? 'حقیقی کسٹمر ریویوز کے ساتھ اپنی کلک ریٹ 17٪ تک بڑھائیں' : 'عزز معدلات النقر بنسبة تصل إلى 17٪ مع تقييمات العملاء الأصلية',
      stat: '+17%'
    },
    {
      icon: <Users className="w-12 h-12" />,
      title: language === 'en' ? 'Improve Conversion' : language === 'ur' ? 'تبدیلی کو بہتر بنائیں' : 'تحسين التحويل',
      description: language === 'en' ? 'Increase conversion rate by up to 15% with trust badges and verified reviews' : language === 'ur' ? 'ٹرسٹ بیجز اور تصدیق شدہ ریویوز کے ساتھ تبدیلی کی شرح 15٪ تک بڑھائیں' : 'زيادة معدل التحويل بنسبة تصل إلى 15٪ مع شارات الثقة والمراجعات الموثقة',
      stat: '+15%'
    },
    {
      icon: <Shield className="w-12 h-12" />,
      title: language === 'en' ? 'Build Trust' : language === 'ur' ? 'اعتماد بنائیں' : 'بناء الثقة',
      description: language === 'en' ? 'Gain customer confidence with our verified trust badge and buyer protection' : language === 'ur' ? 'ہمارے تصدیق شدہ ٹرسٹ بیج اور خریدار کے تحفظ کے ساتھ صارفین کا اعتماد حاصل کریں' : 'اكتسب ثقة العملاء مع شارة الثقة الموثقة وحماية المشتري',
      stat: '100%'
    }
  ];

  const features = [
    {
      icon: <Star className="w-8 h-8" />,
      title: language === 'en' ? 'Collect Reviews' : language === 'ur' ? 'جائزے جمع کریں' : 'جمع التقييمات',
      description: language === 'en' ? 'Automatically collect authentic customer reviews' : language === 'ur' ? 'خودکار طور پر حقیقی کسٹمر ریویوز جمع کریں' : 'جمع تقييمات العملاء الأصلية تلقائيًا'
    },
    {
      icon: <Shield className="w-8 h-8" />,
      title: language === 'en' ? 'Trust Badge' : language === 'ur' ? 'ٹرسٹ بیج' : 'شارة الثقة',
      description: language === 'en' ? 'Display verified trust badge on your shop' : language === 'ur' ? 'اپنی دکان پر تصدیق شدہ ٹرسٹ بیج دکھائیں' : 'عرض شارة الثقة الموثقة على متجرك'
    },
    {
      icon: <CheckCircle className="w-8 h-8" />,
      title: language === 'en' ? 'Buyer Protection' : language === 'ur' ? 'خریدار کا تحفظ' : 'حماية المشتري',
      description: language === 'en' ? 'Money-back guarantee for all payment methods' : language === 'ur' ? 'تمام ادائیگی کے طریقوں کے لیے رقم واپسی کی ضمانت' : 'ضمان استرداد الأموال لجميع طرق الدفع'
    },
    {
      icon: <Zap className="w-8 h-8" />,
      title: language === 'en' ? 'Easy Integration' : language === 'ur' ? 'آسان انٹیگریشن' : 'التكامل السهل',
      description: language === 'en' ? 'Quick setup with all major e-commerce platforms' : language === 'ur' ? 'تمام بڑے ای کامرس پلیٹ فارمز کے ساتھ تیز سیٹ اپ' : 'الإعداد السريع مع جميع منصات التجارة الإلكترونية الرئيسية'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-yellow-50 via-amber-50 to-white py-20">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h1 className="text-5xl font-bold mb-6 text-gray-900">
                {language === 'en' ? 'Win Trust from Over 45 Million Shoppers' : language === 'ur' ? '45 ملین سے زیادہ خریداروں سے اعتماد جیتیں' : 'اكتسب ثقة أكثر من 45 مليون متسوق'}
              </h1>
              <p className="text-xl text-gray-600 mb-8">
                {language === 'en' ? 'Join the Community of Trust to gain and retain customers' : language === 'ur' ? 'صارفین کو حاصل کرنے اور برقرار رکھنے کے لیے اعتماد کی کمیونٹی میں شامل ہوں' : 'انضم إلى مجتمع الثقة لكسب العملاء والاحتفاظ بهم'}
              </p>
              <div className="flex space-x-4">
                <Link to="/signup">
                  <Button size="lg" className="bg-gradient-to-r from-yellow-400 to-amber-500 hover:from-yellow-500 hover:to-amber-600 text-black font-semibold">
                    {language === 'en' ? 'Get Started Free' : language === 'ur' ? 'مفت شروع کریں' : 'ابدأ مجانًا'}
                  </Button>
                </Link>
                <Link to="/contact">
                  <Button size="lg" variant="outline">
                    {language === 'en' ? 'Contact Sales' : language === 'ur' ? 'سیلز سے رابطہ کریں' : 'اتصل بالمبيعات'}
                  </Button>
                </Link>
              </div>
            </div>
            <div className="relative">
              <img
                src="https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=600&h=400&fit=crop"
                alt="Business Growth"
                className="rounded-2xl shadow-2xl"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <h2 className="text-4xl font-bold text-center mb-16 text-gray-900">
            {language === 'en' ? 'Grow Your Business' : language === 'ur' ? 'اپنے کاروبار کو بڑھائیں' : 'نمِّ عملك'}
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            {benefits.map((benefit, index) => (
              <Card key={index} className="text-center hover:shadow-xl transition-shadow duration-300">
                <CardContent className="p-8">
                  <div className="inline-flex p-4 bg-gradient-to-br from-yellow-400 to-amber-500 rounded-full text-white mb-6">
                    {benefit.icon}
                  </div>
                  <div className="text-4xl font-bold text-yellow-600 mb-4">{benefit.stat}</div>
                  <h3 className="text-xl font-bold mb-3 text-gray-900">{benefit.title}</h3>
                  <p className="text-gray-600">{benefit.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-gradient-to-br from-gray-50 to-yellow-50">
        <div className="container mx-auto px-4">
          <h2 className="text-4xl font-bold text-center mb-16 text-gray-900">
            {language === 'en' ? 'How It Works' : language === 'ur' ? 'یہ کیسے کام کرتا ہے' : 'كيف يعمل'}
          </h2>
          <div className="grid md:grid-cols-2 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="flex space-x-4 bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow duration-300">
                <div className="flex-shrink-0">
                  <div className="p-3 bg-gradient-to-br from-yellow-400 to-amber-500 rounded-lg text-white">
                    {feature.icon}
                  </div>
                </div>
                <div>
                  <h3 className="text-xl font-bold mb-2 text-gray-900">{feature.title}</h3>
                  <p className="text-gray-600">{feature.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-yellow-400 via-amber-500 to-yellow-400">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold text-black mb-6">
            {language === 'en' ? 'Start Building Trust Today' : language === 'ur' ? 'آج ہی اعتماد بنانا شروع کریں' : 'ابدأ ببناء الثقة اليوم'}
          </h2>
          <p className="text-xl text-black/80 mb-8">
            {language === 'en' ? 'Join thousands of successful online shops' : language === 'ur' ? 'ہزاروں کامیاب آن لائن دکانوں میں شامل ہوں' : 'انضم إلى آلاف المتاجر الناجحة عبر الإنترنت'}
          </p>
          <Link to="/signup">
            <Button size="lg" className="bg-black text-white hover:bg-gray-900 text-lg px-8 py-6">
              {language === 'en' ? 'Get Started Now' : language === 'ur' ? 'ابھی شروع کریں' : 'ابدأ الآن'}
            </Button>
          </Link>
        </div>
      </section>
    </div>
  );
};

export default Business;