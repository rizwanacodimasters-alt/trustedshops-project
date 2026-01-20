import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { useToast } from '../hooks/use-toast';
import { Mail, Lock, User, Store, Building2, Phone, Globe } from 'lucide-react';

const SignUpBusiness = () => {
  const { register } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
    companyName: '',
    phone: '',
    website: ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validation
    if (formData.password !== formData.confirmPassword) {
      toast({
        title: "Fehler",
        description: "Passwörter stimmen nicht überein!",
        variant: "destructive"
      });
      return;
    }

    if (formData.password.length < 6) {
      toast({
        title: "Fehler",
        description: "Passwort muss mindestens 6 Zeichen lang sein!",
        variant: "destructive"
      });
      return;
    }

    setLoading(true);
    
    const result = await register({
      full_name: formData.fullName,
      email: formData.email,
      password: formData.password,
      role: 'shop_owner'  // ← Shop Owner Role
    });
    
    setLoading(false);
    
    if (result.success) {
      toast({
        title: "Erfolg!",
        description: "Ihr Account wurde erstellt. Bitte verifizieren Sie Ihre E-Mail.",
      });
      
      // Redirect to email verification
      navigate('/email-verification', { state: { email: formData.email } });
    } else {
      // Error is already shown by register function
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-indigo-50 to-white py-12 px-4">
      <Card className="w-full max-w-2xl shadow-xl">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
            <Store className="w-8 h-8 text-white" />
          </div>
          <CardTitle className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
            Business Account Erstellen
          </CardTitle>
          <CardDescription className="text-lg mt-2">
            Registrieren Sie sich als Shop-Betreiber und starten Sie noch heute
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Info Box */}
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg mb-6">
              <h4 className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
                <Building2 className="w-5 h-5" />
                Business Account Vorteile
              </h4>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>✓ Eigene Shop-Profile erstellen und verwalten</li>
                <li>✓ Kundenbewertungen einsehen und beantworten</li>
                <li>✓ Verifizierungs-Badge beantragen</li>
                <li>✓ Detaillierte Statistiken und Reports</li>
              </ul>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              {/* Personal Information */}
              <div className="space-y-4">
                <h3 className="font-semibold text-gray-900 text-sm uppercase tracking-wide">
                  Persönliche Informationen
                </h3>
                
                <div className="space-y-2">
                  <Label htmlFor="fullName">Vollständiger Name *</Label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                    <Input
                      id="fullName"
                      type="text"
                      placeholder="Max Mustermann"
                      value={formData.fullName}
                      onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
                      className="pl-10"
                      required
                      minLength={2}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email">E-Mail Adresse *</Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                    <Input
                      id="email"
                      type="email"
                      placeholder="max@firma.de"
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      className="pl-10"
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="password">Passwort *</Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                    <Input
                      id="password"
                      type="password"
                      placeholder="••••••••"
                      value={formData.password}
                      onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                      className="pl-10"
                      required
                      minLength={6}
                    />
                  </div>
                  <p className="text-xs text-gray-500">Mindestens 6 Zeichen</p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="confirmPassword">Passwort bestätigen *</Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                    <Input
                      id="confirmPassword"
                      type="password"
                      placeholder="••••••••"
                      value={formData.confirmPassword}
                      onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                      className="pl-10"
                      required
                    />
                  </div>
                </div>
              </div>

              {/* Business Information (Optional for now) */}
              <div className="space-y-4">
                <h3 className="font-semibold text-gray-900 text-sm uppercase tracking-wide">
                  Business Informationen (Optional)
                </h3>
                
                <div className="space-y-2">
                  <Label htmlFor="companyName">Firmenname</Label>
                  <div className="relative">
                    <Building2 className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                    <Input
                      id="companyName"
                      type="text"
                      placeholder="Meine Firma GmbH"
                      value={formData.companyName}
                      onChange={(e) => setFormData({ ...formData, companyName: e.target.value })}
                      className="pl-10"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="phone">Telefonnummer</Label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                    <Input
                      id="phone"
                      type="tel"
                      placeholder="+49 123 456789"
                      value={formData.phone}
                      onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                      className="pl-10"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="website">Webseite</Label>
                  <div className="relative">
                    <Globe className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                    <Input
                      id="website"
                      type="url"
                      placeholder="https://meine-firma.de"
                      value={formData.website}
                      onChange={(e) => setFormData({ ...formData, website: e.target.value })}
                      className="pl-10"
                    />
                  </div>
                </div>

                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-xs text-gray-600">
                    💡 Sie können später weitere Shop-Details im Dashboard hinzufügen
                  </p>
                </div>
              </div>
            </div>

            {/* Terms */}
            <div className="pt-4 border-t">
              <div className="flex items-start gap-2">
                <input
                  type="checkbox"
                  id="terms"
                  required
                  className="mt-1"
                />
                <label htmlFor="terms" className="text-sm text-gray-600">
                  Ich akzeptiere die <Link to="/terms" className="text-blue-600 hover:underline">AGB</Link> und{' '}
                  <Link to="/privacy" className="text-blue-600 hover:underline">Datenschutzerklärung</Link>
                </label>
              </div>
            </div>

            <Button
              type="submit"
              className="w-full bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white font-semibold py-6 text-lg"
              disabled={loading}
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Account wird erstellt...
                </>
              ) : (
                <>
                  <Store className="w-5 h-5 mr-2" />
                  Business Account Erstellen
                </>
              )}
            </Button>
          </form>

          <div className="mt-6 text-center space-y-4">
            <p className="text-sm text-gray-600">
              Bereits registriert?{' '}
              <Link to="/signin" className="text-blue-600 hover:text-blue-700 font-semibold">
                Jetzt anmelden
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
              Nur als Kunde registrieren?{' '}
              <Link to="/signup" className="text-amber-600 hover:text-amber-700 font-semibold">
                Kunden-Account erstellen
              </Link>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default SignUpBusiness;
