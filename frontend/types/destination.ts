// Destination Intelligence Types
// For I6: Destination Intelligence section

export interface DestinationIntelligence {
  countryOverview: CountryOverview;
  weather: WeatherForecast;
  currency: CurrencyInfo;
  culture: CulturalNorms;
  laws: UnusualLaws;
  safety: SafetyInfo;
  news: NewsItem[];
}

export interface CountryOverview {
  name: string;
  code: string;
  capital: string;
  region: string;
  subregion: string;
  population: number;
  area: number; // in km²
  languages: string[];
  timezones: string[];
  coordinates: {
    lat: number;
    lng: number;
  };
  borderingCountries: string[];
  drivingSide: 'left' | 'right';
  politicalSystem?: string;
  currency: {
    code: string;
    name: string;
    symbol: string;
  };
  flag?: string;
  officialWebsite?: string;
  tourismWebsite?: string;
}

export interface WeatherForecast {
  dailyForecasts: DailyForecast[];
  bestTimeToVisit: string;
  packingRecommendations: string[];
  climateType?: string;
}

export interface DailyForecast {
  date: string; // ISO date string
  tempHigh: number; // in Celsius
  tempLow: number; // in Celsius
  condition: WeatherCondition;
  precipitationChance: number; // percentage 0-100
  humidity?: number; // percentage 0-100
  windSpeed?: number; // km/h
  uvIndex?: number; // 0-11+
}

export type WeatherCondition =
  | 'sunny'
  | 'partly-cloudy'
  | 'cloudy'
  | 'rainy'
  | 'stormy'
  | 'snowy'
  | 'windy'
  | 'foggy';

export interface CurrencyInfo {
  localCurrency: {
    code: string;
    name: string;
    symbol: string;
  };
  exchangeRate: number; // relative to USD
  atmAvailability: 'widespread' | 'common' | 'limited' | 'rare';
  atmFees: string;
  creditCardAcceptance: 'widespread' | 'common' | 'limited' | 'rare';
  tippingCustoms: string;
  costOfLiving: {
    level: 'very-low' | 'low' | 'moderate' | 'high' | 'very-high';
    estimates: CostEstimate[];
  };
  currencyExchangeTips: string[];
}

export interface CostEstimate {
  category: string; // e.g., "Meal at restaurant", "Coffee", "Taxi (1km)"
  cost: {
    min: number;
    max: number;
    currency: string;
  };
}

export interface CulturalNorms {
  dressCode: string;
  greetings: string;
  customs: string[];
  dos: string[];
  donts: string[];
  religiousConsiderations?: string;
  languageTips?: string[];
  etiquetteGuides?: ExternalLink[];
}

export interface UnusualLaws {
  restrictions: LegalRestriction[];
  importRestrictions?: string[];
  photographyRestrictions?: string[];
  internetRestrictions?: string[];
  legalResources?: ExternalLink[];
}

export interface LegalRestriction {
  title: string;
  description: string;
  severity: 'info' | 'warning' | 'critical';
  penalty?: string;
}

export interface SafetyInfo {
  overallSafetyRating: 1 | 2 | 3 | 4 | 5; // 1 = very unsafe, 5 = very safe
  safetyAlerts: SafetyAlert[];
  crimeRates: {
    overall: 'very-low' | 'low' | 'moderate' | 'high' | 'very-high';
    pettyTheft: 'very-low' | 'low' | 'moderate' | 'high' | 'very-high';
    violentCrime: 'very-low' | 'low' | 'moderate' | 'high' | 'very-high';
  };
  emergencyNumbers: EmergencyContact[];
  healthRisks: HealthRisk[];
  travelAdvisories?: ExternalLink[];
}

export interface SafetyAlert {
  type: 'general' | 'health' | 'political' | 'natural-disaster' | 'terrorism';
  severity: 'info' | 'caution' | 'warning' | 'danger';
  title: string;
  description: string;
  date?: string;
}

export interface EmergencyContact {
  service: string; // e.g., "Police", "Ambulance", "Fire"
  number: string;
  notes?: string;
}

export interface HealthRisk {
  risk: string; // e.g., "Malaria", "Dengue Fever"
  severity: 'low' | 'moderate' | 'high';
  prevention: string;
  vaccinationRequired?: boolean;
}

export interface NewsItem {
  id: string;
  headline: string;
  summary: string;
  date: string; // ISO date string
  source: string;
  url: string;
  relevance: 'high' | 'medium' | 'low';
  category?: 'politics' | 'economy' | 'culture' | 'tourism' | 'health' | 'general';
}

export interface ExternalLink {
  title: string;
  url: string;
  type?: 'official' | 'government' | 'tourism' | 'third-party';
}

// Card state management
export interface CardState {
  isExpanded: boolean;
  isLoading: boolean;
  hasError: boolean;
  errorMessage?: string;
}

// Analytics callbacks
export interface DestinationCallbacks {
  onCardExpand?: (cardId: string) => void;
  onCardCollapse?: (cardId: string) => void;
  onExternalLinkClick?: (url: string, title: string) => void;
}
