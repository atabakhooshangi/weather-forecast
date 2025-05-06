import pandas as pd
import numpy as np
import joblib
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # disable GPU
import tensorflow as tf
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import seaborn as sns


# --- 1. Load models and scalers ---
scaler_X = joblib.load('models_scalers/scaler_X_latest.pkl')
label_encoder = joblib.load('models_scalers/label_encoder_condition.pkl')
model_temp = tf.keras.models.load_model('models_scalers/lstm_temperature_latest.keras')
model_cond = tf.keras.models.load_model('models_scalers/lstm_condition_classifier_latest.keras')

# --- 2. Define features exactly like training ---
features = [
    'air_temperature', 'dew_point', 'relative_humidity', 'precipitation',
    'wind_speed', 'wind_direction', 'wdir_sin', 'wdir_cos',
    'pressure', 'hour_sin', 'hour_cos', 'dayofyear_sin', 'dayofyear_cos'
]

# --- 3. Load dataset (the same you trained with) ---
raw_df = pd.read_parquet('./station_datasets/full_concat_data_cleaned.parquet')
raw_df['timestamp'] = pd.to_datetime(raw_df['timestamp'])
raw_df = raw_df.sort_values(['station_id', 'timestamp']).reset_index(drop=True)

# --- 4. Prepare inputs ---
X_scaled = scaler_X.transform(raw_df[features])

# --- 5. Create sequences ---
def create_sequences(X, y, window_size=24):
    Xs, ys = [], []
    for i in range(window_size, len(X)):
        Xs.append(X[i-window_size:i])
        ys.append(y[i])
    return np.array(Xs), np.array(ys)

# Temperature
X_temp, y_temp = create_sequences(X_scaled, raw_df['air_temperature'].values)
print(1)
# Condition
X_cond, y_cond = create_sequences(X_scaled, label_encoder.transform(raw_df['condition_group'].values))
print(1)
# --- 6. Train/Test Split (same as training) ---
X_temp_train, X_temp_test, y_temp_train, y_temp_test = train_test_split(X_temp, y_temp, test_size=0.2, random_state=42)
X_cond_train, X_cond_test, y_cond_train, y_cond_test = train_test_split(X_cond, y_cond, test_size=0.2, random_state=42)
print(1)
# --- 7. Predict and Evaluate ---

# Temperature
y_temp_pred = model_temp.predict(X_temp_test, verbose=0)

mae = mean_absolute_error(y_temp_test, y_temp_pred)
mse = mean_squared_error(y_temp_test, y_temp_pred)
rmse = np.sqrt(mse)
r2 = r2_score(y_temp_test, y_temp_pred)
print(1)
print("🔵 Temperature Evaluation:")
print(f"MAE: {mae:.3f}")
print(f"MSE: {mse:.3f}")
print(f"RMSE: {rmse:.3f}")
print(f"R² Score: {r2:.3f}")

# Condition
y_cond_pred_probs = model_cond.predict(X_cond_test, verbose=0)
y_cond_pred_classes = np.argmax(y_cond_pred_probs, axis=1)

acc = accuracy_score(y_cond_test, y_cond_pred_classes)
print("\n🟣 Condition Evaluation:")
print(f"Accuracy: {acc:.3f}")
print("\nClassification Report:")
print(classification_report(y_cond_test, y_cond_pred_classes, target_names=label_encoder.classes_))


# --- Plot Temperature Real vs Predicted ---
plt.figure(figsize=(12,6))
plt.plot(y_temp_test[:500], label='Actual Temperature')
plt.plot(y_temp_pred[:500], label='Predicted Temperature')
plt.title('Temperature Prediction vs Actual (first 500 samples)')
plt.xlabel('Sample')
plt.ylabel('Temperature (°C)')
plt.legend()
plt.grid()
plt.tight_layout()
plt.savefig('temperature_prediction_vs_actual.png', dpi=300)
plt.show()

# --- Plot Confusion Matrix for Condition ---
cm = confusion_matrix(y_cond_test, y_cond_pred_classes)
plt.figure(figsize=(10,8))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=label_encoder.classes_, yticklabels=label_encoder.classes_)
plt.title('Condition Prediction - Confusion Matrix')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.xticks(rotation=45)
plt.yticks(rotation=45)
plt.tight_layout()
plt.savefig('condition_confusion_matrix.png', dpi=300)
plt.show()