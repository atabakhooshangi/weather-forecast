# Weather Forecast System

A comprehensive weather forecasting system that includes data collection, processing, model training, and a web interface.

## System Components

- **Frontend**: Vue.js web application
- **Backend**: FastAPI service
- **Database**: Cassandra for weather data storage
- **Cache**: Redis for caching
- **Model Service**: Python service for ETL and model operations

## Prerequisites

- Docker and Docker Compose
- Git

## Getting Started

1. Clone the repository:
```bash
git clone <repository-url>
cd weather-forecast
```

2. Start all services:
```bash
docker-compose up -d
```

This will start all services with the following container names:
- Frontend: `weather-frontend`
- Backend: `weather-backend`
- Redis: `weather-redis`
- Cassandra: `weather-cassandra`
- Model Service: `weather-model`

## Accessing Services

### Frontend
- URL: http://localhost:5173
- Container: `weather-frontend`
- Access logs: `docker logs weather-frontend`

### Backend API
- URL: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Container: `weather-backend`
- Access logs: `docker logs weather-backend`

### Redis
- Port: 6381
- Container: `weather-redis`
- Access CLI: `docker exec -it weather-redis redis-cli -p 6381`

### Cassandra
- Port: 9042
- Container: `weather-cassandra`
- Access CQL Shell: `docker exec -it weather-cassandra cqlsh -u cassandra -p cassandra`

## Running ETL Pipeline

The ETL pipeline can be run manually through the model service container:

1. Access the model container:
```bash
docker exec -it weather-model bash
```

2. Run the ETL pipeline:
```bash
# Run without loading to Cassandra
poetry run python model/etl/etl.py

# Run with loading to Cassandra
poetry run python model/etl/etl.py --cassandra
```

## Checking Cassandra Data

To check the data loaded into Cassandra:

1. Access Cassandra CQL shell:
```bash
docker exec -it weather-cassandra cqlsh -u cassandra -p cassandra
```

2. Check the data:
```bash
 cqlsh -e "SELECT count(*) FROM weather_forecast.weather_data;"
```



## Running Model Training

To run model training scripts:

1. Access the model container:
```bash
docker exec -it weather-model bash
```

2. Run the desired model script:
```bash
# For temperature model
poetry run python model/temperature_model.py

# For weather condition model
poetry run python model/weather_condition_model.py

# For precipitation model
poetry run python model/precipation.py
```

## Stopping Services

To stop all services:
```bash
docker-compose down
```

To stop and remove all data volumes:
```bash
docker-compose down -v
```

## Troubleshooting

1. If services fail to start, check logs:
```bash
docker-compose logs
```

2. To restart a specific service:
```bash
docker-compose restart <service-name>
```

3. To rebuild a specific service:
```bash
docker-compose up -d --build <service-name>
```

## Development

- Frontend code is in the `frontend/` directory
- Backend code is in the `backend/` directory
- Model and ETL code is in the `model/` directory
- Database initialization scripts are in the `db/` directory