# Weather Forecast Application

A full-stack weather forecasting application that provides detailed weather predictions for various stations. The application uses machine learning models to predict temperature, precipitation, humidity, and weather conditions.

## Features

- Real-time weather forecasts for multiple stations
- 12-hour detailed forecast view
- Daily forecast overview
- Temperature, precipitation, and humidity predictions
- Weather condition predictions
- Caching with Redis for improved performance

## Prerequisites

- Docker and Docker Compose installed
- At least 4GB of RAM (for ML model inference)
- Python 3.11.9 (if running locally)
- Node.js 20 (if running frontend locally)

## Project Structure

```
weather-forecast/
├── backend/              # FastAPI backend
│   ├── api/             # API endpoints and dependencies
│   ├── config/          # Configuration files
│   ├── models/          # ML model files
│   ├── schemas/         # Pydantic models
│   └── services/        # Business logic
├── frontend/            # Vue.js frontend
│   ├── src/            # Source files
│   ├── public/         # Static assets
│   └── components/     # Vue components
└── docker-compose.yml   # Docker configuration
```

## Running with Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd weather-forecast
   ```

2. Build and start the containers:
   ```bash
   docker-compose up --build
   ```

3. Access the application:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/api/docs

## Running Locally

### Backend Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install poetry
   poetry install
   ```

3. Start Redis:
   ```bash
   docker run -d -p 6381:6381 redis:7-alpine redis-server --port 6381
   ```

4. Run the backend:
   ```bash
   cd backend
   poetry run uvicorn main:app --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

## Environment Variables

### Backend
- `REDIS_HOST`: Redis host (default: redis)
- `REDIS_PORT`: Redis port (default: 6381)
- `REDIS_DB`: Redis database number (default: 0)
- `REDIS_USERNAME`: Redis username (optional)
- `REDIS_PASSWORD`: Redis password (optional)

### Frontend
- `VITE_API_URL`: Backend API URL (default: http://localhost:8000)

## API Endpoints

- `GET /forecast/?station_id={id}`: Get weather forecast for a specific station
  - Parameters:
    - `station_id`: Station identifier (required)

## Available Stations

The application supports the following weather stations:

| Station ID | Station Name | Latitude | Longitude |
|------------|--------------|----------|-----------|
| 12756      | Szecseny     | 48.1167  | 19.5167   |
| 12840      | Budapest Met Center | 47.5167 | 19.0333 |
| 12882      | Debrecen     | 47.4833  | 21.6      |
| ...        | ...          | ...      | ...       |

(Full list available in the application)

## Troubleshooting

1. If you encounter port conflicts:
   - Check if port 8000 (backend) or 5173 (frontend) is already in use
   - Modify the ports in docker-compose.yml if needed

2. If Redis connection fails:
   - Ensure Redis is running on port 6381
   - Check if the Redis container is healthy

3. If model loading fails:
   - Verify that all model files are present in the correct directories
   - Check file permissions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license information here]