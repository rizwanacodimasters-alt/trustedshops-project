import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import customerAPI from '../services/customer-api';
import { reviewAPI } from '../services/api';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Badge } from '../components/ui/badge';
import { useToast } from '../hooks/use-toast';
import EditReviewDialog from '../components/customer/EditReviewDialog';
import DeleteReviewDialog from '../components/customer/DeleteReviewDialog';
import { 
  User, Star, Heart, Bell, Settings, MessageSquare, 
  TrendingUp, Award, ShoppingBag, Edit, Trash2, Eye, EyeOff,
  AlertCircle, CheckCircle, Clock, Filter
} from 'lucide-react';

const CustomerDashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  
  // Data states
  const [dashboard, setDashboard] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [profile, setProfile] = useState(null);
  
  // Filter & sort states
  const [reviewSort, setReviewSort] = useState('newest');
  const [shopFilter, setShopFilter] = useState('');
  
  // Form states
  const [editingProfile, setEditingProfile] = useState(false);
  const [profileForm, setProfileForm] = useState({});
  const [passwordForm, setPasswordForm] = useState({ current_password: '', new_password: '', confirm_password: '' });
  const [showPassword, setShowPassword] = useState(false);
  
  // Dialog states
  const [editReviewDialog, setEditReviewDialog] = useState({ open: false, review: null });
  const [deleteReviewDialog, setDeleteReviewDialog] = useState({ open: false, review: null });
  
  // Search state
  const [reviewSearchTerm, setReviewSearchTerm] = useState('');

  useEffect(() => {
    if (!user || user.role !== 'shopper') {
      navigate('/');
      return;
    }
    fetchAllData();
  }, [user, navigate]);

  const fetchAllData = async () => {
    try {
      setLoading(true);
      const [dashboardRes, reviewsRes, favoritesRes, notificationsRes, profileRes] = await Promise.all([
        customerAPI.getDashboard(),
        customerAPI.getMyReviews({ sort_by: reviewSort, search: reviewSearchTerm || undefined }),
        customerAPI.getFavorites(),
        customerAPI.getNotifications(),
        customerAPI.getProfile()
      ]);
      
      setDashboard(dashboardRes.data);
      setReviews(reviewsRes.data.reviews || []);
      setFavorites(favoritesRes.data.favorites || []);
      setNotifications(notificationsRes.data.notifications || []);
      setProfile(profileRes.data);
      setProfileForm(profileRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
      toast({ title: 'Error', description: 'Failed to load dashboard', variant: 'destructive' });
    } finally {
      setLoading(false);
    }
  };

  const handleRemoveFavorite = async (shopId) => {
    try {
      await customerAPI.removeFavorite(shopId);
      setFavorites(favorites.filter(f => f.id !== shopId));
      toast({ title: 'Erfolg', description: 'Shop aus Favoriten entfernt' });
    } catch (error) {
      toast({ title: 'Fehler', description: 'Aktion fehlgeschlagen', variant: 'destructive' });
    }
  };

  const handleMarkAsRead = async (notificationId) => {
    try {
      await customerAPI.markAsRead(notificationId);
      setNotifications(notifications.map(n => n.id === notificationId ? {...n, read: true} : n));
    } catch (error) {
      console.error('Error marking notification:', error);
    }
  };

  const handleEditReview = (review) => {
    setEditReviewDialog({ open: true, review });
  };

  const handleDeleteReview = (review) => {
    setDeleteReviewDialog({ open: true, review });
  };

  const handleReviewSuccess = () => {
    fetchAllData(); // Refresh data after edit/delete
  };

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    try {
      await customerAPI.updateProfile({
        full_name: profileForm.full_name,
        phone: profileForm.phone,
        address: profileForm.address,
        language: profileForm.language
      });
      setProfile(profileForm);
      setEditingProfile(false);
      toast({ title: 'Erfolg', description: 'Profil aktualisiert' });
    } catch (error) {
      toast({ title: 'Fehler', description: 'Profil konnte nicht aktualisiert werden', variant: 'destructive' });
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    if (passwordForm.new_password !== passwordForm.confirm_password) {
      toast({ title: 'Fehler', description: 'Passwörter stimmen nicht überein', variant: 'destructive' });
      return;
    }
    try {
      await customerAPI.changePassword({
        current_password: passwordForm.current_password,
        new_password: passwordForm.new_password
      });
      setPasswordForm({ current_password: '', new_password: '', confirm_password: '' });
      toast({ title: 'Erfolg', description: 'Passwort geändert' });
    } catch (error) {
      toast({ title: 'Fehler', description: error.response?.data?.detail || 'Passwort konnte nicht geändert werden', variant: 'destructive' });
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-500 mx-auto"></div><p className="mt-4 text-gray-600">Laden...</p></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Mein Dashboard</h1>
          <p className="text-gray-600">Willkommen zurück, {dashboard?.user?.full_name}!</p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="bg-white p-1 rounded-lg shadow">
            <TabsTrigger value="overview">Übersicht</TabsTrigger>
            <TabsTrigger value="reviews">Bewertungen</TabsTrigger>
            <TabsTrigger value="favorites">Favoriten</TabsTrigger>
            <TabsTrigger value="notifications">Benachrichtigungen</TabsTrigger>
            <TabsTrigger value="profile">Profil</TabsTrigger>
          </TabsList>

          {/* 1. Overview */}
          <TabsContent value="overview">
            <div className="grid md:grid-cols-4 gap-6 mb-8">
              {[
                { icon: <MessageSquare/>, title: 'Bewertungen', value: dashboard?.statistics?.total_reviews || 0, color: 'blue' },
                { icon: <Star/>, title: 'Ø Bewertung', value: dashboard?.statistics?.average_rating_given?.toFixed(1) || '0.0', color: 'yellow' },
                { icon: <Heart/>, title: 'Favoriten', value: dashboard?.statistics?.favorite_shops || 0, color: 'red' },
                { icon: <Bell/>, title: 'Benachrichtigungen', value: dashboard?.statistics?.unread_notifications || 0, color: 'green' }
              ].map((stat, i) => (
                <Card key={i}>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-600">{stat.title}</p>
                        <p className="text-3xl font-bold text-gray-900 mt-1">{stat.value}</p>
                      </div>
                      <div className={`p-3 bg-${stat.color}-100 rounded-lg text-${stat.color}-600`}>{stat.icon}</div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            <Card className="mb-6">
              <CardHeader><CardTitle>Letzte Aktivitäten</CardTitle></CardHeader>
              <CardContent>
                {dashboard?.recent_reviews?.length > 0 ? (
                  <div className="space-y-4">
                    {dashboard.recent_reviews.map((review) => (
                      <div key={review.id} className="flex items-start space-x-4 p-4 border rounded-lg">
                        <MessageSquare className="w-5 h-5 text-gray-400 mt-1"/>
                        <div className="flex-1">
                          <div className="flex items-center justify-between mb-1">
                            <p className="font-semibold">{review.shop_name}</p>
                            <div className="flex">{[...Array(5)].map((_, i) => <Star key={i} className={`w-4 h-4 ${i < review.rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}`}/>)}</div>
                          </div>
                          <p className="text-sm text-gray-600 line-clamp-2">{review.comment}</p>
                          <p className="text-xs text-gray-400 mt-1">{new Date(review.created_at).toLocaleDateString('de-DE')}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : <p className="text-gray-500 text-center py-8">Noch keine Aktivitäten</p>}
              </CardContent>
            </Card>
          </TabsContent>

          {/* 3. Reviews */}
          <TabsContent value="reviews">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Meine Bewertungen ({reviews.length})</CardTitle>
                  <div className="flex gap-2">
                    <Select value={reviewSort} onValueChange={(v) => { setReviewSort(v); customerAPI.getMyReviews({ sort_by: v, search: reviewSearchTerm || undefined }).then(r => setReviews(r.data.reviews || [])); }}>
                      <SelectTrigger className="w-40"><SelectValue/></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="newest">Neueste</SelectItem>
                        <SelectItem value="oldest">Älteste</SelectItem>
                        <SelectItem value="highest">Höchste Sterne</SelectItem>
                        <SelectItem value="lowest">Niedrigste Sterne</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                {/* Search Bar */}
                <div className="mt-4">
                  <div className="relative">
                    <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <input
                      type="text"
                      placeholder="Suche in deinen Bewertungen..."
                      value={reviewSearchTerm}
                      onChange={(e) => {
                        setReviewSearchTerm(e.target.value);
                        const searchValue = e.target.value;
                        setTimeout(() => {
                          customerAPI.getMyReviews({ sort_by: reviewSort, search: searchValue || undefined })
                            .then(r => setReviews(r.data.reviews || []));
                        }, 300);
                      }}
                      className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500"
                    />
                    {reviewSearchTerm && (
                      <button
                        onClick={() => {
                          setReviewSearchTerm('');
                          customerAPI.getMyReviews({ sort_by: reviewSort }).then(r => setReviews(r.data.reviews || []));
                        }}
                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                      >
                        ×
                      </button>
                    )}
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {reviews.length > 0 ? (
                  <div className="space-y-4">
                    {reviews.map((review) => (
                      <Card key={review.id}>
                        <CardContent className="p-6">
                          <div className="flex items-start justify-between mb-4">
                            <div className="flex-1">
                              <div className="flex items-center gap-2">
                                <h3 className="font-semibold text-lg">{review.shop_name}</h3>
                                {/* Status Badge */}
                                {review.status === 'pending' && (
                                  <Badge className="bg-orange-100 text-orange-800">
                                    <Clock className="w-3 h-3 mr-1" />
                                    Wartet auf Freigabe
                                  </Badge>
                                )}
                                {review.status === 'approved' && (
                                  <Badge className="bg-green-100 text-green-800">
                                    <CheckCircle className="w-3 h-3 mr-1" />
                                    Freigegeben
                                  </Badge>
                                )}
                                {review.status === 'rejected' && (
                                  <Badge className="bg-red-100 text-red-800">
                                    <AlertCircle className="w-3 h-3 mr-1" />
                                    Abgelehnt
                                  </Badge>
                                )}
                              </div>
                              <p className="text-sm text-gray-500">{review.shop_category}</p>
                              <div className="flex items-center mt-2">{[...Array(5)].map((_, i) => <Star key={i} className={`w-5 h-5 ${i < review.rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}`}/>)}</div>
                            </div>
                            <div className="flex gap-2">
                              <Button variant="outline" size="sm" onClick={() => handleEditReview(review)}>
                                <Edit className="w-4 h-4"/>
                              </Button>
                              <Button variant="outline" size="sm" onClick={() => handleDeleteReview(review)}>
                                <Trash2 className="w-4 h-4 text-red-600"/>
                              </Button>
                            </div>
                          </div>
                          <p className="text-gray-700 mb-3">{review.comment}</p>
                          
                          {/* Proof Section for Low-Star Reviews */}
                          {review.rating <= 3 && (review.proof_photos?.length > 0 || review.proof_order_number) && (
                            <div className="bg-gray-50 rounded-lg p-4 mt-3 border-l-4 border-amber-400">
                              <p className="text-sm font-semibold text-gray-900 mb-2 flex items-center">
                                <FileText className="w-4 h-4 mr-2" />
                                Eingereichte Nachweise
                              </p>
                              {review.proof_order_number && (
                                <p className="text-sm text-gray-700 mb-2">
                                  <span className="font-medium">Bestellnummer:</span> {review.proof_order_number}
                                </p>
                              )}
                              {review.proof_photos && review.proof_photos.length > 0 && (
                                <div>
                                  <p className="text-sm font-medium text-gray-700 mb-2">
                                    Produktfotos ({review.proof_photos.length}):
                                  </p>
                                  <div className="grid grid-cols-3 gap-2">
                                    {review.proof_photos.map((photo, idx) => (
                                      <img
                                        key={idx}
                                        src={photo}
                                        alt={`Nachweis ${idx + 1}`}
                                        className="w-full h-24 object-cover rounded border cursor-pointer hover:opacity-75"
                                        onClick={() => window.open(photo, '_blank')}
                                      />
                                    ))}
                                  </div>
                                </div>
                              )}
                            </div>
                          )}
                          
                          {/* Admin Notes if Rejected */}
                          {review.status === 'rejected' && review.admin_notes && (
                            <div className="bg-red-50 rounded-lg p-4 mt-3">
                              <p className="text-sm font-semibold text-red-900 mb-1">Ablehnungsgrund:</p>
                              <p className="text-sm text-red-800">{review.admin_notes}</p>
                            </div>
                          )}
                          
                          {review.response && (
                            <div className="bg-amber-50 rounded-lg p-4 mt-3">
                              <p className="text-sm font-semibold text-amber-900 mb-1">Antwort vom Shop:</p>
                              <p className="text-sm text-amber-800">{review.response}</p>
                            </div>
                          )}
                          <div className="flex items-center justify-between mt-4 pt-4 border-t">
                            <p className="text-xs text-gray-500">{new Date(review.created_at).toLocaleDateString('de-DE')}</p>
                            <div className="flex gap-2">
                              {review.response && (
                                <Badge className="bg-green-100 text-green-800">
                                  Beantwortet
                                </Badge>
                              )}
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                ) : <p className="text-center text-gray-500 py-12">Noch keine Bewertungen abgegeben</p>}
              </CardContent>
            </Card>
          </TabsContent>

          {/* 6. Favorites */}
          <TabsContent value="favorites">
            <Card>
              <CardHeader><CardTitle>Meine Favoriten-Shops ({favorites.length})</CardTitle></CardHeader>
              <CardContent>
                {favorites.length > 0 ? (
                  <div className="grid md:grid-cols-2 gap-4">
                    {favorites.map((shop) => (
                      <Card key={shop.id}>
                        <CardContent className="p-6">
                          <div className="flex items-start justify-between mb-3">
                            <div className="flex-1">
                              <h3 className="font-semibold text-lg">{shop.name}</h3>
                              <p className="text-sm text-gray-500">{shop.category}</p>
                            </div>
                            <Button variant="ghost" size="sm" onClick={() => handleRemoveFavorite(shop.id)}><Heart className="w-5 h-5 fill-red-500 text-red-500"/></Button>
                          </div>
                          <div className="flex items-center mb-3">{[...Array(5)].map((_, i) => <Star key={i} className={`w-4 h-4 ${i < Math.round(shop.rating) ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}`}/>)}<span className="ml-2 text-sm text-gray-600">{shop.rating.toFixed(1)} ({shop.review_count} Bewertungen)</span></div>
                          {shop.is_verified && <Badge className="bg-green-100 text-green-800"><CheckCircle className="w-3 h-3 mr-1"/>Verifiziert</Badge>}
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                ) : <p className="text-center text-gray-500 py-12">Noch keine Favoriten-Shops gespeichert</p>}
              </CardContent>
            </Card>
          </TabsContent>

          {/* 5. Notifications */}
          <TabsContent value="notifications">
            <Card>
              <CardHeader><CardTitle>Benachrichtigungen</CardTitle></CardHeader>
              <CardContent>
                {notifications.length > 0 ? (
                  <div className="space-y-3">
                    {notifications.map((notif) => (
                      <div key={notif.id} className={`p-4 border rounded-lg cursor-pointer transition ${notif.read ? 'bg-white' : 'bg-blue-50 border-blue-200'}`} onClick={() => !notif.read && handleMarkAsRead(notif.id)}>
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              {notif.type === 'info' && <Bell className="w-4 h-4 text-blue-500"/>}
                              {notif.type === 'success' && <CheckCircle className="w-4 h-4 text-green-500"/>}
                              {notif.type === 'warning' && <AlertCircle className="w-4 h-4 text-orange-500"/>}
                              <h4 className="font-semibold">{notif.title}</h4>
                            </div>
                            <p className="text-sm text-gray-600">{notif.message}</p>
                            <p className="text-xs text-gray-400 mt-1">{new Date(notif.created_at).toLocaleDateString('de-DE')}</p>
                          </div>
                          {!notif.read && <Badge className="bg-blue-500">Neu</Badge>}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : <p className="text-center text-gray-500 py-12">Keine Benachrichtigungen</p>}
              </CardContent>
            </Card>
          </TabsContent>

          {/* 7. Profile */}
          <TabsContent value="profile">
            <div className="grid md:grid-cols-2 gap-6">
              <Card>
                <CardHeader><CardTitle>Persönliche Daten</CardTitle></CardHeader>
                <CardContent>
                  <form onSubmit={handleUpdateProfile} className="space-y-4">
                    <div><Label>Name</Label><Input value={profileForm.full_name || ''} onChange={(e) => setProfileForm({...profileForm, full_name: e.target.value})} disabled={!editingProfile}/></div>
                    <div><Label>Email</Label><Input value={profileForm.email || ''} disabled/></div>
                    <div><Label>Telefon</Label><Input value={profileForm.phone || ''} onChange={(e) => setProfileForm({...profileForm, phone: e.target.value})} disabled={!editingProfile}/></div>
                    <div><Label>Adresse</Label><Textarea value={profileForm.address || ''} onChange={(e) => setProfileForm({...profileForm, address: e.target.value})} disabled={!editingProfile}/></div>
                    <div><Label>Sprache</Label>
                      <Select value={profileForm.language || 'en'} onValueChange={(v) => setProfileForm({...profileForm, language: v})} disabled={!editingProfile}>
                        <SelectTrigger><SelectValue/></SelectTrigger>
                        <SelectContent><SelectItem value="en">English</SelectItem><SelectItem value="de">Deutsch</SelectItem><SelectItem value="ur">اردو</SelectItem><SelectItem value="ar">العربية</SelectItem></SelectContent>
                      </Select>
                    </div>
                    {editingProfile ? (
                      <div className="flex gap-2"><Button type="submit">Speichern</Button><Button type="button" variant="outline" onClick={() => { setEditingProfile(false); setProfileForm(profile); }}>Abbrechen</Button></div>
                    ) : <Button type="button" onClick={() => setEditingProfile(true)}><Edit className="w-4 h-4 mr-2"/>Bearbeiten</Button>}
                  </form>
                </CardContent>
              </Card>

              <Card>
                <CardHeader><CardTitle>Passwort ändern</CardTitle></CardHeader>
                <CardContent>
                  <form onSubmit={handleChangePassword} className="space-y-4">
                    <div><Label>Aktuelles Passwort</Label><div className="relative"><Input type={showPassword ? 'text' : 'password'} value={passwordForm.current_password} onChange={(e) => setPasswordForm({...passwordForm, current_password: e.target.value})} required/><button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-1/2 -translate-y-1/2">{showPassword ? <EyeOff className="w-4 h-4 text-gray-400"/> : <Eye className="w-4 h-4 text-gray-400"/>}</button></div></div>
                    <div><Label>Neues Passwort</Label><Input type="password" value={passwordForm.new_password} onChange={(e) => setPasswordForm({...passwordForm, new_password: e.target.value})} required/></div>
                    <div><Label>Passwort bestätigen</Label><Input type="password" value={passwordForm.confirm_password} onChange={(e) => setPasswordForm({...passwordForm, confirm_password: e.target.value})} required/></div>
                    <Button type="submit">Passwort ändern</Button>
                  </form>
                </CardContent>
              </Card>
            </div>

            <Card className="mt-6 border-red-200">
              <CardHeader><CardTitle className="text-red-600">Gefahrenzone</CardTitle></CardHeader>
              <CardContent>
                <p className="text-gray-600 mb-4">Das Löschen Ihres Kontos ist unwiderruflich. Alle Ihre Daten werden permanent gelöscht.</p>
                <Button variant="outline" className="text-red-600 border-red-600 hover:bg-red-50" onClick={async () => { if (window.confirm('Konto wirklich löschen? Dies kann nicht rückgängig gemacht werden!')) { try { await customerAPI.deleteAccount(); logout(); navigate('/'); toast({ title: 'Konto gelöscht' }); } catch (e) { toast({ title: 'Fehler', variant: 'destructive' }); } }}}>Konto löschen</Button>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>

      {/* Dialogs */}
      <EditReviewDialog
        open={editReviewDialog.open}
        onClose={() => setEditReviewDialog({ open: false, review: null })}
        review={editReviewDialog.review}
        onSuccess={handleReviewSuccess}
      />
      
      <DeleteReviewDialog
        open={deleteReviewDialog.open}
        onClose={() => setDeleteReviewDialog({ open: false, review: null })}
        review={deleteReviewDialog.review}
        onSuccess={handleReviewSuccess}
      />
    </div>
  );
};

export default CustomerDashboard;
