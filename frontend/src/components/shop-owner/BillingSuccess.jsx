import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { billingAPI } from '../../services/api';
import { CheckCircle, Loader2 } from 'lucide-react';

const BillingSuccess = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('checking');
  const [paymentDetails, setPaymentDetails] = useState(null);
  const sessionId = searchParams.get('session_id');

  useEffect(() => {
    if (sessionId) {
      pollPaymentStatus(sessionId);
    }
  }, [sessionId]);

  const pollPaymentStatus = async (sessionId, attempts = 0) => {
    const maxAttempts = 5;
    const pollInterval = 2000; // 2 seconds

    if (attempts >= maxAttempts) {
      setStatus('timeout');
      return;
    }

    try {
      const response = await billingAPI.getCheckoutStatus(sessionId);
      
      if (response.data.payment_status === 'paid') {
        setStatus('success');
        setPaymentDetails(response.data);
        return;
      } else if (response.data.status === 'expired') {
        setStatus('expired');
        return;
      }

      // Continue polling
      setTimeout(() => pollPaymentStatus(sessionId, attempts + 1), pollInterval);
    } catch (error) {
      console.error('Error checking payment status:', error);
      setStatus('error');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4">
      <Card className="max-w-md w-full">
        <CardHeader>
          <CardTitle className="text-center">Payment Status</CardTitle>
        </CardHeader>
        <CardContent className="text-center">
          {status === 'checking' && (
            <>
              <Loader2 className="w-16 h-16 text-yellow-500 mx-auto mb-4 animate-spin" />
              <h3 className="text-lg font-semibold mb-2">Processing Payment</h3>
              <p className="text-gray-600">Please wait while we confirm your payment...</p>
            </>
          )}

          {status === 'success' && (
            <>
              <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2 text-green-700">Payment Successful!</h3>
              <p className="text-gray-600 mb-4">
                Thank you for your subscription. Your account has been upgraded.
              </p>
              {paymentDetails && (
                <div className="bg-gray-50 rounded-lg p-4 mb-4 text-left">
                  <p className="text-sm text-gray-600">
                    <strong>Amount:</strong> {paymentDetails.currency.toUpperCase()} {(paymentDetails.amount_total / 100).toFixed(2)}
                  </p>
                </div>
              )}
              <Button
                onClick={() => navigate('/shop-dashboard')}
                className="w-full bg-gradient-to-r from-yellow-400 to-amber-500 hover:from-yellow-500 hover:to-amber-600 text-black"
              >
                Return to Dashboard
              </Button>
            </>
          )}

          {status === 'timeout' && (
            <>
              <div className="w-16 h-16 rounded-full bg-orange-100 mx-auto mb-4 flex items-center justify-center">
                <span className="text-3xl">⏱️</span>
              </div>
              <h3 className="text-lg font-semibold mb-2">Payment Check Timeout</h3>
              <p className="text-gray-600 mb-4">
                We're still processing your payment. Please check your email for confirmation.
              </p>
              <Button
                onClick={() => navigate('/shop-dashboard')}
                variant="outline"
                className="w-full"
              >
                Return to Dashboard
              </Button>
            </>
          )}

          {status === 'expired' && (
            <>
              <div className="w-16 h-16 rounded-full bg-red-100 mx-auto mb-4 flex items-center justify-center">
                <span className="text-3xl">❌</span>
              </div>
              <h3 className="text-lg font-semibold mb-2">Payment Expired</h3>
              <p className="text-gray-600 mb-4">
                Your payment session has expired. Please try again.
              </p>
              <Button
                onClick={() => navigate('/shop-dashboard')}
                className="w-full"
              >
                Return to Dashboard
              </Button>
            </>
          )}

          {status === 'error' && (
            <>
              <div className="w-16 h-16 rounded-full bg-red-100 mx-auto mb-4 flex items-center justify-center">
                <span className="text-3xl">⚠️</span>
              </div>
              <h3 className="text-lg font-semibold mb-2">Error</h3>
              <p className="text-gray-600 mb-4">
                There was an error checking your payment status. Please contact support.
              </p>
              <Button
                onClick={() => navigate('/shop-dashboard')}
                variant="outline"
                className="w-full"
              >
                Return to Dashboard
              </Button>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default BillingSuccess;
