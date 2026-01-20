import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useLanguage } from '../context/LanguageContext';
import { useAuth } from '../context/AuthContext';
import { translations } from '../utils/translations';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { useToast } from '../hooks/use-toast';
import { FormError, FormSuccess, PasswordStrengthIndicator } from '../components/ui/form-error';
import { validateEmail, validatePassword, validatePasswordMatch, validateName, calculatePasswordStrength } from '../utils/validation';
import { Mail, Lock, User, Eye, EyeOff } from 'lucide-react';

const SignUp = () => {
  const { language } = useLanguage();
  const t = translations[language];
  const { register } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [passwordStrength, setPasswordStrength] = useState(null);

  // Real-time validation
  useEffect(() => {
    const newErrors = {};
    
    if (touched.fullName) {
      const nameValidation = validateName(formData.fullName);
      if (!nameValidation.valid) newErrors.fullName = nameValidation.message;
    }
    
    if (touched.email) {
      const emailValidation = validateEmail(formData.email);
      if (!emailValidation.valid) newErrors.email = emailValidation.message;
    }
    
    if (touched.password) {
      const passwordValidation = validatePassword(formData.password);
      if (!passwordValidation.valid) newErrors.password = passwordValidation.message;
      setPasswordStrength(calculatePasswordStrength(formData.password));
    }
    
    if (touched.confirmPassword) {
      const matchValidation = validatePasswordMatch(formData.password, formData.confirmPassword);
      if (!matchValidation.valid) newErrors.confirmPassword = matchValidation.message;
    }
    
    setErrors(newErrors);
  }, [formData, touched]);

  const handleBlur = (field) => {
    setTouched({ ...touched, [field]: true });
  };

  const handleChange = (field, value) => {
    setFormData({ ...formData, [field]: value });
  };

  const validateForm = () => {
    const nameValidation = validateName(formData.fullName);
    const emailValidation = validateEmail(formData.email);
    const passwordValidation = validatePassword(formData.password);
    const matchValidation = validatePasswordMatch(formData.password, formData.confirmPassword);
    
    const newErrors = {};
    if (!nameValidation.valid) newErrors.fullName = nameValidation.message;
    if (!emailValidation.valid) newErrors.email = emailValidation.message;
    if (!passwordValidation.valid) newErrors.password = passwordValidation.message;
    if (!matchValidation.valid) newErrors.confirmPassword = matchValidation.message;
    
    setErrors(newErrors);
    setTouched({ fullName: true, email: true, password: true, confirmPassword: true });
    
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      toast({
        title: "Fehler",
        description: "Bitte korrigieren Sie die Fehler im Formular",
        variant: "destructive"
      });
      return;
    }

    setLoading(true);
    
    const result = await register({
      full_name: formData.fullName,
      email: formData.email,
      password: formData.password,
      role: 'shopper'
    });
    
    setLoading(false);
    
    if (result.success) {
      toast({
        title: "Erfolg!",
        description: "Ihr Account wurde erstellt. Bitte verifizieren Sie Ihre E-Mail.",
      });
      
      // Redirect to email verification
      navigate('/email-verification', { state: { email: formData.email } });
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-yellow-50 via-amber-50 to-white py-12 px-4">
      <Card className="w-full max-w-md shadow-xl">
        <CardHeader className="text-center">
          <CardTitle className="text-3xl font-bold bg-gradient-to-r from-yellow-500 to-amber-600 bg-clip-text text-transparent">
            {t.logo}
          </CardTitle>
          <CardDescription className="text-lg mt-2">{t.signUpTitle}</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="fullName">
                <User className="inline w-4 h-4 mr-2" />
                Vollständiger Name
              </Label>
              <Input
                id="fullName"
                type="text"
                value={formData.fullName}
                onChange={(e) => handleChange('fullName', e.target.value)}
                onBlur={() => handleBlur('fullName')}
                placeholder="Ihr vollständiger Name"
                className={`pl-10 ${errors.fullName ? 'border-red-500' : ''}`}
                required
              />
              <FormError message={errors.fullName} />
            </div>

            <div className="space-y-2">
              <Label htmlFor="email">
                <Mail className="inline w-4 h-4 mr-2" />
                E-Mail-Adresse
              </Label>
              <Input
                id="email"
                type="email"
                placeholder="ihre.email@beispiel.de"
                value={formData.email}
                onChange={(e) => handleChange('email', e.target.value)}
                onBlur={() => handleBlur('email')}
                className={`${errors.email ? 'border-red-500' : ''}`}
                required
              />
              <FormError message={errors.email} />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">
                <Lock className="inline w-4 h-4 mr-2" />
                Passwort
              </Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="Mindestens 8 Zeichen"
                  value={formData.password}
                  onChange={(e) => handleChange('password', e.target.value)}
                  onBlur={() => handleBlur('password')}
                  className={`pr-10 ${errors.password ? 'border-red-500' : ''}`}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
              <FormError message={errors.password} />
              {formData.password && <PasswordStrengthIndicator strength={passwordStrength} />}
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirmPassword">
                <Lock className="inline w-4 h-4 mr-2" />
                Passwort bestätigen
              </Label>
              <div className="relative">
                <Input
                  id="confirmPassword"
                  type={showConfirmPassword ? "text" : "password"}
                  placeholder="Passwort wiederholen"
                  value={formData.confirmPassword}
                  onChange={(e) => handleChange('confirmPassword', e.target.value)}
                  onBlur={() => handleBlur('confirmPassword')}
                  className={`pr-10 ${errors.confirmPassword ? 'border-red-500' : ''}`}
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showConfirmPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
              <FormError message={errors.confirmPassword} />
              {formData.confirmPassword && !errors.confirmPassword && formData.password === formData.confirmPassword && (
                <FormSuccess message="Passwörter stimmen überein" />
              )}
            </div>

            <Button
              type="submit"
              className="w-full bg-gradient-to-r from-yellow-400 to-amber-500 hover:from-yellow-500 hover:to-amber-600 text-black font-semibold"
              disabled={loading || Object.keys(errors).length > 0}
            >
              {loading ? 'Konto wird erstellt...' : 'Konto erstellen'}
            </Button>
          </form>

          <div className="mt-6 text-center space-y-4">
            <p className="text-sm text-gray-600">
              {t.alreadyHaveAccount}{' '}
              <Link to="/signin" className="text-amber-600 hover:text-amber-700 font-semibold">
                {t.signIn}
              </Link>
            </p>
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">oder</span>
              </div>
            </div>
            <p className="text-sm text-gray-600">
              Shop betreiben?{' '}
              <Link to="/signup/business" className="text-blue-600 hover:text-blue-700 font-semibold">
                Business Account erstellen
              </Link>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default SignUp;