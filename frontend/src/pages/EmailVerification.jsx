import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { useToast } from '../hooks/use-toast';
import { useAuth } from '../context/AuthContext';
import { Mail, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import axios from 'axios';

const EmailVerification = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { toast } = useToast();
  const { user, updateUser } = useAuth();
  const [email, setEmail] = useState('');
  const [code, setCode] = useState(['', '', '', '', '']);
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [verified, setVerified] = useState(false);
  const [timer, setTimer] = useState(0);

  useEffect(() => {
    // Get email from location state, AuthContext, or localStorage
    const stateEmail = location.state?.email;
    const userEmail = user?.email;
    const storedEmail = localStorage.getItem('pending_verification_email');
    
    const targetEmail = stateEmail || userEmail || storedEmail;
    
    if (targetEmail) {
      setEmail(targetEmail);
      localStorage.setItem('pending_verification_email', targetEmail);
      // Auto-send code on mount if coming from registration
      if (stateEmail) {
        sendVerificationCode(targetEmail);
      }
    } else {
      // No email found, redirect to signup
      navigate('/signup');
    }
  }, [location, navigate, user]);

  useEffect(() => {
    if (timer > 0) {
      const interval = setInterval(() => {
        setTimer(t => t - 1);
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [timer]);

  const sendVerificationCode = async (emailToSend) => {
    const targetEmail = emailToSend || email;
    if (!targetEmail) return;

    setSending(true);
    try {
      const response = await axios.post(
        `${process.env.REACT_APP_BACKEND_URL}/api/email-verification/send-code`,
        { email: targetEmail }
      );

      toast({
        title: 'Code gesendet!',
        description: `Verifizierungscode wurde an ${targetEmail} gesendet`,
      });

      // Show code in toast for testing (remove in production)
      if (response.data.code) {
        toast({
          title: '🔐 Test Code',
          description: `Ihr Code lautet: ${response.data.code}`,
          duration: 10000,
        });
      }

      setTimer(60); // 60 seconds cooldown
    } catch (error) {
      toast({
        title: 'Fehler',
        description: error.response?.data?.detail || 'Code konnte nicht gesendet werden',
        variant: 'destructive',
      });
    } finally {
      setSending(false);
    }
  };

  const handleCodeChange = (index, value) => {
    // Only allow digits
    if (value && !/^\d$/.test(value)) return;

    const newCode = [...code];
    newCode[index] = value;
    setCode(newCode);

    // Auto-focus next input
    if (value && index < 4) {
      document.getElementById(`code-${index + 1}`)?.focus();
    }
  };

  const handleKeyDown = (index, e) => {
    if (e.key === 'Backspace' && !code[index] && index > 0) {
      document.getElementById(`code-${index - 1}`)?.focus();
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text');
    const digits = pastedData.replace(/\D/g, '').slice(0, 5);
    
    const newCode = digits.split('');
    while (newCode.length < 5) newCode.push('');
    setCode(newCode);

    // Focus last filled input
    const lastIndex = Math.min(digits.length, 4);
    document.getElementById(`code-${lastIndex}`)?.focus();
  };

  const handleVerify = async () => {
    const fullCode = code.join('');
    
    if (fullCode.length !== 5) {
      toast({
        title: 'Ungültig',
        description: 'Bitte geben Sie den 5-stelligen Code ein',
        variant: 'destructive',
      });
      return;
    }

    setLoading(true);
    try {
      await axios.post(
        `${process.env.REACT_APP_BACKEND_URL}/api/email-verification/verify-code`,
        { email, code: fullCode }
      );

      // Update user's email_verified status in AuthContext
      updateUser({ email_verified: true });
      
      setVerified(true);
      localStorage.removeItem('pending_verification_email');

      toast({
        title: 'Erfolg!',
        description: 'Ihre E-Mail wurde erfolgreich verifiziert',
      });

      // Wait a bit then redirect
      setTimeout(() => {
        const currentUser = user || JSON.parse(localStorage.getItem('user') || '{}');
        if (currentUser.role === 'shop_owner') {
          navigate('/shop-dashboard');
        } else if (currentUser.role === 'admin') {
          navigate('/admin');
        } else {
          navigate('/my-dashboard');
        }
      }, 2000);
    } catch (error) {
      toast({
        title: 'Fehler',
        description: error.response?.data?.detail || 'Ungültiger Code',
        variant: 'destructive',
      });
      setCode(['', '', '', '', '']);
      document.getElementById('code-0')?.focus();
    } finally {
      setLoading(false);
    }
  };

  if (verified) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-emerald-100">
        <Card className="w-full max-w-md shadow-xl">
          <CardContent className="p-12 text-center">
            <div className="mb-6">
              <div className="mx-auto w-20 h-20 bg-green-100 rounded-full flex items-center justify-center">
                <CheckCircle className="w-12 h-12 text-green-600" />
              </div>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Verifiziert!</h2>
            <p className="text-gray-600">Sie werden weitergeleitet...</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
      <Card className="w-full max-w-md shadow-xl">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center">
            <Mail className="w-8 h-8 text-white" />
          </div>
          <CardTitle className="text-2xl">E-Mail Verifizierung</CardTitle>
          <CardDescription className="mt-2">
            Geben Sie den 5-stelligen Code ein, den wir an<br />
            <strong>{email}</strong> gesendet haben
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Code Input */}
          <div>
            <div className="flex justify-center gap-2" onPaste={handlePaste}>
              {code.map((digit, index) => (
                <Input
                  key={index}
                  id={`code-${index}`}
                  type="text"
                  maxLength={1}
                  value={digit}
                  onChange={(e) => handleCodeChange(index, e.target.value)}
                  onKeyDown={(e) => handleKeyDown(index, e)}
                  className="w-14 h-14 text-center text-2xl font-bold"
                  disabled={loading}
                />
              ))}
            </div>
          </div>

          {/* Verify Button */}
          <Button
            onClick={handleVerify}
            disabled={loading || code.some(d => !d)}
            className="w-full bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white font-semibold py-6"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Wird verifiziert...
              </>
            ) : (
              'Code verifizieren'
            )}
          </Button>

          {/* Resend */}
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-2">Code nicht erhalten?</p>
            <Button
              variant="outline"
              onClick={() => sendVerificationCode()}
              disabled={sending || timer > 0}
              className="text-sm"
            >
              {sending ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Wird gesendet...
                </>
              ) : timer > 0 ? (
                `Erneut senden in ${timer}s`
              ) : (
                'Code erneut senden'
              )}
            </Button>
          </div>

          {/* Info */}
          <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-xs text-blue-800 flex items-start gap-2">
              <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
              <span>
                Der Code ist 15 Minuten gültig. Überprüfen Sie auch Ihren Spam-Ordner.
              </span>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default EmailVerification;
