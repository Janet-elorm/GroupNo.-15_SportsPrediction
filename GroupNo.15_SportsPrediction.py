# -*- coding: utf-8 -*-
"""SPORTS PREDICTIONS_FIFA22

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1d_8Z6RHyplMpZ_nM5zwaM21X7Zbn7OcV
"""

import pandas as pd
import numpy as np
from google.colab import drive
from sklearn.preprocessing import StandardScaler,OneHotEncoder
from sklearn.decomposition import PCA
from sklearn.model_selection import cross_val_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

drive.mount('/content/drive')

"""Here, we are loading both the training and testing datasets for two different seasons (21 and 22) of player data from FIFA."""

# Load the 'players_21' dataset for training and the 'players_22' dataset for testing
fifa_train = pd.read_csv('/content/drive/My Drive/Colab Notebooks/mycopy/players_21.csv')
fifa_test = pd.read_csv('/content/drive/My Drive/Colab Notebooks/mycopy/players_22.csv')

"""Executing this block of code, helps to quickly assess the structure and quality of the training dataset, including the number of columns, data types, and the extent of missing data. This information is fundamental to understanding the data and preparing it for further analysis and machine learning model training."""

# Explore the training data(players_21)
print("Training Data Info:")
print(fifa_train.info())
print("\nMissing Values in Training Data:")
print(fifa_train.isnull().sum())

# Explore the testing data(players_22)
print("\nTesting Data Info:")
print(fifa_test.info())
print("\nMissing Values in Testing Data:")
print(fifa_test.isnull().sum())

"""these code blocks are used to remove specific columns from the fifa_train and fifa_test datasets that are considered unwanted or irrelevant for the analysis or machine learning tasks."""

unwanted_columns_21 = ['player_url','player_face_url ', 'club_logo_url', 'club_flag_url','nation_logo_url','nation_flag_url' ]
fifa_train_cleaned = fifa_train.drop(columns=unwanted_columns_21, errors='ignore')

unwanted_columns_22 = ['player_url','player_face_url ', 'club_logo_url', 'club_flag_url','nation_logo_url','nation_flag_url' ]
fifa_test_cleaned = fifa_test.drop(columns=unwanted_columns_22, errors='ignore')

fifa_train_cleaned

fifa_train_cleaned[["release_clause_eur","value_eur","dob","potential","age","gk","sofifa_id", "rb" ]]

fifa_train_cleaned[["release_clause_eur","value_eur","dob","potential","age","gk","sofifa_id", "rb" ]].info()
fifa_train_cleaned["movement_reactions"].info()
fifa_train_cleaned["wage_eur" ].info()
 ##  " wage_eur"

fifa_test_cleaned.info()

"""By removing columns with a significant number of missing values (in this example, more than 30%), this method deals with missing data. High amounts of missing data are often deleted from columns because they could not include information that is valuable for analysis or modeling, and their inclusion could skew the findings. The datasets utilized for analysis and machine learning are as clear and useful as possible thanks to this data pretreatment phase.





"""

# Identify columns with more than 30% missing values in the training dataset
missing_threshold_21 = (fifa_train_cleaned.isnull().sum() / len(fifa_train_cleaned)) * 100
columns_21_with_high_missing = missing_threshold_21[missing_threshold_21 > 30].index

# Drop the identified columns from the training dataset
fifa_train_cleaned.drop(columns=columns_21_with_high_missing, inplace=True)

# Identify columns with more than 30% missing values in the test dataset
missing_threshold_22 = (fifa_test_cleaned.isnull().sum() / len(fifa_test_cleaned)) * 100
columns_22_with_high_missing = missing_threshold_22[missing_threshold_22 > 30].index

# Drop the identified columns from the test dataset
fifa_test_cleaned.drop(columns=columns_22_with_high_missing, inplace=True)

"""Categorical and non-categorical (usually numerical) columns in the training (fifa_train_cleaned) and test (fifa_test_cleaned) datasets are identified and divided into two groups by this code block.

"""

