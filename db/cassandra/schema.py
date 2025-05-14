from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model

class WeatherData(Model):
    """Cassandra model for storing weather data in a time-series format."""
    __keyspace__ = 'weather_forecast'
    __table_name__ = 'weather_data'
    
    # Partition key: station_id for data locality
    # Clustering key: timestamp for time-series queries
    station_id = columns.Text(partition_key=True)
    timestamp = columns.DateTime(primary_key=True, clustering_order="DESC")
    
    # Weather metrics
    air_temperature = columns.Float()
    dew_point = columns.Float()
    relative_humidity = columns.Float()
    precipitation = columns.Float()
    wind_speed = columns.Float()
    pressure = columns.Float()
    condition_group = columns.Text()
    
    # Metadata
    created_at = columns.DateTime()
    updated_at = columns.DateTime() 