import type { TripItinerary } from '@/types/itinerary';

// Sample 5-day Tokyo itinerary
export const sampleItinerary: TripItinerary = {
  tripId: 'trip-tokyo-2024',
  tripName: 'Tokyo Adventure',
  destination: 'Tokyo, Japan',
  startDate: '2024-03-15',
  endDate: '2024-03-19',
  currency: 'JPY',
  totalBudget: 250000,
  days: [
    // Day 1
    {
      dayNumber: 1,
      date: '2024-03-15',
      location: 'Shibuya & Harajuku',
      timeBlocks: [
        {
          id: 'tb-1-morning',
          timeOfDay: 'morning',
          activities: [
            {
              id: 'act-1-1',
              name: 'Meiji Shrine',
              category: 'culture',
              startTime: '09:00',
              endTime: '11:00',
              duration: 120,
              location: {
                name: 'Meiji Jingu',
                address: '1-1 Yoyogikamizonocho, Shibuya City, Tokyo',
                coordinates: { lat: 35.6764, lng: 139.6993 },
                neighborhood: 'Harajuku',
                transportInfo: 'Harajuku Station (JR Yamanote Line)',
              },
              description: 'Historic Shinto shrine surrounded by forest. Free entrance.',
              cost: { amount: 0, currency: 'JPY', perPerson: true },
              priority: 'must-see',
              accessibility: { wheelchairAccessible: true },
            },
            {
              id: 'act-1-2',
              name: 'Takeshita Street Shopping',
              category: 'shopping',
              startTime: '11:30',
              endTime: '13:00',
              duration: 90,
              location: {
                name: 'Takeshita Dori',
                address: 'Jingumae, Shibuya City, Tokyo',
                coordinates: { lat: 35.6702, lng: 139.7027 },
                neighborhood: 'Harajuku',
              },
              description: 'Trendy shopping street with fashion boutiques and crepe stands.',
              cost: {
                amount: 3000,
                currency: 'JPY',
                perPerson: true,
                notes: 'Shopping budget estimate',
              },
              priority: 'recommended',
            },
          ],
        },
        {
          id: 'tb-1-afternoon',
          timeOfDay: 'afternoon',
          activities: [
            {
              id: 'act-1-3',
              name: 'Lunch at Ichiran Ramen',
              category: 'food',
              startTime: '13:00',
              endTime: '14:00',
              duration: 60,
              location: {
                name: 'Ichiran Shibuya',
                address: '1-22-7 Jinnan, Shibuya City, Tokyo',
                coordinates: { lat: 35.6617, lng: 139.7006 },
                neighborhood: 'Shibuya',
              },
              description: 'Famous solo-dining ramen experience.',
              cost: { amount: 1200, currency: 'JPY', perPerson: true },
              priority: 'must-see',
            },
            {
              id: 'act-1-4',
              name: 'Shibuya Crossing & Hachiko Statue',
              category: 'culture',
              startTime: '14:30',
              endTime: '16:00',
              duration: 90,
              location: {
                name: 'Shibuya Scramble Crossing',
                address: '2-chōme-2 Dōgenzaka, Shibuya City, Tokyo',
                coordinates: { lat: 35.6595, lng: 139.7004 },
                neighborhood: 'Shibuya',
              },
              description:
                "World's busiest pedestrian crossing. View from Starbucks for best photo op.",
              cost: { amount: 0, currency: 'JPY', perPerson: true },
              priority: 'must-see',
            },
          ],
        },
        {
          id: 'tb-1-evening',
          timeOfDay: 'evening',
          activities: [
            {
              id: 'act-1-5',
              name: 'teamLab Borderless',
              category: 'entertainment',
              startTime: '18:00',
              endTime: '20:00',
              duration: 120,
              location: {
                name: 'Mori Building Digital Art Museum',
                address: 'Azabudai Hills, Minato City, Tokyo',
                coordinates: { lat: 35.6596, lng: 139.7428 },
                neighborhood: 'Azabudai',
              },
              description: 'Immersive digital art museum. Book tickets in advance!',
              cost: { amount: 3800, currency: 'JPY', perPerson: true },
              bookingInfo: {
                required: true,
                website: 'https://www.teamlab.art/e/borderless/',
                bookingStatus: 'confirmed',
              },
              priority: 'must-see',
            },
          ],
        },
      ],
    },
    // Day 2
    {
      dayNumber: 2,
      date: '2024-03-16',
      location: 'Asakusa & Tokyo Skytree',
      timeBlocks: [
        {
          id: 'tb-2-morning',
          timeOfDay: 'morning',
          activities: [
            {
              id: 'act-2-1',
              name: 'Senso-ji Temple',
              category: 'culture',
              startTime: '09:00',
              endTime: '11:00',
              duration: 120,
              location: {
                name: 'Senso-ji',
                address: '2-3-1 Asakusa, Taito City, Tokyo',
                coordinates: { lat: 35.7148, lng: 139.7967 },
                neighborhood: 'Asakusa',
                transportInfo: 'Asakusa Station (Ginza Line)',
              },
              description: "Tokyo's oldest Buddhist temple. Explore Nakamise shopping street.",
              cost: { amount: 0, currency: 'JPY', perPerson: true },
              priority: 'must-see',
            },
          ],
        },
        {
          id: 'tb-2-afternoon',
          timeOfDay: 'afternoon',
          activities: [
            {
              id: 'act-2-2',
              name: 'Tokyo Skytree Observatory',
              category: 'culture',
              startTime: '13:00',
              endTime: '15:00',
              duration: 120,
              location: {
                name: 'Tokyo Skytree',
                address: '1-1-2 Oshiage, Sumida City, Tokyo',
                coordinates: { lat: 35.7101, lng: 139.8107 },
                neighborhood: 'Oshiage',
              },
              description:
                'Tallest structure in Japan. 360° views from 350m and 450m observation decks.',
              cost: { amount: 3100, currency: 'JPY', perPerson: true },
              priority: 'recommended',
            },
          ],
        },
        {
          id: 'tb-2-evening',
          timeOfDay: 'evening',
          activities: [
            {
              id: 'act-2-3',
              name: 'Dinner at Tsukiji Outer Market',
              category: 'food',
              startTime: '18:00',
              endTime: '20:00',
              duration: 120,
              location: {
                name: 'Tsukiji Outer Market',
                address: 'Tsukiji, Chuo City, Tokyo',
                coordinates: { lat: 35.6654, lng: 139.7707 },
                neighborhood: 'Tsukiji',
              },
              description: 'Fresh sushi and seafood. Try omakase or street food stalls.',
              cost: { amount: 5000, currency: 'JPY', perPerson: true },
              priority: 'must-see',
            },
          ],
        },
      ],
    },
    // Day 3
    {
      dayNumber: 3,
      date: '2024-03-17',
      location: 'Akihabara & Ueno',
      timeBlocks: [
        {
          id: 'tb-3-morning',
          timeOfDay: 'morning',
          activities: [
            {
              id: 'act-3-1',
              name: 'Ueno Park & Museums',
              category: 'nature',
              startTime: '09:00',
              endTime: '12:00',
              duration: 180,
              location: {
                name: 'Ueno Park',
                address: 'Uenokoen, Taito City, Tokyo',
                coordinates: { lat: 35.7148, lng: 139.7744 },
                neighborhood: 'Ueno',
              },
              description: 'Beautiful park with museums. Cherry blossoms if in season!',
              cost: { amount: 0, currency: 'JPY', perPerson: true },
              priority: 'recommended',
            },
          ],
        },
        {
          id: 'tb-3-afternoon',
          timeOfDay: 'afternoon',
          activities: [
            {
              id: 'act-3-2',
              name: 'Akihabara Electric Town',
              category: 'shopping',
              startTime: '14:00',
              endTime: '17:00',
              duration: 180,
              location: {
                name: 'Akihabara',
                address: 'Sotokanda, Chiyoda City, Tokyo',
                coordinates: { lat: 35.7022, lng: 139.7745 },
                neighborhood: 'Akihabara',
              },
              description: 'Electronics, anime, manga shopping paradise. Visit maid cafes!',
              cost: { amount: 5000, currency: 'JPY', perPerson: true, notes: 'Shopping estimate' },
              priority: 'recommended',
            },
          ],
        },
        {
          id: 'tb-3-evening',
          timeOfDay: 'evening',
          activities: [
            {
              id: 'act-3-3',
              name: 'Dinner at Kanda Yabu Soba',
              category: 'food',
              startTime: '18:00',
              endTime: '19:30',
              duration: 90,
              location: {
                name: 'Kanda Yabu Soba',
                address: '2-10 Kanda Awajicho, Chiyoda City, Tokyo',
                coordinates: { lat: 35.6969, lng: 139.7673 },
                neighborhood: 'Kanda',
              },
              description: 'Historic soba restaurant since 1880. Traditional atmosphere.',
              cost: { amount: 1500, currency: 'JPY', perPerson: true },
              priority: 'recommended',
            },
          ],
        },
      ],
    },
    // Day 4
    {
      dayNumber: 4,
      date: '2024-03-18',
      location: 'Odaiba & Tokyo Bay',
      timeBlocks: [
        {
          id: 'tb-4-morning',
          timeOfDay: 'morning',
          activities: [
            {
              id: 'act-4-1',
              name: 'Tsukiji Fish Market Tour',
              category: 'food',
              startTime: '06:00',
              endTime: '08:00',
              duration: 120,
              location: {
                name: 'Toyosu Market',
                address: '6-6-2 Toyosu, Koto City, Tokyo',
                coordinates: { lat: 35.6417, lng: 139.7851 },
                neighborhood: 'Toyosu',
              },
              description: 'Early morning tuna auction viewing. Fresh sushi breakfast!',
              cost: { amount: 3000, currency: 'JPY', perPerson: true },
              priority: 'must-see',
              notes: 'Must wake up early! Auction starts at 5:30 AM',
            },
          ],
        },
        {
          id: 'tb-4-afternoon',
          timeOfDay: 'afternoon',
          activities: [
            {
              id: 'act-4-2',
              name: 'Odaiba Waterfront',
              category: 'entertainment',
              startTime: '13:00',
              endTime: '17:00',
              duration: 240,
              location: {
                name: 'Odaiba Seaside Park',
                address: '1-chōme Daiba, Minato City, Tokyo',
                coordinates: { lat: 35.6292, lng: 139.7744 },
                neighborhood: 'Odaiba',
              },
              description: 'Waterfront area with shopping, teamLab Planets, Gundam statue.',
              cost: { amount: 4000, currency: 'JPY', perPerson: true },
              priority: 'recommended',
            },
          ],
        },
        {
          id: 'tb-4-evening',
          timeOfDay: 'evening',
          activities: [
            {
              id: 'act-4-3',
              name: 'Rainbow Bridge Sunset',
              category: 'nature',
              startTime: '18:00',
              endTime: '19:00',
              duration: 60,
              location: {
                name: 'Rainbow Bridge',
                address: 'Konan, Minato City, Tokyo',
                coordinates: { lat: 35.6333, lng: 139.7636 },
                neighborhood: 'Odaiba',
              },
              description: 'Beautiful sunset views of Tokyo Bay.',
              cost: { amount: 0, currency: 'JPY', perPerson: true },
              priority: 'optional',
            },
          ],
        },
      ],
    },
    // Day 5
    {
      dayNumber: 5,
      date: '2024-03-19',
      location: 'Shinjuku & Departure',
      timeBlocks: [
        {
          id: 'tb-5-morning',
          timeOfDay: 'morning',
          activities: [
            {
              id: 'act-5-1',
              name: 'Shinjuku Gyoen National Garden',
              category: 'nature',
              startTime: '09:00',
              endTime: '11:00',
              duration: 120,
              location: {
                name: 'Shinjuku Gyoen',
                address: '11 Naitomachi, Shinjuku City, Tokyo',
                coordinates: { lat: 35.6852, lng: 139.71 },
                neighborhood: 'Shinjuku',
              },
              description: 'Beautiful Japanese garden. Perfect for morning stroll.',
              cost: { amount: 500, currency: 'JPY', perPerson: true },
              priority: 'recommended',
            },
          ],
        },
        {
          id: 'tb-5-afternoon',
          timeOfDay: 'afternoon',
          activities: [
            {
              id: 'act-5-2',
              name: 'Last-minute Souvenir Shopping',
              category: 'shopping',
              startTime: '12:00',
              endTime: '14:00',
              duration: 120,
              location: {
                name: 'Don Quijote Shinjuku',
                address: '1-16-5 Kabukicho, Shinjuku City, Tokyo',
                coordinates: { lat: 35.6938, lng: 139.7006 },
                neighborhood: 'Shinjuku',
              },
              description: 'Mega discount store with everything. Perfect for souvenirs.',
              cost: { amount: 10000, currency: 'JPY', perPerson: true, notes: 'Souvenir budget' },
              priority: 'optional',
            },
            {
              id: 'act-5-3',
              name: 'Departure to Narita Airport',
              category: 'transport',
              startTime: '15:00',
              endTime: '17:00',
              duration: 120,
              location: {
                name: 'Narita Express from Shinjuku',
                address: 'Shinjuku Station',
                coordinates: { lat: 35.6896, lng: 139.7006 },
                neighborhood: 'Shinjuku',
              },
              description: "N'EX train to Narita Airport. Check in 3 hours before flight.",
              cost: { amount: 3250, currency: 'JPY', perPerson: true },
              priority: 'must-see',
            },
          ],
        },
      ],
    },
  ],
  flights: [
    {
      id: 'flight-outbound',
      type: 'outbound',
      departure: {
        airportCode: 'LAX',
        airportName: 'Los Angeles International Airport',
        city: 'Los Angeles',
        country: 'United States',
        datetime: '2024-03-14T22:00:00-08:00',
        terminal: 'TBIT',
      },
      arrival: {
        airportCode: 'NRT',
        airportName: 'Narita International Airport',
        city: 'Tokyo',
        country: 'Japan',
        datetime: '2024-03-16T04:30:00+09:00',
        terminal: '1',
      },
      duration: 690, // 11.5 hours
      price: {
        amount: 850,
        currency: 'USD',
        fareClass: 'economy',
      },
      airline: 'Japan Airlines',
      flightNumber: 'JL 061',
      stops: 0,
      bookingStatus: 'booked',
    },
    {
      id: 'flight-return',
      type: 'return',
      departure: {
        airportCode: 'NRT',
        airportName: 'Narita International Airport',
        city: 'Tokyo',
        country: 'Japan',
        datetime: '2024-03-19T19:00:00+09:00',
        terminal: '1',
      },
      arrival: {
        airportCode: 'LAX',
        airportName: 'Los Angeles International Airport',
        city: 'Los Angeles',
        country: 'United States',
        datetime: '2024-03-19T12:30:00-08:00',
        terminal: 'TBIT',
      },
      duration: 630, // 10.5 hours
      price: {
        amount: 920,
        currency: 'USD',
        fareClass: 'economy',
      },
      airline: 'Japan Airlines',
      flightNumber: 'JL 062',
      stops: 0,
      bookingStatus: 'booked',
    },
  ],
};

// Helper function to get activities by category
export function getActivitiesByCategory(itinerary: TripItinerary) {
  const categoryCounts: Record<string, number> = {};

  itinerary.days.forEach((day) => {
    day.timeBlocks.forEach((block) => {
      block.activities.forEach((activity) => {
        categoryCounts[activity.category] = (categoryCounts[activity.category] || 0) + 1;
      });
    });
  });

  return categoryCounts;
}

// Helper function to calculate total cost
export function calculateTotalCost(itinerary: TripItinerary): number {
  let total = 0;

  itinerary.days.forEach((day) => {
    day.timeBlocks.forEach((block) => {
      block.activities.forEach((activity) => {
        if (activity.cost) {
          total += activity.cost.amount;
        }
      });
    });
  });

  return total;
}
