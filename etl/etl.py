import os
import glob
import pandas as pd
import numpy as np
from meteostat import Point, Hourly
from datetime import datetime
import requests
from PIL import Image
from io import BytesIO

class WeatherETLPipeline:
    WEATHER_GROUP_MAPPING = {
        1: "Clear", 2: "Clear",
        3: "Cloudy", 4: "Cloudy",
        5: "Fog", 6: "Fog",
        7: "Rainy", 8: "Rainy", 9: "Rainy", 10: "Rainy", 11: "Rainy",
        12: "Rainy", 13: "Rainy",
        14: "Snowy", 15: "Snowy", 16: "Snowy",
        17: "Rainy", 18: "Rainy",
        19: "Snowy", 20: "Snowy",
        21: "Snowy", 22: "Snowy",
        23: "Thunderstorm", 24: "Thunderstorm", 25: "Thunderstorm", 26: "Thunderstorm",
        27: "Storm"
    }

    def __init__(self, stations_csv, output_dir, start_date, end_date=datetime.today(), validate_satellite=True):
        self.stations_csv = stations_csv
        self.output_dir = output_dir
        self.start_date = start_date
        self.end_date = end_date
        self.validate_satellite = validate_satellite
        os.makedirs(self.output_dir, exist_ok=True)

    def map_weather_group(self, code):
        if pd.isna(code):
            return "Unknown"
        return self.WEATHER_GROUP_MAPPING.get(int(code), "Unknown")

    def fetch_and_clean_station(self, station):
        print(f"Fetching: {station['name']}...")
        pt = Point(station["latitude"], station["longitude"])

        df = Hourly(pt, self.start_date, self.end_date).fetch().reset_index()
        if df.empty:
            print(f"⚠️ No data found for {station['name']}")
            return None

        df = df.rename(columns={
            "time": "timestamp",
            "temp": "air_temperature",
            "dwpt": "dew_point",
            "rhum": "relative_humidity",
            "prcp": "precipitation",
            "wdir": "wind_direction",
            "wspd": "wind_speed",
            "pres": "pressure",
            "coco": "condition_code"
        })

        df["condition_group"] = df["condition_code"].apply(self.map_weather_group)
        df["station_id"] = station["id"]

        df.dropna(subset=[
            "air_temperature", "dew_point", "relative_humidity",
            "precipitation", "wind_speed", "pressure", "condition_group"
        ], inplace=True)

        if df.empty:
            print(f"⚠️ All rows dropped after cleaning for {station['name']}")
            return None

        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["hour"] = df["timestamp"].dt.hour
        df["dayofyear"] = df["timestamp"].dt.dayofyear

        df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
        df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
        df["dayofyear_sin"] = np.sin(2 * np.pi * df["dayofyear"] / 365)
        df["dayofyear_cos"] = np.cos(2 * np.pi * df["dayofyear"] / 365)

        df["wind_direction"] = df["wind_direction"].fillna(0)
        df["wdir_rad"] = np.deg2rad(df["wind_direction"])
        df["wdir_sin"] = np.sin(df["wdir_rad"])
        df["wdir_cos"] = np.cos(df["wdir_rad"])

        return df

    def validate_with_satellite(self, df, lat, lon):
        latest_time = df['timestamp'].max().strftime('%Y-%m-%d')
        url = f"https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi?" \
              f"service=WMS&request=GetMap&layers=MODIS_Terra_CorrectedReflectance_TrueColor" \
              f"&styles=&format=image/png&transparent=true&version=1.1.1" \
              f"&height=256&width=256&bbox={lon-1},{lat-1},{lon+1},{lat+1}&srs=EPSG:4326" \
              f"&time={latest_time}"
        try:
            response = requests.get(url, timeout=10)
            img = Image.open(BytesIO(response.content))
            gray = img.convert('L')
            brightness = np.mean(np.array(gray))

            recent_condition = df[df['timestamp'] == df['timestamp'].max()]['condition_group'].values[0]
            print(f"🔍 {df['station_id'].iloc[0]} Satellite brightness: {brightness:.1f} vs condition: {recent_condition}")

            if recent_condition == 'Clear' and brightness < 100:
                print(f"⚠️ Mismatch: CLEAR reported, but satellite looks CLOUDY.")
            elif recent_condition == 'Cloudy' and brightness > 130:
                print(f"⚠️ Mismatch: CLOUDY reported, but satellite looks CLEAR.")
            else:
                print(f"✅ Satellite validation aligned.")
        except Exception as e:
            print(f"⚠️ Satellite validation failed: {e}")

    def run(self):
        stations_list = pd.read_csv(self.stations_csv).to_dict(orient="records")
        all_dfs = []

        for station in stations_list:
            df = self.fetch_and_clean_station(station)
            if df is None:
                continue

            if self.validate_satellite:
                self.validate_with_satellite(df, station["latitude"], station["longitude"])

            name = station["name"].replace(" ", "_").replace("/", "_").replace("__", "_").lower()
            path = os.path.join(self.output_dir, f"{name}_data.parquet")
            df.to_parquet(path, index=False)
            all_dfs.append(df)

        if all_dfs:
            merged_df = pd.concat(all_dfs, ignore_index=True)
            merged_path = os.path.join(self.output_dir, "full_concat_data_cleaned.parquet")
            merged_df.to_parquet(merged_path, index=False)
            print(f"✅ Merged dataset shape: {merged_df.shape}")
            print(f"✅ Cleaned full dataset saved to {merged_path}")
        else:
            print("❌ No station data processed.")


if __name__ == "__main__":
    pipeline = WeatherETLPipeline(
        stations_csv="stations.csv",
        output_dir="station_datasets",
        start_date=datetime(2024, 5, 1),
        end_date=datetime.today(),
        validate_satellite=True  # Set to False if you want to skip satellite check
    )
    pipeline.run()
