import React from 'react';
import { Star } from 'lucide-react';
import { Card, CardContent } from './ui/card';

const ReviewCard = ({ review }) => {
  const renderStars = (rating) => {
    return Array.from({ length: 5 }, (_, index) => (
      <Star
        key={index}
        className={`w-4 h-4 ${
          index < rating
            ? 'fill-yellow-400 text-yellow-400'
            : 'text-gray-300'
        }`}
      />
    ));
  };

  // Format date if it's an ISO string
  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString();
    } catch {
      return dateStr;
    }
  };

  return (
    <Card className="hover:shadow-lg transition-shadow duration-300">
      <CardContent className="p-6">
        {/* User Info */}
        <div className="flex items-start space-x-4 mb-4">
          <div className="w-12 h-12 rounded-full bg-gradient-to-br from-yellow-400 to-amber-500 flex items-center justify-center text-white font-bold text-lg flex-shrink-0">
            {review.user_initials || review.userInitials || 'U'}
          </div>
          <div className="flex-1">
            <div className="flex items-center justify-between mb-1">
              <h4 className="font-semibold text-gray-900">{review.user_name || review.userName || 'Anonymous'}</h4>
              <span className="text-xs text-gray-500">{formatDate(review.created_at || review.date)}</span>
            </div>
            <div className="flex items-center space-x-1 mb-2">
              {renderStars(review.rating || 0)}
            </div>
          </div>
        </div>

        {/* Review Text */}
        <p className="text-gray-700 mb-4">{review.comment || 'No comment'}</p>

        {/* Shop Info */}
        <div className="pt-4 border-t">
          <span className="text-sm text-gray-500">{review.shop_name || review.shopName || 'Shop'}</span>
          <p className="text-xs font-mono text-gray-400 mt-1">{review.shop_website || review.shopWebsite || ''}</p>
        </div>
      </CardContent>
    </Card>
  );
};

export default ReviewCard;