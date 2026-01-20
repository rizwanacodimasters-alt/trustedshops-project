import React, { useState, useEffect } from 'react';
import { adminAPI } from '../../services/api';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { useToast } from '../../hooks/use-toast';
import { SHOP_CATEGORIES } from '../../utils/categories';
import CreateShopAdmin from './CreateShopAdmin';
import { Search, ShieldCheck, Ban, Trash2, Play, Plus } from 'lucide-react';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select';

const AdminShops = () => {
  const [shops, setShops] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [isCreateShopOpen, setIsCreateShopOpen] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    fetchShops();
  }, [page, statusFilter, categoryFilter]);

  const fetchShops = async () => {
    setLoading(true);
    try {
      const params = { page, limit: 20 };
      if (search) params.search = search;
      if (statusFilter && statusFilter !== 'all') params.status_filter = statusFilter;
      if (categoryFilter && categoryFilter !== 'all') params.category = categoryFilter;

      console.log('Fetching shops with params:', params);
      const response = await adminAPI.getAllShops(params);
      console.log('Shops response:', response.data);
      
      const shopsData = response.data.data || [];
      setShops(shopsData);
      setTotalPages(response.data.pages || 1);
      
      if (shopsData.length === 0 && page === 1) {
        toast({
          title: 'No shops found',
          description: 'There are currently no shops in the database.',
        });
      }
    } catch (error) {
      console.error('Error fetching shops:', error);
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to load shops',
        variant: 'destructive',
      });
      setShops([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    setPage(1);
    fetchShops();
  };

  const handleVerifyShop = async (shopId) => {
    try {
      await adminAPI.verifyShop(shopId, 'Verified by admin');
      toast({
        title: 'Success',
        description: 'Shop verified successfully',
      });
      fetchShops();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to verify shop',
        variant: 'destructive',
      });
    }
  };

  const handleSuspendShop = async (shopId) => {
    const reason = window.prompt('Enter suspension reason:');
    if (!reason) return;

    try {
      await adminAPI.suspendShop(shopId, reason);
      toast({
        title: 'Success',
        description: 'Shop suspended successfully',
      });
      fetchShops();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to suspend shop',
        variant: 'destructive',
      });
    }
  };

  const handleActivateShop = async (shopId) => {
    try {
      await adminAPI.activateShop(shopId);
      toast({
        title: 'Success',
        description: 'Shop activated successfully',
      });
      fetchShops();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to activate shop',
        variant: 'destructive',
      });
    }
  };

  const handleDeleteShop = async (shopId) => {
    if (!window.confirm('Are you sure you want to permanently delete this shop?')) return;

    try {
      await adminAPI.deleteShop(shopId);
      toast({
        title: 'Success',
        description: 'Shop deleted successfully',
      });
      fetchShops();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to delete shop',
        variant: 'destructive',
      });
    }
  };

  const handleBanShop = async (shopId) => {
    const reason = window.prompt('Enter ban reason:');
    if (!reason) return;

    if (!window.confirm('Are you sure you want to ban this shop permanently?')) return;

    try {
      await adminAPI.banShop(shopId, reason);
      toast({
        title: 'Success',
        description: 'Shop banned successfully',
      });
      fetchShops();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to ban shop',
        variant: 'destructive',
      });
    }
  };

  if (loading && shops.length === 0) {
    return (
      <Card>
        <CardContent className="p-12 text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-yellow-500"></div>
          <p className="mt-4 text-gray-600">Loading shops...</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Shop Management</CardTitle>
          <Button
            onClick={() => setIsCreateShopOpen(true)}
            className="bg-gradient-to-r from-green-400 to-green-500 hover:from-green-500 hover:to-green-600 text-white"
          >
            <Plus className="w-4 h-4 mr-2" />
            Create Shop
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {/* Search and Filters */}
        <div className="flex flex-col gap-4 mb-6">
          <div className="flex gap-2">
            <Input
              placeholder="Search shops..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              className="flex-1"
            />
            <Button onClick={handleSearch}>
              <Search className="w-4 h-4 mr-2" />
              Search
            </Button>
          </div>
          <div className="flex gap-4">
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="suspended">Suspended</SelectItem>
                <SelectItem value="banned">Banned</SelectItem>
              </SelectContent>
            </Select>
            <Select value={categoryFilter} onValueChange={setCategoryFilter}>
              <SelectTrigger className="w-64">
                <SelectValue placeholder="Filter by category" />
              </SelectTrigger>
              <SelectContent className="max-h-[300px]">
                <SelectItem value="all">All Categories</SelectItem>
                {SHOP_CATEGORIES.map((cat) => (
                  <SelectItem key={cat} value={cat}>
                    {cat}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Shops Table */}
        {shops.length === 0 && !loading ? (
          <div className="text-center py-12 bg-gray-50 rounded-lg">
            <div className="text-gray-400 mb-4">
              <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No shops found</h3>
            <p className="text-gray-600 mb-4">
              {search || statusFilter || categoryFilter
                ? 'Try adjusting your search or filters'
                : 'Get started by creating your first shop'}
            </p>
            {!search && !statusFilter && !categoryFilter && (
              <Button
                onClick={() => setIsCreateShopOpen(true)}
                className="bg-gradient-to-r from-green-400 to-green-500"
              >
                <Plus className="w-4 h-4 mr-2" />
                Create First Shop
              </Button>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-3">Shop</th>
                  <th className="text-left p-3">Owner</th>
                  <th className="text-left p-3">Category</th>
                  <th className="text-left p-3">
                    <div className="flex items-center gap-1">
                      <span className="text-yellow-500">★</span>
                      <span>Rating & Reviews</span>
                    </div>
                  </th>
                  <th className="text-left p-3">Status</th>
                  <th className="text-right p-3">Actions</th>
                </tr>
              </thead>
              <tbody>
                {shops.map((shop) => (
                <tr key={shop.id} className="border-b hover:bg-gray-50">
                  <td className="p-3">
                    <div>
                      <p className="font-medium text-gray-900">{shop.name}</p>
                      <p className="text-sm text-gray-500">{shop.website}</p>
                    </div>
                  </td>
                  <td className="p-3">
                    <div className="text-sm">
                      <p>{shop.owner_name || 'N/A'}</p>
                      <p className="text-gray-500">{shop.owner_email || ''}</p>
                    </div>
                  </td>
                  <td className="p-3">
                    <Badge className="bg-blue-100 text-blue-800">{shop.category}</Badge>
                  </td>
                  <td className="p-3">
                    <div className="flex items-center gap-2">
                      <div className="flex flex-col">
                        <div className="flex items-center gap-1">
                          <span className="text-yellow-500 font-bold">★</span>
                          <span className="font-semibold text-gray-900">
                            {(shop.rating || 0).toFixed(1)}
                          </span>
                        </div>
                        <div className="flex items-center gap-1 text-xs text-gray-500">
                          <span>{shop.review_count || 0}</span>
                          <span>{shop.review_count === 1 ? 'review' : 'reviews'}</span>
                        </div>
                      </div>
                      {shop.review_count > 0 && (
                        <div className="flex flex-col items-center">
                          <div className="w-16 bg-gray-200 rounded-full h-1.5">
                            <div 
                              className={`h-1.5 rounded-full ${
                                shop.rating >= 4.5 ? 'bg-green-500' :
                                shop.rating >= 3.5 ? 'bg-yellow-500' :
                                shop.rating >= 2.5 ? 'bg-orange-500' :
                                'bg-red-500'
                              }`}
                              style={{ width: `${(shop.rating / 5) * 100}%` }}
                            ></div>
                          </div>
                        </div>
                      )}
                    </div>
                  </td>
                  <td className="p-3">
                    <div className="space-y-1">
                      <Badge className={shop.is_verified ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                        {shop.is_verified ? 'Verified' : 'Not Verified'}
                      </Badge>
                      {shop.status && (
                        <Badge
                          className={`${
                            shop.status === 'active'
                              ? 'bg-green-100 text-green-800'
                              : shop.status === 'suspended'
                              ? 'bg-yellow-100 text-yellow-800'
                              : 'bg-red-100 text-red-800'
                          }`}
                        >
                          {shop.status}
                        </Badge>
                      )}
                    </div>
                  </td>
                  <td className="p-3">
                    <div className="flex justify-end gap-2">
                      {!shop.is_verified && (
                        <Button size="sm" variant="outline" onClick={() => handleVerifyShop(shop.id)} title="Verify">
                          <ShieldCheck className="w-4 h-4" />
                        </Button>
                      )}
                      {shop.status !== 'suspended' ? (
                        <Button size="sm" variant="outline" onClick={() => handleSuspendShop(shop.id)} title="Suspend">
                          Suspend
                        </Button>
                      ) : (
                        <Button size="sm" variant="outline" onClick={() => handleActivateShop(shop.id)} title="Activate">
                          <Play className="w-4 h-4" />
                        </Button>
                      )}
                      <Button size="sm" variant="outline" onClick={() => handleBanShop(shop.id)} title="Ban">
                        <Ban className="w-4 h-4" />
                      </Button>
                      <Button size="sm" variant="destructive" onClick={() => handleDeleteShop(shop.id)} title="Delete">
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </td>
                </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Review Statistics Summary */}
        {shops.length > 0 && (
          <div className="mt-6 p-4 bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg border border-yellow-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-6">
                <div className="flex items-center gap-2">
                  <span className="text-yellow-600 text-2xl">★</span>
                  <div>
                    <p className="text-sm text-gray-600">Average Rating</p>
                    <p className="text-xl font-bold text-gray-900">
                      {(shops.reduce((sum, shop) => sum + (shop.rating || 0), 0) / shops.length).toFixed(2)}
                    </p>
                  </div>
                </div>
                <div className="h-12 w-px bg-yellow-300"></div>
                <div>
                  <p className="text-sm text-gray-600">Total Reviews</p>
                  <p className="text-xl font-bold text-gray-900">
                    {shops.reduce((sum, shop) => sum + (shop.review_count || 0), 0)}
                  </p>
                </div>
                <div className="h-12 w-px bg-yellow-300"></div>
                <div>
                  <p className="text-sm text-gray-600">Shops with Reviews</p>
                  <p className="text-xl font-bold text-gray-900">
                    {shops.filter(shop => (shop.review_count || 0) > 0).length} / {shops.length}
                  </p>
                </div>
                <div className="h-12 w-px bg-yellow-300"></div>
                <div>
                  <p className="text-sm text-gray-600">Highest Rated</p>
                  <p className="text-xl font-bold text-gray-900">
                    {Math.max(...shops.map(shop => shop.rating || 0)).toFixed(1)} ★
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

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
      
      {/* Create Shop Modal */}
      <CreateShopAdmin
        isOpen={isCreateShopOpen}
        onClose={() => setIsCreateShopOpen(false)}
        onSuccess={fetchShops}
      />
    </Card>
  );
};

export default AdminShops;