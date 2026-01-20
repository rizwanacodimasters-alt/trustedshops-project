import React from 'react';
import { useLanguage } from '../context/LanguageContext';
import { translations } from '../utils/translations';
import { Users, Target, Award, Globe } from 'lucide-react';

const About = () => {
  const { language } = useLanguage();
  const t = translations[language];

  const values = [
    {
      icon: <Users className="w-12 h-12" />,
      title: language === 'en' ? 'Trust First' : language === 'ur' ? 'پہلے اعتماد' : 'الثقة أولاً',
      description: language === 'en' ? 'We build trust between online shops and customers worldwide' : language === 'ur' ? 'ہم دنیا بھر میں آن لائن دکانوں اور کسٹمرز کے درمیان اعتماد قائم کرتے ہیں' : 'نبني الثقة بين المتاجر عبر الإنترنت والعملاء في جميع أنحاء العالم'
    },
    {
      icon: <Target className="w-12 h-12" />,
      title: language === 'en' ? 'Customer Focus' : language === 'ur' ? 'کسٹمر فوکس' : 'التركيز على العميل',
      description: language === 'en' ? 'Every decision we make puts our customers first' : language === 'ur' ? 'ہم جو بھی فیصلہ کرتے ہیں اس میں اپنے کسٹمرز کو پہلے رکھتے ہیں' : 'كل قرار نتخذه يضع عملاءنا في المقام الأول'
    },
    {
      icon: <Award className="w-12 h-12" />,
      title: language === 'en' ? 'Excellence' : language === 'ur' ? 'بہترین' : 'التميز',
      description: language === 'en' ? 'We strive for excellence in everything we do' : language === 'ur' ? 'ہم ہر کام میں بہترین ہونے کی کوشش کرتے ہیں' : 'نسعى جاهدين للتميز في كل ما نفعله'
    },
    {
      icon: <Globe className="w-12 h-12" />,
      title: language === 'en' ? 'Global Reach' : language === 'ur' ? 'عالمی رسائی' : 'الوصول العالمي',
      description: language === 'en' ? 'Serving customers in over 40 countries worldwide' : language === 'ur' ? 'دنیا بھر میں 40 سے زائد ممالک میں کسٹمرز کی خدمت' : 'خدمة العملاء في أكثر من 40 دولة حول العالم'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-yellow-50 via-amber-50 to-white py-20">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center">
            <h1 className="text-5xl font-bold mb-6 text-gray-900">
              {language === 'en' ? 'We Are #trstd' : language === 'ur' ? 'ہم #trstd ہیں' : 'نحن #trstd'}
            </h1>
            <p className="text-xl text-gray-600 leading-relaxed">
              {language === 'en' ? "In the age of fake, trust matters more than ever. We're passionate about creating a space you can recommend to your loved ones - a place where trust comes first. We call it #trstd, Europe's Community of Trust, where everything is based on authenticity." : language === 'ur' ? 'جعلی پن کے دور میں، اعتماد پہلے سے کہیں زیادہ اہم ہے۔ ہم ایک ایسی جگہ بنانے میں پرجوش ہیں جسے آپ اپنے پیاروں کو تجویز کر سکیں - ایک ایسی جگہ جہاں اعتماد پہلے آتا ہے۔' : 'في عصر التزييف، أصبحت الثقة أكثر أهمية من أي وقت مضى. نحن متحمسون لإنشاء مساحة يمكنك التوصية بها لأحبائك - مكان تأتي فيه الثقة أولاً.'}
            </p>
          </div>
        </div>
      </section>

      {/* Mission Section */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-2 gap-12 items-center max-w-6xl mx-auto">
            <div>
              <h2 className="text-4xl font-bold mb-6 text-gray-900">
                {language === 'en' ? 'Our Mission' : language === 'ur' ? 'ہمارا مشن' : 'مهمتنا'}
              </h2>
              <p className="text-lg text-gray-600 leading-relaxed mb-6">
                {language === 'en' ? 'Behind #trstd is the team at TrustedShops - we are committed to making online shopping safer, fairer and more trustworthy for everyone.' : language === 'ur' ? '#trstd کے پیچھے TrustedShops کی ٹیم ہے - ہم آن لائن خریداری کو سب کے لیے زیادہ محفوظ، منصفانہ اور قابل اعتماد بنانے کے لیے پرعزم ہیں۔' : 'خلف #trstd يقف فريق TrustedShops - نحن ملتزمون بجعل التسوق عبر الإنترنت أكثر أمانًا وعدالة وموثوقية للجميع.'}
              </p>
              <p className="text-lg text-gray-600 leading-relaxed">
                {language === 'en' ? 'We work with passion to create a space where trust is paramount. With over 45 million shoppers and 32,000 shops, we are building the largest community of trust in Europe.' : language === 'ur' ? 'ہم جوش کے ساتھ ایک ایسی جگہ بنانے کے لیے کام کرتے ہیں جہاں اعتماد سب سے اہم ہے۔ 45 ملین سے زائد خریداروں اور 32,000 دکانوں کے ساتھ، ہم یورپ میں اعتماد کی سب سے بڑی کمیونٹی بنا رہے ہیں۔' : 'نعمل بشغف لإنشاء مساحة تكون فيها الثقة ذات أهمية قصوى. مع أكثر من 45 مليون متسوق و32،000 متجر، نبني أكبر مجتمع للثقة في أوروبا.'}
              </p>
            </div>
            <div className="relative">
              <img
                src="https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=600&h=400&fit=crop"
                alt="Team"
                className="rounded-2xl shadow-2xl"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Values Section */}
      <section className="py-20 bg-gradient-to-br from-gray-50 to-yellow-50">
        <div className="container mx-auto px-4">
          <h2 className="text-4xl font-bold text-center mb-16 text-gray-900">
            {language === 'en' ? 'Our Values' : language === 'ur' ? 'ہماری قدریں' : 'قيمنا'}
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8 max-w-6xl mx-auto">
            {values.map((value, index) => (
              <div key={index} className="bg-white p-8 rounded-xl shadow-lg text-center hover:shadow-xl transition-shadow duration-300">
                <div className="inline-flex p-4 bg-gradient-to-br from-yellow-400 to-amber-500 rounded-full text-white mb-6">
                  {value.icon}
                </div>
                <h3 className="text-xl font-bold mb-3 text-gray-900">{value.title}</h3>
                <p className="text-gray-600">{value.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto text-center">
            <div>
              <div className="text-5xl font-bold bg-gradient-to-r from-yellow-500 to-amber-600 bg-clip-text text-transparent mb-2">
                45M+
              </div>
              <p className="text-gray-600 text-lg">
                {language === 'en' ? 'Shoppers' : language === 'ur' ? 'خریدار' : 'متسوقون'}
              </p>
            </div>
            <div>
              <div className="text-5xl font-bold bg-gradient-to-r from-yellow-500 to-amber-600 bg-clip-text text-transparent mb-2">
                32K+
              </div>
              <p className="text-gray-600 text-lg">
                {language === 'en' ? 'Shops' : language === 'ur' ? 'دکانیں' : 'متاجر'}
              </p>
            </div>
            <div>
              <div className="text-5xl font-bold bg-gradient-to-r from-yellow-500 to-amber-600 bg-clip-text text-transparent mb-2">
                1M+
              </div>
              <p className="text-gray-600 text-lg">
                {language === 'en' ? 'Daily Transactions' : language === 'ur' ? 'روزانہ لین دین' : 'معاملات يومية'}
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default About;