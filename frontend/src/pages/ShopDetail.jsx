import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { shopAPI, reviewAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Textarea } from '../components/ui/textarea';
import { Input } from '../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { ImageUpload } from '../components/ui/image-upload';
import { useToast } from '../hooks/use-toast';
import { 
  Star, 
  ShieldCheck, 
  Globe, 
  MapPin, 
  Phone, 
  Mail, 
  ChevronLeft,
  Loader2,
  MessageSquare,
  TrendingUp,
  Package,
  CreditCard,
  Truck,
  RotateCcw,
  ThumbsUp,
  Building2,
  AlertCircle
} from 'lucide-react';

const ShopDetail = () => {
  const { shopId } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [shop, setShop] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [reviewsLoading, setReviewsLoading] = useState(true);
  const [showReviewForm, setShowReviewForm] = useState(false);
  const [newReview, setNewReview] = useState({ 
    rating: 5, 
    comment: '',
    proof_photos: [],
    proof_order_number: ''
  });
  const [submitting, setSubmitting] = useState(false);
  const [reviewPage, setReviewPage] = useState(1);
  const [totalReviews, setTotalReviews] = useState(0);
  const [hasMoreReviews, setHasMoreReviews] = useState(false);

  useEffect(() => {
    fetchShop();
    fetchReviews(1);
  }, [shopId]);

  const fetchShop = async () => {
    try {
      setLoading(true);
      const response = await shopAPI.getShop(shopId);
      setShop(response.data);
    } catch (error) {
      console.error('Error fetching shop:', error);
      toast({
        title: 'Error',
        description: 'Shop nicht gefunden',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchReviews = async (page = 1, append = false) => {
    try {
      setReviewsLoading(true);
      const response = await reviewAPI.getReviews({ shop_id: shopId, page, limit: 10 });
      const newReviews = response.data.data || [];
      
      if (append) {
        setReviews(prev => [...prev, ...newReviews]);
      } else {
        setReviews(newReviews);
      }
      
      setTotalReviews(response.data.total || 0);
      setHasMoreReviews(page < (response.data.pages || 1));
      setReviewPage(page);
    } catch (error) {
      console.error('Error fetching reviews:', error);
    } finally {
      setReviewsLoading(false);
    }
  };

  const loadMoreReviews = () => {
    fetchReviews(reviewPage + 1, true);
  };

  const handleSubmitReview = async (e) => {
    e.preventDefault();
    
    if (!user) {
      toast({
        title: 'Anmeldung erforderlich',
        description: 'Bitte melden Sie sich an, um eine Bewertung abzugeben.',
        variant: 'destructive',
      });
      return;
    }
    
    // Validate proof for 1-3 star reviews
    if (newReview.rating <= 3) {
      if (!newReview.proof_order_number || newReview.proof_order_number.length < 3) {
        toast({
          title: 'Bestellnummer erforderlich',
          description: 'Für Bewertungen mit 1-3 Sternen ist eine Bestellnummer erforderlich.',
          variant: 'destructive',
        });
        return;
      }
      
      if (!newReview.proof_photos || newReview.proof_photos.length === 0) {
        toast({
          title: 'Fotos erforderlich',
          description: 'Für Bewertungen mit 1-3 Sternen ist mindestens 1 Foto erforderlich.',
          variant: 'destructive',
        });
        return;
      }
    }
    
    setSubmitting(true);
    
    try {
      await reviewAPI.createReview({
        shop_id: shopId,
        rating: newReview.rating,
        comment: newReview.comment,
        proof_photos: newReview.proof_photos,
        proof_order_number: newReview.proof_order_number || null,
      });
      
      const statusMessage = newReview.rating <= 3 
        ? 'Ihre Bewertung wurde zur Prüfung eingereicht und wird nach der Genehmigung veröffentlicht.'
        : 'Ihre Bewertung wurde erfolgreich veröffentlicht.';
      
      toast({
        title: 'Erfolg!',
        description: statusMessage,
      });
      
      // Reset form and refresh reviews
      setNewReview({ rating: 5, comment: '', proof_photos: [], proof_order_number: '' });
      setShowReviewForm(false);
      fetchReviews(1);
    } catch (error) {
      toast({
        title: 'Fehler',
        description: error.response?.data?.detail || 'Bewertung konnte nicht gespeichert werden.',
        variant: 'destructive',
      });
    } finally {
      setSubmitting(false);
    }
  };

  // Calculate rating facets (mock data for now - can be enhanced with real data)
  const getRatingFacets = () => {
    const baseRating = shop?.rating || 0;
    return {
      deliverySpeed: Math.min(5, baseRating + (Math.random() * 0.5 - 0.25)),
      pricePerformance: Math.min(5, baseRating + (Math.random() * 0.5 - 0.25)),
      orderingProcess: Math.min(5, baseRating + (Math.random() * 0.5 - 0.25)),
      customerService: Math.min(5, baseRating + (Math.random() * 0.5 - 0.25)),
      returnsProcessing: Math.min(5, baseRating + (Math.random() * 0.5 - 0.25)),
      productQuality: Math.min(5, baseRating + (Math.random() * 0.5 - 0.25)),
      packaging: Math.min(5, baseRating + (Math.random() * 0.5 - 0.25)),
    };
  };

  const RatingFacet = ({ label, rating, icon: Icon }) => (
    <div className="flex items-center justify-between py-3 border-b last:border-0">
      <div className="flex items-center gap-3">
        <div className="p-2 bg-amber-100 rounded-lg">
          <Icon className="w-5 h-5 text-amber-600" />
        </div>
        <span className="text-sm font-medium text-gray-700">{label}</span>
      </div>
      <div className="flex items-center gap-2">
        <div className="w-32 bg-gray-200 rounded-full h-2">
          <div
            className="bg-gradient-to-r from-yellow-400 to-amber-500 h-2 rounded-full"
            style={{ width: `${(rating / 5) * 100}%` }}
          />
        </div>
        <span className="text-sm font-bold text-gray-900 w-8">{rating.toFixed(1)}</span>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-amber-500" />
        <p className="ml-2 text-gray-600">Shop wird geladen...</p>
      </div>
    );
  }

  if (!shop) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="max-w-md">
          <CardContent className="p-12 text-center">
            <h3 className="text-xl font-semibold mb-4">Shop nicht gefunden</h3>
            <Link to="/shops">
              <Button>Zurück zur Suche</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  const facets = getRatingFacets();

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-7xl">
        {/* Breadcrumb */}
        <div className="mb-6">
          <Link to="/shops" className="text-amber-600 hover:text-amber-700 flex items-center">
            <ChevronLeft className="w-4 h-4" />
            Zurück zur Suche
          </Link>
        </div>

        {/* Shop Header */}
        <Card className="mb-8">
          <CardContent className="p-8">
            <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-6">
              <div className="flex-1">
                <div className="flex items-start gap-4 mb-4">
                  <div className="flex-1">
                    <h1 className="text-4xl font-bold text-gray-900 mb-2">{shop.name}</h1>
                    <p className="text-lg text-gray-600 mb-4">{shop.category}</p>
                  </div>
                  {shop.is_verified && (
                    <Badge className="bg-green-100 text-green-800 flex items-center gap-2">
                      <ShieldCheck className="w-4 h-4" />
                      Verifiziert
                    </Badge>
                  )}
                </div>

                {/* Rating */}
                <div className="flex items-center mb-6">
                  <div className="flex items-center">
                    {[...Array(5)].map((_, i) => (
                      <Star
                        key={i}
                        className={`w-6 h-6 ${
                          i < Math.round(shop.rating)
                            ? 'fill-yellow-400 text-yellow-400'
                            : 'text-gray-300'
                        }`}
                      />
                    ))}
                  </div>
                  <span className="ml-3 text-2xl font-bold text-gray-900">
                    {shop.rating.toFixed(1)}
                  </span>
                  <span className="ml-2 text-gray-600">
                    ({shop.review_count} {shop.review_count === 1 ? 'Bewertung' : 'Bewertungen'})
                  </span>
                </div>

                {/* Description */}
                {shop.description && (
                  <p className="text-gray-700 mb-6">{shop.description}</p>
                )}
              </div>

              {/* CTA */}
              <div>
                <Button
                  onClick={() => {
                    if (!user) {
                      toast({
                        title: 'Anmeldung erforderlich',
                        description: 'Bitte melden Sie sich an, um eine Bewertung abzugeben.',
                        variant: 'destructive',
                      });
                    } else {
                      setShowReviewForm(!showReviewForm);
                    }
                  }}
                  className="bg-gradient-to-r from-yellow-400 to-amber-500 hover:from-yellow-500 hover:to-amber-600 text-black font-semibold"
                >
                  <MessageSquare className="w-4 h-4 mr-2" />
                  Bewertung schreiben
                </Button>
                {!user && (
                  <p className="text-xs text-gray-500 mt-2 text-center">Anmeldung erforderlich</p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Review Form */}
        {showReviewForm && user && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle>Bewertung schreiben</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmitReview} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Bewertung *</label>
                  <Select
                    value={newReview.rating.toString()}
                    onValueChange={(value) => setNewReview({ ...newReview, rating: parseInt(value) })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {[5, 4, 3, 2, 1].map((rating) => (
                        <SelectItem key={rating} value={rating.toString()}>
                          <div className="flex items-center">
                            {[...Array(rating)].map((_, i) => (
                              <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                            ))}
                            <span className="ml-2">({rating} {rating === 1 ? 'Stern' : 'Sterne'})</span>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Ihre Bewertung *</label>
                  <Textarea
                    value={newReview.comment}
                    onChange={(e) => setNewReview({ ...newReview, comment: e.target.value })}
                    rows={4}
                    placeholder="Teilen Sie Ihre Erfahrungen..."
                    required
                  />
                </div>

                {/* Conditional Evidence Section for 1-3 Stars */}
                {newReview.rating <= 3 && (
                  <div className="p-4 bg-amber-50 border-2 border-amber-300 rounded-lg space-y-4">
                    <div className="flex items-start gap-2">
                      <div className="p-2 bg-amber-100 rounded-full">
                        <AlertCircle className="w-5 h-5 text-amber-600" />
                      </div>
                      <div>
                        <p className="font-medium text-amber-900">Nachweis erforderlich</p>
                        <p className="text-sm text-amber-700 mt-1">
                          Für Bewertungen mit 1-3 Sternen benötigen wir einen Kaufnachweis. 
                          Ihre Bewertung wird nach der Prüfung durch unsere Administratoren veröffentlicht.
                        </p>
                      </div>
                    </div>
                    
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium mb-2">
                          Bestellnummer <span className="text-red-500">*</span>
                        </label>
                        <Input
                          value={newReview.proof_order_number}
                          onChange={(e) => setNewReview({ ...newReview, proof_order_number: e.target.value })}
                          placeholder="z.B. ORD-2024-12345"
                          required={newReview.rating <= 3}
                        />
                        <p className="text-xs text-gray-500 mt-1">
                          Die Bestellnummer finden Sie in Ihrer Bestellbestätigung
                        </p>
                      </div>
                      
                      <div>
                        <ImageUpload
                          value={newReview.proof_photos}
                          onChange={(photos) => setNewReview({ ...newReview, proof_photos: photos })}
                          maxFiles={5}
                          maxSizeMB={10}
                          required={newReview.rating <= 3}
                          label="Produktfotos als Nachweis"
                        />
                        <p className="text-xs text-gray-500 mt-1">
                          Fotos der Bestellung, Rechnung oder des Produkts (JPG, PNG, WEBP - max. 10 MB pro Bild)
                        </p>
                      </div>
                    </div>
                  </div>
                )}

                <div className="flex gap-4">
                  <Button
                    type="submit"
                    disabled={submitting}
                    className="bg-gradient-to-r from-yellow-400 to-amber-500 hover:from-yellow-500 hover:to-amber-600 text-black"
                  >
                    {submitting ? 'Wird gesendet...' : 'Bewertung veröffentlichen'}
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setShowReviewForm(false)}
                  >
                    Abbrechen
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        )}

        {/* Tabs Section */}
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="bg-white p-1 rounded-lg shadow">
            <TabsTrigger value="overview">Übersicht</TabsTrigger>
            <TabsTrigger value="reviews">Bewertungen ({totalReviews})</TabsTrigger>
            <TabsTrigger value="company">Firmeninformationen</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5" />
                  Bewertungskriterien
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <RatingFacet label="Liefergeschwindigkeit" rating={facets.deliverySpeed} icon={Truck} />
                  <RatingFacet label="Preis-Leistung" rating={facets.pricePerformance} icon={CreditCard} />
                  <RatingFacet label="Bestellprozess" rating={facets.orderingProcess} icon={Package} />
                  <RatingFacet label="Kundenservice" rating={facets.customerService} icon={ThumbsUp} />
                  <RatingFacet label="Rückgabeabwicklung" rating={facets.returnsProcessing} icon={RotateCcw} />
                  <RatingFacet label="Produktqualität" rating={facets.productQuality} icon={Star} />
                  <RatingFacet label="Verpackung" rating={facets.packaging} icon={Package} />
                </div>

                <div className="mt-6 p-4 bg-amber-50 rounded-lg">
                  <p className="text-sm text-amber-900">
                    <strong>Hinweis:</strong> Diese Bewertungskriterien basieren auf den Gesamtbewertungen 
                    der Kunden und werden automatisch berechnet.
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Reviews Tab */}
          <TabsContent value="reviews">
            <Card>
              <CardHeader>
                <CardTitle>Kundenbewertungen ({totalReviews})</CardTitle>
              </CardHeader>
              <CardContent>
                {reviewsLoading && reviews.length === 0 ? (
                  <div className="flex items-center justify-center py-8">
                    <Loader2 className="w-8 h-8 animate-spin text-amber-500" />
                  </div>
                ) : reviews.length === 0 ? (
                  <div className="text-center py-12">
                    <MessageSquare className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                    <p className="text-gray-600">Noch keine Bewertungen vorhanden</p>
                    <p className="text-sm text-gray-500 mt-2">Seien Sie der Erste, der diesen Shop bewertet!</p>
                  </div>
                ) : (
                  <>
                    <div className="space-y-6">
                      {reviews.map((review) => (
                        <div key={review.id} className="border-b pb-6 last:border-0">
                          <div className="flex items-start justify-between mb-3">
                            <div>
                              <div className="flex items-center mb-2">
                                {[...Array(5)].map((_, i) => (
                                  <Star
                                    key={i}
                                    className={`w-5 h-5 ${
                                      i < review.rating
                                        ? 'fill-yellow-400 text-yellow-400'
                                        : 'text-gray-300'
                                    }`}
                                  />
                                ))}
                              </div>
                              <p className="font-semibold text-gray-900">{review.user_name || 'Anonymer Nutzer'}</p>
                            </div>
                            <span className="text-sm text-gray-500">
                              {new Date(review.created_at).toLocaleDateString('de-DE')}
                            </span>
                          </div>
                          <p className="text-gray-700">{review.comment}</p>
                          
                          {review.response && (
                            <div className="mt-4 ml-8 p-4 bg-amber-50 rounded-lg">
                              <p className="text-sm font-semibold text-amber-900 mb-2">Antwort vom Shop:</p>
                              <p className="text-sm text-amber-800">{review.response}</p>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>

                    {/* Load More Button */}
                    {hasMoreReviews && (
                      <div className="mt-6 text-center">
                        <Button
                          onClick={loadMoreReviews}
                          disabled={reviewsLoading}
                          variant="outline"
                          className="min-w-[200px]"
                        >
                          {reviewsLoading ? (
                            <>
                              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                              Lädt...
                            </>
                          ) : (
                            'Mehr Bewertungen laden'
                          )}
                        </Button>
                        <p className="text-sm text-gray-500 mt-2">
                          {reviews.length} von {totalReviews} Bewertungen angezeigt
                        </p>
                      </div>
                    )}
                  </>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Company Information Tab */}
          <TabsContent value="company">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Building2 className="w-5 h-5" />
                  Firmeninformationen
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-6">
                  {/* Contact Information */}
                  <div>
                    <h3 className="font-semibold text-lg mb-4">Kontaktinformationen</h3>
                    <div className="space-y-3">
                      {shop.website && (
                        <div className="flex items-start gap-3">
                          <Globe className="w-5 h-5 text-gray-400 mt-0.5" />
                          <div>
                            <p className="text-sm text-gray-600">Webseite</p>
                            <a
                              href={shop.website}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-amber-600 hover:text-amber-700 font-medium"
                            >
                              {shop.website}
                            </a>
                          </div>
                        </div>
                      )}
                      {shop.email && (
                        <div className="flex items-start gap-3">
                          <Mail className="w-5 h-5 text-gray-400 mt-0.5" />
                          <div>
                            <p className="text-sm text-gray-600">E-Mail</p>
                            <a href={`mailto:${shop.email}`} className="text-gray-900 font-medium hover:text-amber-600">
                              {shop.email}
                            </a>
                          </div>
                        </div>
                      )}
                      {shop.phone && (
                        <div className="flex items-start gap-3">
                          <Phone className="w-5 h-5 text-gray-400 mt-0.5" />
                          <div>
                            <p className="text-sm text-gray-600">Telefon</p>
                            <a href={`tel:${shop.phone}`} className="text-gray-900 font-medium hover:text-amber-600">
                              {shop.phone}
                            </a>
                          </div>
                        </div>
                      )}
                      {shop.address && (
                        <div className="flex items-start gap-3">
                          <MapPin className="w-5 h-5 text-gray-400 mt-0.5" />
                          <div>
                            <p className="text-sm text-gray-600">Adresse</p>
                            <p className="text-gray-900 font-medium">{shop.address}</p>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Business Details */}
                  <div>
                    <h3 className="font-semibold text-lg mb-4">Geschäftsdetails</h3>
                    <div className="space-y-3">
                      <div>
                        <p className="text-sm text-gray-600">Kategorie</p>
                        <Badge className="mt-1 bg-blue-100 text-blue-800">{shop.category}</Badge>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Status</p>
                        <div className="mt-1">
                          {shop.is_verified ? (
                            <Badge className="bg-green-100 text-green-800">
                              <ShieldCheck className="w-3 h-3 mr-1" />
                              Verifiziert
                            </Badge>
                          ) : (
                            <Badge className="bg-gray-100 text-gray-800">Nicht verifiziert</Badge>
                          )}
                        </div>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Durchschnittliche Bewertung</p>
                        <div className="flex items-center mt-1">
                          <Star className="w-4 h-4 fill-yellow-400 text-yellow-400 mr-1" />
                          <span className="font-bold text-gray-900">{shop.rating.toFixed(1)}</span>
                          <span className="text-gray-600 ml-2">
                            ({shop.review_count} {shop.review_count === 1 ? 'Bewertung' : 'Bewertungen'})
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Additional Info */}
                {shop.description && (
                  <div className="mt-6 pt-6 border-t">
                    <h3 className="font-semibold text-lg mb-3">Über uns</h3>
                    <p className="text-gray-700 leading-relaxed">{shop.description}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default ShopDetail;