# Identify categorical columns by selecting columns with 'object' data type
categorical_columns_21 = fifa_train_cleaned.select_dtypes(include=['object']).columns
non_categorical_columns_21 = fifa_train_cleaned.select_dtypes(exclude=['object']).columns

# For the test data (assuming you want to perform the same separation)
categorical_columns_22 = fifa_test_cleaned.select_dtypes(include=['object']).columns
non_categorical_columns_22 = fifa_test_cleaned.select_dtypes(exclude=['object']).columns

"""This code block demonstrates the use of a SimpleImputer from scikit-learn to handle missing values in numeric columns in both the training (fifa_train_cleaned) and test (fifa_test_cleaned) datasets"""

from sklearn.impute import SimpleImputer

# Create a SimpleImputer for numeric columns with the 'mean' strategy
numeric_imputer = SimpleImputer(strategy='mean')

# Fit and transform the imputer on the training dataset (numeric columns)
fifa_train_cleaned[non_categorical_columns_21] = numeric_imputer.fit_transform(fifa_train_cleaned[non_categorical_columns_21])

# Transform the imputer on the test dataset (numeric columns)
fifa_test_cleaned[non_categorical_columns_22] = numeric_imputer.transform(fifa_test_cleaned[non_categorical_columns_22])

"""This code block demonstrates the use of a SimpleImputer for handling missing values in categorical columns (columns with data type 'object') in both the training (fifa_train_cleaned) and test (fifa_test_cleaned) datasets."""

# Create a SimpleImputer for categorical columns with the 'most_frequent' strategy
categorical_imputer = SimpleImputer(strategy='most_frequent')

# Fit and transform the imputer on the training dataset (categorical columns)
fifa_train_cleaned[categorical_columns_21] = categorical_imputer.fit_transform(fifa_train_cleaned[categorical_columns_21])

# Transform the imputer on the test dataset (categorical columns)
fifa_test_cleaned[categorical_columns_22] = categorical_imputer.transform(fifa_test_cleaned[categorical_columns_22])

"""Encoding categorical columns is essential when working with machine learning algorithms, as they often require numerical input. The LabelEncoder is used here to transform categorical values into numerical labels, making the data suitable for modeling"""

from sklearn.preprocessing import LabelEncoder

# Combine the training and test datasets
fifa_combined = pd.concat([fifa_train_cleaned, fifa_test_cleaned], axis=0)

# Initialize a LabelEncoder
label_encoder = LabelEncoder()

# Encode categorical columns in the combined dataset
for column in categorical_columns_21:
    fifa_combined[column] = label_encoder.fit_transform(fifa_combined[column])

# Split the combined dataset back into training and test datasets
fifa_train_encoded = fifa_combined[:len(fifa_train_cleaned)]
fifa_test_encoded = fifa_combined[len(fifa_train_cleaned):]

""" the encoded categorical columns and the original numerical columns are combined to create new datasets for both the training and test datasets.The purpose of combining encoded categorical and numerical columns in this manner is to prepare the data for machine learning."""

#Combine encoded categorical and numerical columns for training dataset
fifa_train_combined = pd.concat([fifa_train_encoded[categorical_columns_21], fifa_train_cleaned[non_categorical_columns_21]], axis=1)

# Combine encoded categorical and numerical columns for test dataset
fifa_test_combined = pd.concat([fifa_test_encoded[categorical_columns_21], fifa_test_cleaned[non_categorical_columns_21]], axis=1)

"""Random Forest Regressor model is used to calculate feature importances for the training dataset, and the top N most important features are printed.

The feature importances may be used for feature selection and interpretation and are useful for determining which features have the most impact on the model's predictions.

"""

from sklearn.ensemble import RandomForestRegressor

# Extract the target variable 'overall' from the datasets
y_train = fifa_train_combined['overall']
y_test = fifa_test_combined['overall']

