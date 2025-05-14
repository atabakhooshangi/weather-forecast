from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
import os
from datetime import datetime

def init_cassandra():
    """Initialize Cassandra database with required keyspace and table."""
    
    # Get Cassandra connection details from environment variables
    CASSANDRA_HOST = os.getenv('CASSANDRA_HOST', 'localhost')
    CASSANDRA_PORT = int(os.getenv('CASSANDRA_PORT', 9042))
    CASSANDRA_USER = os.getenv('CASSANDRA_USER', 'cassandra')
    CASSANDRA_PASSWORD = os.getenv('CASSANDRA_PASSWORD', 'cassandra')
    
    # Connect to Cassandra
    auth_provider = PlainTextAuthProvider(username=CASSANDRA_USER, password=CASSANDRA_PASSWORD)
    cluster = Cluster([CASSANDRA_HOST], port=CASSANDRA_PORT, auth_provider=auth_provider)
    session = cluster.connect()
    
    # Create keyspace if not exists
    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS weather_forecast
        WITH replication = {
            'class': 'SimpleStrategy',
            'replication_factor': 1
        }
    """)
    
    # Use the keyspace
    session.set_keyspace('weather_forecast')
    
    # Create table if not exists
    session.execute("""
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
        ) WITH CLUSTERING ORDER BY (timestamp DESC)
    """)
    
    # Create indexes for common queries
    session.execute("""
        CREATE INDEX IF NOT EXISTS ON weather_forecast.weather_data (condition_group)
    """)
    
    print("✅ Cassandra database initialized successfully!")
    session.shutdown()
    cluster.shutdown()

if __name__ == "__main__":
    init_cassandra() 