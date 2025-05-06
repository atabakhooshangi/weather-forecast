FROM python:3.11.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy poetry files
COPY pyproject.toml poetry.lock ./

# Configure Poetry to create virtual environment in the project directory
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Create the necessary directories
RUN mkdir -p /app/backend/api
RUN mkdir -p /app/backend/config
RUN mkdir -p /app/backend/schemas
RUN mkdir -p /app/backend/services
RUN mkdir -p /app/models/temperature
RUN mkdir -p /app/models/condition
RUN mkdir -p /app/models/precipation
RUN mkdir -p /app/models/relative_humidity

# Copy backend files
COPY backend/main.py /app/backend/
COPY backend/api/ /app/backend/api/
COPY backend/config/ /app/backend/config/
COPY backend/schemas/ /app/backend/schemas/
COPY backend/services/ /app/backend/services/

# Copy models
COPY backend/models/temperature/ /app/models/temperature/
COPY backend/models/condition/ /app/models/condition/
COPY backend/models/precipation/ /app/models/precipation/
COPY backend/models/relative_humidity/ /app/models/relative_humidity/

# Add the current directory to Python path
ENV PYTHONPATH=/app

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["poetry", "run", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"] 