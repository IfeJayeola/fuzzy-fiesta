from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import FileResponse, JsonResponse
from django.conf import settings
from django.db.models import Q
from .models import Country, RefreshMetadata
from .serializers import CountrySerializer
from .services import CountryDataService, ExternalAPIError
from .image_generator import SummaryImageGenerator
import os

@api_view(['POST'])
def refresh_countries(request):
    """
    Fetch all countries and exchange rates, then cache them in the database
    """
    try:
        # Process and store countries
        processed_count, metadata = CountryDataService.process_and_store_countries()
        
        # Generate summary image
        SummaryImageGenerator.generate_summary_image()
        
        return Response({
            'message': f'Successfully refreshed {processed_count} countries',
            'total_countries': metadata.total_countries,
            'last_refreshed_at': metadata.last_refreshed_at
        }, status=status.HTTP_200_OK)
        
    except ExternalAPIError as e:
        return Response({
            'error': 'External data source unavailable',
            'details': str(e)
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    
    except Exception as e:
        return Response({
            'error': 'Internal server error',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def list_countries(request):
    """
    Get all countries from the database with optional filters and sorting
    Query params:
    - region: Filter by region (e.g., ?region=Africa)
    - currency: Filter by currency code (e.g., ?currency=NGN)
    - sort: Sort results (e.g., ?sort=gdp_desc, ?sort=gdp_asc, ?sort=population_desc)
    """
    try:
        queryset = Country.objects.all()
        
        # Filter by region
        region = request.GET.get('region')
        if region:
            queryset = queryset.filter(region__iexact=region)
        
        # Filter by currency
        currency = request.GET.get('currency')
        if currency:
            queryset = queryset.filter(currency_code__iexact=currency)
        
        # Sorting
        sort_param = request.GET.get('sort')
        if sort_param:
            if sort_param == 'gdp_desc':
                queryset = queryset.order_by('-estimated_gdp')
            elif sort_param == 'gdp_asc':
                queryset = queryset.order_by('estimated_gdp')
            elif sort_param == 'population_desc':
                queryset = queryset.order_by('-population')
            elif sort_param == 'population_asc':
                queryset = queryset.order_by('population')
            elif sort_param == 'name_asc':
                queryset = queryset.order_by('name')
            elif sort_param == 'name_desc':
                queryset = queryset.order_by('-name')
        
        serializer = CountrySerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'error': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_country(request, name):
    """
    Get one country by name
    """
    try:
        country = Country.objects.get(name__iexact=name)
        serializer = CountrySerializer(country)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except Country.DoesNotExist:
        return Response({
            'error': 'Country not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({
            'error': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
def delete_country(request, name):
    """
    Delete a country record
    """
    try:
        country = Country.objects.get(name__iexact=name)
        country.delete()
        
        # Update metadata
        metadata = RefreshMetadata.get_instance()
        metadata.total_countries = Country.objects.count()
        metadata.save()
        
        return Response({
            'message': f'Country {name} deleted successfully'
        }, status=status.HTTP_200_OK)
    
    except Country.DoesNotExist:
        return Response({
            'error': 'Country not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response({
            'error': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_status(request):
    """
    Show total countries and last refresh timestamp
    """
    try:
        metadata = RefreshMetadata.get_instance()
        return Response({
            'total_countries': metadata.total_countries,
            'last_refreshed_at': metadata.last_refreshed_at
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'error': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_summary_image(request):
    """
    Serve the generated summary image
    """
    try:
        image_path = settings.CACHE_DIR / 'summary.png'
        
        if not os.path.exists(image_path):
            return Response({
                'error': 'Summary image not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return FileResponse(open(image_path, 'rb'), content_type='image/png')
    
    except Exception as e:
        return Response({
            'error': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
