import React, { useState } from 'react';
import { useLanguage } from '../context/LanguageContext';
import { translations } from '../utils/translations';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Card, CardContent } from '../components/ui/card';
import { useToast } from '../hooks/use-toast';
import { Mail, Phone, MapPin, Clock } from 'lucide-react';

const Contact = () => {
  const { language } = useLanguage();
  const t = translations[language];
  const { toast } = useToast();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    
    // Simulate form submission
    setTimeout(() => {
      toast({
        title: language === 'en' ? 'Message Sent!' : language === 'ur' ? 'پیغام بھیج دیا گیا!' : 'تم إرسال الرسالة!',
        description: language === 'en' ? 'We\'ll get back to you soon.' : language === 'ur' ? 'ہم جلد ہی آپ سے رابطہ کریں گے۔' : 'سنعود إليك قريبًا.'
      });
      setFormData({ name: '', email: '', subject: '', message: '' });
      setLoading(false);
    }, 1000);
  };

  const contactInfo = [
    {
      icon: <Mail className="w-6 h-6" />,
      title: language === 'en' ? 'Email' : language === 'ur' ? 'ای میل' : 'البريد الإلكتروني',
      value: 'support@trustedshops.com'
    },
    {
      icon: <Phone className="w-6 h-6" />,
      title: language === 'en' ? 'Phone' : language === 'ur' ? 'فون' : 'الهاتف',
      value: '+49 221 99999999'
    },
    {
      icon: <MapPin className="w-6 h-6" />,
      title: language === 'en' ? 'Address' : language === 'ur' ? 'پتہ' : 'العنوان',
      value: 'Cologne, Germany'
    },
    {
      icon: <Clock className="w-6 h-6" />,
      title: language === 'en' ? 'Working Hours' : language === 'ur' ? 'کام کے اوقات' : 'ساعات العمل',
      value: language === 'en' ? 'Mon-Fri: 9AM-6PM CET' : language === 'ur' ? 'پیر-جمعہ: 9صبح-6شام' : 'الإثنين-الجمعة: 9ص-6م'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-20">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold mb-6 text-gray-900">
            {language === 'en' ? 'Get In Touch' : language === 'ur' ? 'رابطہ میں رہیں' : 'تواصل معنا'}
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            {language === 'en' ? 'Have questions? We\'d love to hear from you. Send us a message and we\'ll respond as soon as possible.' : language === 'ur' ? 'سوالات ہیں؟ ہم آپ سے سننا پسند کریں گے۔ ہمیں پیغام بھیجیں اور ہم جلد سے جلد جواب دیں گے۔' : 'لديك أسئلة؟ يسعدنا أن نسمع منك. أرسل لنا رسالة وسنرد في أقرب وقت ممكن.'}
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-12 max-w-6xl mx-auto">
          {/* Contact Form */}
          <Card>
            <CardContent className="p-8">
              <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                  <Label htmlFor="name">
                    {language === 'en' ? 'Name' : language === 'ur' ? 'نام' : 'الاسم'}
                  </Label>
                  <Input
                    id="name"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                    placeholder={language === 'en' ? 'Your name' : language === 'ur' ? 'آپ کا نام' : 'اسمك'}
                  />
                </div>

                <div>
                  <Label htmlFor="email">
                    {language === 'en' ? 'Email' : language === 'ur' ? 'ای میل' : 'البريد الإلكتروني'}
                  </Label>
                  <Input
                    id="email"
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    required
                    placeholder={language === 'en' ? 'your@email.com' : language === 'ur' ? 'your@email.com' : 'your@email.com'}
                  />
                </div>

                <div>
                  <Label htmlFor="subject">
                    {language === 'en' ? 'Subject' : language === 'ur' ? 'موضوع' : 'الموضوع'}
                  </Label>
                  <Input
                    id="subject"
                    value={formData.subject}
                    onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                    required
                    placeholder={language === 'en' ? 'How can we help?' : language === 'ur' ? 'ہم کیسے مدد کر سکتے ہیں؟' : 'كيف يمكننا مساعدتك؟'}
                  />
                </div>

                <div>
                  <Label htmlFor="message">
                    {language === 'en' ? 'Message' : language === 'ur' ? 'پیغام' : 'الرسالة'}
                  </Label>
                  <Textarea
                    id="message"
                    value={formData.message}
                    onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                    required
                    rows={5}
                    placeholder={language === 'en' ? 'Tell us more...' : language === 'ur' ? 'ہمیں مزید بتائیں...' : 'أخبرنا المزيد...'}
                  />
                </div>

                <Button
                  type="submit"
                  className="w-full bg-gradient-to-r from-yellow-400 to-amber-500 hover:from-yellow-500 hover:to-amber-600 text-black font-semibold"
                  disabled={loading}
                >
                  {loading 
                    ? (language === 'en' ? 'Sending...' : language === 'ur' ? 'بھیجا جا رہا ہے...' : 'جارٍ الإرسال...')
                    : (language === 'en' ? 'Send Message' : language === 'ur' ? 'پیغام بھیجیں' : 'إرسال الرسالة')
                  }
                </Button>
              </form>
            </CardContent>
          </Card>

          {/* Contact Information */}
          <div className="space-y-8">
            <div>
              <h2 className="text-3xl font-bold mb-6 text-gray-900">
                {language === 'en' ? 'Contact Information' : language === 'ur' ? 'رابطہ کی معلومات' : 'معلومات الاتصال'}
              </h2>
              <p className="text-gray-600 mb-8">
                {language === 'en' ? 'Reach out to us through any of these channels.' : language === 'ur' ? 'ان میں سے کسی بھی ذریعے سے ہم سے رابطہ کریں۔' : 'تواصل معنا من خلال أي من هذه القنوات.'}
              </p>
            </div>

            {contactInfo.map((info, index) => (
              <Card key={index} className="hover:shadow-lg transition-shadow duration-300">
                <CardContent className="p-6">
                  <div className="flex items-start space-x-4">
                    <div className="p-3 bg-gradient-to-br from-yellow-400 to-amber-500 rounded-lg text-white">
                      {info.icon}
                    </div>
                    <div>
                      <h3 className="font-semibold text-lg mb-1 text-gray-900">{info.title}</h3>
                      <p className="text-gray-600">{info.value}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}

            {/* Map Placeholder */}
            <div className="bg-gray-200 rounded-lg h-64 flex items-center justify-center">
              <p className="text-gray-500">
                {language === 'en' ? 'Map Location' : language === 'ur' ? 'نقشہ کی جگہ' : 'موقع الخريطة'}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Contact;