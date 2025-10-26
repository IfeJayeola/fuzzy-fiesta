from django.db import models

# Create your models here.

class Country(models.Model):
    name = models.CharField(max_length=255, unique=True)
    capital = models.CharField(max_length=255, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    population = models.BigIntegerField()
    currency_code = models.CharField(max_length=10, null=True, blank=True)
    exchange_rate = models.DecimalField(max_digits=20, decimal_places=6, null=True, blank=True)
    estimated_gdp = models.DecimalField(max_digits=30, decimal_places=2, null=True, blank=True)
    flag_url = models.URLField(max_length=500, blank=True, null=True)
    last_refreshed_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'countries'
        ordering = ['name']
        verbose_name_plural = 'Countries'
    
    def __str__(self):
        return self.name


class RefreshMetadata(models.Model):
    last_refreshed_at = models.DateTimeField(auto_now=True)
    total_countries = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'refresh_metadata'
    
    @classmethod
    def get_instance(cls):
        obj, created = cls.objects.get_or_create(id=1)
        return obj