# Split the combined training dataset into features and target variable
X_train = fifa_train_combined.drop(columns=['overall'])
X_test = fifa_test_combined.drop(columns=['overall'])
# Create a RandomForestRegressor model to calculate feature importances
rf_model = RandomForestRegressor(random_state=42)
rf_model.fit(X_train, y_train)

# Get feature importances
feature_importances = rf_model.feature_importances_

# Create a DataFrame to store feature names and their importance scores
feature_importance_df = pd.DataFrame({'Feature': X_train.columns, 'Importance': feature_importances})

# Sort features by importance in descending order
sorted_feature_importance = feature_importance_df.sort_values(by='Importance', ascending=False)

# Select the top N features (e.g., top 10)
N = 10
top_N_features = sorted_feature_importance['Feature'][:N]

# Print the top N features
print(top_N_features)

from sklearn.ensemble import RandomForestRegressor

# Extract the target variable 'overall' from the datasets
y_test = fifa_test_combined['overall']

# Split the combined test dataset into features and target variable
X_test = fifa_test_combined.drop(columns=['overall'])

# Create a RandomForestRegressor model to calculate feature importances
rf22_model = RandomForestRegressor(random_state=42)
rf22_model.fit(X_test, y_test)  # Fit the model with the test set data

# Get feature importances
feature_importances_22 = rf22_model.feature_importances_

# Create a DataFrame to store feature names and their importance scores
feature_importance_df22 = pd.DataFrame({'Feature': X_test.columns, 'Importance': feature_importances_22})

# Sort features by importance in descending order
sorted_feature_importance_22 = feature_importance_df22.sort_values(by='Importance', ascending=False)

# Select the top N features (e.g., top 10)
N = 10
top_N_features_22 = sorted_feature_importance_22['Feature'][:N]

# Print the top N features
print(top_N_features_22)

top_N_features_21.info()

"""scaling the features is to ensure that all features have the same scale, making it easier for machine learning models to learn from the data."""

from sklearn.preprocessing import StandardScaler
X_train=fifa_train_combined[top_N_features]
Y_train=fifa_train_combined['overall']

# Initialize the StandardScaler
scaler = StandardScaler()


# Fit and transform the scaler on the training data
X_train_scaled = scaler.fit_transform(X_train)

# Transform the test data using the same scaler
X_test_scaled = scaler.transform(X_test)

# Now, X_train_scaled and X_test_scaled contain your scaled features

X_test_scaled[top_N_features_22]

from sklearn.preprocessing import StandardScaler

# Initialize the StandardScaler
scaler = StandardScaler()

# Reshape the target arrays to be 2D
y_train_scaled = y_train.values.reshape(-1, 1)
y_test_scaled = y_test.values.reshape(-1, 1)

# Fit and transform the scaler on the training data
y_train_scaled = scaler.fit_transform(y_train_scaled)

# Transform the test data using the same scaler
y_test_scaled = scaler.transform(y_test_scaled)

"""For developing and testing machine learning models, this stage is essential. It makes sure the model is tested on a different subset of data than it was trained on, allowing you to evaluate the model's performance and generalization skills.

"""

from sklearn.model_selection import train_test_split

# Split the scaled data into training and testing sets
X_train_split, X_test_split, y_train_split, y_test_split = train_test_split(X_train_scaled, y_train, test_size=0.2, random_state=42)

"""Random Forest algorithm is used to build a regression model for predicting the target variable. It also employs hyperparameter tuning using GridSearchCV.

This method effectively uses grid search across a variety of hyperparameters to optimize a Random Forest regression model, reporting the performance of the best model on test data. The objective is to identify the hyperparameter configurations that produce the highest prediction performance for the specified dataset.
"""

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_absolute_error
import pandas as pd

# ... (previous code for data preprocessing, data loading, and scaling)

