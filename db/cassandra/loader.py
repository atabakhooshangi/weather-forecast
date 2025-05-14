import pandas as pd
from cassandra.cqlengine import connection
from cassandra.cqlengine.management import sync_table
from datetime import datetime
import os
from .schema import WeatherData

class CassandraLoader:
    def __init__(self):
        """Initialize Cassandra connection and sync the table schema."""
        # Get Cassandra connection details from environment variables
        CASSANDRA_HOST = os.getenv('CASSANDRA_HOST', 'localhost')
        CASSANDRA_PORT = int(os.getenv('CASSANDRA_PORT', 9042))
        CASSANDRA_USER = os.getenv('CASSANDRA_USER', 'cassandra')
        CASSANDRA_PASSWORD = os.getenv('CASSANDRA_PASSWORD', 'cassandra')
        
        # Connect to Cassandra
        connection.setup(
            [CASSANDRA_HOST],
            "weather_forecast",
            auth_provider={
                'username': CASSANDRA_USER,
                'password': CASSANDRA_PASSWORD
            },
            protocol_version=4
        )
        
        # Sync the table schema
        sync_table(WeatherData)
    
    def load_parquet_to_cassandra(self, parquet_file: str):
        """Load data from a parquet file into Cassandra."""
        print(f"📥 Loading data from {parquet_file} to Cassandra...")
        
        # Read parquet file
        df = pd.read_parquet(parquet_file)
        
        # Ensure timestamp is datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Get current time for metadata
        now = datetime.utcnow()
        
        # Prepare batch of records
        records = []
        for _, row in df.iterrows():
            record = WeatherData.create(
                station_id=row['station_id'],
                timestamp=row['timestamp'],
                air_temperature=float(row['air_temperature']),
                dew_point=float(row['dew_point']),
                relative_humidity=float(row['relative_humidity']),
                precipitation=float(row['precipitation']),
                wind_speed=float(row['wind_speed']),
                pressure=float(row['pressure']),
                condition_group=row['condition_group'],
                created_at=now,
                updated_at=now
            )
            records.append(record)
        
        # Batch insert records
        WeatherData.batch_create(records)
        print(f"✅ Successfully loaded {len(records)} records to Cassandra")
    
    def load_all_parquet_files(self, directory: str):
        """Load all parquet files from a directory into Cassandra."""
        parquet_files = [f for f in os.listdir(directory) if f.endswith('.parquet')]
        
        for file in parquet_files:
            file_path = os.path.join(directory, file)
            self.load_parquet_to_cassandra(file_path)
        
        print(f"✅ Completed loading {len(parquet_files)} parquet files to Cassandra")

if __name__ == "__main__":
    # Example usage
    loader = CassandraLoader()
    loader.load_all_parquet_files("../station_datasets") 