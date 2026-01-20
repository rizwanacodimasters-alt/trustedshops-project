import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Textarea } from '../ui/textarea';
import { useToast } from '../../hooks/use-toast';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '../ui/alert-dialog';
import { Star, CheckCircle, XCircle, Eye, Clock, Filter, Image, MessageSquare, FileText } from 'lucide-react';
import axios from 'axios';

const AdminReviews = () => {
  const { toast } = useToast();
  const [reviews, setReviews] = useState([]);
  const [pendingReviews, setPendingReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // all, pending, approved, rejected
  const [selectedReview, setSelectedReview] = useState(null);
  const [showApproveDialog, setShowApproveDialog] = useState(false);
  const [showRejectDialog, setShowRejectDialog] = useState(false);
  const [showProofDialog, setShowProofDialog] = useState(false);
  const [adminNotes, setAdminNotes] = useState('');
  const [actionLoading, setActionLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchReviews();
    fetchPendingReviews();
  }, [filter, searchTerm]);

  const fetchReviews = async () => {
    try {
      const token = localStorage.getItem('token');
      const params = {};
      if (filter !== 'all') {
        params.status_filter = filter;
      }
      if (searchTerm) {
        params.search = searchTerm;
      }
      
      console.log('Fetching reviews with filter:', filter, 'search:', searchTerm);
      
      const response = await axios.get(
        `${process.env.REACT_APP_BACKEND_URL}/api/admin/reviews`,
        {
          headers: { Authorization: `Bearer ${token}` },
          params
        }
      );
      
      console.log('Reviews response:', response.data);
      
      setReviews(response.data.data || []);
    } catch (error) {
      console.error('Error fetching reviews:', error);
      console.error('Error details:', error.response?.data);
      toast({
        title: 'Fehler',
        description: error.response?.data?.detail || 'Bewertungen konnten nicht geladen werden',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchPendingReviews = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${process.env.REACT_APP_BACKEND_URL}/api/admin/reviews/pending`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setPendingReviews(response.data.data || []);
    } catch (error) {
      console.error('Error fetching pending reviews:', error);
    }
  };

  const handleApprove = async () => {
    if (!selectedReview) return;
    
    setActionLoading(true);
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${process.env.REACT_APP_BACKEND_URL}/api/admin/reviews/${selectedReview._id}/action`,
        {
          action: 'approve',
          admin_notes: adminNotes || undefined
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      toast({
        title: 'Erfolg!',
        description: 'Bewertung wurde genehmigt'
      });
      
      setShowApproveDialog(false);
      setSelectedReview(null);
      setAdminNotes('');
      fetchReviews();
      fetchPendingReviews();
    } catch (error) {
      toast({
        title: 'Fehler',
        description: error.response?.data?.detail || 'Genehmigung fehlgeschlagen',
        variant: 'destructive'
      });
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async () => {
    if (!selectedReview) return;
    
    setActionLoading(true);
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${process.env.REACT_APP_BACKEND_URL}/api/admin/reviews/${selectedReview._id}/action`,
        {
          action: 'reject',
          admin_notes: adminNotes || undefined
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      toast({
        title: 'Erfolg!',
        description: 'Bewertung wurde abgelehnt'
      });
      
      setShowRejectDialog(false);
      setSelectedReview(null);
      setAdminNotes('');
      fetchReviews();
      fetchPendingReviews();
    } catch (error) {
      toast({
        title: 'Fehler',
        description: error.response?.data?.detail || 'Ablehnung fehlgeschlagen',
        variant: 'destructive'
      });
    } finally {
      setActionLoading(false);
    }
  };

  const openProofViewer = (review) => {
    setSelectedReview(review);
    setShowProofDialog(true);
  };

  const getStatusBadge = (status) => {
    const styles = {
      pending: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
      published: 'bg-blue-100 text-blue-800'
    };
    
    const labels = {
      pending: 'Ausstehend',
      approved: 'Genehmigt',
      rejected: 'Abgelehnt',
      published: 'Veröffentlicht'
    };
    
    return (
      <Badge className={styles[status] || 'bg-gray-100 text-gray-800'}>
        {labels[status] || status}
      </Badge>
    );
  };

  const getReviewTypeBadge = (type) => {
    const styles = {
      verified: 'bg-green-100 text-green-800',
      imported: 'bg-purple-100 text-purple-800',
      unverified: 'bg-gray-100 text-gray-800'
    };
    
    const labels = {
      verified: '✓ Verifiziert',
      imported: 'Importiert',
      unverified: 'Nicht verifiziert'
    };
    
    return (
      <Badge className={styles[type] || 'bg-gray-100 text-gray-800'}>
        {labels[type] || type}
      </Badge>
    );
  };

  const renderStars = (rating) => {
    return (
      <div className="flex">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={`w-4 h-4 ${
              star <= rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'
            }`}
          />
        ))}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Lade Bewertungen...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Pending Reviews Alert */}
      {pendingReviews.length > 0 && (
        <Card className="border-yellow-200 bg-yellow-50">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <Clock className="w-5 h-5 text-yellow-600" />
              <div className="flex-1">
                <p className="font-medium text-yellow-800">
                  {pendingReviews.length} Bewertung{pendingReviews.length !== 1 ? 'en' : ''} warte{pendingReviews.length !== 1 ? 'n' : 't'} auf Genehmigung
                </p>
                <p className="text-sm text-yellow-700">
                  Low-Star-Bewertungen (1-2 Sterne) benötigen Ihre Prüfung und Genehmigung
                </p>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setFilter('pending')}
                className="border-yellow-600 text-yellow-600 hover:bg-yellow-100"
              >
                Anzeigen
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Filters */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>Bewertungen Verwalten</CardTitle>
            <div className="flex gap-2">
              <Button
                variant={filter === 'all' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilter('all')}
              >
                Alle
              </Button>
              <Button
                variant={filter === 'pending' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilter('pending')}
              >
                Ausstehend
              </Button>
              <Button
                variant={filter === 'approved' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilter('approved')}
              >
                Genehmigt
              </Button>
              <Button
                variant={filter === 'rejected' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilter('rejected')}
              >
                Abgelehnt
              </Button>
            </div>
          </div>
          {/* Search Bar */}
          <div className="mt-4">
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <input
                type="text"
                placeholder="Suche in Bewertungen (Kommentar, Shop, Benutzer)..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500"
              />
              {searchTerm && (
                <button
                  onClick={() => setSearchTerm('')}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  ×
                </button>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {reviews.length === 0 ? (
              <p className="text-center text-gray-500 py-8">Keine Bewertungen gefunden</p>
            ) : (
              reviews.map((review) => (
                <div key={review._id} className="border rounded-lg p-4 space-y-3">
                  {/* Header */}
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium">{review.user_name || 'Unbekannt'}</span>
                        <span className="text-gray-400">→</span>
                        <span className="text-gray-700">{review.shop_name || 'Unbekannt'}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        {renderStars(review.rating)}
                        {getReviewTypeBadge(review.review_type)}
                        {getStatusBadge(review.status)}
                      </div>
                    </div>
                    <div className="text-right text-sm text-gray-500">
                      {new Date(review.created_at).toLocaleDateString('de-DE')}
                    </div>
                  </div>

                  {/* Comment */}
                  <p className="text-gray-700">{review.comment}</p>

                  {/* Proof Indicator */}
                  {review.rating <= 2 && review.proof_photos && review.proof_photos.length > 0 && (
                    <div className="flex items-center gap-2 text-sm text-blue-600">
                      <FileText className="w-4 h-4" />
                      <span>Nachweis vorhanden ({review.proof_photos.length} Fotos)</span>
                    </div>
                  )}

                  {/* Admin Notes */}
                  {review.admin_notes && (
                    <div className="bg-gray-50 p-3 rounded">
                      <p className="text-sm font-medium text-gray-700 mb-1">Admin-Notizen:</p>
                      <p className="text-sm text-gray-600">{review.admin_notes}</p>
                    </div>
                  )}

                  {/* Actions */}
                  <div className="flex gap-2 pt-2 border-t">
                    {review.status === 'pending' && (
                      <>
                        {review.rating <= 2 && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => openProofViewer(review)}
                          >
                            <Eye className="w-4 h-4 mr-2" />
                            Nachweis ansehen
                          </Button>
                        )}
                        <Button
                          variant="outline"
                          size="sm"
                          className="text-green-600 border-green-600 hover:bg-green-50"
                          onClick={() => {
                            setSelectedReview(review);
                            setShowApproveDialog(true);
                          }}
                        >
                          <CheckCircle className="w-4 h-4 mr-2" />
                          Genehmigen
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          className="text-red-600 border-red-600 hover:bg-red-50"
                          onClick={() => {
                            setSelectedReview(review);
                            setShowRejectDialog(true);
                          }}
                        >
                          <XCircle className="w-4 h-4 mr-2" />
                          Ablehnen
                        </Button>
                      </>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>

      {/* Approve Dialog */}
      <AlertDialog open={showApproveDialog} onOpenChange={setShowApproveDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Bewertung genehmigen?</AlertDialogTitle>
            <AlertDialogDescription>
              Diese Bewertung wird veröffentlicht und in die Shop-Bewertung einberechnet.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium">Admin-Notizen (optional)</label>
              <Textarea
                value={adminNotes}
                onChange={(e) => setAdminNotes(e.target.value)}
                placeholder="Interne Notizen zur Genehmigung..."
                rows={3}
              />
            </div>
          </div>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={actionLoading}>Abbrechen</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleApprove}
              disabled={actionLoading}
              className="bg-green-600 hover:bg-green-700"
            >
              {actionLoading ? 'Genehmige...' : 'Genehmigen'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Reject Dialog */}
      <AlertDialog open={showRejectDialog} onOpenChange={setShowRejectDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Bewertung ablehnen?</AlertDialogTitle>
            <AlertDialogDescription>
              Diese Bewertung wird nicht veröffentlicht und bleibt ausgeblendet.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium">Grund für Ablehnung (optional)</label>
              <Textarea
                value={adminNotes}
                onChange={(e) => setAdminNotes(e.target.value)}
                placeholder="Z.B. Unzureichender Nachweis, unangemessene Sprache..."
                rows={3}
              />
            </div>
          </div>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={actionLoading}>Abbrechen</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleReject}
              disabled={actionLoading}
              className="bg-red-600 hover:bg-red-700"
            >
              {actionLoading ? 'Lehne ab...' : 'Ablehnen'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Proof Viewer Dialog */}
      <AlertDialog open={showProofDialog} onOpenChange={setShowProofDialog}>
        <AlertDialogContent className="max-w-3xl">
          <AlertDialogHeader>
            <AlertDialogTitle>Nachweis-Dokumente</AlertDialogTitle>
            <AlertDialogDescription>
              Prüfen Sie die hochgeladenen Nachweise für diese Low-Star-Bewertung
            </AlertDialogDescription>
          </AlertDialogHeader>
          {selectedReview && (
            <div className="space-y-4">
              {/* Photos */}
              {selectedReview.proof_photos && selectedReview.proof_photos.length > 0 && (
                <div>
                  <h4 className="font-medium mb-2">Produktfotos ({selectedReview.proof_photos.length})</h4>
                  <div className="grid grid-cols-3 gap-2">
                    {selectedReview.proof_photos.map((photo, index) => (
                      <img
                        key={index}
                        src={photo}
                        alt={`Proof ${index + 1}`}
                        className="w-full h-32 object-cover rounded border"
                      />
                    ))}
                  </div>
                </div>
              )}
              
              {/* Order Number */}
              {selectedReview.proof_order_number && (
                <div>
                  <h4 className="font-medium mb-2">Bestellnummer</h4>
                  <p className="p-2 bg-gray-100 rounded font-mono">{selectedReview.proof_order_number}</p>
                </div>
              )}
              
              {/* Chat History */}
              {selectedReview.proof_chat_history && (
                <div>
                  <h4 className="font-medium mb-2">Chat-Verlauf</h4>
                  <p className="text-sm text-gray-600">Datei vorhanden (Base64 encoded)</p>
                </div>
              )}
            </div>
          )}
          <AlertDialogFooter>
            <AlertDialogCancel>Schließen</AlertDialogCancel>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default AdminReviews;
