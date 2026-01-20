import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { useToast } from '../../hooks/use-toast';
import { ShieldCheck, Award, Star, TrendingUp, Copy, Check } from 'lucide-react';

const TrustBadges = ({ shops, onUpdate }) => {
  const { toast } = useToast();
  const [selectedShop, setSelectedShop] = useState(shops?.[0] || null);
  const [copiedBadge, setCopiedBadge] = useState(null);

  const handleCopyCode = (badgeType, code) => {
    navigator.clipboard.writeText(code);
    setCopiedBadge(badgeType);
    toast({
      title: 'Copied!',
      description: 'Badge code copied to clipboard',
    });
    setTimeout(() => setCopiedBadge(null), 2000);
  };

  const badges = [
    {
      type: 'verification',
      icon: <ShieldCheck className="w-8 h-8 text-green-500" />,
      title: 'Verification Badge',
      description: 'Show customers your shop is verified',
      available: selectedShop?.is_verified || false,
      code: `<div style="display:inline-flex;align-items:center;padding:8px 16px;background:#10b981;color:white;border-radius:8px;font-size:14px;">
  <svg style="width:20px;height:20px;margin-right:8px;" fill="currentColor" viewBox="0 0 20 20">
    <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z"/>
    <path fill-rule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm9.707 5.707a1 1 0 00-1.414-1.414L9 12.586l-1.293-1.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
  </svg>
  Verified Shop
</div>`
    },
    {
      type: 'rating',
      icon: <Star className="w-8 h-8 text-yellow-500" />,
      title: 'Rating Badge',
      description: 'Display your average rating',
      available: true,
      code: `<div style="display:inline-flex;align-items:center;padding:8px 16px;background:#fbbf24;color:#1f2937;border-radius:8px;font-size:14px;font-weight:600;">
  <svg style="width:20px;height:20px;margin-right:8px;" fill="currentColor" viewBox="0 0 20 20">
    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
  </svg>
  ${selectedShop?.rating?.toFixed(1) || '0.0'} / 5.0
</div>`
    },
    {
      type: 'reviews',
      icon: <Award className="w-8 h-8 text-blue-500" />,
      title: 'Review Count Badge',
      description: 'Show how many reviews you have',
      available: true,
      code: `<div style="display:inline-flex;align-items:center;padding:8px 16px;background:#3b82f6;color:white;border-radius:8px;font-size:14px;">
  <svg style="width:20px;height:20px;margin-right:8px;" fill="currentColor" viewBox="0 0 20 20">
    <path fill-rule="evenodd" d="M18 13V5a2 2 0 00-2-2H4a2 2 0 00-2 2v8a2 2 0 002 2h3l3 3 3-3h3a2 2 0 002-2zM5 7a1 1 0 011-1h8a1 1 0 110 2H6a1 1 0 01-1-1zm1 3a1 1 0 100 2h3a1 1 0 100-2H6z" clip-rule="evenodd"/>
  </svg>
  ${selectedShop?.review_count || 0} Reviews
</div>`
    },
    {
      type: 'trusted',
      icon: <TrendingUp className="w-8 h-8 text-purple-500" />,
      title: 'Trusted Shop Badge',
      description: 'Complete trust indicator',
      available: selectedShop?.is_verified && (selectedShop?.rating || 0) >= 4.0,
      code: `<div style="display:inline-flex;align-items:center;padding:12px 20px;background:linear-gradient(135deg,#a855f7,#6366f1);color:white;border-radius:12px;font-size:16px;font-weight:600;box-shadow:0 4px 6px rgba(0,0,0,0.1);">
  <svg style="width:24px;height:24px;margin-right:8px;" fill="currentColor" viewBox="0 0 20 20">
    <path fill-rule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
  </svg>
  Trusted Shop
</div>`
    }
  ];

  if (!shops || shops.length === 0) {
    return (
      <Card>
        <CardContent className="p-12 text-center">
          <Award className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-700 mb-2">No Shops</h3>
          <p className="text-gray-500">Create a shop first to get trust badges.</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Shop Selector */}
      {shops.length > 1 && (
        <Card>
          <CardHeader>
            <CardTitle>Select Shop</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-4">
              {shops.map((shop) => (
                <button
                  key={shop.id}
                  onClick={() => setSelectedShop(shop)}
                  className={`p-4 border rounded-lg text-left transition-all ${
                    selectedShop?.id === shop.id
                      ? 'border-yellow-500 bg-yellow-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <h3 className="font-semibold text-gray-900">{shop.name}</h3>
                  <p className="text-sm text-gray-500 mt-1">{shop.category}</p>
                </button>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Trust Badges */}
      <Card>
        <CardHeader>
          <CardTitle>Trust Badges</CardTitle>
          <CardDescription>
            Add these badges to your website to build customer trust. Simply copy the HTML code and paste it into your site.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-6">
            {badges.map((badge) => (
              <Card key={badge.type} className={!badge.available ? 'opacity-50' : ''}>
                <CardContent className="p-6">
                  <div className="flex items-start space-x-4 mb-4">
                    <div className="p-3 bg-gray-50 rounded-lg">
                      {badge.icon}
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 mb-1">{badge.title}</h3>
                      <p className="text-sm text-gray-600">{badge.description}</p>
                    </div>
                  </div>

                  {badge.available ? (
                    <div>
                      <div className="bg-gray-50 rounded-lg p-4 mb-3">
                        <div dangerouslySetInnerHTML={{ __html: badge.code.split('\n').slice(0, 2).join('\n') }} />
                      </div>
                      <Button
                        variant="outline"
                        className="w-full"
                        onClick={() => handleCopyCode(badge.type, badge.code)}
                      >
                        {copiedBadge === badge.type ? (
                          <>
                            <Check className="w-4 h-4 mr-2 text-green-500" />
                            Copied!
                          </>
                        ) : (
                          <>
                            <Copy className="w-4 h-4 mr-2" />
                            Copy HTML Code
                          </>
                        )}
                      </Button>
                    </div>
                  ) : (
                    <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                      <p className="text-sm text-orange-800">
                        {badge.type === 'verification'
                          ? 'Complete shop verification to unlock this badge'
                          : badge.type === 'trusted'
                          ? 'Requires verification and 4.0+ rating'
                          : 'Not available yet'}
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Integration Instructions */}
      <Card>
        <CardHeader>
          <CardTitle>How to Add Badges to Your Website</CardTitle>
        </CardHeader>
        <CardContent>
          <ol className="list-decimal list-inside space-y-3 text-gray-700">
            <li>Click "Copy HTML Code" on any available badge above</li>
            <li>Open your website's HTML editor or page builder</li>
            <li>Paste the code where you want the badge to appear</li>
            <li>Save and publish your changes</li>
          </ol>
          <div className="mt-4 p-4 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-800">
              <strong>Pro Tip:</strong> Place badges near checkout buttons, in your footer, or on product pages to maximize trust and conversions.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default TrustBadges;