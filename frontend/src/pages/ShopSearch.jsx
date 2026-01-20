import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { shopAPI, searchAPI } from '../services/api';
import { Card, CardContent } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { useToast } from '../hooks/use-toast';
import { Search, Star, ShieldCheck, Filter, ChevronLeft, ChevronRight, Loader2 } from 'lucide-react';

const ShopSearch = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const { toast } = useToast();
  const [shops, setShops] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || '');
  const [category, setCategory] = useState(searchParams.get('category') || '');
  const [categories, setCategories] = useState([]);
  const [pagination, setPagination] = useState({ page: 1, pages: 1, total: 0 });
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    fetchShops();
    fetchCategories();
  }, [searchParams]);

  const fetchCategories = async () => {
    try {
      const response = await searchAPI.getCategories();
      // Extract category names from objects
      const cats = (response.data.categories || []).map(cat => cat.name || cat);
      setCategories(cats);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const fetchShops = async () => {
    try {
      setLoading(true);
      const params = {
        page: parseInt(searchParams.get('page')) || 1,
        limit: 12,
        q: searchParams.get('q') || undefined,
        category: searchParams.get('category') || undefined,
      };

      const response = await searchAPI.searchShops(params);
      setShops(response.data.data || []);
      setPagination({
        page: response.data.page,
        pages: response.data.pages,
        total: response.data.total
      });
    } catch (error) {
      console.error('Error fetching shops:', error);
      toast({
        title: 'Error',
        description: 'Failed to load shops',
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    const newParams = new URLSearchParams();
    if (searchQuery) newParams.set('q', searchQuery);
    if (category) newParams.set('category', category);
    setSearchParams(newParams);
  };

  const handleCategoryChange = (value) => {
    setCategory(value === 'all' ? '' : value);
    const newParams = new URLSearchParams(searchParams);
    if (value && value !== 'all') {
      newParams.set('category', value);
    } else {
      newParams.delete('category');
    }
    newParams.delete('page');
    setSearchParams(newParams);
  };

  const handlePageChange = (newPage) => {
    const newParams = new URLSearchParams(searchParams);
    newParams.set('page', newPage.toString());
    setSearchParams(newParams);
    window.scrollTo(0, 0);
  };

  const clearFilters = () => {
    setSearchQuery('');
    setCategory('');
    setSearchParams(new URLSearchParams());
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section with Search */}
      <div className="bg-gradient-to-r from-yellow-400 to-amber-500 py-16">
        <div className="container mx-auto px-4">
          <h1 className="text-4xl font-bold text-center text-white mb-4">
            Finden Sie vertrauenswürdige Shops
          </h1>
          <p className="text-center text-white mb-8">
            Durchsuchen Sie {pagination.total} geprüfte Online-Shops
          </p>

          {/* Search Bar */}
          <form onSubmit={handleSearch} className="max-w-3xl mx-auto">
            <div className="flex gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
                <Input
                  type="text"
                  placeholder="Shop-Name, Kategorie oder Stichwort..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-12 h-14 text-lg bg-white"
                />
              </div>
              <Button
                type="submit"
                className="h-14 px-8 bg-white text-black hover:bg-gray-100 font-semibold"
              >
                Suchen
              </Button>
            </div>
          </form>
        </div>
      </div>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Filters Sidebar */}
          <div className="lg:w-64">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-semibold text-lg flex items-center">
                    <Filter className="w-5 h-5 mr-2" />
                    Filter
                  </h3>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={clearFilters}
                    className="text-amber-600 hover:text-amber-700"
                  >
                    Zurücksetzen
                  </Button>
                </div>

                <div className="space-y-4">
                  {/* Category Filter */}
                  <div>
                    <label className="text-sm font-medium mb-2 block">Kategorie</label>
                    <Select value={category || 'all'} onValueChange={handleCategoryChange}>
                      <SelectTrigger>
                        <SelectValue placeholder="Alle Kategorien" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">Alle Kategorien</SelectItem>
                        {categories.map((cat) => (
                          <SelectItem key={cat} value={cat}>
                            {cat}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Active Filters */}
                  {(searchQuery || category) && (
                    <div className="pt-4 border-t">
                      <p className="text-sm font-medium mb-2">Aktive Filter:</p>
                      <div className="space-y-2">
                        {searchQuery && (
                          <Badge className="bg-amber-100 text-amber-800">
                            Suche: {searchQuery}
                          </Badge>
                        )}
                        {category && (
                          <Badge className="bg-blue-100 text-blue-800">
                            {category}
                          </Badge>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Results */}
          <div className="flex-1">
            {/* Results Header */}
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900">
                {searchQuery ? `Suchergebnisse für "${searchQuery}"` : 'Alle Shops'}
              </h2>
              <p className="text-gray-600">
                {pagination.total} {pagination.total === 1 ? 'Shop' : 'Shops'} gefunden
              </p>
            </div>

            {/* Loading State */}
            {loading && (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-amber-500" />
                <p className="ml-2 text-gray-600">Shops werden geladen...</p>
              </div>
            )}

            {/* No Results */}
            {!loading && shops.length === 0 && (
              <Card>
                <CardContent className="p-12 text-center">
                  <Search className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-gray-700 mb-2">
                    Keine Shops gefunden
                  </h3>
                  <p className="text-gray-600 mb-4">
                    Versuchen Sie es mit anderen Suchbegriffen oder passen Sie Ihre Filter an.
                  </p>
                  <Button onClick={clearFilters}>Filter zurücksetzen</Button>
                </CardContent>
              </Card>
            )}

            {/* Shop Grid */}
            {!loading && shops.length > 0 && (
              <>
                <div className="grid md:grid-cols-2 xl:grid-cols-3 gap-6 mb-8">
                  {shops.map((shop) => (
                    <Link key={shop.id} to={`/shop/${shop.id}`}>
                      <Card className="h-full hover:shadow-xl transition-shadow duration-300 cursor-pointer">
                        <CardContent className="p-6">
                          <div className="flex items-start justify-between mb-4">
                            <div className="flex-1">
                              <h3 className="font-bold text-lg text-gray-900 mb-1 line-clamp-2">
                                {shop.name}
                              </h3>
                              <p className="text-sm text-gray-600 mb-2">{shop.category}</p>
                            </div>
                            {shop.is_verified && (
                              <ShieldCheck className="w-6 h-6 text-green-500 flex-shrink-0" />
                            )}
                          </div>

                          {/* Rating */}
                          <div className="flex items-center mb-3">
                            <div className="flex items-center">
                              {[...Array(5)].map((_, i) => (
                                <Star
                                  key={i}
                                  className={`w-4 h-4 ${
                                    i < Math.round(shop.rating)
                                      ? 'fill-yellow-400 text-yellow-400'
                                      : 'text-gray-300'
                                  }`}
                                />
                              ))}
                            </div>
                            <span className="ml-2 text-sm font-semibold text-gray-900">
                              {shop.rating.toFixed(1)}
                            </span>
                            <span className="ml-1 text-sm text-gray-500">
                              ({shop.review_count} {shop.review_count === 1 ? 'Bewertung' : 'Bewertungen'})
                            </span>
                          </div>

                          {/* Description */}
                          {shop.description && (
                            <p className="text-sm text-gray-600 line-clamp-2 mb-3">
                              {shop.description}
                            </p>
                          )}

                          {/* Website */}
                          <p className="text-sm text-amber-600 hover:text-amber-700 font-medium truncate">
                            {shop.website}
                          </p>

                          {/* Badges */}
                          <div className="flex flex-wrap gap-2 mt-4">
                            {shop.is_verified && (
                              <Badge className="bg-green-100 text-green-800">
                                Verifiziert
                              </Badge>
                            )}
                            <Badge className="bg-blue-100 text-blue-800">
                              {shop.category}
                            </Badge>
                          </div>
                        </CardContent>
                      </Card>
                    </Link>
                  ))}
                </div>

                {/* Pagination */}
                {pagination.pages > 1 && (
                  <div className="flex items-center justify-center gap-2">
                    <Button
                      variant="outline"
                      onClick={() => handlePageChange(pagination.page - 1)}
                      disabled={pagination.page === 1}
                    >
                      <ChevronLeft className="w-4 h-4" />
                      Zurück
                    </Button>

                    <div className="flex gap-2">
                      {[...Array(pagination.pages)].map((_, index) => {
                        const page = index + 1;
                        // Show first, last, current, and adjacent pages
                        if (
                          page === 1 ||
                          page === pagination.pages ||
                          (page >= pagination.page - 1 && page <= pagination.page + 1)
                        ) {
                          return (
                            <Button
                              key={page}
                              variant={page === pagination.page ? 'default' : 'outline'}
                              onClick={() => handlePageChange(page)}
                              className={page === pagination.page ? 'bg-amber-500 hover:bg-amber-600' : ''}
                            >
                              {page}
                            </Button>
                          );
                        } else if (
                          page === pagination.page - 2 ||
                          page === pagination.page + 2
                        ) {
                          return <span key={page} className="px-2">...</span>;
                        }
                        return null;
                      })}
                    </div>

                    <Button
                      variant="outline"
                      onClick={() => handlePageChange(pagination.page + 1)}
                      disabled={pagination.page === pagination.pages}
                    >
                      Weiter
                      <ChevronRight className="w-4 h-4" />
                    </Button>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ShopSearch;