# Feature selection using RandomForest feature importances
rf_model = RandomForestRegressor(random_state=42)
# Train the model using only the top N features
rf_model.fit(X_train[top_N_features], y_train)



# Define the model
rf_model = RandomForestRegressor(random_state=42)

# Define hyperparameters to tune
param_grid = {
    'n_estimators': [50, 100],
    'max_depth': [4, 6]
}

# Create GridSearchCV
grid = GridSearchCV(rf_model, param_grid, cv=5, scoring='neg_mean_absolute_error', n_jobs=-1)

# Fit the model to the training data
grid.fit(X_train_split, y_train_split)

# Get the best model
best_rf_model = grid.best_estimator_

# Evaluate the best model on the test set
y_pred = best_rf_model.predict(X_test_split)
mae = mean_absolute_error(y_test_split, y_pred)

print(f'RandomForestRegressor MAE with selected features: {mae}')

"""XGBoost regression model is used to build a model for predicting the target variable, and hyperparameter tuning is performed using GridSearchCV.

This code is responsible for fine-tuning an XGBoost regression model using grid search over a range of hyperparameters and reporting the performance of the best model on the test data. The goal is to find the hyperparameter settings that lead to the best predictive accuracy for the given dataset.
"""

from xgboost import XGBRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_absolute_error

# ... (previous code for data preprocessing, data loading, and scaling)

# Feature selection using XGBoost feature importances
xgb_model = XGBRegressor(random_state=42)
xgb_model.fit(X_train, y_train)

# Re-evaluate the model with selected features
# Define the model
xgb_model = XGBRegressor(random_state=42)

# Define hyperparameters to tune
param_grid = {
    'n_estimators': [50, 100],
    'max_depth': [4, 6]
}

# Create GridSearchCV
grid = GridSearchCV(xgb_model, param_grid, cv=5, scoring='neg_mean_absolute_error', n_jobs=-1)

# Fit the model to the training data
grid.fit(X_train_split, y_train_split)

# Get the best model
best_xgb_model = grid.best_estimator_

# Evaluate the best model on the test set
y_pred = best_xgb_model.predict(X_test_split)
mae = mean_absolute_error(y_test_split, y_pred)

print(f'XGBoost MAE with selected features: {mae}')

"""Similar to the previous code for XGBoost, this code is responsible for fine-tuning a Gradient Boosting regression model using grid search over a range of hyperparameters and reporting the performance of the best model on the test data."""

from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_absolute_error

# ... (previous code for data preprocessing, data loading, and scaling)

# Feature selection using Gradient Boosting feature importances
gb_model = GradientBoostingRegressor(random_state=42)
gb_model.fit(X_train, y_train)

# Re-evaluate the model with selected features
# Define the model
gb_model = GradientBoostingRegressor(random_state=42)

# Define hyperparameters to tune
param_grid = {
    'n_estimators': [50, 100],
    'max_depth': [2, 4]
}

# Create GridSearchCV
grid = GridSearchCV(gb_model, param_grid, cv=5, scoring='neg_mean_absolute_error', n_jobs=-1)

# Fit the model to the training data
grid.fit(X_train_split, y_train_split)

# Get the best model
best_gb_model = grid.best_estimator_

# Evaluate the best model on the test set
y_pred = best_gb_model.predict(X_test_split)
mae = mean_absolute_error(y_test_split, y_pred)

print(f'Gradient Boosting MAE with selected features: {mae}')

"""an ensemble model called VotingRegressor is created by combining three individual regression models (XGBoost, Random Forest, and Gradient Boosting) to make predictions

Ensemble models combine the strengths of multiple individual models to potentially improve predictive accuracy
"""

# Create a VotingRegressor ensemble model
from sklearn.ensemble import VotingRegressor
from sklearn.ensemble import BaggingRegressor
ensemble_model = VotingRegressor(estimators=[
    ('xgb', best_xgb_model),
    ('rf', best_rf_model),
    ('gb', best_gb_model)
])

