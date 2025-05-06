# services/predictor.py

import pandas as pd
import numpy as np
import os

from backend.schemas import ForcastOutputBase

# Disable GPU
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

# Optional: Turn off oneDNN optimizations (for perfect reproducibility)
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

from datetime import datetime, timedelta
from meteostat import Point, Hourly
import joblib
import tensorflow as tf
from redis.asyncio import Redis
from backend.services.station import StationLookup

class AsyncWeatherPredictor:
    def __init__(self, redis: Redis):
        self.redis = redis
        self.features = [
            'air_temperature', 'dew_point', 'relative_humidity', 'precipitation',
            'wind_speed', 'wind_direction', 'wdir_sin', 'wdir_cos',
            'pressure', 'hour_sin', 'hour_cos', 'dayofyear_sin', 'dayofyear_cos'
        ]
        self.scaler_X = joblib.load('models/scaler_X_latest.pkl')
        self.label_encoder = joblib.load('models/label_encoder_condition.pkl')
        self.model_temp = tf.keras.models.load_model('models/lstm_temperature_latest.keras')
        self.model_cond = tf.keras.models.load_model('models/lstm_condition_classifier_latest.keras')

    async def fetch_recent_data(self, station_name: str, latitude: float, longitude: float, hours_back=24):
        cache_key = f"station_cache:{station_name.lower().replace(' ', '_')}"
        cached_data = await self.redis.get(cache_key)

        if cached_data:
            df = pd.read_json(cached_data.decode('utf-8'))
        else:
            pt = Point(latitude, longitude)
            end_date = datetime.now()
            start_date = end_date - timedelta(hours=hours_back)

            df = Hourly(pt, start_date, end_date).fetch().reset_index()

            if df.empty or len(df) < 24:
                raise ValueError(f"❌ Not enough data fetched ({len(df)}) for {station_name}")

            df = df.rename(columns={
                "time": "timestamp",
                "temp": "air_temperature",
                "dwpt": "dew_point",
                "rhum": "relative_humidity",
                "prcp": "precipitation",
                "wdir": "wind_direction",
                "wspd": "wind_speed",
                "pres": "pressure"
            })

            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            df['dayofyear'] = df['timestamp'].dt.dayofyear
            df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
            df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
            df['dayofyear_sin'] = np.sin(2 * np.pi * df['dayofyear'] / 365)
            df['dayofyear_cos'] = np.cos(2 * np.pi * df['dayofyear'] / 365)
            df['wdir_sin'] = np.sin(np.deg2rad(df['wind_direction']))
            df['wdir_cos'] = np.cos(np.deg2rad(df['wind_direction']))

            df = df[self.features]
            await self.redis.set(cache_key, df.to_json(), ex=3600)

        return df.tail(24)

    async def predict(self, station_id: str, predict_hours: int = 72):
        station = StationLookup.get_station(station_id)
        recent_data = await self.fetch_recent_data(station.name, station.latitude, station.longitude)

        predicted_results = []
        history = recent_data.copy()
        base_timestamp = datetime.now()

        for step in range(predict_hours):
            X_scaled = self.scaler_X.transform(history)
            X_scaled = np.expand_dims(X_scaled, axis=0)

            temp_pred = self.model_temp.predict(X_scaled)[0][0]
            cond_probs = self.model_cond.predict(X_scaled)[0]
            cond_pred = self.label_encoder.inverse_transform([np.argmax(cond_probs)])[0]


            prediction = ForcastOutputBase(
                temperature=f"{round(temp_pred,2)}",
                condition=cond_pred,
                timestamp=(base_timestamp + timedelta(hours=step)).isoformat(),
                type="hourly"
            )
            predicted_results.append(prediction)

            # Update history
            new_row = history.iloc[-1].copy()
            new_row['air_temperature'] = temp_pred
            history = pd.concat([history, pd.DataFrame([new_row])], ignore_index=True)
            history = history.iloc[1:]  # keep last 24h

        return predicted_results
