# train_temperature_model.py

import pandas as pd
import numpy as np
import joblib
import os

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # disable GPU
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Bidirectional, Dropout

# --- Settings ---
WINDOW_SIZE = 24
EPOCHS = 30
BATCH_SIZE = 64

# --- Load dataset ---
raw_df = pd.read_parquet('../etl/station_datasets/full_concat_data_cleaned.parquet')
raw_df['timestamp'] = pd.to_datetime(raw_df['timestamp'])
raw_df = raw_df.sort_values(['station_id', 'timestamp']).reset_index(drop=True)

# --- Features ---
features = [
    'air_temperature', 'dew_point', 'relative_humidity', 'precipitation',
    'wind_speed', 'wind_direction', 'wdir_sin', 'wdir_cos',
    'pressure', 'hour_sin', 'hour_cos', 'dayofyear_sin', 'dayofyear_cos'
]

target = 'air_temperature'

# --- Scaling inputs ---
if os.path.exists('models_scalers/scaler_X_latest.pkl'):
    scaler_X = joblib.load('models_scalers/scaler_X_latest.pkl')

else:
    scaler_X = MinMaxScaler()
    X_scaled = scaler_X.fit_transform(raw_df[features])
    joblib.dump(scaler_X, 'models_scalers/scaler_X_latest.pkl')


# --- Create sequences ---
def create_sequences(X, y, window_size=24):
    Xs, ys = [], []
    for i in range(window_size, len(X)):
        Xs.append(X[i - window_size:i])
        ys.append(y[i])
    return np.array(Xs), np.array(ys)


X_temp, y_temp = create_sequences(X_scaled, raw_df[target].values)

# --- Train/Test Split ---
X_train, X_test, y_train, y_test = train_test_split(X_temp, y_temp, test_size=0.2, random_state=42)

# --- Build Temperature Model ---
model = Sequential()
model.add(Bidirectional(LSTM(128, return_sequences=True), input_shape=(X_train.shape[1], X_train.shape[2])))
model.add(Dropout(0.2))
model.add(Bidirectional(LSTM(64)))
model.add(Dropout(0.2))
model.add(Dense(1))

model.compile(optimizer='adam', loss='mse', metrics=['mae'])

# --- Train ---
history = model.fit(
    X_train, y_train,
    validation_data=(X_test, y_test),
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    verbose=2
)

# --- Save Model ---
model.save('lstm_temperature_latest.keras')
print("✅ Temperature model saved as 'lstm_temperature_latest.keras'")