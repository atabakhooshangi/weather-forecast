FROM python:3.11.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy poetry files from root
COPY pyproject.toml poetry.lock ./

# Configure Poetry to create virtual environment in the project directory
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-interaction --no-ansi --no-root

# Copy model directory contents
COPY model/ /app/model/

# Set environment variables
ENV PYTHONPATH=/app

# The container will keep running but won't execute any commands automatically
CMD ["tail", "-f", "/dev/null"] 