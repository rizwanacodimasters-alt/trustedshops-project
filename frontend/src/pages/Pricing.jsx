import React from 'react';
import { Link } from 'react-router-dom';
import { useLanguage } from '../context/LanguageContext';
import { translations } from '../utils/translations';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Check } from 'lucide-react';

const Pricing = () => {
  const { language } = useLanguage();
  const t = translations[language];

  const plans = [
    {
      name: language === 'en' ? 'Starter' : language === 'ur' ? 'شروعات' : 'البداية',
      price: language === 'en' ? 'Free' : language === 'ur' ? 'مفت' : 'مجاني',
      description: language === 'en' ? 'Perfect for getting started' : language === 'ur' ? 'شروع کرنے کے لیے بہترین' : 'مثالي للبدء',
      features: [
        language === 'en' ? 'Up to 10 shops' : language === 'ur' ? '10 دکانیں تک' : 'ما يصل إلى 10 متاجر',
        language === 'en' ? 'Unlimited reviews' : language === 'ur' ? 'لامحدود جائزے' : 'تقييمات غير محدودة',
        language === 'en' ? 'Basic analytics' : language === 'ur' ? 'بنیادی تجزیات' : 'التحليلات الأساسية',
        language === 'en' ? 'Email support' : language === 'ur' ? 'ای میل سپورٹ' : 'دعم البريد الإلكتروني'
      ],
      cta: language === 'en' ? 'Start Free' : language === 'ur' ? 'مفت شروع کریں' : 'ابدأ مجانًا',
      popular: false
    },
    {
      name: language === 'en' ? 'Professional' : language === 'ur' ? 'پیشہ ورانہ' : 'احترافي',
      price: language === 'en' ? '$29/month' : language === 'ur' ? '$29/ماہ' : '$29/شهر',
      description: language === 'en' ? 'For growing businesses' : language === 'ur' ? 'بڑھتے ہوئے کاروبار کے لیے' : 'للشركات المتنامية',
      features: [
        language === 'en' ? 'Up to 50 shops' : language === 'ur' ? '50 دکانیں تک' : 'ما يصل إلى 50 متجرًا',
        language === 'en' ? 'Unlimited reviews' : language === 'ur' ? 'لامحدود جائزے' : 'تقييمات غير محدودة',
        language === 'en' ? 'Advanced analytics' : language === 'ur' ? 'جدید تجزیات' : 'التحليلات المتقدمة',
        language === 'en' ? 'Priority support' : language === 'ur' ? 'ترجیحی سپورٹ' : 'الدعم ذو الأولوية',
        language === 'en' ? 'Trust badge' : language === 'ur' ? 'ٹرسٹ بیج' : 'شارة الثقة',
        language === 'en' ? 'Custom branding' : language === 'ur' ? 'حسب ضرورت برانڈنگ' : 'العلامة التجارية المخصصة'
      ],
      cta: language === 'en' ? 'Get Started' : language === 'ur' ? 'شروع کریں' : 'ابدأ',
      popular: true
    },
    {
      name: language === 'en' ? 'Enterprise' : language === 'ur' ? 'انٹرپرائز' : 'المؤسسة',
      price: language === 'en' ? 'Custom' : language === 'ur' ? 'حسب ضرورت' : 'مخصص',
      description: language === 'en' ? 'For large organizations' : language === 'ur' ? 'بڑی تنظیموں کے لیے' : 'للمؤسسات الكبيرة',
      features: [
        language === 'en' ? 'Unlimited shops' : language === 'ur' ? 'لامحدود دکانیں' : 'متاجر غير محدودة',
        language === 'en' ? 'Unlimited reviews' : language === 'ur' ? 'لامحدود جائزے' : 'تقييمات غير محدودة',
        language === 'en' ? 'Custom analytics' : language === 'ur' ? 'حسب ضرورت تجزیات' : 'التحليلات المخصصة',
        language === 'en' ? '24/7 dedicated support' : language === 'ur' ? '24/7 وقف شدہ سپورٹ' : 'دعم مخصص على مدار الساعة',
        language === 'en' ? 'White-label solution' : language === 'ur' ? 'وائٹ لیبل حل' : 'حل العلامة البيضاء',
        language === 'en' ? 'API access' : language === 'ur' ? 'API رسائی' : 'الوصول إلى API',
        language === 'en' ? 'Custom integrations' : language === 'ur' ? 'حسب ضرورت انٹیگریشن' : 'التكاملات المخصصة'
      ],
      cta: language === 'en' ? 'Contact Sales' : language === 'ur' ? 'سیلز سے رابطہ کریں' : 'اتصل بالمبيعات',
      popular: false
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-20">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold mb-6 text-gray-900">
            {language === 'en' ? 'Simple, Transparent Pricing' : language === 'ur' ? 'سادہ، شفاف قیمتیں' : 'تسعير بسيط وشفاف'}
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            {language === 'en' ? 'Choose the plan that fits your business needs. No hidden fees, no surprises.' : language === 'ur' ? 'وہ منصوبہ منتخب کریں جو آپ کے کاروبار کی ضروریات کے مطابق ہو۔ کوئی چھپی ہوئی فیس نہیں، کوئی حیرت نہیں۔' : 'اختر الخطة التي تناسب احتياجات عملك. لا رسوم مخفية، لا مفاجآت.'}
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-8 max-w-7xl mx-auto">
          {plans.map((plan, index) => (
            <Card key={index} className={`relative ${plan.popular ? 'border-yellow-500 border-2 shadow-2xl transform scale-105' : ''}`}>
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <span className="bg-gradient-to-r from-yellow-400 to-amber-500 text-black px-4 py-1 rounded-full text-sm font-semibold">
                    {language === 'en' ? 'POPULAR' : language === 'ur' ? 'مقبول' : 'شائع'}
                  </span>
                </div>
              )}
              
              <CardHeader className="text-center pb-8">
                <CardTitle className="text-2xl font-bold mb-2">{plan.name}</CardTitle>
                <div className="text-4xl font-bold text-gray-900 mb-2">{plan.price}</div>
                <p className="text-gray-600">{plan.description}</p>
              </CardHeader>
              
              <CardContent>
                <ul className="space-y-4 mb-8">
                  {plan.features.map((feature, idx) => (
                    <li key={idx} className="flex items-start">
                      <Check className="w-5 h-5 text-green-500 mr-3 flex-shrink-0 mt-0.5" />
                      <span className="text-gray-700">{feature}</span>
                    </li>
                  ))}
                </ul>
                
                <Link to={plan.price === 'Free' || plan.price === 'مفت' || plan.price === 'مجاني' ? '/signup' : '/contact'}>
                  <Button 
                    className={`w-full ${
                      plan.popular 
                        ? 'bg-gradient-to-r from-yellow-400 to-amber-500 hover:from-yellow-500 hover:to-amber-600 text-black' 
                        : 'bg-gray-900 hover:bg-gray-800 text-white'
                    }`}
                    size="lg"
                  >
                    {plan.cta}
                  </Button>
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* FAQ Section */}
        <div className="mt-20 max-w-3xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12 text-gray-900">
            {language === 'en' ? 'Frequently Asked Questions' : language === 'ur' ? 'اکثر پوچھے گئے سوالات' : 'الأسئلة الشائعة'}
          </h2>
          <div className="space-y-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="font-bold text-lg mb-2">
                {language === 'en' ? 'Can I switch plans later?' : language === 'ur' ? 'کیا میں بعد میں منصوبہ تبدیل کر سکتا ہوں؟' : 'هل يمكنني تبديل الخطط لاحقًا؟'}
              </h3>
              <p className="text-gray-600">
                {language === 'en' ? 'Yes, you can upgrade or downgrade your plan at any time.' : language === 'ur' ? 'ہاں، آپ کسی بھی وقت اپنے منصوبے کو اپ گریڈ یا ڈاؤن گریڈ کر سکتے ہیں۔' : 'نعم، يمكنك ترقية أو تخفيض خطتك في أي وقت.'}
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="font-bold text-lg mb-2">
                {language === 'en' ? 'Is there a free trial?' : language === 'ur' ? 'کیا مفت ٹرائل ہے؟' : 'هل هناك نسخة تجريبية مجانية؟'}
              </h3>
              <p className="text-gray-600">
                {language === 'en' ? 'Yes, the Starter plan is completely free with no time limit.' : language === 'ur' ? 'ہاں، شروعاتی منصوبہ مکمل طور پر مفت ہے اور کوئی وقت کی حد نہیں ہے۔' : 'نعم، خطة البداية مجانية تمامًا بدون حد زمني.'}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Pricing;