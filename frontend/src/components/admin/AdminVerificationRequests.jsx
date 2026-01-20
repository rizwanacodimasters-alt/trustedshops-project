import React, { useState, useEffect } from 'react';
import { verificationAPI } from '../../services/api';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { useToast } from '../../hooks/use-toast';
import { ShieldCheck, XCircle, Clock, CheckCircle, ExternalLink } from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select';
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

const AdminVerificationRequests = () => {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('pending');
  const [requestToApprove, setRequestToApprove] = useState(null);
  const [requestToReject, setRequestToReject] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    fetchRequests();
  }, [statusFilter]);

  const fetchRequests = async () => {
    setLoading(true);
    try {
      const response = await verificationAPI.getAllVerificationRequests(statusFilter);
      setRequests(response.data.data || []);
    } catch (error) {
      console.error('Error fetching verification requests:', error);
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to load verification requests',
        variant: 'destructive',
      });
      setRequests([]);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async (shopId) => {
    setActionLoading(true);
    try {
      await verificationAPI.approveVerification(shopId);
      toast({
        title: 'Success',
        description: 'Shop verification approved successfully',
      });
      setRequestToApprove(null);
      await fetchRequests();
    } catch (error) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to approve verification',
        variant: 'destructive',
      });
    } finally {
      setActionLoading(false);
    }
  };

  const handleReject = async (shopId) => {
    setActionLoading(true);
    try {
      await verificationAPI.rejectVerification(shopId);
      toast({
        title: 'Success',
        description: 'Shop verification rejected',
      });
      setRequestToReject(null);
      await fetchRequests();
    } catch (error) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to reject verification',
        variant: 'destructive',
      });
    } finally {
      setActionLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'pending':
        return <Badge className="bg-yellow-100 text-yellow-800 border-yellow-200"><Clock className="w-3 h-3 mr-1" />Pending</Badge>;
      case 'verified':
        return <Badge className="bg-green-100 text-green-800 border-green-200"><CheckCircle className="w-3 h-3 mr-1" />Approved</Badge>;
      case 'rejected':
        return <Badge className="bg-red-100 text-red-800 border-red-200"><XCircle className="w-3 h-3 mr-1" />Rejected</Badge>;
      default:
        return <Badge className="bg-gray-100 text-gray-800">{status}</Badge>;
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('de-DE', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading && requests.length === 0) {
    return (
      <Card>
        <CardContent className="p-12 text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-yellow-500"></div>
          <p className="mt-4 text-gray-600">Loading verification requests...</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <ShieldCheck className="w-6 h-6" />
              Verification Requests
            </CardTitle>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Requests</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="verified">Approved</SelectItem>
                <SelectItem value="rejected">Rejected</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardHeader>
        <CardContent>
          {requests.length === 0 && !loading ? (
            <div className="text-center py-12 bg-gray-50 rounded-lg">
              <div className="text-gray-400 mb-4">
                <ShieldCheck className="mx-auto h-12 w-12" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No verification requests</h3>
              <p className="text-gray-600">
                {statusFilter === 'pending'
                  ? 'No pending verification requests at the moment'
                  : `No ${statusFilter} verification requests found`}
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-3">Shop</th>
                    <th className="text-left p-3">Owner</th>
                    <th className="text-left p-3">Category</th>
                    <th className="text-left p-3">Requested</th>
                    <th className="text-left p-3">Status</th>
                    <th className="text-right p-3">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {requests.map((request) => (
                    <tr key={request.id} className="border-b hover:bg-gray-50">
                      <td className="p-3">
                        <div>
                          <p className="font-medium text-gray-900">{request.shop_name}</p>
                          {request.shop_website && (
                            <a
                              href={request.shop_website}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1"
                            >
                              {request.shop_website}
                              <ExternalLink className="w-3 h-3" />
                            </a>
                          )}
                        </div>
                      </td>
                      <td className="p-3">
                        <div className="text-sm">
                          <p className="font-medium">{request.owner_name || 'Unknown'}</p>
                          <p className="text-gray-500">{request.owner_email || ''}</p>
                        </div>
                      </td>
                      <td className="p-3">
                        <Badge className="bg-blue-100 text-blue-800">
                          {request.shop_category || 'N/A'}
                        </Badge>
                      </td>
                      <td className="p-3">
                        <div className="text-sm text-gray-600">
                          {formatDate(request.created_at)}
                        </div>
                      </td>
                      <td className="p-3">
                        {getStatusBadge(request.status)}
                      </td>
                      <td className="p-3">
                        <div className="flex justify-end gap-2">
                          {request.status === 'pending' && (
                            <>
                              <Button
                                size="sm"
                                variant="outline"
                                className="bg-green-50 hover:bg-green-100 text-green-700 border-green-200"
                                onClick={() => setRequestToApprove(request)}
                                disabled={actionLoading}
                              >
                                <CheckCircle className="w-4 h-4 mr-1" />
                                Approve
                              </Button>
                              <Button
                                size="sm"
                                variant="outline"
                                className="bg-red-50 hover:bg-red-100 text-red-700 border-red-200"
                                onClick={() => setRequestToReject(request)}
                                disabled={actionLoading}
                              >
                                <XCircle className="w-4 h-4 mr-1" />
                                Reject
                              </Button>
                            </>
                          )}
                          {request.status === 'verified' && (
                            <Badge className="bg-green-100 text-green-800">
                              ✓ Verified on {formatDate(request.verified_at)}
                            </Badge>
                          )}
                          {request.status === 'rejected' && (
                            <Badge className="bg-red-100 text-red-800">
                              ✗ Rejected on {formatDate(request.rejected_at)}
                            </Badge>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Summary */}
          {requests.length > 0 && (
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600">
                Total requests: <strong>{requests.length}</strong>
                {statusFilter === 'all' && (
                  <>
                    {' • '}
                    Pending: <strong className="text-yellow-700">
                      {requests.filter(r => r.status === 'pending').length}
                    </strong>
                    {' • '}
                    Approved: <strong className="text-green-700">
                      {requests.filter(r => r.status === 'verified').length}
                    </strong>
                    {' • '}
                    Rejected: <strong className="text-red-700">
                      {requests.filter(r => r.status === 'rejected').length}
                    </strong>
                  </>
                )}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Approve Dialog */}
      <AlertDialog open={!!requestToApprove} onOpenChange={() => setRequestToApprove(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2 text-green-600">
              <CheckCircle className="w-5 h-5" />
              Approve Verification Request
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to approve the verification request for{' '}
              <strong>{requestToApprove?.shop_name}</strong>?
              <br /><br />
              This will mark the shop as verified and it will display the verified badge to customers.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={actionLoading}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => requestToApprove && handleApprove(requestToApprove.shop_id)}
              className="bg-green-600 hover:bg-green-700"
              disabled={actionLoading}
            >
              {actionLoading ? 'Approving...' : 'Approve Verification'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Reject Dialog */}
      <AlertDialog open={!!requestToReject} onOpenChange={() => setRequestToReject(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2 text-red-600">
              <XCircle className="w-5 h-5" />
              Reject Verification Request
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to reject the verification request for{' '}
              <strong>{requestToReject?.shop_name}</strong>?
              <br /><br />
              The shop owner will need to submit a new request if they wish to get verified in the future.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={actionLoading}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => requestToReject && handleReject(requestToReject.shop_id)}
              className="bg-red-600 hover:bg-red-700"
              disabled={actionLoading}
            >
              {actionLoading ? 'Rejecting...' : 'Reject Request'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default AdminVerificationRequests;
