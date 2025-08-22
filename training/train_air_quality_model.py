"""
LSTM Model Training for Air Quality Forecasting
Uses free libraries (TensorFlow/Keras) to train air quality prediction models
"""

import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AirQualityModelTrainer:
    """Trains LSTM models for air quality forecasting"""
    
    def __init__(self, data_path: str = "../data"):
        self.data_path = data_path
        self.models_path = "../models"
        os.makedirs(self.models_path, exist_ok=True)
        
        # Model parameters
        self.sequence_length = 24  # 24 hours of historical data
        self.prediction_hours = 24  # Predict next 24 hours
        self.feature_columns = ['aqi', 'pm25', 'pm10', 'no2', 'so2', 'co', 'o3', 'temperature', 'humidity']
        self.target_column = 'aqi'
        
        # Training parameters
        self.epochs = 100
        self.batch_size = 32
        self.validation_split = 0.2
        self.learning_rate = 0.001
        
        # Scalers
        self.feature_scaler = MinMaxScaler()
        self.target_scaler = MinMaxScaler()
        
        # Model
        self.model = None
        
    def load_and_preprocess_data(self) -> pd.DataFrame:
        """
        Load and preprocess air quality data
        """
        logger.info("Loading air quality data...")
        
        # Try to load synthetic data first
        data_files = [f for f in os.listdir(self.data_path) if 'air_quality' in f and f.endswith('.csv')]
        
        if not data_files:
            raise FileNotFoundError("No air quality data files found. Run data_collection.py first.")
        
        # Load the most recent file
        latest_file = sorted(data_files)[-1]
        filepath = os.path.join(self.data_path, latest_file)
        
        df = pd.read_csv(filepath)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        logger.info(f"Loaded {len(df)} records from {latest_file}")
        
        # Preprocess data
        df = self._preprocess_data(df)
        
        return df
    
    def _preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess the air quality data
        """
        logger.info("Preprocessing data...")
        
        # Remove rows with missing values
        df = df.dropna(subset=self.feature_columns + [self.target_column])
        
        # Remove outliers (values beyond 3 standard deviations)
        for col in self.feature_columns + [self.target_column]:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
        
        # Sort by timestamp
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        # Add time-based features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['month'] = df['timestamp'].dt.month
        
        # Add cyclical encoding for time features
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        
        # Update feature columns to include time features
        self.feature_columns.extend(['hour_sin', 'hour_cos', 'day_sin', 'day_cos', 'month_sin', 'month_cos'])
        
        logger.info(f"Preprocessed data shape: {df.shape}")
        return df
    
    def create_sequences(self, df: pd.DataFrame) -> tuple:
        """
        Create sequences for LSTM training
        """
        logger.info("Creating sequences for LSTM...")
        
        # Prepare features and target
        features = df[self.feature_columns].values
        target = df[self.target_column].values
        
        # Scale the data
        features_scaled = self.feature_scaler.fit_transform(features)
        target_scaled = self.target_scaler.fit_transform(target.reshape(-1, 1)).flatten()
        
        # Create sequences
        X, y = [], []
        
        for i in range(self.sequence_length, len(features_scaled) - self.prediction_hours + 1):
            # Input sequence
            X.append(features_scaled[i-self.sequence_length:i])
            # Target sequence (next 24 hours)
            y.append(target_scaled[i:i+self.prediction_hours])
        
        X = np.array(X)
        y = np.array(y)
        
        logger.info(f"Created {len(X)} sequences")
        logger.info(f"X shape: {X.shape}, y shape: {y.shape}")
        
        return X, y
    
    def build_model(self, input_shape: tuple) -> Sequential:
        """
        Build LSTM model architecture
        """
        logger.info("Building LSTM model...")
        
        model = Sequential([
            # First LSTM layer
            LSTM(128, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            
            # Second LSTM layer
            LSTM(64, return_sequences=False),
            Dropout(0.2),
            
            # Dense layers
            Dense(32, activation='relu'),
            Dropout(0.1),
            
            # Output layer
            Dense(self.prediction_hours, activation='linear')
        ])
        
        # Compile model
        model.compile(
            optimizer=Adam(learning_rate=self.learning_rate),
            loss='mse',
            metrics=['mae']
        )
        
        model.summary()
        return model
    
    def train_model(self, X: np.ndarray, y: np.ndarray) -> dict:
        """
        Train the LSTM model
        """
        logger.info("Training LSTM model...")
        
        # Split data
        split_idx = int(len(X) * (1 - self.validation_split))
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]
        
        # Build model
        self.model = self.build_model((X.shape[1], X.shape[2]))
        
        # Callbacks
        callbacks = [
            EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True,
                verbose=1
            ),
            ModelCheckpoint(
                filepath=os.path.join(self.models_path, 'lstm_air_quality_best.h5'),
                monitor='val_loss',
                save_best_only=True,
                verbose=1
            )
        ]
        
        # Train model
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=self.epochs,
            batch_size=self.batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        # Save final model
        final_model_path = os.path.join(self.models_path, 'lstm_air_quality.h5')
        self.model.save(final_model_path)
        logger.info(f"Model saved to {final_model_path}")
        
        return history.history
    
    def evaluate_model(self, X: np.ndarray, y: np.ndarray) -> dict:
        """
        Evaluate the trained model
        """
        logger.info("Evaluating model...")
        
        # Split data
        split_idx = int(len(X) * (1 - self.validation_split))
        X_test, y_test = X[split_idx:], y[split_idx:]
        
        # Make predictions
        y_pred_scaled = self.model.predict(X_test)
        
        # Inverse transform predictions
        y_pred = self.target_scaler.inverse_transform(y_pred_scaled)
        y_true = self.target_scaler.inverse_transform(y_test)
        
        # Calculate metrics for each prediction horizon
        metrics = {}
        for i in range(self.prediction_hours):
            horizon = i + 1
            mse = mean_squared_error(y_true[:, i], y_pred[:, i])
            mae = mean_absolute_error(y_true[:, i], y_pred[:, i])
            r2 = r2_score(y_true[:, i], y_pred[:, i])
            
            metrics[f'horizon_{horizon}h'] = {
                'mse': mse,
                'mae': mae,
                'r2': r2,
                'rmse': np.sqrt(mse)
            }
        
        # Overall metrics (average across all horizons)
        overall_metrics = {
            'overall_mse': np.mean([metrics[f'horizon_{i+1}h']['mse'] for i in range(self.prediction_hours)]),
            'overall_mae': np.mean([metrics[f'horizon_{i+1}h']['mae'] for i in range(self.prediction_hours)]),
            'overall_r2': np.mean([metrics[f'horizon_{i+1}h']['r2'] for i in range(self.prediction_hours)]),
            'overall_rmse': np.mean([metrics[f'horizon_{i+1}h']['rmse'] for i in range(self.prediction_hours)])
        }
        
        metrics['overall'] = overall_metrics
        
        logger.info(f"Overall RMSE: {overall_metrics['overall_rmse']:.2f}")
        logger.info(f"Overall MAE: {overall_metrics['overall_mae']:.2f}")
        logger.info(f"Overall R²: {overall_metrics['overall_r2']:.3f}")
        
        return metrics, y_true, y_pred
    
    def plot_results(self, history: dict, metrics: dict, y_true: np.ndarray, y_pred: np.ndarray):
        """
        Plot training results and predictions
        """
        logger.info("Creating plots...")
        
        # Create plots directory
        plots_dir = os.path.join(self.models_path, 'plots')
        os.makedirs(plots_dir, exist_ok=True)
        
        # Plot 1: Training history
        plt.figure(figsize=(12, 4))
        
        plt.subplot(1, 2, 1)
        plt.plot(history['loss'], label='Training Loss')
        plt.plot(history['val_loss'], label='Validation Loss')
        plt.title('Model Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        
        plt.subplot(1, 2, 2)
        plt.plot(history['mae'], label='Training MAE')
        plt.plot(history['val_mae'], label='Validation MAE')
        plt.title('Model MAE')
        plt.xlabel('Epoch')
        plt.ylabel('MAE')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig(os.path.join(plots_dir, 'training_history.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        # Plot 2: Prediction vs Actual (first 100 samples, 24h horizon)
        plt.figure(figsize=(15, 10))
        
        for i in range(min(4, self.prediction_hours)):
            plt.subplot(2, 2, i+1)
            horizon = i + 1
            
            # Plot first 100 samples
            sample_size = min(100, len(y_true))
            plt.scatter(y_true[:sample_size, i], y_pred[:sample_size, i], alpha=0.6)
            plt.plot([y_true[:sample_size, i].min(), y_true[:sample_size, i].max()], 
                    [y_true[:sample_size, i].min(), y_true[:sample_size, i].max()], 'r--', lw=2)
            
            plt.xlabel('Actual AQI')
            plt.ylabel('Predicted AQI')
            plt.title(f'{horizon}h Horizon Prediction')
            
            # Add R² score
            r2 = metrics[f'horizon_{horizon}h']['r2']
            plt.text(0.05, 0.95, f'R² = {r2:.3f}', transform=plt.gca().transAxes, 
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
        
        plt.tight_layout()
        plt.savefig(os.path.join(plots_dir, 'predictions_vs_actual.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        # Plot 3: Metrics by prediction horizon
        horizons = list(range(1, self.prediction_hours + 1))
        rmse_values = [metrics[f'horizon_{h}h']['rmse'] for h in horizons]
        mae_values = [metrics[f'horizon_{h}h']['mae'] for h in horizons]
        r2_values = [metrics[f'horizon_{h}h']['r2'] for h in horizons]
        
        plt.figure(figsize=(15, 5))
        
        plt.subplot(1, 3, 1)
        plt.plot(horizons, rmse_values, 'o-', color='red')
        plt.title('RMSE by Prediction Horizon')
        plt.xlabel('Horizon (hours)')
        plt.ylabel('RMSE')
        plt.grid(True)
        
        plt.subplot(1, 3, 2)
        plt.plot(horizons, mae_values, 'o-', color='blue')
        plt.title('MAE by Prediction Horizon')
        plt.xlabel('Horizon (hours)')
        plt.ylabel('MAE')
        plt.grid(True)
        
        plt.subplot(1, 3, 3)
        plt.plot(horizons, r2_values, 'o-', color='green')
        plt.title('R² by Prediction Horizon')
        plt.xlabel('Horizon (hours)')
        plt.ylabel('R²')
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig(os.path.join(plots_dir, 'metrics_by_horizon.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Plots saved to {plots_dir}")
    
    def save_model_info(self, metrics: dict, history: dict):
        """
        Save model information and metrics
        """
        model_info = {
            "model_name": "LSTM Air Quality Forecaster",
            "created_at": datetime.now().isoformat(),
            "model_parameters": {
                "sequence_length": self.sequence_length,
                "prediction_hours": self.prediction_hours,
                "feature_columns": self.feature_columns,
                "target_column": self.target_column,
                "epochs": self.epochs,
                "batch_size": self.batch_size,
                "learning_rate": self.learning_rate
            },
            "training_parameters": {
                "final_epochs": len(history['loss']),
                "final_train_loss": history['loss'][-1],
                "final_val_loss": history['val_loss'][-1],
                "final_train_mae": history['mae'][-1],
                "final_val_mae": history['val_mae'][-1]
            },
            "performance_metrics": metrics,
            "model_files": {
                "model": "lstm_air_quality.h5",
                "best_model": "lstm_air_quality_best.h5",
                "scalers": "air_quality_scalers.pkl"
            }
        }
        
        # Save model info
        info_path = os.path.join(self.models_path, 'lstm_air_quality_info.json')
        with open(info_path, 'w') as f:
            json.dump(model_info, f, indent=2, default=str)
        
        logger.info(f"Model information saved to {info_path}")
    
    def train(self) -> dict:
        """
        Complete training pipeline
        """
        logger.info("Starting LSTM air quality model training...")
        
        # Load and preprocess data
        df = self.load_and_preprocess_data()
        
        # Create sequences
        X, y = self.create_sequences(df)
        
        # Train model
        history = self.train_model(X, y)
        
        # Evaluate model
        metrics, y_true, y_pred = self.evaluate_model(X, y)
        
        # Create plots
        self.plot_results(history, metrics, y_true, y_pred)
        
        # Save model information
        self.save_model_info(metrics, history)
        
        logger.info("LSTM air quality model training completed!")
        
        return {
            "metrics": metrics,
            "history": history,
            "model_path": os.path.join(self.models_path, 'lstm_air_quality.h5')
        }

def main():
    """Main function to run training"""
    trainer = AirQualityModelTrainer()
    results = trainer.train()
    
    print("\n" + "="*50)
    print("LSTM AIR QUALITY MODEL TRAINING COMPLETE")
    print("="*50)
    print(f"Overall RMSE: {results['metrics']['overall']['overall_rmse']:.2f}")
    print(f"Overall MAE: {results['metrics']['overall']['overall_mae']:.2f}")
    print(f"Overall R²: {results['metrics']['overall']['overall_r2']:.3f}")
    print(f"Model saved to: {results['model_path']}")
    print("="*50)

if __name__ == "__main__":
    main() 