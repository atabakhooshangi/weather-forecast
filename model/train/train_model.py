import pandas as pd
import numpy as np
import joblib
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # Disable GPU
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, LSTM, Dense, RepeatVector, TimeDistributed, Dropout
from tensorflow.keras.callbacks import ReduceLROnPlateau, EarlyStopping
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

# --- Load Dataset ---
raw_df = pd.read_parquet('./station_datasets/full_concat_data_cleaned.parquet')
raw_df['timestamp'] = pd.to_datetime(raw_df['timestamp'])
raw_df = raw_df.sort_values(['station_id', 'timestamp']).reset_index(drop=True)

# --- Features ---
features = [
    'air_temperature', 'dew_point', 'relative_humidity', 'precipitation',
    'wind_speed', 'wind_direction', 'wdir_sin', 'wdir_cos',
    'pressure', 'hour_sin', 'hour_cos', 'dayofyear_sin', 'dayofyear_cos'
]

# --- Target ---
target_feature = 'relative_humidity'

# --- Scale Features ---
scaler_X = MinMaxScaler()
X_scaled = scaler_X.fit_transform(raw_df[features])
joblib.dump(scaler_X, 'scaler_x_relative_humidity.pkl')

scaler_y = MinMaxScaler()
y_scaled = scaler_y.fit_transform(raw_df[[target_feature]])
joblib.dump(scaler_y, 'scaler_y_relative_humidity.pkl')

# --- Create Sequences ---
HISTORY_STEPS = 96   # past 4 days (96h)
FUTURE_STEPS  = 24   # predict 24h

X_encoder, y_decoder = [], []

for i in range(HISTORY_STEPS, len(X_scaled) - FUTURE_STEPS):
    X_encoder.append(X_scaled[i-HISTORY_STEPS:i])
    y_decoder.append(y_scaled[i:i+FUTURE_STEPS].flatten())

X_encoder = np.array(X_encoder)
y_decoder = np.array(y_decoder)

# --- Train/Test Split ---
X_train, X_test, y_train, y_test = train_test_split(X_encoder, y_decoder, test_size=0.2, random_state=42)

# --- Build Optimized Seq2Seq Model ---

# Encoder
encoder_inputs = Input(shape=(HISTORY_STEPS, len(features)))
encoder_l1 = LSTM(128, return_sequences=True)(encoder_inputs)
encoder_l1 = Dropout(0.2)(encoder_l1)
encoder_l2 = LSTM(64, return_state=True)
encoder_outputs, state_h, state_c = encoder_l2(encoder_l1)

# Decoder
decoder_inputs = RepeatVector(FUTURE_STEPS)(state_h)
decoder_l1 = LSTM(64, return_sequences=True)(decoder_inputs, initial_state=[state_h, state_c])
decoder_l1 = Dropout(0.2)(decoder_l1)

decoder_outputs = TimeDistributed(Dense(1))(decoder_l1)

# Build Model
model = Model(encoder_inputs, decoder_outputs)

model.compile(optimizer='adam', loss='mae', metrics=['mse'])
model.summary()

# --- Callbacks ---
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=1e-5, verbose=1)
early_stop = EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True, verbose=1)

# --- Train ---
history = model.fit(
    X_train, y_train.reshape(y_train.shape[0], FUTURE_STEPS, 1),
    validation_data=(X_test, y_test.reshape(y_test.shape[0], FUTURE_STEPS, 1)),
    epochs=80,
    batch_size=32,
    callbacks=[reduce_lr, early_stop],
    verbose=2
)

# --- Save Model ---
model.save('seq2seq_relative_humidity_forecast.keras')
print("✅ Seq2Seq optimized2 model saved!")


import time

time.sleep(10)


# --- Load Dataset ---
raw_df = pd.read_parquet('./station_datasets/full_concat_data_cleaned.parquet')
raw_df['timestamp'] = pd.to_datetime(raw_df['timestamp'])
raw_df = raw_df.sort_values(['station_id', 'timestamp']).reset_index(drop=True)

# --- Features ---
features = [
    'air_temperature', 'dew_point', 'relative_humidity', 'precipitation',
    'wind_speed', 'wind_direction', 'wdir_sin', 'wdir_cos',
    'pressure', 'hour_sin', 'hour_cos', 'dayofyear_sin', 'dayofyear_cos'
]

# --- Target ---
target_feature = 'precipitation'

# --- Scale Features ---
scaler_X = MinMaxScaler()
X_scaled = scaler_X.fit_transform(raw_df[features])
joblib.dump(scaler_X, 'scaler_x_precipitation.pkl')

scaler_y = MinMaxScaler()
y_scaled = scaler_y.fit_transform(raw_df[[target_feature]])
joblib.dump(scaler_y, 'scaler_y_precipitation.pkl')

# --- Create Sequences ---
HISTORY_STEPS = 96   # past 4 days (96h)
FUTURE_STEPS  = 24   # predict 24h

X_encoder, y_decoder = [], []

for i in range(HISTORY_STEPS, len(X_scaled) - FUTURE_STEPS):
    X_encoder.append(X_scaled[i-HISTORY_STEPS:i])
    y_decoder.append(y_scaled[i:i+FUTURE_STEPS].flatten())

X_encoder = np.array(X_encoder)
y_decoder = np.array(y_decoder)

# --- Train/Test Split ---
X_train, X_test, y_train, y_test = train_test_split(X_encoder, y_decoder, test_size=0.2, random_state=42)

# --- Build Optimized Seq2Seq Model ---

# Encoder
encoder_inputs = Input(shape=(HISTORY_STEPS, len(features)))
encoder_l1 = LSTM(128, return_sequences=True)(encoder_inputs)
encoder_l1 = Dropout(0.2)(encoder_l1)
encoder_l2 = LSTM(64, return_state=True)
encoder_outputs, state_h, state_c = encoder_l2(encoder_l1)

# Decoder
decoder_inputs = RepeatVector(FUTURE_STEPS)(state_h)
decoder_l1 = LSTM(64, return_sequences=True)(decoder_inputs, initial_state=[state_h, state_c])
decoder_l1 = Dropout(0.2)(decoder_l1)

decoder_outputs = TimeDistributed(Dense(1))(decoder_l1)

# Build Model
model = Model(encoder_inputs, decoder_outputs)

model.compile(optimizer='adam', loss='mae', metrics=['mse'])
model.summary()

# --- Callbacks ---
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=1e-5, verbose=1)
early_stop = EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True, verbose=1)

# --- Train ---
history = model.fit(
    X_train, y_train.reshape(y_train.shape[0], FUTURE_STEPS, 1),
    validation_data=(X_test, y_test.reshape(y_test.shape[0], FUTURE_STEPS, 1)),
    epochs=80,
    batch_size=32,
    callbacks=[reduce_lr, early_stop],
    verbose=2
)

# --- Save Model ---
model.save('seq2seq_precipitation_forecast.keras')
print("✅ Seq2Seq optimized2 model saved!")
