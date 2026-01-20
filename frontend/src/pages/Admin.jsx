import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { adminAPI } from '../services/api';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Users, Store, ShieldCheck, AlertTriangle, TrendingUp, FileText } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import AdminUsers from '../components/admin/AdminUsers';
import AdminShops from '../components/admin/AdminShops';
import AdminVerificationRequests from '../components/admin/AdminVerificationRequests';
import AdminReviews from '../components/admin/AdminReviews';
import SecurityMonitoring from '../components/admin/SecurityMonitoring';

const Admin = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is admin
    if (!user || user.role !== 'admin') {
      navigate('/');
      return;
    }
    
    fetchDashboard();
  }, [user, navigate]);

  const fetchDashboard = async () => {
    try {
      const response = await adminAPI.getDashboardOverview();
      setDashboard(response.data);
    } catch (error) {
      console.error('Error fetching dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-500"></div>
          <p className="mt-4 text-gray-600">Loading admin dashboard...</p>
        </div>
      </div>
    );
  }

  if (!dashboard) {
    return <div>Error loading dashboard</div>;
  }

  const stats = [
    {
      icon: <Users className="w-8 h-8" />,
      title: 'Total Users',
      value: dashboard.statistics.total_users,
      subtitle: `${dashboard.statistics.active_users} active`,
      color: 'from-blue-500 to-blue-600'
    },
    {
      icon: <Store className="w-8 h-8" />,
      title: 'Total Shops',
      value: dashboard.statistics.total_shops,
      subtitle: `${dashboard.statistics.verified_shops} verified`,
      color: 'from-green-500 to-green-600'
    },
    {
      icon: <FileText className="w-8 h-8" />,
      title: 'Total Reviews',
      value: dashboard.statistics.total_reviews,
      subtitle: `${dashboard.recent_activity.new_reviews_30d} this month`,
      color: 'from-purple-500 to-purple-600'
    },
    {
      icon: <ShieldCheck className="w-8 h-8" />,
      title: 'Pending Verifications',
      value: dashboard.statistics.pending_verifications,
      subtitle: 'Awaiting approval',
      color: 'from-yellow-500 to-yellow-600'
    },
    {
      icon: <AlertTriangle className="w-8 h-8" />,
      title: 'Security Alerts',
      value: dashboard.statistics.active_security_alerts,
      subtitle: `${dashboard.statistics.critical_alerts} critical`,
      color: 'from-red-500 to-red-600'
    },
    {
      icon: <TrendingUp className="w-8 h-8" />,
      title: 'Total Orders',
      value: dashboard.statistics.total_orders,
      subtitle: `${dashboard.recent_activity.new_orders_30d} this month`,
      color: 'from-indigo-500 to-indigo-600'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Admin Dashboard</h1>
          <p className="text-gray-600">Manage users, shops, and platform settings</p>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
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

        {/* Management Tabs */}
        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="bg-white p-1 rounded-lg shadow">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="users">Users</TabsTrigger>
            <TabsTrigger value="shops">Shops</TabsTrigger>
            <TabsTrigger value="reviews">Reviews</TabsTrigger>
            <TabsTrigger value="verification">Verification</TabsTrigger>
            <TabsTrigger value="security">Security</TabsTrigger>
          </TabsList>

          <TabsContent value="overview">
            <div className="grid md:grid-cols-2 gap-6">
              {/* Recent Users */}
              <Card>
                <CardHeader>
                  <CardTitle>Recent Users</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {dashboard.recent_users.slice(0, 5).map((user) => (
                      <div key={user.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div>
                          <p className="font-medium text-gray-900">{user.full_name}</p>
                          <p className="text-sm text-gray-500">{user.email}</p>
                        </div>
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          user.role === 'admin' ? 'bg-red-100 text-red-800' :
                          user.role === 'shop_owner' ? 'bg-blue-100 text-blue-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {user.role}
                        </span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Top Shops */}
              <Card>
                <CardHeader>
                  <CardTitle>Top Rated Shops</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {dashboard.top_shops.slice(0, 5).map((shop) => (
                      <div key={shop.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div>
                          <p className="font-medium text-gray-900">{shop.name}</p>
                          <p className="text-sm text-gray-500">{shop.category}</p>
                        </div>
                        <div className="text-right">
                          <p className="font-bold text-yellow-600">⭐ {shop.rating}</p>
                          <p className="text-xs text-gray-500">{shop.review_count} reviews</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="users">
            <AdminUsers />
          </TabsContent>

          <TabsContent value="shops">
            <AdminShops />
          </TabsContent>

          <TabsContent value="reviews">
            <AdminReviews />
          </TabsContent>

          <TabsContent value="verification">
            <AdminVerificationRequests />
          </TabsContent>

          <TabsContent value="security">
            <SecurityMonitoring />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Admin;
