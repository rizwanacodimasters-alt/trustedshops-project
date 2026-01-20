import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { User, Mail, Calendar, Shield, Edit2, Save, X } from 'lucide-react';
import { useToast } from '../hooks/use-toast';

const MyAccount = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [isEditing, setIsEditing] = useState(false);
  const [editedName, setEditedName] = useState(user?.full_name || '');

  // Redirect if not logged in
  React.useEffect(() => {
    if (!user) {
      navigate('/signin');
    }
  }, [user, navigate]);

  if (!user) {
    return null;
  }

  const handleSave = async () => {
    // TODO: Implement API call to update user profile
    toast({
      title: 'Coming Soon',
      description: 'Profile update feature will be implemented soon.',
    });
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditedName(user.full_name);
    setIsEditing(false);
  };

  const getRoleBadgeColor = (role) => {
    switch (role) {
      case 'admin':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'shop_owner':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'shopper':
        return 'bg-green-100 text-green-800 border-green-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getRoleLabel = (role) => {
    switch (role) {
      case 'admin':
        return 'Administrator';
      case 'shop_owner':
        return 'Shop Owner';
      case 'shopper':
        return 'Customer';
      default:
        return role;
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('de-DE', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const getDashboardLink = () => {
    switch (user.role) {
      case 'admin':
        return '/admin';
      case 'shop_owner':
        return '/shop-dashboard';
      case 'shopper':
        return '/my-dashboard';
      default:
        return '/';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-4xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">My Account</h1>
          <p className="text-gray-600">Manage your account settings and preferences</p>
        </div>

        <Tabs defaultValue="profile" className="space-y-6">
          <TabsList className="bg-white p-1 rounded-lg shadow">
            <TabsTrigger value="profile">Profile</TabsTrigger>
            <TabsTrigger value="security">Security</TabsTrigger>
            <TabsTrigger value="preferences">Preferences</TabsTrigger>
          </TabsList>

          {/* Profile Tab */}
          <TabsContent value="profile">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span className="flex items-center gap-2">
                    <User className="w-5 h-5" />
                    Profile Information
                  </span>
                  {!isEditing && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setIsEditing(true)}
                    >
                      <Edit2 className="w-4 h-4 mr-2" />
                      Edit
                    </Button>
                  )}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Full Name */}
                <div className="flex items-start justify-between py-4 border-b">
                  <div className="flex items-center gap-3 flex-1">
                    <div className="p-2 bg-blue-100 rounded-lg">
                      <User className="w-5 h-5 text-blue-600" />
                    </div>
                    <div className="flex-1">
                      <p className="text-sm text-gray-600 mb-1">Full Name</p>
                      {isEditing ? (
                        <Input
                          value={editedName}
                          onChange={(e) => setEditedName(e.target.value)}
                          className="max-w-md"
                        />
                      ) : (
                        <p className="text-lg font-semibold text-gray-900">
                          {user.full_name}
                        </p>
                      )}
                    </div>
                  </div>
                </div>

                {/* Email */}
                <div className="flex items-start justify-between py-4 border-b">
                  <div className="flex items-center gap-3 flex-1">
                    <div className="p-2 bg-purple-100 rounded-lg">
                      <Mail className="w-5 h-5 text-purple-600" />
                    </div>
                    <div className="flex-1">
                      <p className="text-sm text-gray-600 mb-1">Email Address</p>
                      <p className="text-lg font-semibold text-gray-900">{user.email}</p>
                      <p className="text-xs text-gray-500 mt-1">
                        Email cannot be changed
                      </p>
                    </div>
                  </div>
                </div>

                {/* Role */}
                <div className="flex items-start justify-between py-4 border-b">
                  <div className="flex items-center gap-3 flex-1">
                    <div className="p-2 bg-yellow-100 rounded-lg">
                      <Shield className="w-5 h-5 text-yellow-600" />
                    </div>
                    <div className="flex-1">
                      <p className="text-sm text-gray-600 mb-2">Account Role</p>
                      <Badge className={getRoleBadgeColor(user.role)}>
                        {getRoleLabel(user.role)}
                      </Badge>
                    </div>
                  </div>
                </div>

                {/* Created At */}
                <div className="flex items-start justify-between py-4">
                  <div className="flex items-center gap-3 flex-1">
                    <div className="p-2 bg-green-100 rounded-lg">
                      <Calendar className="w-5 h-5 text-green-600" />
                    </div>
                    <div className="flex-1">
                      <p className="text-sm text-gray-600 mb-1">Member Since</p>
                      <p className="text-lg font-semibold text-gray-900">
                        {formatDate(user.created_at)}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                {isEditing && (
                  <div className="flex gap-3 pt-4">
                    <Button onClick={handleSave} className="flex-1">
                      <Save className="w-4 h-4 mr-2" />
                      Save Changes
                    </Button>
                    <Button variant="outline" onClick={handleCancel} className="flex-1">
                      <X className="w-4 h-4 mr-2" />
                      Cancel
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card className="mt-6">
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button
                  variant="outline"
                  className="w-full justify-start"
                  onClick={() => navigate(getDashboardLink())}
                >
                  Go to Dashboard
                </Button>
                {user.role === 'shopper' && (
                  <Button
                    variant="outline"
                    className="w-full justify-start"
                    onClick={() => navigate('/shops')}
                  >
                    Browse Shops
                  </Button>
                )}
                {user.role === 'shop_owner' && (
                  <Button
                    variant="outline"
                    className="w-full justify-start"
                    onClick={() => navigate('/shop-dashboard')}
                  >
                    Manage Shops
                  </Button>
                )}
                <Button
                  variant="outline"
                  className="w-full justify-start text-red-600 hover:text-red-700 hover:bg-red-50"
                  onClick={logout}
                >
                  Logout
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Security Tab */}
          <TabsContent value="security">
            <Card>
              <CardHeader>
                <CardTitle>Security Settings</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                    <h3 className="font-semibold text-blue-900 mb-2">Password</h3>
                    <p className="text-sm text-blue-800 mb-3">
                      Keep your account secure with a strong password
                    </p>
                    <Button variant="outline" size="sm">
                      Change Password
                    </Button>
                  </div>

                  <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                    <h3 className="font-semibold text-gray-900 mb-2">
                      Two-Factor Authentication
                    </h3>
                    <p className="text-sm text-gray-600 mb-3">
                      Coming soon - Add an extra layer of security
                    </p>
                    <Button variant="outline" size="sm" disabled>
                      Enable 2FA
                    </Button>
                  </div>

                  <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                    <h3 className="font-semibold text-gray-900 mb-2">Active Sessions</h3>
                    <p className="text-sm text-gray-600 mb-3">
                      Manage devices where you're logged in
                    </p>
                    <Button variant="outline" size="sm" disabled>
                      View Sessions
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Preferences Tab */}
          <TabsContent value="preferences">
            <Card>
              <CardHeader>
                <CardTitle>Preferences</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                    <h3 className="font-semibold text-gray-900 mb-2">Language</h3>
                    <p className="text-sm text-gray-600 mb-3">
                      Change your preferred language (English, اردو, العربية)
                    </p>
                    <p className="text-sm text-blue-600">
                      Use the language selector in the header
                    </p>
                  </div>

                  <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                    <h3 className="font-semibold text-gray-900 mb-2">
                      Email Notifications
                    </h3>
                    <p className="text-sm text-gray-600 mb-3">
                      Coming soon - Control what emails you receive
                    </p>
                    <Button variant="outline" size="sm" disabled>
                      Manage Notifications
                    </Button>
                  </div>

                  <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                    <h3 className="font-semibold text-gray-900 mb-2">Privacy</h3>
                    <p className="text-sm text-gray-600 mb-3">
                      Coming soon - Control your privacy settings
                    </p>
                    <Button variant="outline" size="sm" disabled>
                      Privacy Settings
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default MyAccount;
