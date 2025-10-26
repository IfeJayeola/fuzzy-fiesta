# Country Currency & Exchange API

A RESTful API built with Django and Django REST Framework that fetches country data from external APIs, calculates estimated GDP based on exchange rates, and provides CRUD operations.

## Features

- Fetch country data from RestCountries API
- Fetch exchange rates from Open Exchange Rates API
- Calculate estimated GDP for each country
- Store and cache data in MySQL database
- Generate summary images with top countries by GDP
- Filter and sort countries by region, currency, and GDP
- Full CRUD operations

## Tech Stack

- **Framework**: Django 4.2.7
- **API**: Django REST Framework 3.14.0
- **Database**: MySQL (with PostgreSQL support)
- **Image Processing**: Pillow
- **HTTP Requests**: requests library

## Prerequisites

- Python 3.8+
- MySQL 5.7+ or PostgreSQL 12+
- pip (Python package manager)
- Virtual environment (recommended)

## Installation & Setup

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd country-exchange-api
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

#### For MySQL:

```bash
# Login to MySQL
mysql -u root -p

# Create database
CREATE DATABASE countries_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Create user (optional)
CREATE USER 'countries_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON countries_db.* TO 'countries_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### For PostgreSQL:

```bash
# Login to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE countries_db;

# Create user (optional)
CREATE USER countries_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE countries_db TO countries_user;
\q
```

### 5. Environment Configuration

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
SECRET_KEY=your-super-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# MySQL Configuration
DATABASE_URL=mysql://countries_user:your_password@localhost:3306/countries_db

# Or PostgreSQL
# DATABASE_URL=postgresql://countries_user:your_password@localhost:5432/countries_db

# External APIs (default values provided)
COUNTRIES_API_URL=https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies
EXCHANGE_API_URL=https://open.er-api.com/v6/latest/USD

# Cache directory
CACHE_DIR=cache
```

### 6. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 8. Run Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`

## API Endpoints

### 1. Refresh Countries Data

**POST** `/countries/refresh`

Fetches data from external APIs and updates the database.

```bash
curl -X POST http://localhost:8000/countries/refresh
```

**Response:**
```json
{
  "message": "Successfully refreshed 250 countries",
  "total_countries": 250,
  "last_refreshed_at": "2025-10-26T18:00:00Z"
}
```

### 2. Get All Countries

**GET** `/countries`

Retrieve all countries with optional filters and sorting.

**Query Parameters:**
- `region` - Filter by region (e.g., `?region=Africa`)
- `currency` - Filter by currency code (e.g., `?currency=NGN`)
- `sort` - Sort results: `gdp_desc`, `gdp_asc`, `population_desc`, `population_asc`, `name_asc`, `name_desc`

```bash
# Get all countries
curl http://localhost:8000/countries

# Filter by region
curl http://localhost:8000/countries?region=Africa

# Filter by currency
curl http://localhost:8000/countries?currency=USD

# Sort by GDP (descending)
curl http://localhost:8000/countries?sort=gdp_desc

# Combine filters
curl http://localhost:8000/countries?region=Africa&sort=gdp_desc
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Nigeria",
    "capital": "Abuja",
    "region": "Africa",
    "population": 206139589,
    "currency_code": "NGN",
    "exchange_rate": "1600.230000",
    "estimated_gdp": "25767448125.20",
    "flag_url": "https://flagcdn.com/ng.svg",
    "last_refreshed_at": "2025-10-26T18:00:00Z"
  }
]
```

### 3. Get Single Country

**GET** `/countries/:name`

Retrieve a specific country by name.

```bash
curl http://localhost:8000/countries/Nigeria
```

**Response:**
```json
{
  "id": 1,
  "name": "Nigeria",
  "capital": "Abuja",
  "region": "Africa",
  "population": 206139589,
  "currency_code": "NGN",
  "exchange_rate": "1600.230000",
  "estimated_gdp": "25767448125.20",
  "flag_url": "https://flagcdn.com/ng.svg",
  "last_refreshed_at": "2025-10-26T18:00:00Z"
}
```

### 4. Delete Country

**DELETE** `/countries/:name`

Delete a country record.

```bash
curl -X DELETE http://localhost:8000/countries/Nigeria
```

