import pandas as pd
def load_dataset():
    data = pd.read_csv(r"data/Custom_Crops_yield_Historical_Dataset.csv")
    x = data.drop("Yield_kg_per_ha",axis=1)
    y = data["Yield_kg_per_ha"]
    return x,y
def preview_data():
    data = pd.read_csv(r"data/Custom_Crops_yield_Historical_Dataset.csv")
    print("\nCustom_Crops_yield_Historical_Dataset preview (first 5 rows):\n")
    print(data.head())
    print("\nDataset info:\n")
    print(data.info())
    print("\nMissing values:\n")
    print(data.isnull().sum())
if __name__ == "__main__":
    load_dataset()
    preview_data()