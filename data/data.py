import pandas as pd
def load_dataset():
    data = pd.read_csv(r"data/Custom_Crops_yield_Historical_Dataset.csv")
    data.columns = data.columns.str.strip().str.lower().str.replace(" ", "_")
    x = data.drop(["state_code","dist_code","total_n_kg","total_p_kg","total_k_kg","yield_kg_per_ha"],axis=1)
    x.columns = x.columns.str.strip().str.lower().str.replace(" ", "_")
    y = data["yield_kg_per_ha"]
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