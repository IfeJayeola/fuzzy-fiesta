from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from .models import Country, RefreshMetadata
from datetime import datetime

class SummaryImageGenerator:
    
    @staticmethod
    def generate_summary_image():
        """Generate a summary image with country statistics"""
        
        # Image dimensions and colors
        width, height = 800, 600
        bg_color = (255, 255, 255)
        text_color = (0, 0, 0)
        header_color = (41, 128, 185)
        
        # Create image
        img = Image.new('RGB', (width, height), bg_color)
        draw = ImageDraw.Draw(img)
        
        # Try to use a better font, fall back to default if not available
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
            header_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            text_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        except:
            title_font = ImageFont.load_default()
            header_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
        
        # Get data
        metadata = RefreshMetadata.get_instance()
        total_countries = metadata.total_countries
        last_refreshed = metadata.last_refreshed_at.strftime('%Y-%m-%d %H:%M:%S UTC')
        
        # Get top 5 countries by GDP
        top_countries = Country.objects.filter(
            estimated_gdp__isnull=False
        ).order_by('-estimated_gdp')[:5]
        
        # Draw header background
        draw.rectangle([(0, 0), (width, 80)], fill=header_color)
        
        # Draw title
        title = "Country Data Summary"
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(((width - title_width) / 2, 20), title, fill=(255, 255, 255), font=title_font)
        
        # Draw total countries
        y_position = 120
        total_text = f"Total Countries: {total_countries}"
        draw.text((50, y_position), total_text, fill=text_color, font=header_font)
        
        # Draw top 5 header
        y_position += 60
        draw.text((50, y_position), "Top 5 Countries by Estimated GDP:", fill=text_color, font=header_font)
        
        # Draw top 5 countries
        y_position += 40
        for i, country in enumerate(top_countries, 1):
            gdp_formatted = f"${country.estimated_gdp:,.2f}"
            country_text = f"{i}. {country.name}: {gdp_formatted}"
            draw.text((70, y_position), country_text, fill=text_color, font=text_font)
            y_position += 35
        
        # Draw timestamp at bottom
        timestamp_text = f"Last Refreshed: {last_refreshed}"
        timestamp_bbox = draw.textbbox((0, 0), timestamp_text, font=text_font)
        timestamp_width = timestamp_bbox[2] - timestamp_bbox[0]
        draw.text(((width - timestamp_width) / 2, height - 50), timestamp_text, fill=text_color, font=text_font)
        
        # Save image
        image_path = settings.CACHE_DIR / 'summary.png'
        img.save(image_path)
        
        return image_path