# Fit the ensemble model to the training data
ensemble_model.fit(X_train_split, y_train_split)

# Evaluate the ensemble model on the test set
y_pred = ensemble_model.predict(X_test_split)
mae = mean_absolute_error(y_test_split, y_pred)

print(f'Ensemble Model MAE with selected features: {mae}')

""" this code is to determine which of the three models is the most effective in making predictions for the given task. The model with the lowest MAE is considered the best model in terms of predictive accuracy"""

# Compare the MAE of the three models
mae_rf = mean_absolute_error(y_test_split, best_rf_model.predict(X_test_split))
mae_xgb = mean_absolute_error(y_test_split, best_xgb_model.predict(X_test_split))
mae_gb = mean_absolute_error(y_test_split, best_gb_model.predict(X_test_split))

# Find the model with the lowest MAE
best_model = None
best_mae = float('inf')

if mae_rf < best_mae:
    best_model = best_rf_model
    best_mae = mae_rf

if mae_xgb < best_mae:
    best_model = best_xgb_model
    best_mae = mae_xgb

if mae_gb < best_mae:
    best_model = best_gb_model
    best_mae = mae_gb

# Print the best model and its MAE
print(f'Best Model: {best_model.__class__.__name__}')
print(f'Best Model MAE: {best_mae}')

"""Measuring the Mean Absolute Error (MAE) of the Random Forest model (best_rf_model) on the 'players_22' dataset and reporting it.

"""

from sklearn.metrics import r2_score
# Evaluate the Random Forest model on 'players_22' data
y_pred_rf = best_rf_model.predict(X_test_scaled)
mae_rf = mean_absolute_error(y_test, y_pred_rf)
print(f'Random Forest MAE on players_22: {mae_rf}')

"""evaluating the XGBoost model (best_xgb_model) on the 'players_22'"""

# Evaluate the XGBoost model on 'players_22' data
y_pred_xgb = best_xgb_model.predict(X_test_scaled)
mae_xgb = mean_absolute_error(y_test, y_pred_xgb)
print(f'XGBoost MAE on players_22: {mae_xgb}')

"""evaluating the Gradient Boosting model (best_gb_model) on the 'players_22'"""

# Evaluate the Gradient Boosting model on 'players_22' data
y_pred_gb = best_gb_model.predict(X_test_scaled)
mae_gb = mean_absolute_error(y_test, y_pred_gb)
print(f'Gradient Boosting MAE on players_22: {mae_gb}')

"""evaluating the ensemble model (ensemble_model) on the 'players_22' dataset"""

# Evaluate the Ensemble model on 'players_22' data
y_pred_ensemble = ensemble_model.predict(X_test_scaled)
mae_ensemble = mean_absolute_error(y_test, y_pred_ensemble)
print(f'Ensemble Model MAE on players_22: {mae_ensemble}')

"""comparing the Mean Absolute Error (MAE) values of different models (Random Forest, XGBoost, and Gradient Boosting) to determine which model performed the best on the 'players_22' dataset"""

# Compare MAE values to select the best model
best_model = None
best_mae = float('inf')

if mae_rf < best_mae:
    best_model = "Random Forest"
    best_mae = mae_rf

if mae_xgb < best_mae:
    best_model = "XGBoost"
    best_mae = mae_xgb

if mae_gb < best_mae:
    best_model = "Gradient Boosting"
    best_mae = mae_gb

print(f'The best model for "players_22" data is: {best_model} with MAE: {best_mae}')

import pickle

# Replace 'best_rf_model' with your selected best model (Random Forest, XGBoost, or Gradient Boosting)
best_model = best_rf_model

# Define the filename for the pickle file
filename = '/content/drive/My Drive/Colab Notebooks/mycopy/model.pkl'

# Save the best model to a pickle file
with open(filename, 'wb') as file:
    pickle.dump(best_model, file)

print(f"Best model saved to {filename}")
