#!/bin/bash

# Wait for Cassandra to be ready
echo "Waiting for Cassandra to be ready..."
until cqlsh -u cassandra -p cassandra -e "describe keyspaces" > /dev/null 2>&1; do
    echo "Cassandra is not ready yet... waiting"
    sleep 2
done

echo "Cassandra is ready! Initializing database..."

# Create keyspace and table
cqlsh -u cassandra -p cassandra -e "
CREATE KEYSPACE IF NOT EXISTS weather_forecast
WITH replication = {
    'class': 'SimpleStrategy',
    'replication_factor': 1
};

USE weather_forecast;

CREATE TABLE IF NOT EXISTS weather_data (
    station_id text,
    timestamp timestamp,
    air_temperature float,
    dew_point float,
    relative_humidity float,
    precipitation float,
    wind_speed float,
    pressure float,
    condition_group text,
    created_at timestamp,
    updated_at timestamp,
    PRIMARY KEY (station_id, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);

CREATE INDEX IF NOT EXISTS ON weather_forecast.weather_data (condition_group);
"

echo "✅ Cassandra initialization completed!" 