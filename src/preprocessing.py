
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
from config import (
    DATA_PATH, COLS_TO_DROP, CATEGORICAL_COLS,
    NUMERICAL_COLS, TARGET_ATTRITION
)


def load_data():
    df = pd.read_csv(DATA_PATH)
    print(f" Data Loaded: {df.shape[0]} rows, {df.shape[1]} columns")
    return df


def drop_useless_columns(df):
  
    df = df.drop(columns=[col for col in COLS_TO_DROP if col in df.columns])
    print(f" Dropped useless columns: {COLS_TO_DROP}")
    return df


def handle_missing_values(df):
    
    missing = df.isnull().sum()
    missing = missing[missing > 0]

    if missing.empty:
        print(" No missing values found!")
    else:
        print(f"Missing values found:\n{missing}")
        # Fill numerical with median
        for col in NUMERICAL_COLS:
            if col in df.columns and df[col].isnull().any():
                df[col].fillna(df[col].median(), inplace=True)
        # Fill categorical with mode
        for col in CATEGORICAL_COLS:
            if col in df.columns and df[col].isnull().any():
                df[col].fillna(df[col].mode()[0], inplace=True)

    return df


def encode_target(df):
    """Encode Attrition: Yes=1, No=0."""
    df[TARGET_ATTRITION] = df[TARGET_ATTRITION].map({"Yes": 1, "No": 0})
    print(f" Target encoded then Attrition: Yes=1, No=0")
    print(f"   Attrition rate: {df[TARGET_ATTRITION].mean():.2%}")
    return df


def encode_categoricals(df):
    """Label encode categorical columns."""
    le = LabelEncoder()
    for col in CATEGORICAL_COLS:
        if col in df.columns:
            df[col] = le.fit_transform(df[col].astype(str))
    print(f"Categorical columns encoded: {CATEGORICAL_COLS}")
    return df


def scale_numerical(df):
   
    scaler = StandardScaler()
    cols_to_scale = [col for col in NUMERICAL_COLS if col in df.columns]
    df[cols_to_scale] = scaler.fit_transform(df[cols_to_scale])
    print(f" Numerical columns scaled ({len(cols_to_scale)} columns)")
    return df, scaler


def preprocess(scale=True):
    """
    Full preprocessing pipeline.
    Returns:
        df_processed : cleaned & encoded DataFrame
        scaler       : fitted StandardScaler (or None)
    """
    df = load_data()
    df = drop_useless_columns(df)
    df = handle_missing_values(df)
    df = encode_target(df)
    df = encode_categoricals(df)

    scaler = None
    if scale:
        df, scaler = scale_numerical(df)

    print(f"\n Preprocessing Done .... Final shape: {df.shape}")
    return df, scaler


if __name__ == "__main__":
    df, scaler = preprocess()
    print(df.head())
