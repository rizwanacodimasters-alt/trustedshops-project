// Mock data for TrustedShops clone

export const mockShops = [
  {
    id: '1',
    name: 'Bike-Mailorder',
    description: 'Your online shop for bicycles, e-bikes, parts and accessories. Top brands, fast shipping, top service.',
    logo: 'https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=200&h=200&fit=crop',
    image: 'https://images.unsplash.com/photo-1511994298241-608e28f14fde?w=800&h=600&fit=crop',
    rating: 4.81,
    reviewCount: 23614,
    website: 'bike-mailorder.com',
    category: 'Sports & Outdoors'
  },
  {
    id: '2',
    name: 'Lerros',
    description: 'Timeless men\'s fashion with quality and comfort – stylish companions for your everyday since 1979.',
    logo: 'https://images.unsplash.com/photo-1523381210434-271e8be1f52b?w=200&h=200&fit=crop',
    image: 'https://images.unsplash.com/photo-1490114538077-0a7f8cb49891?w=800&h=600&fit=crop',
    rating: 4.81,
    reviewCount: 13369,
    website: 'lerros.com',
    category: 'Fashion'
  },
  {
    id: '3',
    name: 'Yves Rocher',
    description: 'For over 60 years: skin care from plant power, responsible and effective.',
    logo: 'https://images.unsplash.com/photo-1556228852-80d7c6d04a70?w=200&h=200&fit=crop',
    image: 'https://images.unsplash.com/photo-1596755389378-c31d21fd1273?w=800&h=600&fit=crop',
    rating: 4.76,
    reviewCount: 123544,
    website: 'yves-rocher.de',
    category: 'Beauty & Care'
  },
  {
    id: '4',
    name: 'Fleurop',
    description: 'Order fresh flowers online – hand-tied by florists, personally delivered, worldwide delivery.',
    logo: 'https://images.unsplash.com/photo-1490750967868-88aa4486c946?w=200&h=200&fit=crop',
    image: 'https://images.unsplash.com/photo-1487070183336-b863922373d4?w=800&h=600&fit=crop',
    rating: 4.50,
    reviewCount: 300257,
    website: 'fleurop.de',
    category: 'Gifts & Flowers'
  },
  {
    id: '5',
    name: 'Vorwerk',
    description: 'Kobold & Thermomix: Innovations for a better home.',
    logo: 'https://images.unsplash.com/photo-1556911220-bff31c812dba?w=200&h=200&fit=crop',
    image: 'https://images.unsplash.com/photo-1556911220-e15b29be8c8f?w=800&h=600&fit=crop',
    rating: 4.59,
    reviewCount: 146518,
    website: 'vorwerk.com',
    category: 'Home & Kitchen'
  },
  {
    id: '6',
    name: 'CEWE',
    description: 'High-quality photo books, creative photo products and reliable online printing for unforgettable moments.',
    logo: 'https://images.unsplash.com/photo-1452860606245-08befc0ff44b?w=200&h=200&fit=crop',
    image: 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=800&h=600&fit=crop',
    rating: 4.73,
    reviewCount: 79334,
    website: 'cewe.de',
    category: 'Photo & Print'
  },
  {
    id: '7',
    name: 'FRED & FELIA',
    description: 'Dog and cat food – like homemade! With food-grade ingredients, made in Bavaria.',
    logo: 'https://images.unsplash.com/photo-1450778869180-41d0601e046e?w=200&h=200&fit=crop',
    image: 'https://images.unsplash.com/photo-1548199973-03cce0bbc87b?w=800&h=600&fit=crop',
    rating: 4.72,
    reviewCount: 17414,
    website: 'fredandfelia.com',
    category: 'Pets'
  },
  {
    id: '8',
    name: 'medimops',
    description: 'Over 4 million checked second-hand items up to 70% cheaper – shop sustainably at medimops!',
    logo: 'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=200&h=200&fit=crop',
    image: 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=800&h=600&fit=crop',
    rating: 4.62,
    reviewCount: 1105262,
    website: 'medimops.de',
    category: 'Books & Media'
  }
];

export const mockReviews = [
  {
    id: '1',
    userName: 'Wolfgang B.',
    userInitials: 'WB',
    date: '2025-09-09',
    rating: 5,
    comment: 'Fast delivery, good communication',
    shopName: 'Bike-Mailorder',
    shopWebsite: 'bike-mailorder.com'
  },
  {
    id: '2',
    userName: 'Adrian N.',
    userInitials: 'AN',
    date: '2025-08-04',
    rating: 5,
    comment: 'A great product. Very good ingredients, very tasty and top service 👍',
    shopName: 'FRED & FELIA',
    shopWebsite: 'fredandfelia.com'
  },
  {
    id: '3',
    userName: 'Evelyne B.',
    userInitials: 'EB',
    date: '2025-09-08',
    rating: 5,
    comment: 'Stools arrived quickly. The color is beautiful and the quality is right too. Value for money very good.',
    shopName: 'Vorwerk',
    shopWebsite: 'vorwerk.com'
  },
  {
    id: '4',
    userName: 'Tim D.',
    userInitials: 'TD',
    date: '2025-07-09',
    rating: 5,
    comment: 'Always had good experience. Fast and quality, thanks!',
    shopName: 'CEWE',
    shopWebsite: 'cewe.de'
  },
  {
    id: '5',
    userName: 'Nadine S.',
    userInitials: 'NS',
    date: '2025-09-05',
    rating: 5,
    comment: 'Very nice communication, fair price, very good quality.',
    shopName: 'Lerros',
    shopWebsite: 'lerros.com'
  },
  {
    id: '6',
    userName: 'Lisa M.',
    userInitials: 'LM',
    date: '2025-06-13',
    rating: 5,
    comment: 'Ordered for the second time. Delivery came within 2 days – top!',
    shopName: 'Fleurop',
    shopWebsite: 'fleurop.de'
  },
  {
    id: '7',
    userName: 'Peter D.',
    userInitials: 'PD',
    date: '2025-08-12',
    rating: 5,
    comment: 'Prompt and fast delivery',
    shopName: 'Yves Rocher',
    shopWebsite: 'yves-rocher.de'
  },
  {
    id: '8',
    userName: 'Michael K.',
    userInitials: 'MK',
    date: '2025-08-15',
    rating: 5,
    comment: 'Very good advice and comprehensive!',
    shopName: 'medimops',
    shopWebsite: 'medimops.de'
  }
];

export const statistics = {
  shoppers: '45 Million',
  shops: '32,000',
  dailyTransactions: '1 Million'
};