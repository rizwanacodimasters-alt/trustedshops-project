import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import axios from 'axios';
import { 
  Search, ShieldCheck, ShieldAlert, Star, AlertTriangle, 
  CheckCircle, XCircle, Info, TrendingUp, Store
} from 'lucide-react';

const FakeShopChecker = () => {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [statistics, setStatistics] = useState(null);

  useEffect(() => {
    fetchStatistics();
  }, []);

  const fetchStatistics = async () => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_BACKEND_URL}/api/fake-check/statistics`);
      setStatistics(response.data);
    } catch (error) {
      console.error('Error fetching statistics:', error);
    }
  };

  const handleCheck = async (e) => {
    e.preventDefault();
    if (!url.trim()) return;

    setLoading(true);
    try {
      const response = await axios.post(
        `${process.env.REACT_APP_BACKEND_URL}/api/fake-check/check`,
        { url }
      );
      setResult(response.data);
    } catch (error) {
      console.error('Error checking URL:', error);
      alert('Fehler beim Überprüfen der URL');
    } finally {
      setLoading(false);
    }
  };

  const getTrustColor = (score) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getTrustLabel = (score) => {
    if (score >= 80) return 'Vertrauenswürdig';
    if (score >= 50) return 'Eingeschränkt vertrauenswürdig';
    return 'Nicht vertrauenswürdig';
  };

  const getTrustIcon = (score) => {
    if (score >= 80) return <ShieldCheck className="w-16 h-16 text-green-600" />;
    if (score >= 50) return <ShieldAlert className="w-16 h-16 text-yellow-600" />;
    return <ShieldAlert className="w-16 h-16 text-red-600" />;
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="container mx-auto px-4">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Fake-Shop Finder
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Überprüfen Sie Online-Shops auf Vertrauenswürdigkeit. Geben Sie die Shop-URL ein und erhalten Sie sofort eine Einschätzung.
          </p>
        </div>

        {/* Statistics */}
        {statistics && (
          <div className="grid md:grid-cols-4 gap-6 mb-12">
            {[
              { icon: <Store />, label: 'Registrierte Shops', value: statistics.total_shops, color: 'blue' },
              { icon: <ShieldCheck />, label: 'Verifizierte Shops', value: statistics.verified_shops, color: 'green' },
              { icon: <Star />, label: 'Bewertungen', value: statistics.total_reviews, color: 'yellow' },
              { icon: <TrendingUp />, label: 'Ø Bewertung', value: statistics.average_rating.toFixed(1), color: 'purple' }
            ].map((stat, i) => (
              <Card key={i}>
                <CardContent className="p-6 text-center">
                  <div className={`p-3 bg-${stat.color}-100 rounded-full w-12 h-12 mx-auto mb-3 flex items-center justify-center`}>
                    <div className={`text-${stat.color}-600`}>{stat.icon}</div>
                  </div>
                  <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
                  <p className="text-sm text-gray-600 mt-1">{stat.label}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Search Section */}
        <Card className="max-w-4xl mx-auto mb-8">
          <CardHeader>
            <CardTitle className="text-center">Shop-URL überprüfen</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleCheck} className="space-y-4">
              <div className="flex gap-4">
                <div className="flex-1 relative">
                  <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                  <Input
                    type="text"
                    placeholder="z.B. https://example-shop.de oder example-shop.de"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    className="pl-12 h-14 text-lg"
                    required
                  />
                </div>
                <Button
                  type="submit"
                  disabled={loading}
                  className="h-14 px-8 bg-gradient-to-r from-yellow-400 to-amber-500 hover:from-yellow-500 hover:to-amber-600 text-black font-semibold"
                >
                  {loading ? 'Prüfe...' : 'Shop prüfen'}
                </Button>
              </div>
              <p className="text-sm text-gray-500 text-center">
                Geben Sie die vollständige URL des Online-Shops ein, den Sie überprüfen möchten.
              </p>
            </form>
          </CardContent>
        </Card>

        {/* Results */}
        {result && (
          <div className="max-w-4xl mx-auto space-y-6">
            {/* Trust Score Card */}
            <Card className="border-2" style={{ borderColor: result.trust_score >= 80 ? '#10b981' : result.trust_score >= 50 ? '#f59e0b' : '#ef4444' }}>
              <CardContent className="p-8">
                <div className="text-center">
                  <div className="mb-4">{getTrustIcon(result.trust_score)}</div>
                  <h2 className={`text-3xl font-bold mb-2 ${getTrustColor(result.trust_score)}`}>
                    {getTrustLabel(result.trust_score)}
                  </h2>
                  <div className="flex items-center justify-center gap-3 mb-4">
                    <span className="text-5xl font-bold text-gray-900">{result.trust_score}</span>
                    <span className="text-2xl text-gray-500">/100</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-4 mb-6">
                    <div
                      className="h-4 rounded-full transition-all duration-500"
                      style={{
                        width: `${result.trust_score}%`,
                        backgroundColor: result.trust_score >= 80 ? '#10b981' : result.trust_score >= 50 ? '#f59e0b' : '#ef4444'
                      }}
                    />
                  </div>
                </div>

                {result.is_registered && (
                  <div className="bg-blue-50 rounded-lg p-6 mb-6">
                    <div className="flex items-start gap-4">
                      <Store className="w-8 h-8 text-blue-600 flex-shrink-0" />
                      <div className="flex-1">
                        <h3 className="text-xl font-bold text-gray-900 mb-2">{result.shop_name}</h3>
                        <div className="flex flex-wrap gap-3">
                          <Badge className="bg-blue-100 text-blue-800">{result.category}</Badge>
                          {result.is_verified && (
                            <Badge className="bg-green-100 text-green-800">
                              <CheckCircle className="w-3 h-3 mr-1" />
                              Verifiziert
                            </Badge>
                          )}
                        </div>
                        {result.rating && (
                          <div className="flex items-center mt-3">
                            {[...Array(5)].map((_, i) => (
                              <Star
                                key={i}
                                className={`w-5 h-5 ${
                                  i < Math.round(result.rating)
                                    ? 'fill-yellow-400 text-yellow-400'
                                    : 'text-gray-300'
                                }`}
                              />
                            ))}
                            <span className="ml-2 font-semibold">{result.rating.toFixed(1)}</span>
                            <span className="ml-1 text-gray-600">({result.review_count} Bewertungen)</span>
                          </div>
                        )}
                        {result.shop_id && (
                          <Link
                            to={`/shop/${result.shop_id}`}
                            className="inline-block mt-4 text-blue-600 hover:text-blue-700 font-semibold"
                          >
                            Shop-Details ansehen →
                          </Link>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {!result.is_registered && (
                  <div className="bg-red-50 rounded-lg p-6 mb-6">
                    <div className="flex items-start gap-4">
                      <XCircle className="w-8 h-8 text-red-600 flex-shrink-0" />
                      <div>
                        <h3 className="text-xl font-bold text-red-900 mb-2">Shop nicht registriert</h3>
                        <p className="text-red-800">
                          Dieser Shop ist nicht in unserer Datenbank registriert. Das bedeutet nicht automatisch, dass es sich um einen Fake-Shop handelt, aber Sie sollten besonders vorsichtig sein.
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Warnings */}
            {result.warnings && result.warnings.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-orange-600">
                    <AlertTriangle className="w-5 h-5" />
                    Warnhinweise
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {result.warnings.map((warning, i) => (
                      <li key={i} className="flex items-start gap-2 text-gray-700">
                        <span className="text-orange-500 mt-0.5">•</span>
                        <span>{warning}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )}

            {/* Recommendations */}
            {result.recommendations && result.recommendations.length > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-blue-600">
                    <Info className="w-5 h-5" />
                    Empfehlungen & Hinweise
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {result.recommendations.map((rec, i) => (
                      <li key={i} className="flex items-start gap-2 text-gray-700">
                        <span className="text-blue-500 mt-0.5">•</span>
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )}

            {/* General Tips */}
            <Card className="bg-gradient-to-r from-blue-50 to-indigo-50">
              <CardHeader>
                <CardTitle>🛡️ Allgemeine Tipps zum sicheren Online-Shopping</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3 text-gray-700">
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                    <span><strong>Impressum prüfen:</strong> Seriöse Shops haben ein vollständiges Impressum mit Anschrift und Kontaktdaten</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                    <span><strong>Sichere Zahlungsmethoden:</strong> Nutzen Sie PayPal, Kreditkarte oder Rechnung statt Vorkasse</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                    <span><strong>HTTPS-Verschlüsselung:</strong> Die Website sollte eine sichere Verbindung (https://) nutzen</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                    <span><strong>Bewertungen lesen:</strong> Suchen Sie nach unabhängigen Bewertungen auf verschiedenen Plattformen</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                    <span><strong>Preise vergleichen:</strong> Unrealistisch günstige Preise können ein Warnsignal sein</span>
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
};

export default FakeShopChecker;
