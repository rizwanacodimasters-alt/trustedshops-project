import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { dashboardAPI, verificationAPI } from '../services/api';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { useToast } from '../hooks/use-toast';
import { 
  Store, 
  Star, 
  MessageSquare, 
  TrendingUp, 
  AlertCircle, 
  ShieldCheck,
  Settings,
  CreditCard,
  FileText
} from 'lucide-react';
import ShopProfile from '../components/shop-owner/ShopProfile';
import ReviewManagement from '../components/shop-owner/ReviewManagement';
import TrustBadges from '../components/shop-owner/TrustBadges';
import Billing from '../components/shop-owner/Billing';
import CreateShopModal from '../components/shop-owner/CreateShopModal';

const ShopOwnerDashboard = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isCreateShopOpen, setIsCreateShopOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    // Check if user is shop owner
    if (!user || (user.role !== 'shop_owner' && user.role !== 'admin')) {
      navigate('/');
      return;
    }
    
    fetchDashboard();
  }, [user, navigate]);

  const fetchDashboard = async () => {
    try {
      const response = await dashboardAPI.getShopOwnerDashboard();
      setDashboard(response.data);
    } catch (error) {
      console.error('Error fetching dashboard:', error);
      toast({
        title: 'Error',
        description: 'Failed to load dashboard data',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleRequestVerification = async (shopId) => {
    try {
      await verificationAPI.requestVerification(shopId);
      toast({
        title: 'Success!',
        description: 'Verification request submitted successfully. An admin will review it soon.',
      });
      fetchDashboard();
    } catch (error) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to request verification',
        variant: 'destructive',
      });
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-500"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (!dashboard) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="max-w-md">
          <CardContent className="p-6 text-center">
            <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Dashboard Data</h3>
            <p className="text-gray-600 mb-4">Unable to load your dashboard.</p>
            <Button onClick={() => window.location.reload()}>Retry</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const stats = [
    {
      icon: <Store className="w-8 h-8" />,
      title: 'Total Shops',
      value: dashboard.statistics.total_shops,
      subtitle: `${dashboard.statistics.verified_shops} verified`,
      color: 'from-blue-500 to-blue-600'
    },
    {
      icon: <Star className="w-8 h-8" />,
      title: 'Average Rating',
      value: dashboard.statistics.average_rating.toFixed(2),
      subtitle: `${dashboard.statistics.total_reviews} total reviews`,
      color: 'from-yellow-500 to-yellow-600'
    },
    {
      icon: <MessageSquare className="w-8 h-8" />,
      title: 'Unanswered Reviews',
      value: dashboard.statistics.unanswered_reviews,
      subtitle: 'Need response',
      color: 'from-orange-500 to-orange-600'
    },
    {
      icon: <TrendingUp className="w-8 h-8" />,
      title: 'New Reviews (30d)',
      value: dashboard.statistics.new_reviews_30d,
      subtitle: 'This month',
      color: 'from-green-500 to-green-600'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Shop Owner Dashboard</h1>
          <p className="text-gray-600">Welcome back, {user.full_name}!</p>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => (
            <Card key={index} className="hover:shadow-lg transition-shadow duration-300">
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-600 mb-1">{stat.title}</p>
                    <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
                    <p className="text-sm text-gray-500 mt-1">{stat.subtitle}</p>
                  </div>
                  <div className={`p-3 bg-gradient-to-br ${stat.color} rounded-lg text-white`}>
                    {stat.icon}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Quick Actions */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-4">
              <Button 
                className="bg-gradient-to-r from-green-400 to-green-500 hover:from-green-500 hover:to-green-600 text-white font-semibold"
                onClick={() => setIsCreateShopOpen(true)}
              >
                <Store className="w-4 h-4 mr-2" />
                Create New Shop
              </Button>
              <Button 
                className="bg-gradient-to-r from-yellow-400 to-amber-500 hover:from-yellow-500 hover:to-amber-600 text-black font-semibold"
                onClick={() => setActiveTab('reviews')}
              >
                <MessageSquare className="w-4 h-4 mr-2" />
                Respond to Reviews
              </Button>
              <Button 
                variant="outline"
                onClick={() => setActiveTab('profile')}
              >
                <Settings className="w-4 h-4 mr-2" />
                Edit Shop Profile
              </Button>
              <Button 
                variant="outline"
                onClick={() => {
                  if (dashboard.shops && dashboard.shops.length > 0) {
                    handleRequestVerification(dashboard.shops[0].id);
                  } else {
                    toast({
                      title: 'No Shops',
                      description: 'Please create a shop first',
                      variant: 'destructive',
                    });
                  }
                }}
              >
                <ShieldCheck className="w-4 h-4 mr-2" />
                Request Verification
              </Button>
              <Button 
                variant="outline"
                onClick={() => {
                  toast({
                    title: 'Coming Soon',
                    description: 'Reports feature is under development',
                  });
                }}
              >
                <FileText className="w-4 h-4 mr-2" />
                View Reports
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* My Shops Overview */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>My Shops</CardTitle>
          </CardHeader>
          <CardContent>
            {dashboard.shops && dashboard.shops.length > 0 ? (
              <div className="grid md:grid-cols-2 gap-4">
                {dashboard.shops.map((shop) => (
                  <div key={shop.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <h3 className="font-semibold text-lg text-gray-900">{shop.name}</h3>
                        <p className="text-sm text-gray-500">{shop.website}</p>
                      </div>
                      <Badge className={shop.is_verified ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                        {shop.is_verified ? 'Verified' : 'Not Verified'}
                      </Badge>
                    </div>
                    <div className="flex items-center space-x-4 text-sm">
                      <div>
                        <span className="font-semibold">⭐ {shop.rating}</span>
                        <span className="text-gray-500 ml-1">({shop.review_count} reviews)</span>
                      </div>
                      <Badge className="bg-blue-100 text-blue-800">{shop.category}</Badge>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <Store className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-700 mb-2">No Shops Yet</h3>
                <p className="text-gray-500 mb-4">Create your first shop to get started</p>
                <Button 
                  className="bg-gradient-to-r from-yellow-400 to-amber-500 hover:from-yellow-500 hover:to-amber-600 text-black"
                  onClick={() => setIsCreateShopOpen(true)}
                >
                  Create Shop
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Reviews */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Recent Reviews</CardTitle>
          </CardHeader>
          <CardContent>
            {dashboard.recent_reviews && dashboard.recent_reviews.length > 0 ? (
              <div className="space-y-4">
                {dashboard.recent_reviews.slice(0, 5).map((review) => (
                  <div key={review.id} className="border-b pb-4 last:border-0">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-yellow-400 to-amber-500 flex items-center justify-center text-white font-bold">
                          {review.user_initials || 'U'}
                        </div>
                        <div>
                          <p className="font-semibold text-gray-900">{review.user_name || 'Anonymous'}</p>
                          <div className="flex items-center">
                            {[...Array(5)].map((_, i) => (
                              <Star
                                key={i}
                                className={`w-4 h-4 ${
                                  i < review.rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'
                                }`}
                              />
                            ))}
                          </div>
                        </div>
                      </div>
                      <span className="text-xs text-gray-500">
                        {new Date(review.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    <p className="text-gray-700 text-sm mb-2">{review.comment}</p>
                    <p className="text-xs text-gray-500">Shop: {review.shop_name}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-center text-gray-500 py-8">No reviews yet</p>
            )}
          </CardContent>
        </Card>

        {/* Management Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="bg-white p-1 rounded-lg shadow">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="profile">Shop Profile</TabsTrigger>
            <TabsTrigger value="reviews">Reviews</TabsTrigger>
            <TabsTrigger value="badges">Trust Badges</TabsTrigger>
            <TabsTrigger value="billing">Billing</TabsTrigger>
          </TabsList>

          <TabsContent value="overview">
            <Card>
              <CardHeader>
                <CardTitle>System Notifications</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {dashboard.statistics.unanswered_reviews > 0 && (
                    <div className="flex items-start space-x-3 p-3 bg-orange-50 rounded-lg">
                      <AlertCircle className="w-5 h-5 text-orange-500 mt-0.5" />
                      <div>
                        <p className="font-semibold text-gray-900">Pending Review Responses</p>
                        <p className="text-sm text-gray-600">
                          You have {dashboard.statistics.unanswered_reviews} reviews waiting for your response
                        </p>
                        <Button
                          size="sm"
                          className="mt-2"
                          onClick={() => setActiveTab('reviews')}
                        >
                          Respond Now
                        </Button>
                      </div>
                    </div>
                  )}
                  {dashboard.statistics.verified_shops < dashboard.statistics.total_shops && (
                    <div className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                      <ShieldCheck className="w-5 h-5 text-blue-500 mt-0.5" />
                      <div>
                        <p className="font-semibold text-gray-900">Verification Pending</p>
                        <p className="text-sm text-gray-600">
                          {dashboard.statistics.total_shops - dashboard.statistics.verified_shops} shop(s) not yet verified. Request verification to build trust.
                        </p>
                      </div>
                    </div>
                  )}
                  {dashboard.statistics.verified_shops === dashboard.statistics.total_shops && dashboard.statistics.total_shops > 0 && (
                    <div className="flex items-start space-x-3 p-3 bg-green-50 rounded-lg">
                      <ShieldCheck className="w-5 h-5 text-green-500 mt-0.5" />
                      <div>
                        <p className="font-semibold text-gray-900">All Shops Verified!</p>
                        <p className="text-sm text-gray-600">
                          Congratulations! All your shops are verified and trusted.
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="profile">
            <ShopProfile shops={dashboard.shops} onUpdate={fetchDashboard} onCreateShop={() => setIsCreateShopOpen(true)} />
          </TabsContent>

          <TabsContent value="reviews">
            <ReviewManagement shops={dashboard.shops} />
          </TabsContent>

          <TabsContent value="badges">
            <TrustBadges shops={dashboard.shops} onUpdate={fetchDashboard} />
          </TabsContent>

          <TabsContent value="billing">
            <Billing />
          </TabsContent>
        </Tabs>
      </div>

      {/* Create Shop Modal */}
      <CreateShopModal 
        isOpen={isCreateShopOpen}
        onClose={() => setIsCreateShopOpen(false)}
        onSuccess={fetchDashboard}
      />
    </div>
  );
};

export default ShopOwnerDashboard;