import React, { useState } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { translations } from '../utils/translations';
import { ChevronDown, ChevronUp } from 'lucide-react';

const FAQ = () => {
  const { language } = useLanguage();
  const t = translations[language];
  const [openIndex, setOpenIndex] = useState(null);

  const faqs = [
    {
      question: language === 'en' ? 'What is TrustedShops?' : language === 'ur' ? 'TrustedShops کیا ہے؟' : 'ما هو TrustedShops؟',
      answer: language === 'en' ? 'TrustedShops is Europe\'s Community of Trust, connecting real shops with real shoppers. We provide trust badges, buyer protection, and authentic customer reviews to make online shopping safer and more trustworthy.' : language === 'ur' ? 'TrustedShops یورپ کی اعتماد کی کمیونٹی ہے، جو حقیقی دکانوں کو حقیقی خریداروں سے جوڑتی ہے۔ ہم ٹرسٹ بیج، خریدار کی حفاظت، اور مستند کسٹمر ریویوز فراہم کرتے ہیں۔' : 'TrustedShops هو مجتمع الثقة في أوروبا، يربط المتاجر الحقيقية بالمتسوقين الحقيقيين. نقدم شارات الثقة وحماية المشتري ومراجعات العملاء الأصلية.'
    },
    {
      question: language === 'en' ? 'How do I register my shop?' : language === 'ur' ? 'میں اپنی دکان کیسے رجسٹر کروں؟' : 'كيف أسجل متجري؟',
      answer: language === 'en' ? 'Simply sign up for a free account, then navigate to your dashboard to add your shop details. Once verified, you can start collecting reviews and displaying the trust badge.' : language === 'ur' ? 'بس ایک مفت اکاؤنٹ کے لیے سائن اپ کریں، پھر اپنے ڈیش بورڈ پر جائیں اور اپنی دکان کی تفصیلات شامل کریں۔ تصدیق ہونے کے بعد، آپ جائزے جمع کرنا شروع کر سکتے ہیں۔' : 'قم بالتسجيل للحصول على حساب مجاني، ثم انتقل إلى لوحة القيادة لإضافة تفاصيل متجرك. بعد التحقق، يمكنك البدء في جمع المراجعات.'
    },
    {
      question: language === 'en' ? 'How much does it cost?' : language === 'ur' ? 'اس کی قیمت کتنی ہے؟' : 'كم يكلف؟',
      answer: language === 'en' ? 'We offer a free Starter plan to get you started. As your business grows, you can upgrade to our Professional ($29/month) or Enterprise (custom pricing) plans.' : language === 'ur' ? 'ہم شروع کرنے کے لیے ایک مفت سٹارٹر پلان پیش کرتے ہیں۔ جیسے جیسے آپ کا کاروبار بڑھتا ہے، آپ ہمارے پروفیشنل ($29/ماہ) یا انٹرپرائز پلانز میں اپ گریڈ کر سکتے ہیں۔' : 'نقدم خطة مجانية للمبتدئين. مع نمو عملك، يمكنك الترقية إلى خططنا الاحترافية (29 دولارًا/شهر) أو المؤسسة.'
    },
    {
      question: language === 'en' ? 'Are the reviews authentic?' : language === 'ur' ? 'کیا ریویوز مستند ہیں؟' : 'هل المراجعات أصلية؟',
      answer: language === 'en' ? 'Yes! All reviews on #trstd are verified and come from real customers who have made actual purchases. We have strict verification processes to ensure authenticity.' : language === 'ur' ? 'ہاں! #trstd پر تمام ریویوز تصدیق شدہ ہیں اور حقیقی کسٹمرز سے آتے ہیں جنہوں نے اصل خریداری کی ہے۔ ہمارے پاس مستند تصدیق کے سخت عمل ہیں۔' : 'نعم! جميع المراجعات على #trstd موثقة وتأتي من عملاء حقيقيين قاموا بعمليات شراء فعلية.'
    },
    {
      question: language === 'en' ? 'What is buyer protection?' : language === 'ur' ? 'خریدار کی حفاظت کیا ہے؟' : 'ما هي حماية المشتري؟',
      answer: language === 'en' ? 'Buyer protection provides customers with a money-back guarantee up to €20,000 for all payment methods. If something goes wrong with their order, they are protected.' : language === 'ur' ? 'خریدار کی حفاظت کسٹمرز کو تمام ادائیگی کے طریقوں کے لیے €20,000 تک کی رقم واپسی کی ضمانت فراہم کرتی ہے۔ اگر ان کے آرڈر میں کچھ غلط ہو جاتا ہے، تو وہ محفوظ ہیں۔' : 'توفر حماية المشتري ضمان استرداد الأموال حتى €20,000 لجميع طرق الدفع. إذا حدث خطأ ما في طلبهم، فهم محميون.'
    },
    {
      question: language === 'en' ? 'How do I integrate TrustedShops into my shop?' : language === 'ur' ? 'میں TrustedShops کو اپنی دکان میں کیسے انٹیگریٹ کروں؟' : 'كيف أدمج TrustedShops في متجري؟',
      answer: language === 'en' ? 'We offer easy integration with all major e-commerce platforms including Shopify, WooCommerce, Magento, and more. Simply install our plugin or add a code snippet to your website.' : language === 'ur' ? 'ہم تمام بڑے ای کامرس پلیٹ فارمز جیسے Shopify، WooCommerce، Magento اور بہت سے کے ساتھ آسان انٹیگریشن پیش کرتے ہیں۔ بس ہمارا پلگ ان انسٹال کریں یا اپنی ویب سائٹ میں کوڈ شامل کریں۔' : 'نقدم تكاملًا سهلًا مع جميع منصات التجارة الإلكترونية الرئيسية بما في ذلك Shopify وWooCommerce وMagento.'
    },
    {
      question: language === 'en' ? 'Can I cancel my subscription anytime?' : language === 'ur' ? 'کیا میں کسی بھی وقت اپنی سبسکرپشن منسوخ کر سکتا ہوں؟' : 'هل يمكنني إلغاء اشتراكي في أي وقت؟',
      answer: language === 'en' ? 'Yes, you can cancel your subscription at any time. The free Starter plan has no commitment, and paid plans can be cancelled with 30 days notice.' : language === 'ur' ? 'ہاں، آپ کسی بھی وقت اپنی سبسکرپشن منسوخ کر سکتے ہیں۔ مفت سٹارٹر پلان میں کوئی عزم نہیں ہے، اور ادا شدہ پلانز 30 دن کے نوٹس کے ساتھ منسوخ کیے جا سکتے ہیں۔' : 'نعم، يمكنك إلغاء اشتراكك في أي وقت. الخطة المجانية ليس لها التزام، ويمكن إلغاء الخطط المدفوعة بإشعار مدته 30 يومًا.'
    },
    {
      question: language === 'en' ? 'Do you offer customer support?' : language === 'ur' ? 'کیا آپ کسٹمر سپورٹ پیش کرتے ہیں؟' : 'هل تقدمون دعم العملاء؟',
      answer: language === 'en' ? 'Yes! We offer email support for all plans, priority support for Professional plans, and dedicated 24/7 support for Enterprise customers.' : language === 'ur' ? 'ہاں! ہم تمام پلانز کے لیے ای میل سپورٹ، پروفیشنل پلانز کے لیے ترجیحی سپورٹ، اور انٹرپرائز کسٹمرز کے لیے 24/7 وقف شدہ سپورٹ پیش کرتے ہیں۔' : 'نعم! نقدم دعم البريد الإلكتروني لجميع الخطط، ودعم ذو أولوية للخطط الاحترافية، ودعم مخصص على مدار الساعة لعملاء المؤسسة.'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-20">
      <div className="container mx-auto px-4 max-w-4xl">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold mb-6 text-gray-900">
            {language === 'en' ? 'Frequently Asked Questions' : language === 'ur' ? 'عمومی سوالات' : 'الأسئلة الشائعة'}
          </h1>
          <p className="text-xl text-gray-600">
            {language === 'en' ? 'Find answers to common questions about TrustedShops' : language === 'ur' ? 'TrustedShops کے بارے میں عام سوالات کے جوابات تلاش کریں' : 'اعثر على إجابات للأسئلة الشائعة حول TrustedShops'}
          </p>
        </div>

        {/* FAQ Accordion */}
        <div className="space-y-4">
          {faqs.map((faq, index) => (
            <div key={index} className="bg-white rounded-lg shadow-md overflow-hidden">
              <button
                onClick={() => setOpenIndex(openIndex === index ? null : index)}
                className="w-full px-6 py-4 flex items-center justify-between text-left hover:bg-gray-50 transition-colors duration-200"
              >
                <span className="font-semibold text-lg text-gray-900">{faq.question}</span>
                {openIndex === index ? (
                  <ChevronUp className="w-5 h-5 text-gray-500 flex-shrink-0" />
                ) : (
                  <ChevronDown className="w-5 h-5 text-gray-500 flex-shrink-0" />
                )}
              </button>
              {openIndex === index && (
                <div className="px-6 py-4 border-t bg-gray-50">
                  <p className="text-gray-700 leading-relaxed">{faq.answer}</p>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Contact CTA */}
        <div className="mt-16 text-center bg-gradient-to-r from-yellow-400 to-amber-500 rounded-2xl p-12">
          <h2 className="text-3xl font-bold text-black mb-4">
            {language === 'en' ? 'Still have questions?' : language === 'ur' ? 'ابھی بھی سوالات ہیں؟' : 'لا تزال لديك أسئلة؟'}
          </h2>
          <p className="text-black/80 mb-6">
            {language === 'en' ? 'Our team is here to help. Contact us anytime.' : language === 'ur' ? 'ہماری ٹیم مدد کے لیے حاضر ہے۔ کسی بھی وقت ہم سے رابطہ کریں۔' : 'فريقنا هنا للمساعدة. اتصل بنا في أي وقت.'}
          </p>
          <a href="/contact">
            <button className="bg-black text-white px-8 py-3 rounded-lg font-semibold hover:bg-gray-900 transition-colors duration-200">
              {language === 'en' ? 'Contact Us' : language === 'ur' ? 'ہم سے رابطہ کریں' : 'اتصل بنا'}
            </button>
          </a>
        </div>
      </div>
    </div>
  );
};

export default FAQ;