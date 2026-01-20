import React from 'react';
import { Star, ExternalLink } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';
import { translations } from '../utils/translations';
import { Card, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';

const ShopCard = ({ shop }) => {
  const { language } = useLanguage();
  const t = translations[language];

  return (
    <Card className="overflow-hidden hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 group">
      {/* Shop Image */}
      <div className="relative h-48 overflow-hidden">
        <img
          src={shop.image}
          alt={shop.name}
          className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent"></div>
        
        {/* Shop Logo */}
        <div className="absolute bottom-4 left-4">
          <div className="w-16 h-16 rounded-full bg-white p-2 shadow-lg">
            <img
              src={shop.logo}
              alt={`${shop.name} logo`}
              className="w-full h-full object-cover rounded-full"
            />
          </div>
        </div>
      </div>

      <CardContent className="p-6">
        {/* Shop Name */}
        <h3 className="text-xl font-bold mb-2 text-gray-900">{shop.name}</h3>
        
        {/* Category Badge */}
        <Badge className="mb-3 bg-yellow-100 text-yellow-800 hover:bg-yellow-200">
          {shop.category}
        </Badge>

        {/* Description */}
        <p className="text-gray-600 text-sm mb-4 line-clamp-2">
          {shop.description}
        </p>

        {/* Rating */}
        <div className="flex items-center space-x-3 mb-4">
          <div className="flex items-center space-x-1">
            <Star className="w-5 h-5 fill-yellow-400 text-yellow-400" />
            <span className="font-bold text-lg text-gray-900">{shop.rating || 0}</span>
          </div>
          <span className="text-gray-500 text-sm">
            ({(shop.review_count || shop.reviewCount || 0).toLocaleString()} {t.reviews})
          </span>
        </div>

        {/* Website Tag */}
        <div className="flex items-center justify-between">
          <span className="text-sm font-mono text-gray-500 bg-gray-100 px-3 py-1 rounded">
            #{shop.website?.split('.')[0] || 'shop'}
          </span>
          
          <Button
            size="sm"
            className="bg-gradient-to-r from-yellow-400 to-amber-500 hover:from-yellow-500 hover:to-amber-600 text-black"
          >
            <ExternalLink className="w-4 h-4 mr-2" />
            {t.visitShop}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default ShopCard;