**Response:**
```json
{
  "message": "Country Nigeria deleted successfully"
}
```

### 5. Get Status

**GET** `/status`

Get total countries and last refresh timestamp.

```bash
curl http://localhost:8000/status
```

**Response:**
```json
{
  "total_countries": 250,
  "last_refreshed_at": "2025-10-26T18:00:00Z"
}
```

### 6. Get Summary Image

**GET** `/countries/image`

Retrieve the generated summary image showing top countries by GDP.

```bash
curl http://localhost:8000/countries/image --output summary.png
```

Returns a PNG image or:
```json
{
  "error": "Summary image not found"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "Validation failed",
  "details": {
    "currency_code": "is required"
  }
}
```

### 404 Not Found
```json
{
  "error": "Country not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

### 503 Service Unavailable
```json
{
  "error": "External data source unavailable",
  "details": "Could not fetch data from countries API"
}
```

## Deployment

### For Railway:

1. Install Railway CLI:
```bash
npm i -g @railway/cli
```

2. Login and initialize:
```bash
railway login
railway init
```

3. Add MySQL plugin in Railway dashboard

4. Set environment variables in Railway:
```bash
railway variables set SECRET_KEY=your-secret-key
railway variables set DEBUG=False
railway variables set ALLOWED_HOSTS=your-app.railway.app
```

5. Deploy:
```bash
railway up
```

6. Run migrations:
```bash
railway run python manage.py migrate
```

### For Heroku:

1. Install Heroku CLI and login:
```bash
heroku login
```

2. Create app:
```bash
heroku create your-app-name
```

3. Add MySQL addon:
```bash
heroku addons:create jawsdb:kitefin
```

4. Set environment variables:
```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False
```

5. Deploy:
```bash
git push heroku main
```

6. Run migrations:
```bash
heroku run python manage.py migrate
```

### For AWS (EC2):

See deployment documentation for detailed AWS setup instructions.

## Project Structure

```
country-exchange-api/
├── countries/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── services.py
│   ├── image_generator.py
│   ├── urls.py
│   ├── utils.py
│   ├── views.py
│   └── migrations/
├── countries_project/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── cache/
│   └── summary.png (generated)
├── .env
├── .env.example
├── .gitignore
├── manage.py
├── README.md
└── requirements.txt
```

## Testing

Run the development server and test endpoints:

```bash
# Test refresh
curl -X POST http://localhost:8000/countries/refresh

# Test get all
curl http://localhost:8000/countries

# Test filters
curl http://localhost:8000/countries?region=Africa&sort=gdp_desc

# Test status
curl http://localhost:8000/status
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | Required |
| `DEBUG` | Debug mode | `False` |
| `ALLOWED_HOSTS` | Comma-separated hosts | `localhost,127.0.0.1` |
| `DATABASE_URL` | Database connection string | MySQL localhost |
| `COUNTRIES_API_URL` | RestCountries API endpoint | RestCountries v2 |
| `EXCHANGE_API_URL` | Exchange rates API endpoint | Open Exchange Rates |
| `CACHE_DIR` | Directory for cached images | `cache` |

## Dependencies

See `requirements.txt` for full list:

- Django==4.2.7
- djangorestframework==3.14.0
- mysqlclient==2.2.0
- requests==2.31.0
- Pillow==10.1.0
- python-dotenv==1.0.0
- gunicorn==21.2.0
- whitenoise==6.6.0

## Troubleshooting

### MySQL Connection Issues

If you get MySQL connection errors:

```bash
# Ubuntu/Debian
sudo apt-get install python3-dev default-libmysqlclient-dev build-essential

# macOS
brew install mysql

# Then reinstall mysqlclient
pip install mysqlclient
```

### PostgreSQL Issues

If using PostgreSQL instead:

```bash
# Update requirements.txt to use psycopg2-binary
pip install psycopg2-binary

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

### Image Generation Issues

If image generation fails, ensure fonts are installed:

```bash
# Ubuntu/Debian
sudo apt-get install fonts-dejavu-core

# macOS
# Fonts are usually pre-installed
```

## License

This project is created for educational purposes.

## Author

Your Name - [your-email@example.com](mailto:your-email@example.com)

## Support

For issues and questions, please open an issue in the GitHub repository.
# fuzzy-fiesta
