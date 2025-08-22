import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Paths to data files
aqi_path = os.path.join('..', 'data', 'delhi_aqi.csv')
waste_path = os.path.join('..', 'data', 'Waste_Management_and_Recycling_India.csv')

# 1. Air Quality Data EDA
print('--- Delhi Air Quality Data EDA ---')
df_aqi = pd.read_csv(aqi_path)
print(df_aqi.info())
print(df_aqi.describe(include='all'))
print('Missing values per column:')
print(df_aqi.isnull().sum())

# Example: Top 5 most polluted locations (by mean AQI)
if 'location' in df_aqi.columns and 'AQI' in df_aqi.columns:
    top_polluted = df_aqi.groupby('location')['AQI'].mean().sort_values(ascending=False).head(5)
    print('Top 5 most polluted locations:')
    print(top_polluted)
    plt.figure(figsize=(8,4))
    sns.barplot(x=top_polluted.index, y=top_polluted.values)
    plt.title('Top 5 Most Polluted Locations (Mean AQI)')
    plt.ylabel('Mean AQI')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# Save cleaned AQI data
df_aqi_clean = df_aqi.dropna()
df_aqi_clean.to_csv(os.path.join('..', 'data', 'delhi_aqi_clean.csv'), index=False)

# 2. Waste Management Data EDA
print('\n--- Waste Management Data EDA ---')
df_waste = pd.read_csv(waste_path)
print(df_waste.info())
print(df_waste.describe(include='all'))
print('Missing values per column:')
print(df_waste.isnull().sum())

# Example: Waste generation by city (if available)
if 'City' in df_waste.columns and 'Waste Generated (tons/day)' in df_waste.columns:
    top_waste = df_waste.groupby('City')['Waste Generated (tons/day)'].mean().sort_values(ascending=False).head(5)
    print('Top 5 cities by waste generation:')
    print(top_waste)
    plt.figure(figsize=(8,4))
    sns.barplot(x=top_waste.index, y=top_waste.values)
    plt.title('Top 5 Cities by Waste Generation')
    plt.ylabel('Waste Generated (tons/day)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# If Delhi-specific data exists, filter and save
if 'City' in df_waste.columns:
    df_waste_delhi = df_waste[df_waste['City'].str.lower().str.contains('delhi')]
    df_waste_delhi_clean = df_waste_delhi.dropna()
    df_waste_delhi_clean.to_csv(os.path.join('..', 'data', 'waste_bins_clean.csv'), index=False)
    print(f"Delhi waste records saved: {len(df_waste_delhi_clean)}")
else:
    df_waste_clean = df_waste.dropna()
    df_waste_clean.to_csv(os.path.join('..', 'data', 'waste_bins_clean.csv'), index=False)
    print(f"Waste records saved: {len(df_waste_clean)}")

print('\nEDA and cleaning complete. Cleaned files: delhi_aqi_clean.csv, waste_bins_clean.csv')
