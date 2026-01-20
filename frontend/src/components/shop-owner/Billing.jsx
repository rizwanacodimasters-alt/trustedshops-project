import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { useToast } from '../../hooks/use-toast';
import { billingAPI } from '../../services/api';
import { CreditCard, Package, Calendar, Download, CheckCircle, Loader2 } from 'lucide-react';

const Billing = () => {
  const { toast } = useToast();
  const [currentSubscription, setCurrentSubscription] = useState(null);
  const [availablePlans, setAvailablePlans] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [upgradingPlan, setUpgradingPlan] = useState(null);

  useEffect(() => {
    fetchBillingData();
  }, []);

  const fetchBillingData = async () => {
    try {
      setLoading(true);
      
      // Fetch subscription, plans, and transactions in parallel
      const [subResponse, plansResponse, transResponse] = await Promise.all([
        billingAPI.getSubscription(),
        billingAPI.getPlans(),
        billingAPI.getTransactions()
      ]);

      setCurrentSubscription(subResponse.data);
      
      // Convert plans object to array
      const plansArray = Object.entries(plansResponse.data.plans).map(([id, plan]) => ({
        id,
        ...plan,
        features: getPlanFeatures(id)
      }));
      setAvailablePlans(plansArray);
      
      setTransactions(transResponse.data.transactions || []);
    } catch (error) {
      console.error('Error fetching billing data:', error);
      toast({
        title: 'Error',
        description: 'Failed to load billing information',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const getPlanFeatures = (planId) => {
    const features = {
      basic: ['1 Shop', 'Up to 100 reviews', 'Basic support', 'Trust badges'],
      professional: ['5 Shops', 'Unlimited reviews', 'Priority support', 'Trust badges', 'Advanced analytics', 'Custom branding'],
      enterprise: ['Unlimited shops', 'Unlimited reviews', '24/7 support', 'Trust badges', 'Advanced analytics', 'Custom branding', 'API access', 'Dedicated manager']
    };
    return features[planId] || [];
  };

  const handleUpgrade = async (planId) => {
    if (currentSubscription?.plan_id === planId) {
      toast({
        title: 'Already Subscribed',
        description: 'You are already on this plan',
      });
      return;
    }

    try {
      setUpgradingPlan(planId);
      
      // Get current origin URL
      const originUrl = window.location.origin;
      
      // Create checkout session
      const response = await billingAPI.createCheckoutSession({
        plan_id: planId,
        origin_url: originUrl
      });

      // Redirect to Stripe Checkout
      if (response.data.url) {
        window.location.href = response.data.url;
      } else {
        throw new Error('No checkout URL received');
      }
    } catch (error) {
      console.error('Error creating checkout:', error);
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to initiate checkout',
        variant: 'destructive',
      });
      setUpgradingPlan(null);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-yellow-500" />
        <p className="ml-2 text-gray-600">Loading billing information...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Current Plan */}
      <Card>
        <CardHeader>
          <CardTitle>Current Plan</CardTitle>
          <CardDescription>Manage your subscription and billing details</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center space-x-3 mb-2">
                <h3 className="text-2xl font-bold text-gray-900">
                  {currentSubscription?.plan_name || 'No Active Plan'}
                </h3>
                <Badge className="bg-green-100 text-green-800">
                  {currentSubscription?.status || 'Inactive'}
                </Badge>
              </div>
              <p className="text-gray-600">
                ${currentSubscription?.price || 0}/{currentSubscription?.currency || 'usd'}
              </p>
              {currentSubscription?.updated_at && (
                <p className="text-sm text-gray-500 mt-2">
                  Last updated: {formatDate(currentSubscription.updated_at)}
                </p>
              )}
            </div>
            <div className="flex space-x-3">
              <Button 
                variant="outline"
                onClick={() => toast({
                  title: 'Coming Soon',
                  description: 'Plan management features will be available soon',
                })}
              >
                Manage Plan
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Available Plans */}
      <Card>
        <CardHeader>
          <CardTitle>Available Plans</CardTitle>
          <CardDescription>Choose the plan that best fits your needs</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-6">
            {availablePlans.map((plan) => {
              const isCurrentPlan = currentSubscription?.plan_id === plan.id;
              const isProfessional = plan.id === 'professional';
              
              return (
                <Card
                  key={plan.id}
                  className={`relative ${
                    isProfessional ? 'border-yellow-500 border-2' : ''
                  }`}
                >
                  {isProfessional && (
                    <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                      <Badge className="bg-gradient-to-r from-yellow-400 to-amber-500 text-black">
                        Most Popular
                      </Badge>
                    </div>
                  )}
                  <CardContent className="p-6">
                    <div className="text-center mb-6">
                      <h3 className="text-xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                      <div className="text-3xl font-bold text-gray-900">
                        ${plan.price}
                        <span className="text-sm text-gray-500 font-normal">/month</span>
                      </div>
                    </div>
                    <ul className="space-y-3 mb-6">
                      {plan.features.map((feature, index) => (
                        <li key={index} className="flex items-start space-x-2 text-sm">
                          <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                          <span className="text-gray-700">{feature}</span>
                        </li>
                      ))}
                    </ul>
                    <Button
                      className={`w-full ${
                        isCurrentPlan
                          ? 'bg-gray-300 text-gray-600 cursor-not-allowed'
                          : isProfessional
                          ? 'bg-gradient-to-r from-yellow-400 to-amber-500 hover:from-yellow-500 hover:to-amber-600 text-black'
                          : ''
                      }`}
                      disabled={isCurrentPlan || upgradingPlan === plan.id}
                      onClick={() => handleUpgrade(plan.id)}
                    >
                      {upgradingPlan === plan.id ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Processing...
                        </>
                      ) : isCurrentPlan ? (
                        'Current Plan'
                      ) : (
                        'Upgrade'
                      )}
                    </Button>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Payment Method */}
      <Card>
        <CardHeader>
          <CardTitle>Payment Method</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg">
                <CreditCard className="w-6 h-6 text-white" />
              </div>
              <div>
                <p className="font-semibold text-gray-900">Stripe Checkout</p>
                <p className="text-sm text-gray-500">Managed by Stripe</p>
              </div>
            </div>
            <Button 
              variant="outline"
              onClick={() => toast({
                title: 'Coming Soon',
                description: 'Payment method management will be available soon',
              })}
            >
              Update
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Billing History */}
      <Card>
        <CardHeader>
          <CardTitle>Billing History</CardTitle>
          <CardDescription>Your past invoices and payments</CardDescription>
        </CardHeader>
        <CardContent>
          {transactions.length > 0 ? (
            <div className="space-y-4">
              {transactions.map((transaction) => (
                <div key={transaction.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center space-x-4">
                    <div className="p-2 bg-gray-50 rounded-lg">
                      <Calendar className="w-5 h-5 text-gray-600" />
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900">
                        {transaction.plan_name || 'Subscription'}
                      </p>
                      <p className="text-sm text-gray-500">
                        {formatDate(transaction.created_at)}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <p className="font-semibold text-gray-900">
                        ${transaction.amount} {transaction.currency?.toUpperCase()}
                      </p>
                      <Badge className={`mt-1 ${
                        transaction.payment_status === 'paid' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-orange-100 text-orange-800'
                      }`}>
                        {transaction.payment_status}
                      </Badge>
                    </div>
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => toast({
                        title: 'Coming Soon',
                        description: 'Invoice download will be available soon',
                      })}
                    >
                      <Download className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-center text-gray-500 py-8">No transactions yet</p>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Billing;