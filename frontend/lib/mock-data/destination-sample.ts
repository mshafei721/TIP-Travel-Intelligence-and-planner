import type { DestinationIntelligence } from '@/types/destination';

// Sample destination intelligence data for Japan
export const sampleDestinationData: DestinationIntelligence = {
  countryOverview: {
    name: 'Japan',
    code: 'JPN',
    capital: 'Tokyo',
    region: 'Asia',
    subregion: 'Eastern Asia',
    population: 125584000,
    area: 377930,
    languages: ['Japanese'],
    timezones: ['UTC+09:00 (JST)'],
    coordinates: {
      lat: 36.2048,
      lng: 138.2529,
    },
    borderingCountries: [],
    drivingSide: 'left',
    politicalSystem: 'Constitutional Monarchy',
    currency: {
      code: 'JPY',
      name: 'Japanese Yen',
      symbol: '¥',
    },
    flag: '🇯🇵',
    officialWebsite: 'https://www.japan.go.jp',
    tourismWebsite: 'https://www.japan.travel',
  },
  weather: {
    dailyForecasts: [
      {
        date: '2025-04-01',
        tempHigh: 18,
        tempLow: 10,
        condition: 'sunny',
        precipitationChance: 10,
        humidity: 55,
        windSpeed: 12,
        uvIndex: 6,
      },
      {
        date: '2025-04-02',
        tempHigh: 19,
        tempLow: 11,
        condition: 'partly-cloudy',
        precipitationChance: 20,
        humidity: 60,
        windSpeed: 15,
        uvIndex: 5,
      },
      {
        date: '2025-04-03',
        tempHigh: 16,
        tempLow: 12,
        condition: 'rainy',
        precipitationChance: 80,
        humidity: 75,
        windSpeed: 18,
        uvIndex: 3,
      },
      {
        date: '2025-04-04',
        tempHigh: 17,
        tempLow: 11,
        condition: 'cloudy',
        precipitationChance: 40,
        humidity: 65,
        windSpeed: 14,
        uvIndex: 4,
      },
      {
        date: '2025-04-05',
        tempHigh: 20,
        tempLow: 12,
        condition: 'sunny',
        precipitationChance: 5,
        humidity: 50,
        windSpeed: 10,
        uvIndex: 7,
      },
    ],
    bestTimeToVisit:
      'March-May (Spring for cherry blossoms) and September-November (Fall for autumn colors)',
    packingRecommendations: [
      'Light jacket or sweater for cool evenings',
      'Comfortable walking shoes',
      'Umbrella (spring has occasional rain)',
      'Sunscreen and hat for sunny days',
      'Layers for variable temperatures',
    ],
    climateType: 'Temperate with four distinct seasons',
  },
  currency: {
    localCurrency: {
      code: 'JPY',
      name: 'Japanese Yen',
      symbol: '¥',
    },
    exchangeRate: 149.85,
    atmAvailability: 'widespread',
    atmFees:
      'Most ATMs charge ¥110-220 per transaction. 7-Eleven ATMs widely accept foreign cards.',
    creditCardAcceptance: 'common',
    tippingCustoms:
      'Tipping is not customary and can be considered rude. Exceptional service is included in the price.',
    costOfLiving: {
      level: 'high',
      estimates: [
        { category: 'Meal at restaurant', cost: { min: 800, max: 3000, currency: 'JPY' } },
        { category: 'Coffee', cost: { min: 350, max: 600, currency: 'JPY' } },
        { category: 'Subway ticket', cost: { min: 170, max: 320, currency: 'JPY' } },
        { category: 'Hotel (budget)', cost: { min: 5000, max: 8000, currency: 'JPY' } },
        { category: 'Hotel (mid-range)', cost: { min: 10000, max: 20000, currency: 'JPY' } },
      ],
    },
    currencyExchangeTips: [
      'Exchange at banks or post offices for better rates',
      'Airport exchange rates are less favorable',
      'Many places still prefer cash over cards',
      '7-Eleven, FamilyMart, and Lawson ATMs accept most foreign cards',
    ],
  },
  culture: {
    dressCode:
      'Modest dress expected at temples and shrines. Remove shoes when entering homes, temples, and some restaurants. Tattoos may be prohibited at some public baths (onsen).',
    greetings:
      'Bow as greeting. Depth of bow indicates respect level. Handshakes acceptable for foreigners but less common.',
    customs: [
      'Gift-giving is important. Present and receive gifts with both hands.',
      'Business cards (meishi) are exchanged with both hands and a slight bow.',
      'Eating while walking is generally frowned upon.',
      'Public displays of affection are uncommon.',
    ],
    dos: [
      'Learn basic Japanese phrases (konnichiwa, arigatou, sumimasen)',
      'Be punctual - lateness is considered disrespectful',
      'Respect queues and personal space',
      'Use chopsticks properly (never stick them upright in rice)',
      'Be quiet on public transportation',
    ],
    donts: [
      "Don't tip (it's considered rude)",
      "Don't wear shoes indoors when asked to remove them",
      "Don't blow your nose in public",
      "Don't talk loudly on trains or buses",
      "Don't pour your own drink when dining with others",
    ],
    religiousConsiderations:
      "Japan is predominantly Shinto and Buddhist. Be respectful at religious sites. Bow before torii gates, don't photograph people praying without permission.",
    languageTips: [
      'English signage is common in major cities',
      'Download translation app - not everyone speaks English',
      'Learn how to read katakana (used for foreign words)',
      'Carry business cards with Japanese on one side',
    ],
  },
  food: {
    mustTryDishes: [
      {
        name: 'Sushi',
        description: 'Fresh seafood served over seasoned rice.',
        type: 'main',
      },
      {
        name: 'Ramen',
        description: 'Noodle soup with rich broth and toppings.',
        type: 'main',
      },
      {
        name: 'Matcha Tea',
        description: 'Traditional green tea prepared as a fine powder.',
        type: 'beverage',
        isVegetarian: true,
        isVegan: true,
      },
    ],
    streetFood: {
      popular: ['Takoyaki', 'Taiyaki', 'Yakitori'],
      safetyRating: 'good',
      tips: ['Choose busy stalls', 'Carry cash for small vendors'],
    },
    diningEtiquette: [
      'Say "itadakimasu" before eating and "gochisousama" after.',
      'Do not stick chopsticks upright in rice.',
      'Slurping noodles is acceptable and shows enjoyment.',
    ],
    dietaryOptions: {
      vegetarian: 'limited',
      vegan: 'rare',
      halal: 'limited',
      kosher: 'rare',
      glutenFree: 'limited',
      notes: 'Specialty restaurants are more common in major cities.',
    },
    priceRanges: [
      {
        mealType: 'street-food',
        priceRange: { min: 300, max: 800, currency: 'JPY' },
        description: 'Snacks and quick bites.',
      },
      {
        mealType: 'casual-dining',
        priceRange: { min: 800, max: 1500, currency: 'JPY' },
      },
      {
        mealType: 'mid-range',
        priceRange: { min: 2000, max: 5000, currency: 'JPY' },
      },
    ],
    recommendations: [
      {
        name: 'Tsukiji Outer Market',
        type: 'market',
        specialty: 'Fresh seafood',
        priceLevel: '$$',
        location: 'Tokyo',
      },
      {
        name: 'Local Ramen Shop',
        type: 'restaurant',
        specialty: 'Tonkotsu ramen',
        priceLevel: '$',
        location: 'Various cities',
      },
    ],
    safetyTips: [
      'Check for allergies and dietary labels.',
      'Avoid raw seafood if you are sensitive.',
    ],
  },
  laws: {
    restrictions: [
      {
        title: 'Drug Possession',
        description:
          'Japan has extremely strict drug laws. Possession of even small amounts of illegal drugs can result in lengthy prison sentences.',
        severity: 'critical',
        penalty: 'Up to 10 years imprisonment',
      },
      {
        title: 'Certain Medications',
        description:
          'Some over-the-counter medications (e.g., cold medicine with pseudoephedrine, ADHD medications) are prohibited. Check before bringing medication.',
        severity: 'critical',
        penalty: 'Arrest and deportation',
      },
      {
        title: 'Dancing in Unlicensed Venues',
        description:
          'Technically, dancing in clubs without proper licenses was illegal until recently. Most clubs now have licenses, but some small venues may not.',
        severity: 'info',
      },
      {
        title: 'Public Intoxication',
        description:
          'While drinking is part of the culture, causing disturbances while drunk can result in arrest.',
        severity: 'warning',
        penalty: 'Detention or fine',
      },
    ],
    importRestrictions: [
      'Firearms and ammunition (including replicas)',
      'Narcotics and psychotropic substances',
      'Pornographic materials',
      'Counterfeit goods',
      'Some medications (check Ministry of Health website)',
    ],
    photographyRestrictions: [
      "Don't photograph people without permission",
      'Some shrines and museums prohibit photography',
      'Military installations are prohibited',
    ],
    internetRestrictions: ['No major internet censorship', 'VPNs are legal and commonly used'],
  },
  safety: {
    overallSafetyRating: 5,
    safetyAlerts: [
      {
        type: 'natural-disaster',
        severity: 'caution',
        title: 'Earthquake Preparedness',
        description:
          'Japan is in an earthquake-prone region. Familiarize yourself with earthquake safety procedures. Download the Safety Tips app for emergency alerts.',
        date: '2025-01-15',
      },
    ],
    crimeRates: {
      overall: 'very-low',
      pettyTheft: 'very-low',
      violentCrime: 'very-low',
    },
    emergencyNumbers: [
      { service: 'Police', number: '110' },
      { service: 'Fire/Ambulance', number: '119' },
      { service: 'Japan Helpline (English)', number: '0570-000-911' },
    ],
    healthRisks: [
      {
        risk: 'Japanese Encephalitis',
        severity: 'low',
        prevention:
          'Vaccination recommended if visiting rural areas during summer months. Use insect repellent.',
        vaccinationRequired: false,
      },
      {
        risk: 'Radiation (Fukushima)',
        severity: 'low',
        prevention: 'Avoid exclusion zone around Fukushima Daiichi. Other areas are safe.',
        vaccinationRequired: false,
      },
    ],
  },
  news: [
    {
      id: '1',
      headline: 'Japan Welcomes Record Number of International Tourists in 2024',
      summary:
        'Tourism rebounds to pre-pandemic levels as Japan reopened its borders. Cherry blossom season saw unprecedented visitor numbers.',
      date: '2025-03-15',
      source: 'Japan Times',
      url: 'https://japantimes.co.jp',
      relevance: 'high',
      category: 'tourism',
    },
    {
      id: '2',
      headline: 'New Digital Nomad Visa Announced for Long-Term Visitors',
      summary:
        'Japan introduces new 6-month digital nomad visa allowing remote workers to stay longer. Applications open April 2025.',
      date: '2025-03-10',
      source: 'NHK World',
      url: 'https://nhk.or.jp',
      relevance: 'high',
      category: 'politics',
    },
    {
      id: '3',
      headline: 'Yen Weakens Against Dollar, Making Japan More Affordable',
      summary:
        'Exchange rate shifts make Japan an attractive destination for foreign travelers with favorable purchasing power.',
      date: '2025-03-01',
      source: 'Bloomberg Japan',
      url: 'https://bloomberg.com',
      relevance: 'medium',
      category: 'economy',
    },
  ],
};
