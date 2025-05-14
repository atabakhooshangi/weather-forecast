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

        # Temperature models & scalers
        self.scaler_X_temp = joblib.load('models/temperature/scaler_X_latest2.pkl')
        self.scaler_y_temp = joblib.load('models/temperature/scaler_y_temperature_latest2.pkl')
        self.model_seq2seq_temp = tf.keras.models.load_model('models/temperature/seq2seq_temperature_forecast_optimized.keras')

        # Humidity models & scalers
        self.scaler_X_rh = joblib.load('models/relative_humidity/scaler_x_relative_humidity.pkl')
        self.scaler_y_rh = joblib.load('models/relative_humidity/scaler_y_relative_humidity.pkl')
        self.model_seq2seq_rh = tf.keras.models.load_model('models/relative_humidity/seq2seq_relative_humidity_forecast.keras')

        # Condition model
        self.model_cond = tf.keras.models.load_model('models/condition/lstm_condition_classifier_latest.keras')
        self.label_encoder = joblib.load('models/condition/label_encoder_condition.pkl')

        # Config
        self.history_steps = 96
        self.future_block = 10  # Predict 10 hours per loop (rolling)

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
        history_features = history[self.features]

        predicted_results = []
        total_predicted_hours = 0

        while total_predicted_hours < predict_hours:
            # Scale inputs
            X_input_temp = self.scaler_X_temp.transform(history_features)
            X_input_rh = self.scaler_X_rh.transform(history_features)

            X_input_temp = np.expand_dims(X_input_temp, axis=0)
            X_input_rh = np.expand_dims(X_input_rh, axis=0)

            # Predict temperature block
            y_pred_temp_scaled = self.model_seq2seq_temp.predict(X_input_temp, verbose=0)[0]
            y_pred_temp = self.scaler_y_temp.inverse_transform(y_pred_temp_scaled).flatten()

            # Predict humidity block
            y_pred_rh_scaled = self.model_seq2seq_rh.predict(X_input_rh, verbose=0)[0]
            y_pred_rh = self.scaler_y_rh.inverse_transform(y_pred_rh_scaled).flatten()

            # How many hours to process this round
            hours_to_add = min(self.future_block, predict_hours - total_predicted_hours)

            for i in range(hours_to_add):
                # Predict condition (we can reuse the same X_input_temp)
                cond_probs = self.model_cond.predict(X_input_temp, verbose=0)[0]
                cond_pred = self.label_encoder.inverse_transform([np.argmax(cond_probs)])[0]

                prediction = ForcastOutputBase(
                    temperature=f"{round(y_pred_temp[i], 2)}",
                    humidity=f"{round(y_pred_rh[i], 2)}",
                    precipitation="0",  # Placeholder if needed
                    condition=cond_pred,
                    timestamp=(base_timestamp + timedelta(hours=total_predicted_hours + i)).replace(minute=0, second=0, microsecond=0).isoformat(),
                    type="hourly"
                )
                predicted_results.append(prediction)

            # Update history for next round
            for temp, rh in zip(y_pred_temp[:hours_to_add], y_pred_rh[:hours_to_add]):
                new_row = history_features.iloc[-1].copy()
                new_row['air_temperature'] = temp
                new_row['relative_humidity'] = rh
                history_features = pd.concat([history_features, pd.DataFrame([new_row])], ignore_index=True)
                history_features = history_features.iloc[1:]  # Keep last 96

            total_predicted_hours += hours_to_add

        return predicted_results
