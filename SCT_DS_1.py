import zipfile
import pandas as pd
import matplotlib.pyplot as plt
import os

ZIP_PATH = "C:/Users/cjani/Downloads/API_SP.POP.TOTL_DS2_en_csv_v2_34.zip"


def load_all_csv_from_zip(zip_path):
    """
    Loads ALL CSV files inside a ZIP archive into a dictionary of DataFrames.
    Key = file name
    Value = pandas DataFrame
    """
    dataframes = {}

    with zipfile.ZipFile(zip_path, "r") as z:
        for file in z.namelist():
            if file.lower().endswith(".csv"):
                with z.open(file) as f:
                    # Main data files have 4 rows of metadata to skip
                    # Metadata files don't need skipping
                    if "Metadata" in file:
                        df = pd.read_csv(f, encoding='utf-8-sig')
                    else:
                        # For main data files, skip first 4 rows (header will be on row 5, which becomes row 0 after skipping)
                        df = pd.read_csv(f, skiprows=4, encoding='utf-8-sig')
                    dataframes[os.path.basename(file)] = df

    return dataframes


# -------- LOAD DATA --------
datasets = load_all_csv_from_zip(ZIP_PATH)

# Choose the main data file (not a metadata file)
# Prioritize files that don't have "Metadata" in their name
main_data_file = None
for filename, df in datasets.items():
    if "Metadata" not in filename:
        main_data_file = filename
        break

if main_data_file:
    df = datasets[main_data_file]
    print(f"Using dataset: {main_data_file}")
else:
    # Fallback to first dataset if no main data file found
    df = list(datasets.values())[0]
    print(f"Using first dataset: {list(datasets.keys())[0]}")


# -------- CONFIG: Set columns to visualize --------
# Set to None if you don't want to visualize that type
categorical_column = None  # Set to column name, or None to create from continuous data
continuous_column = "2020"           # Example: ages, population, years, numeric values

# Create a categorical variable by binning continuous data (if categorical_column is None)
# This creates population size categories for better visualization
CREATE_CATEGORICAL_FROM_CONTINUOUS = True  # Set to True to bin continuous data into categories
CONTINUOUS_COLUMN_FOR_BINNING = "2020"     # Column to use for creating categories


# -------- VISUALIZATION FUNCTIONS --------
def visualize_continuous(series, column_name):
    """
    Creates a histogram for continuous/numeric variables (e.g., ages, population values).
    Shows the distribution of the data.
    """
    # Drop missing values
    series_clean = series.dropna()
    
    plt.figure(figsize=(10, 6))
    plt.hist(series_clean, bins=30, edgecolor='black', alpha=0.7, color='steelblue')
    plt.title(f"Distribution of {column_name}", fontsize=14, fontweight='bold')
    plt.xlabel(column_name, fontsize=12)
    plt.ylabel("Frequency", fontsize=12)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.show()
    
    # Print summary statistics
    print(f"\n{column_name} - Summary Statistics:")
    print(f"  Count: {series_clean.count()}")
    print(f"  Mean: {series_clean.mean():.2f}")
    print(f"  Median: {series_clean.median():.2f}")
    print(f"  Min: {series_clean.min():.2f}")
    print(f"  Max: {series_clean.max():.2f}")
    print(f"  Std Dev: {series_clean.std():.2f}")


def visualize_categorical(series, column_name, top_n=30):
    """
    Creates a bar chart for categorical variables (e.g., genders, countries, categories).
    Shows the frequency distribution of each category.
    """
    # Drop missing values
    series_clean = series.dropna()
    
    # Get value counts and limit to top N
    counts = series_clean.value_counts().head(top_n)
    
    plt.figure(figsize=(12, 6))
    counts.plot(kind="bar", color='steelblue', edgecolor='black', alpha=0.8)
    plt.title(f"Distribution of {column_name} (Top {len(counts)})", fontsize=14, fontweight='bold')
    plt.xlabel(column_name, fontsize=12)
    plt.ylabel("Frequency", fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.show()
    
    # Print summary
    print(f"\n{column_name} - Summary:")
    print(f"  Total unique values: {series_clean.nunique()}")
    print(f"  Total count: {series_clean.count()}")
    print(f"\n  Top {min(10, len(counts))} values:")
    for idx, (value, count) in enumerate(counts.head(10).items(), 1):
        print(f"    {idx}. {value}: {count}")


# -------- VISUALIZE CONTINUOUS VARIABLE (HISTOGRAM) --------
if continuous_column:
    if continuous_column not in df.columns:
        print(f"Warning: Continuous column '{continuous_column}' not found. Available columns: {df.columns.tolist()}")
    else:
        if pd.api.types.is_numeric_dtype(df[continuous_column]):
            print(f"\n{'='*60}")
            print(f"Visualizing CONTINUOUS variable: {continuous_column}")
            print(f"{'='*60}")
            visualize_continuous(df[continuous_column], continuous_column)
        else:
            print(f"Warning: '{continuous_column}' is not a numeric column. Skipping continuous visualization.")


# -------- CREATE CATEGORICAL VARIABLE FROM CONTINUOUS (OPTIONAL) --------
if CREATE_CATEGORICAL_FROM_CONTINUOUS and CONTINUOUS_COLUMN_FOR_BINNING in df.columns:
    # Bin the continuous data into categories for better categorical visualization
    continuous_data = df[CONTINUOUS_COLUMN_FOR_BINNING].dropna()
    
    # Create population size categories (adjust bins based on your data)
    if CONTINUOUS_COLUMN_FOR_BINNING == "2020" or pd.api.types.is_numeric_dtype(df[CONTINUOUS_COLUMN_FOR_BINNING]):
        # Use percentiles to create meaningful bins
        bins = [0, 1e6, 5e6, 10e6, 50e6, 100e6, 500e6, float('inf')]
        labels = ['< 1M', '1M - 5M', '5M - 10M', '10M - 50M', '50M - 100M', '100M - 500M', '> 500M']
        categorical_series = pd.cut(continuous_data, bins=bins, labels=labels, include_lowest=True)
        categorical_column_name = f"{CONTINUOUS_COLUMN_FOR_BINNING} (Population Size Categories)"
        
        print(f"\n{'='*60}")
        print(f"Visualizing CATEGORICAL variable: {categorical_column_name}")
        print(f"{'='*60}")
        visualize_categorical(categorical_series, categorical_column_name, top_n=10)
    else:
        print(f"Cannot create categories from non-numeric column: {CONTINUOUS_COLUMN_FOR_BINNING}")

# -------- VISUALIZE CATEGORICAL VARIABLE (BAR CHART) --------
elif categorical_column:
    if categorical_column not in df.columns:
        print(f"Warning: Categorical column '{categorical_column}' not found. Available columns: {df.columns.tolist()}")
    else:
        print(f"\n{'='*60}")
        print(f"Visualizing CATEGORICAL variable: {categorical_column}")
        print(f"{'='*60}")
        visualize_categorical(df[categorical_column], categorical_column)
