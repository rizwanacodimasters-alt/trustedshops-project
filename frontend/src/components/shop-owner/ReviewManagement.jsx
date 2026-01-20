import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Textarea } from '../ui/textarea';
import { Badge } from '../ui/badge';
import { useToast } from '../../hooks/use-toast';
import { reviewAPI } from '../../services/api';
import { Star, MessageSquare, Send } from 'lucide-react';

const ReviewManagement = ({ shops }) => {
  const { toast } = useToast();
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedShop, setSelectedShop] = useState(shops?.[0]?.id || null);
  const [replyingTo, setReplyingTo] = useState(null);
  const [replyText, setReplyText] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (selectedShop) {
      fetchReviews();
    }
  }, [selectedShop]);

  const fetchReviews = async () => {
    try {
      setLoading(true);
      const response = await reviewAPI.getReviews({ shop_id: selectedShop });
      setReviews(response.data.reviews || []);
    } catch (error) {
      console.error('Error fetching reviews:', error);
      toast({
        title: 'Error',
        description: 'Failed to load reviews',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleReply = async (reviewId) => {
    if (!replyText.trim()) {
      toast({
        title: 'Error',
        description: 'Please enter a response',
        variant: 'destructive',
      });
      return;
    }

    try {
      setSubmitting(true);
      await reviewAPI.respondToReview(reviewId, { response: replyText });
      toast({
        title: 'Success',
        description: 'Response posted successfully!',
      });
      setReplyingTo(null);
      setReplyText('');
      fetchReviews();
    } catch (error) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to post response',
        variant: 'destructive',
      });
    } finally {
      setSubmitting(false);
    }
  };

  if (!shops || shops.length === 0) {
    return (
      <Card>
        <CardContent className="p-12 text-center">
          <MessageSquare className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-700 mb-2">No Shops</h3>
          <p className="text-gray-500">Create a shop first to manage reviews.</p>
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
            <div className="flex flex-wrap gap-2">
              {shops.map((shop) => (
                <Button
                  key={shop.id}
                  variant={selectedShop === shop.id ? 'default' : 'outline'}
                  onClick={() => setSelectedShop(shop.id)}
                  className={selectedShop === shop.id ? 'bg-gradient-to-r from-yellow-400 to-amber-500 text-black' : ''}
                >
                  {shop.name}
                </Button>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Reviews List */}
      <Card>
        <CardHeader>
          <CardTitle>Customer Reviews</CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-yellow-500"></div>
              <p className="mt-2 text-gray-600">Loading reviews...</p>
            </div>
          ) : reviews.length === 0 ? (
            <div className="text-center py-12">
              <MessageSquare className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-700 mb-2">No Reviews Yet</h3>
              <p className="text-gray-500">Reviews for this shop will appear here.</p>
            </div>
          ) : (
            <div className="space-y-6">
              {reviews.map((review) => (
                <div key={review.id} className="border rounded-lg p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-12 h-12 rounded-full bg-gradient-to-br from-yellow-400 to-amber-500 flex items-center justify-center text-white font-bold text-lg">
                        {review.user_name?.[0] || 'U'}
                      </div>
                      <div>
                        <p className="font-semibold text-gray-900">{review.user_name || 'Anonymous'}</p>
                        <div className="flex items-center mt-1">
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
                    <div className="text-right">
                      <p className="text-sm text-gray-500">
                        {new Date(review.created_at).toLocaleDateString()}
                      </p>
                      {review.response ? (
                        <Badge className="mt-2 bg-green-100 text-green-800">Responded</Badge>
                      ) : (
                        <Badge className="mt-2 bg-orange-100 text-orange-800">Needs Response</Badge>
                      )}
                    </div>
                  </div>

                  <p className="text-gray-700 mb-4">{review.comment}</p>

                  {review.response && (
                    <div className="bg-blue-50 rounded-lg p-4 mb-4">
                      <p className="text-sm font-semibold text-blue-900 mb-2">Your Response:</p>
                      <p className="text-blue-800">{review.response}</p>
                    </div>
                  )}

                  {!review.response && (
                    <div>
                      {replyingTo === review.id ? (
                        <div className="space-y-3">
                          <Textarea
                            value={replyText}
                            onChange={(e) => setReplyText(e.target.value)}
                            placeholder="Write your response..."
                            rows={3}
                          />
                          <div className="flex space-x-2">
                            <Button
                              onClick={() => handleReply(review.id)}
                              disabled={submitting}
                              className="bg-gradient-to-r from-yellow-400 to-amber-500 hover:from-yellow-500 hover:to-amber-600 text-black"
                            >
                              <Send className="w-4 h-4 mr-2" />
                              {submitting ? 'Posting...' : 'Post Response'}
                            </Button>
                            <Button
                              variant="outline"
                              onClick={() => {
                                setReplyingTo(null);
                                setReplyText('');
                              }}
                              disabled={submitting}
                            >
                              Cancel
                            </Button>
                          </div>
                        </div>
                      ) : (
                        <Button
                          variant="outline"
                          onClick={() => setReplyingTo(review.id)}
                          className="w-full"
                        >
                          <MessageSquare className="w-4 h-4 mr-2" />
                          Respond to Review
                        </Button>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default ReviewManagement;