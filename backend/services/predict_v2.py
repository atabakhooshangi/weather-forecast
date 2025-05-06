import pandas as pd
import numpy as np
import os

# Environment configs
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

from datetime import datetime, timedelta
from meteostat import Point, Hourly
import joblib
import tensorflow as tf
from redis.asyncio import Redis
from backend.services.station import StationLookup
from backend.schemas import ForcastOutputBase

class AsyncWeatherPredictor:
    def __init__(self, redis: Redis):
        self.redis = redis
        self.features = [
            'air_temperature', 'dew_point', 'relative_humidity', 'precipitation',
            'wind_speed', 'wind_direction', 'wdir_sin', 'wdir_cos',
            'pressure', 'hour_sin', 'hour_cos', 'dayofyear_sin', 'dayofyear_cos'
        ]
        # Load scalers and models
        self.scaler_X = joblib.load('models/temperature/scaler_X_latest2.pkl')
        self.scaler_y = joblib.load('models/temperature/scaler_y_temperature_latest2.pkl')
        self.model_seq2seq_temp = tf.keras.models.load_model('models/temperature/seq2seq_temperature_forecast_optimized.keras')
        self.model_cond = tf.keras.models.load_model('models/condition/lstm_condition_classifier_latest.keras')
        self.label_encoder = joblib.load('models/condition/label_encoder_condition.pkl')

        # Config
        self.history_steps = 96
        self.future_block = 10  # Predict 10 hours per step (rolling)

    async def fetch_recent_data(self, station_name: str, latitude: float, longitude: float, hours_back: int = 96):
        cache_key = f"station_cache:{station_name.lower().replace(' ', '_')}"
        cached_data = await self.redis.get(cache_key)

        if cached_data:
            df = pd.read_json(cached_data.decode('utf-8'))
        else:
            pt = Point(latitude, longitude)
            end_date = datetime.now()
            start_date = end_date - timedelta(hours=hours_back)

            df = Hourly(pt, start_date, end_date).fetch().reset_index()

            if df.empty or len(df) < hours_back:
                raise ValueError(f"❌ Not enough data fetched ({len(df)}) for {station_name}")

            df = df.rename(columns={
                "time": "timestamp",
                "temp": "air_temperature",
                "dwpt": "dew_point",
                "rhum": "relative_humidity",
                "prcp": "precipitation",
                "wspd": "wind_speed",
                "wdir": "wind_direction",
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
            await self.redis.set(cache_key, df.to_json(), ex=3600)

        return df.tail(self.history_steps)

    async def predict(self, station_id: str, predict_hours: int = 72):
        station = StationLookup.get_station(station_id)
        history_df = await self.fetch_recent_data(station.name, station.latitude, station.longitude)

        history = history_df.copy()
        last_history_timestamp = history_df['timestamp'].max()
        base_timestamp = last_history_timestamp + timedelta(hours=1)

        # Only features
        history = history[self.features]

        predicted_results = []
        total_predicted_hours = 0

        while total_predicted_hours < predict_hours:
            # Scale
            X_input = self.scaler_X.transform(history)
            X_input = np.expand_dims(X_input, axis=0)

            # Predict temperature block
            y_pred_scaled = self.model_seq2seq_temp.predict(X_input, verbose=0)[0]
            y_pred_temp = self.scaler_y.inverse_transform(y_pred_scaled).flatten()

            # How many hours to add now
            hours_to_add = min(self.future_block, predict_hours - total_predicted_hours)

            for i in range(hours_to_add):
                # Predict condition using current history
                cond_probs = self.model_cond.predict(X_input, verbose=0)[0]
                cond_pred = self.label_encoder.inverse_transform([np.argmax(cond_probs)])[0]

                prediction = ForcastOutputBase(
                    temperature=f"{round(y_pred_temp[i],2)}",
                    condition=cond_pred,
                    timestamp=(base_timestamp + timedelta(hours=total_predicted_hours+i)).isoformat(),
                    type="hourly"
                )
                predicted_results.append(prediction)

            # Update history for next block
            for temp in y_pred_temp[:hours_to_add]:
                new_row = history.iloc[-1].copy()
                new_row['air_temperature'] = temp
                history = pd.concat([history, pd.DataFrame([new_row])], ignore_index=True)
                history = history.iloc[1:]  # Keep latest 96 rows

            total_predicted_hours += hours_to_add

        return predicted_results
