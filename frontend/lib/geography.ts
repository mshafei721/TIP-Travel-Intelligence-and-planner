/**
 * Geography utilities using country-state-city package
 */

import { Country, City, ICountry, ICity } from 'country-state-city';
import type { SelectOption } from '@/components/ui/SearchableSelect';

// Cache for performance
let countriesCache: SelectOption[] | null = null;
const citiesCache: Map<string, SelectOption[]> = new Map();

/**
 * Get all countries as select options
 */
export function getAllCountries(): SelectOption[] {
  if (countriesCache) {
    return countriesCache;
  }

  const countries = Country.getAllCountries();
  countriesCache = countries.map((country: ICountry) => ({
    value: country.isoCode,
    label: country.name,
  }));

  return countriesCache;
}

/**
 * Get cities for a specific country by ISO code
 */
export function getCitiesForCountry(countryCode: string): SelectOption[] {
  if (!countryCode) {
    return [];
  }

  // Check cache first
  const cached = citiesCache.get(countryCode);
  if (cached) {
    return cached;
  }

  const cities = City.getCitiesOfCountry(countryCode);
  if (!cities) {
    return [];
  }

  const options = cities.map((city: ICity) => ({
    value: city.name,
    label: city.name,
  }));

  // Cache the result
  citiesCache.set(countryCode, options);

  return options;
}

/**
 * Get country name by ISO code
 */
export function getCountryByCode(countryCode: string): ICountry | undefined {
  return Country.getCountryByCode(countryCode);
}

/**
 * Search countries by name (partial match)
 */
export function searchCountries(query: string): SelectOption[] {
  const countries = getAllCountries();
  if (!query) return countries;

  const lowerQuery = query.toLowerCase();
  return countries.filter((country) => country.label.toLowerCase().includes(lowerQuery));
}

/**
 * Get country code from country name
 */
export function getCountryCodeByName(countryName: string): string | undefined {
  const countries = Country.getAllCountries();
  const found = countries.find((c: ICountry) => c.name.toLowerCase() === countryName.toLowerCase());
  return found?.isoCode;
}
