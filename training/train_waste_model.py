"""
Random Forest Model Training for Waste Generation Prediction
Uses free libraries (scikit-learn) to train waste prediction models
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import os
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WasteModelTrainer:
    """Trains Random Forest models for waste generation prediction"""
    
    def __init__(self, data_path: str = "../data"):
        self.data_path = data_path
        self.models_path = "../models"
        os.makedirs(self.models_path, exist_ok=True)
        
        # Model parameters
        self.feature_columns = [
            'fill_level', 'weight', 'temperature', 'humidity', 'methane_level',
            'hour', 'day_of_week', 'month', 'capacity', 'population_density'
        ]
        self.target_column = 'fill_level'
        self.classification_target = 'needs_collection'
        
        # Training parameters
        self.test_size = 0.2
        self.random_state = 42
        self.cv_folds = 5
        
        # Scalers and encoders
        self.feature_scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        
        # Models
        self.regression_model = None
        self.classification_model = None
        
    def load_and_preprocess_data(self) -> tuple:
        """
        Load and preprocess waste management data
        """
        logger.info("Loading waste management data...")
        
        # Load waste bins data
        bins_files = [f for f in os.listdir(self.data_path) if 'waste_bins' in f and f.endswith('.csv')]
        readings_files = [f for f in os.listdir(self.data_path) if 'waste_readings' in f and f.endswith('.csv')]
        
        if not bins_files or not readings_files:
            raise FileNotFoundError("Waste management data files not found. Run data_collection.py first.")
        
        # Load the most recent files
        latest_bins_file = sorted(bins_files)[-1]
        latest_readings_file = sorted(readings_files)[-1]
        
        bins_filepath = os.path.join(self.data_path, latest_bins_file)
        readings_filepath = os.path.join(self.data_path, latest_readings_file)
        
        bins_df = pd.read_csv(bins_filepath)
        readings_df = pd.read_csv(readings_filepath)
        
        logger.info(f"Loaded {len(bins_df)} bins and {len(readings_df)} readings")
        
        # Preprocess data
        bins_df, readings_df = self._preprocess_data(bins_df, readings_df)
        
        return bins_df, readings_df
    
    def _preprocess_data(self, bins_df: pd.DataFrame, readings_df: pd.DataFrame) -> tuple:
        """
        Preprocess the waste management data
        """
        logger.info("Preprocessing waste management data...")
        
        # Merge bins and readings data
        merged_df = readings_df.merge(bins_df, on='bin_id', suffixes=('', '_bin'))
        
        # Add time-based features
        merged_df['timestamp'] = pd.to_datetime(merged_df['timestamp'])
        merged_df['hour'] = merged_df['timestamp'].dt.hour
        merged_df['day_of_week'] = merged_df['timestamp'].dt.dayofweek
        merged_df['month'] = merged_df['timestamp'].dt.month
        merged_df['day_of_year'] = merged_df['timestamp'].dt.dayofyear
        
        # Add cyclical encoding for time features
        merged_df['hour_sin'] = np.sin(2 * np.pi * merged_df['hour'] / 24)
        merged_df['hour_cos'] = np.cos(2 * np.pi * merged_df['hour'] / 24)
        merged_df['day_sin'] = np.sin(2 * np.pi * merged_df['day_of_week'] / 7)
        merged_df['day_cos'] = np.cos(2 * np.pi * merged_df['day_of_week'] / 7)
        merged_df['month_sin'] = np.sin(2 * np.pi * merged_df['month'] / 12)
        merged_df['month_cos'] = np.cos(2 * np.pi * merged_df['month'] / 12)
        
        # Add lag features (previous fill levels)
        merged_df = merged_df.sort_values(['bin_id', 'timestamp'])
        merged_df['fill_level_lag1'] = merged_df.groupby('bin_id')['fill_level'].shift(1)
        merged_df['fill_level_lag2'] = merged_df.groupby('bin_id')['fill_level'].shift(2)
        merged_df['fill_level_lag3'] = merged_df.groupby('bin_id')['fill_level'].shift(3)
        
        # Add rolling statistics
        merged_df['fill_level_rolling_mean_6h'] = merged_df.groupby('bin_id')['fill_level'].rolling(6).mean().reset_index(0, drop=True)
        merged_df['fill_level_rolling_std_6h'] = merged_df.groupby('bin_id')['fill_level'].rolling(6).std().reset_index(0, drop=True)
        
        # Encode categorical variables
        merged_df['bin_type_encoded'] = self.label_encoder.fit_transform(merged_df['bin_type'])
        
        # Update feature columns
        self.feature_columns.extend([
            'hour_sin', 'hour_cos', 'day_sin', 'day_cos', 'month_sin', 'month_cos',
            'fill_level_lag1', 'fill_level_lag2', 'fill_level_lag3',
            'fill_level_rolling_mean_6h', 'fill_level_rolling_std_6h',
            'bin_type_encoded'
        ])
        
        # Remove rows with missing values
        merged_df = merged_df.dropna(subset=self.feature_columns + [self.target_column])
        
        logger.info(f"Preprocessed data shape: {merged_df.shape}")
        return bins_df, merged_df
    
    def prepare_features(self, df: pd.DataFrame) -> tuple:
        """
        Prepare features and targets for training
        """
        logger.info("Preparing features for training...")
        
        # Select features and targets
        X = df[self.feature_columns].values
        y_regression = df[self.target_column].values
        y_classification = df[self.classification_target].values
        
        # Scale features
        X_scaled = self.feature_scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, y_reg_train, y_reg_test, y_clf_train, y_clf_test = train_test_split(
            X_scaled, y_regression, y_classification,
            test_size=self.test_size,
            random_state=self.random_state,
            stratify=y_classification
        )
        
        logger.info(f"Training set size: {len(X_train)}")
        logger.info(f"Test set size: {len(X_test)}")
        
        return (X_train, X_test, y_reg_train, y_reg_test, y_clf_train, y_clf_test)
    
    def train_regression_model(self, X_train: np.ndarray, y_train: np.ndarray) -> RandomForestRegressor:
        """
        Train Random Forest regression model for fill level prediction
        """
        logger.info("Training Random Forest regression model...")
        
        # Define parameter grid for hyperparameter tuning
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [10, 15, 20, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }
        
        # Initialize base model
        base_model = RandomForestRegressor(random_state=self.random_state, n_jobs=-1)
        
        # Grid search for best parameters
        grid_search = GridSearchCV(
            base_model,
            param_grid,
            cv=self.cv_folds,
            scoring='neg_mean_squared_error',
            n_jobs=-1,
            verbose=1
        )
        
        grid_search.fit(X_train, y_train)
        
        # Get best model
        self.regression_model = grid_search.best_estimator_
        
        logger.info(f"Best parameters: {grid_search.best_params_}")
        logger.info(f"Best CV score: {-grid_search.best_score_:.4f}")
        
        return self.regression_model
    
    def train_classification_model(self, X_train: np.ndarray, y_train: np.ndarray) -> RandomForestClassifier:
        """
        Train Random Forest classification model for collection prediction
        """
        logger.info("Training Random Forest classification model...")
        
        # Define parameter grid for hyperparameter tuning
        param_grid = {
            'n_estimators': [50, 100, 200],
            'max_depth': [10, 15, 20, None],
            'min_samples_split': [2, 5, 10],
            'min_samples_leaf': [1, 2, 4]
        }
        
        # Initialize base model
        base_model = RandomForestClassifier(random_state=self.random_state, n_jobs=-1)
        
        # Grid search for best parameters
        grid_search = GridSearchCV(
            base_model,
            param_grid,
            cv=self.cv_folds,
            scoring='f1',
            n_jobs=-1,
            verbose=1
        )
        
        grid_search.fit(X_train, y_train)
        
        # Get best model
        self.classification_model = grid_search.best_estimator_
        
        logger.info(f"Best parameters: {grid_search.best_params_}")
        logger.info(f"Best CV score: {grid_search.best_score_:.4f}")
        
        return self.classification_model
    
    def evaluate_models(self, X_test: np.ndarray, y_reg_test: np.ndarray, y_clf_test: np.ndarray) -> dict:
        """
        Evaluate both regression and classification models
        """
        logger.info("Evaluating models...")
        
        # Regression model evaluation
        y_reg_pred = self.regression_model.predict(X_test)
        reg_metrics = {
            'mse': mean_squared_error(y_reg_test, y_reg_pred),
            'mae': mean_absolute_error(y_reg_test, y_reg_pred),
            'r2': r2_score(y_reg_test, y_reg_pred),
            'rmse': np.sqrt(mean_squared_error(y_reg_test, y_reg_pred))
        }
        
        # Classification model evaluation
        y_clf_pred = self.classification_model.predict(X_test)
        y_clf_pred_proba = self.classification_model.predict_proba(X_test)
        
        clf_report = classification_report(y_clf_test, y_clf_pred, output_dict=True)
        clf_metrics = {
            'accuracy': clf_report['accuracy'],
            'precision': clf_report['weighted avg']['precision'],
            'recall': clf_report['weighted avg']['recall'],
            'f1_score': clf_report['weighted avg']['f1-score']
        }
        
        # Feature importance
        reg_importance = self.regression_model.feature_importances_
        clf_importance = self.classification_model.feature_importances_
        
        feature_importance = {
            'regression': dict(zip(self.feature_columns, reg_importance)),
            'classification': dict(zip(self.feature_columns, clf_importance))
        }
        
        metrics = {
            'regression': reg_metrics,
            'classification': clf_metrics,
            'feature_importance': feature_importance
        }
        
        logger.info(f"Regression RMSE: {reg_metrics['rmse']:.4f}")
        logger.info(f"Regression R²: {reg_metrics['r2']:.4f}")
        logger.info(f"Classification Accuracy: {clf_metrics['accuracy']:.4f}")
        logger.info(f"Classification F1: {clf_metrics['f1_score']:.4f}")
        
        return metrics, y_reg_pred, y_clf_pred, y_clf_pred_proba
    
    def plot_results(self, metrics: dict, y_reg_test: np.ndarray, y_reg_pred: np.ndarray, 
                    y_clf_test: np.ndarray, y_clf_pred: np.ndarray):
        """
        Plot model results and feature importance
        """
        logger.info("Creating plots...")
        
        # Create plots directory
        plots_dir = os.path.join(self.models_path, 'plots')
        os.makedirs(plots_dir, exist_ok=True)
        
        # Plot 1: Regression results
        plt.figure(figsize=(15, 5))
        
        plt.subplot(1, 3, 1)
        plt.scatter(y_reg_test, y_reg_pred, alpha=0.6)
        plt.plot([y_reg_test.min(), y_reg_test.max()], [y_reg_test.min(), y_reg_test.max()], 'r--', lw=2)
        plt.xlabel('Actual Fill Level')
        plt.ylabel('Predicted Fill Level')
        plt.title('Waste Fill Level Prediction')
        
        # Add R² score
        r2 = metrics['regression']['r2']
        plt.text(0.05, 0.95, f'R² = {r2:.3f}', transform=plt.gca().transAxes, 
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
        
        # Plot 2: Classification confusion matrix
        plt.subplot(1, 3, 2)
        cm = confusion_matrix(y_clf_test, y_clf_pred)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
        plt.xlabel('Predicted')
        plt.ylabel('Actual')
        plt.title('Collection Need Prediction')
        
        # Plot 3: Feature importance (regression)
        plt.subplot(1, 3, 3)
        importance_df = pd.DataFrame({
            'feature': self.feature_columns,
            'importance': metrics['feature_importance']['regression']
        }).sort_values('importance', ascending=True)
        
        plt.barh(range(len(importance_df)), importance_df['importance'])
        plt.yticks(range(len(importance_df)), importance_df['feature'])
        plt.xlabel('Feature Importance')
        plt.title('Regression Model Feature Importance')
        
        plt.tight_layout()
        plt.savefig(os.path.join(plots_dir, 'waste_model_results.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        # Plot 4: Feature importance comparison
        plt.figure(figsize=(12, 8))
        
        importance_comparison = pd.DataFrame({
            'feature': self.feature_columns,
            'regression': [metrics['feature_importance']['regression'][f] for f in self.feature_columns],
            'classification': [metrics['feature_importance']['classification'][f] for f in self.feature_columns]
        })
        
        importance_comparison = importance_comparison.sort_values('regression', ascending=True)
        
        x = np.arange(len(importance_comparison))
        width = 0.35
        
        plt.barh(x - width/2, importance_comparison['regression'], width, label='Regression', alpha=0.8)
        plt.barh(x + width/2, importance_comparison['classification'], width, label='Classification', alpha=0.8)
        
        plt.yticks(x, importance_comparison['feature'])
        plt.xlabel('Feature Importance')
        plt.title('Feature Importance Comparison')
        plt.legend()
        
        plt.tight_layout()
        plt.savefig(os.path.join(plots_dir, 'waste_feature_importance.png'), dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Plots saved to {plots_dir}")
    
    def save_models(self):
        """
        Save trained models and scalers
        """
        logger.info("Saving models...")
        
        # Save regression model
        reg_model_path = os.path.join(self.models_path, 'rf_waste_prediction.pkl')
        joblib.dump(self.regression_model, reg_model_path)
        
        # Save classification model
        clf_model_path = os.path.join(self.models_path, 'rf_waste_classification.pkl')
        joblib.dump(self.classification_model, clf_model_path)
        
        # Save scalers and encoders
        scalers_path = os.path.join(self.models_path, 'waste_scalers.pkl')
        joblib.dump({
            'feature_scaler': self.feature_scaler,
            'label_encoder': self.label_encoder
        }, scalers_path)
        
        logger.info(f"Models saved to {self.models_path}")
    
    def save_model_info(self, metrics: dict):
        """
        Save model information and metrics
        """
        model_info = {
            "model_name": "Random Forest Waste Prediction",
            "created_at": datetime.now().isoformat(),
            "model_parameters": {
                "feature_columns": self.feature_columns,
                "target_column": self.target_column,
                "classification_target": self.classification_target,
                "test_size": self.test_size,
                "cv_folds": self.cv_folds
            },
            "regression_model": {
                "best_params": self.regression_model.get_params(),
                "n_estimators": self.regression_model.n_estimators,
                "max_depth": self.regression_model.max_depth
            },
            "classification_model": {
                "best_params": self.classification_model.get_params(),
                "n_estimators": self.classification_model.n_estimators,
                "max_depth": self.classification_model.max_depth
            },
            "performance_metrics": metrics,
            "model_files": {
                "regression_model": "rf_waste_prediction.pkl",
                "classification_model": "rf_waste_classification.pkl",
                "scalers": "waste_scalers.pkl"
            }
        }
        
        # Save model info
        info_path = os.path.join(self.models_path, 'rf_waste_info.json')
        with open(info_path, 'w') as f:
            json.dump(model_info, f, indent=2, default=str)
        
        logger.info(f"Model information saved to {info_path}")
    
    def train(self) -> dict:
        """
        Complete training pipeline
        """
        logger.info("Starting Random Forest waste model training...")
        
        # Load and preprocess data
        bins_df, readings_df = self.load_and_preprocess_data()
        
        # Prepare features
        X_train, X_test, y_reg_train, y_reg_test, y_clf_train, y_clf_test = self.prepare_features(readings_df)
        
        # Train models
        self.train_regression_model(X_train, y_reg_train)
        self.train_classification_model(X_train, y_clf_train)
        
        # Evaluate models
        metrics, y_reg_pred, y_clf_pred, y_clf_pred_proba = self.evaluate_models(
            X_test, y_reg_test, y_clf_test
        )
        
        # Create plots
        self.plot_results(metrics, y_reg_test, y_reg_pred, y_clf_test, y_clf_pred)
        
        # Save models
        self.save_models()
        
        # Save model information
        self.save_model_info(metrics)
        
        logger.info("Random Forest waste model training completed!")
        
        return {
            "metrics": metrics,
            "regression_model_path": os.path.join(self.models_path, 'rf_waste_prediction.pkl'),
            "classification_model_path": os.path.join(self.models_path, 'rf_waste_classification.pkl')
        }

def main():
    """Main function to run training"""
    trainer = WasteModelTrainer()
    results = trainer.train()
    
    print("\n" + "="*50)
    print("RANDOM FOREST WASTE MODEL TRAINING COMPLETE")
    print("="*50)
    print(f"Regression RMSE: {results['metrics']['regression']['rmse']:.4f}")
    print(f"Regression R²: {results['metrics']['regression']['r2']:.4f}")
    print(f"Classification Accuracy: {results['metrics']['classification']['accuracy']:.4f}")
    print(f"Classification F1: {results['metrics']['classification']['f1_score']:.4f}")
    print(f"Models saved to: {results['regression_model_path']}")
    print("="*50)

if __name__ == "__main__":
    main() 