import requests
import random
from decimal import Decimal
from django.conf import settings
from .models import Country, RefreshMetadata

class ExternalAPIError(Exception):
    pass

class CountryDataService:
    
    @staticmethod
    def fetch_countries():
        """Fetch country data from external API"""
        try:
            response = requests.get(settings.COUNTRIES_API_URL, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ExternalAPIError(f"Could not fetch data from countries API: {str(e)}")
    
    @staticmethod
    def fetch_exchange_rates():
        """Fetch exchange rates from external API"""
        try:
            response = requests.get(settings.EXCHANGE_API_URL, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data.get('rates', {})
        except requests.exceptions.RequestException as e:
            raise ExternalAPIError(f"Could not fetch data from exchange rate API: {str(e)}")
    
    @staticmethod
    def calculate_gdp(population, exchange_rate):
        """Calculate estimated GDP"""
        if exchange_rate is None or exchange_rate == 0:
            return None
        
        multiplier = random.uniform(1000, 2000)
        gdp = Decimal(population) * Decimal(multiplier) / Decimal(exchange_rate)
        return round(gdp, 2)
    
    @staticmethod
    def get_currency_code(currencies):
        """Extract first currency code from currencies array"""
        if not currencies or len(currencies) == 0:
            return None
        
        first_currency = currencies[0]
        return first_currency.get('code')
    
    @staticmethod
    def process_and_store_countries():
        """Main method to fetch, process, and store country data"""
        # Fetch data from external APIs
        countries_data = CountryDataService.fetch_countries()
        exchange_rates = CountryDataService.fetch_exchange_rates()
        
        processed_count = 0
        
        for country_data in countries_data:
            name = country_data.get('name')
            capital = country_data.get('capital')
            region = country_data.get('region')
            population = country_data.get('population')
            flag_url = country_data.get('flag')
            currencies = country_data.get('currencies', [])
            
            # Skip if name or population is missing
            if not name or population is None:
                continue
            
            # Get currency code
            currency_code = CountryDataService.get_currency_code(currencies)
            
            # Get exchange rate and calculate GDP
            exchange_rate = None
            estimated_gdp = None
            
            if currency_code:
                exchange_rate = exchange_rates.get(currency_code)
                if exchange_rate:
                    estimated_gdp = CountryDataService.calculate_gdp(population, exchange_rate)
            else:
                # No currency, set GDP to 0
                estimated_gdp = Decimal('0.00')
            
            # Update or create country record
            Country.objects.update_or_create(
                name__iexact=name,
                defaults={
                    'name': name,
                    'capital': capital,
                    'region': region,
                    'population': population,
                    'currency_code': currency_code,
                    'exchange_rate': exchange_rate,
                    'estimated_gdp': estimated_gdp,
                    'flag_url': flag_url,
                }
            )
            processed_count += 1
        
        # Update metadata
        metadata = RefreshMetadata.get_instance()
        metadata.total_countries = Country.objects.count()
        metadata.save()
        
        return processed_count, metadata
