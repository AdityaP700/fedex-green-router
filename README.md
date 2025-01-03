# FedEx Green Router

An intelligent routing system that optimizes delivery routes considering environmental factors and green zones.

## Features

- Optimized route planning considering environmental impact
- Real-time air quality monitoring
- Green zone identification and routing
- Integration with multiple mapping services (TomTom, MapMyIndia)
- Weather condition monitoring
- MongoDB integration for data persistence
- Redis caching for improved performance

## Prerequisites

- Python 3.8 or higher
- MongoDB
- Redis
- API Keys for:
  - TomTom Maps
  - OpenWeather
  - AQICN (Air Quality)
  - MapMyIndia

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/fedex-green-router.git
cd fedex-green-router
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Fill in your API keys and configuration:
```
MONGODB_URI=your_mongodb_connection_string
REDIS_URL=redis://localhost:6379

TOMTOM_API_KEY=your_tomtom_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
AQICN_API_KEY=your_aqicn_api_key
MAPMYINDIA_API_KEY=your_mapmyindia_api_key

SECRET_KEY=your_secret_key
API_KEY=your_api_key
```

## Running the Application

1. Start the FastAPI server:
```bash
uvicorn main:app --reload
```

2. Access the API documentation:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

- `POST /route/optimize`: Calculate optimized route considering environmental factors
- `GET /air-quality/{location}`: Get air quality data for a specific location
- `GET /weather/{location}`: Get weather data for a specific location
- `GET /green-zones/{city}`: Get green zones in a specific city

## Environment Variables

| Variable | Description |
|----------|-------------|
| `MONGODB_URI` | MongoDB connection string |
| `REDIS_URL` | Redis server URL |
| `TOMTOM_API_KEY` | TomTom Maps API key |
| `OPENWEATHER_API_KEY` | OpenWeather API key |
| `AQICN_API_KEY` | Air Quality API key |
| `MAPMYINDIA_API_KEY` | MapMyIndia API key |
| `SECRET_KEY` | Application secret key |
| `API_KEY` | API authentication key |

## Security

- API key authentication required for all endpoints
- Environment variables must be properly secured
- Never commit `.env` file to version control

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 