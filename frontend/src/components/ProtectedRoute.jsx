import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

/**
 * ProtectedRoute component that ensures:
 * 1. User is authenticated
 * 2. User's email is verified
 * 
 * If not authenticated -> redirect to /signin
 * If authenticated but email not verified -> redirect to /email-verification
 */
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  const location = useLocation();

  // Show loading state while checking authentication
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Not authenticated -> redirect to signin
  if (!user) {
    return <Navigate to="/signin" state={{ from: location }} replace />;
  }

  // Authenticated but email not verified -> redirect to email verification
  // EXCEPTION: Admins are auto-verified and don't need email verification
  if (!user.email_verified && user.role !== 'admin') {
    // Allow access to email verification page itself
    if (location.pathname === '/email-verification') {
      return children;
    }
    
    return <Navigate to="/email-verification" state={{ email: user.email }} replace />;
  }

  // Authenticated and verified -> allow access
  return children;
};

export default ProtectedRoute;
