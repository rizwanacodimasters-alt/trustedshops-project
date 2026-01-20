import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { LanguageProvider } from './context/LanguageContext';
import { AuthProvider } from './context/AuthContext';
import { Toaster } from './components/ui/sonner';
import Header from './components/Header';
import Footer from './components/Footer';
import ProtectedRoute from './components/ProtectedRoute';
import Home from './pages/Home';
import SignIn from './pages/SignIn';
import SignUp from './pages/SignUp';
import SignUpBusiness from './pages/SignUpBusiness';
import EmailVerification from './pages/EmailVerification';
import Business from './pages/Business';
import Pricing from './pages/Pricing';
import About from './pages/About';
import FAQ from './pages/FAQ';
import Contact from './pages/Contact';
import Admin from './pages/Admin';
import ShopOwnerDashboard from './pages/ShopOwnerDashboard';
import BillingSuccess from './components/shop-owner/BillingSuccess';
import ShopSearch from './pages/ShopSearch';
import ShopDetail from './pages/ShopDetail';
import CustomerDashboard from './pages/CustomerDashboard';
import FakeShopChecker from './pages/FakeShopChecker';
import MyAccount from './pages/MyAccount';

function App() {
  return (
    <LanguageProvider>
      <AuthProvider>
        <BrowserRouter>
          <div className="App flex flex-col min-h-screen">
            <Header />
            <main className="flex-1">
              <Routes>
                {/* Public Routes */}
                <Route path="/" element={<Home />} />
                <Route path="/business" element={<Business />} />
                <Route path="/pricing" element={<Pricing />} />
                <Route path="/about" element={<About />} />
                <Route path="/faq" element={<FAQ />} />
                <Route path="/contact" element={<Contact />} />
                <Route path="/signin" element={<SignIn />} />
                <Route path="/signup" element={<SignUp />} />
                <Route path="/signup/business" element={<SignUpBusiness />} />
                <Route path="/shops" element={<ShopSearch />} />
                <Route path="/shop/:shopId" element={<ShopDetail />} />
                <Route path="/fake-shops" element={<FakeShopChecker />} />
                
                {/* Email Verification Route (accessible to authenticated users) */}
                <Route 
                  path="/email-verification" 
                  element={
                    <ProtectedRoute>
                      <EmailVerification />
                    </ProtectedRoute>
                  } 
                />
                
                {/* Protected Routes (require email verification) */}
                <Route 
                  path="/admin" 
                  element={
                    <ProtectedRoute>
                      <Admin />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/shop-dashboard" 
                  element={
                    <ProtectedRoute>
                      <ShopOwnerDashboard />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/billing/success" 
                  element={
                    <ProtectedRoute>
                      <BillingSuccess />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/my-dashboard" 
                  element={
                    <ProtectedRoute>
                      <CustomerDashboard />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/profile" 
                  element={
                    <ProtectedRoute>
                      <MyAccount />
                    </ProtectedRoute>
                  } 
                />
              </Routes>
            </main>
            <Footer />
            <Toaster />
          </div>
        </BrowserRouter>
      </AuthProvider>
    </LanguageProvider>
  );
}

export default App;
