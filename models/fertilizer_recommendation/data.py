import pandas as pd
import os
from sklearn.preprocessing import LabelEncoder

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "fertilizer_dataset.csv")

def load_and_preprocess():
    """
    Loads fertilizer dataset, encodes categorical columns,
    and returns dataframe + fitted encoders.
    """
    df = pd.read_csv(DATA_PATH)

    # Encode crop (label column in dataset)
    crop_encoder = LabelEncoder()
    df["crop_encoded"] = crop_encoder.fit_transform(df["label"])

    # Encode fertilizer recommendation (target)
    fertilizer_encoder = LabelEncoder()
    df["fertilizer_encoded"] = fertilizer_encoder.fit_transform(df["Fertilizer_Advice"])

    return df, crop_encoder, fertilizer_encoder
