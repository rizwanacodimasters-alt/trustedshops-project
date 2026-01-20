import React, { useState, useEffect } from 'react';
import { adminAPI } from '../../services/api';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { useToast } from '../../hooks/use-toast';
import { Search, UserX, UserCheck, Trash2, Key, Shield, AlertTriangle } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../ui/dialog';
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
import { Label } from '../ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select';

const AdminUsers = () => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const { toast } = useToast();
  const [selectedUser, setSelectedUser] = useState(null);
  const [showUserDetail, setShowUserDetail] = useState(false);
  const [userToSuspend, setUserToSuspend] = useState(null);
  const [userToDelete, setUserToDelete] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    fetchUsers();
  }, [page, roleFilter]);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const params = { page, limit: 20 };
      if (search) params.search = search;
      if (roleFilter) params.role = roleFilter;

      const response = await adminAPI.getAllUsers(params);
      setUsers(response.data.data);
      setTotalPages(response.data.pages);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to load users',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    setPage(1);
    fetchUsers();
  };

  const handleSuspendUser = async (userId) => {
    setActionLoading(true);
    try {
      await adminAPI.suspendUser(userId, 'Suspended by admin');
      toast({
        title: 'Success',
        description: 'User suspended successfully',
      });
      setUserToSuspend(null);
      await fetchUsers();
    } catch (error) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to suspend user',
        variant: 'destructive',
      });
    } finally {
      setActionLoading(false);
    }
  };

  const handleActivateUser = async (userId) => {
    setActionLoading(true);
    try {
      await adminAPI.activateUser(userId);
      toast({
        title: 'Success',
        description: 'User activated successfully',
      });
      await fetchUsers();
    } catch (error) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to activate user',
        variant: 'destructive',
      });
    } finally {
      setActionLoading(false);
    }
  };

  const handleDeleteUser = async (userId) => {
    setActionLoading(true);
    try {
      await adminAPI.deleteUser(userId);
      toast({
        title: 'Success',
        description: 'User deleted permanently',
      });
      setUserToDelete(null);
      await fetchUsers();
    } catch (error) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to delete user',
        variant: 'destructive',
      });
    } finally {
      setActionLoading(false);
    }
  };

  const handleChangeRole = async (userId, newRole) => {
    setActionLoading(true);
    try {
      await adminAPI.changeRole(userId, newRole);
      toast({
        title: 'Success',
        description: `User role changed to ${newRole}`,
      });
      await fetchUsers();
    } catch (error) {
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to change user role',
        variant: 'destructive',
      });
    } finally {
      setActionLoading(false);
    }
  };

  const viewUserDetail = async (userId) => {
    setActionLoading(true);
    try {
      const response = await adminAPI.getUserDetail(userId);
      setSelectedUser(response.data);
      setShowUserDetail(true);
    } catch (error) {
      console.error('Error loading user details:', error);
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to load user details',
        variant: 'destructive',
      });
    } finally {
      setActionLoading(false);
    }
  };

  if (loading && users.length === 0) {
    return (
      <Card>
        <CardContent className="p-12 text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-yellow-500"></div>
          <p className="mt-4 text-gray-600">Loading users...</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>User Management</CardTitle>
        </CardHeader>
        <CardContent>
          {/* Search and Filters */}
          <div className="flex gap-4 mb-6">
            <div className="flex-1 flex gap-2">
              <Input
                placeholder="Search by name or email..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
              <Button onClick={handleSearch}>
                <Search className="w-4 h-4 mr-2" />
                Search
              </Button>
            </div>
            <Select value={roleFilter} onValueChange={setRoleFilter}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Filter by role" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Roles</SelectItem>
                <SelectItem value="shopper">Shoppers</SelectItem>
                <SelectItem value="shop_owner">Shop Owners</SelectItem>
                <SelectItem value="admin">Admins</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Users Table */}
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-3">User</th>
                  <th className="text-left p-3">Role</th>
                  <th className="text-left p-3">Status</th>
                  <th className="text-left p-3">Stats</th>
                  <th className="text-right p-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => (
                  <tr key={user.id} className="border-b hover:bg-gray-50">
                    <td className="p-3">
                      <div>
                        <p className="font-medium text-gray-900">{user.full_name}</p>
                        <p className="text-sm text-gray-500">{user.email}</p>
                      </div>
                    </td>
                    <td className="p-3">
                      <Badge
                        className={`${
                          user.role === 'admin'
                            ? 'bg-red-100 text-red-800'
                            : user.role === 'shop_owner'
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-green-100 text-green-800'
                        }`}
                      >
                        {user.role}
                      </Badge>
                    </td>
                    <td className="p-3">
                      <Badge className={user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}>
                        {user.is_active ? 'Active' : 'Suspended'}
                      </Badge>
                    </td>
                    <td className="p-3">
                      <div className="text-sm">
                        <p>Reviews: {user.total_reviews || 0}</p>
                        <p>Orders: {user.total_orders || 0}</p>
                        {user.role === 'shop_owner' && <p>Shops: {user.total_shops || 0}</p>}
                      </div>
                    </td>
                    <td className="p-3">
                      <div className="flex justify-end gap-2">
                        <Button 
                          size="sm" 
                          variant="outline" 
                          onClick={() => viewUserDetail(user.id)}
                          disabled={actionLoading}
                        >
                          View
                        </Button>
                        {user.is_active ? (
                          <Button 
                            size="sm" 
                            variant="outline" 
                            onClick={() => setUserToSuspend(user)}
                            disabled={actionLoading}
                          >
                            <UserX className="w-4 h-4" />
                          </Button>
                        ) : (
                          <Button 
                            size="sm" 
                            variant="outline" 
                            onClick={() => handleActivateUser(user.id)}
                            disabled={actionLoading}
                          >
                            <UserCheck className="w-4 h-4" />
                          </Button>
                        )}
                        <Button 
                          size="sm" 
                          variant="destructive" 
                          onClick={() => setUserToDelete(user)}
                          disabled={actionLoading}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="flex justify-between items-center mt-6">
            <p className="text-sm text-gray-600">
              Page {page} of {totalPages}
            </p>
            <div className="flex gap-2">
              <Button variant="outline" disabled={page === 1} onClick={() => setPage(page - 1)}>
                Previous
              </Button>
              <Button variant="outline" disabled={page === totalPages} onClick={() => setPage(page + 1)}>
                Next
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* User Detail Dialog */}
      <Dialog open={showUserDetail} onOpenChange={setShowUserDetail}>
        <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>User Details</DialogTitle>
          </DialogHeader>
          {selectedUser && (
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold mb-2">Basic Information</h3>
                <div className="space-y-2 text-sm">
                  <p><strong>Name:</strong> {selectedUser.full_name}</p>
                  <p><strong>Email:</strong> {selectedUser.email}</p>
                  <p><strong>Role:</strong> {selectedUser.role}</p>
                  <p><strong>Status:</strong> {selectedUser.is_active ? 'Active' : 'Suspended'}</p>
                  <p><strong>2FA:</strong> {selectedUser.two_factor_enabled ? 'Enabled' : 'Disabled'}</p>
                </div>
              </div>

              {selectedUser.login_history && selectedUser.login_history.length > 0 && (
                <div>
                  <h3 className="font-semibold mb-2">Recent Login History</h3>
                  <div className="space-y-2">
                    {selectedUser.login_history.slice(0, 5).map((login, index) => (
                      <div key={login.id || index} className="text-sm bg-gray-50 p-2 rounded">
                        <p><strong>Time:</strong> {new Date(login.timestamp).toLocaleString()}</p>
                        <p><strong>IP:</strong> {login.ip_address}</p>
                        <p><strong>Status:</strong> {login.success ? 'Success' : 'Failed'}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {selectedUser.active_sessions && selectedUser.active_sessions.length > 0 && (
                <div>
                  <h3 className="font-semibold mb-2">Active Sessions ({selectedUser.active_sessions.length})</h3>
                  <div className="space-y-2">
                    {selectedUser.active_sessions.map((session, index) => (
                      <div key={session.id || index} className="flex justify-between items-center bg-gray-50 p-2 rounded text-sm">
                        <div>
                          <p><strong>IP:</strong> {session.ip_address}</p>
                          <p><strong>Created:</strong> {new Date(session.created_at).toLocaleString()}</p>
                        </div>
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={async () => {
                            await adminAPI.terminateSession(selectedUser.id, session.id);
                            toast({ title: 'Session terminated' });
                            viewUserDetail(selectedUser.id);
                          }}
                        >
                          Terminate
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Suspend User Confirmation Dialog */}
      <AlertDialog open={!!userToSuspend} onOpenChange={() => setUserToSuspend(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-orange-600" />
              Suspend User
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to suspend <strong>{userToSuspend?.full_name}</strong> ({userToSuspend?.email})?
              <br /><br />
              The user will be logged out and unable to access their account until reactivated.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={actionLoading}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => userToSuspend && handleSuspendUser(userToSuspend.id)}
              className="bg-orange-600 hover:bg-orange-700"
              disabled={actionLoading}
            >
              {actionLoading ? 'Suspending...' : 'Suspend User'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Delete User Confirmation Dialog */}
      <AlertDialog open={!!userToDelete} onOpenChange={() => setUserToDelete(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2 text-red-600">
              <Trash2 className="w-5 h-5" />
              Delete User Permanently
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to <strong className="text-red-600">permanently delete</strong> {userToDelete?.full_name} ({userToDelete?.email})?
              <br /><br />
              <span className="text-red-600 font-semibold">⚠️ This action cannot be undone!</span>
              <br /><br />
              All user data, including reviews, orders, and activity history will be permanently removed.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={actionLoading}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => userToDelete && handleDeleteUser(userToDelete.id)}
              className="bg-red-600 hover:bg-red-700"
              disabled={actionLoading}
            >
              {actionLoading ? 'Deleting...' : 'Delete Permanently'}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default AdminUsers;