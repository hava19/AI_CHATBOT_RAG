# convert_data.py
import pandas as pd
from datasets import Dataset
import json

print("📊 Membaca data.jsonl...")
with open('data.jsonl', 'r') as f:
    data = [json.loads(line) for line in f]

print(f"✅ Total data: {len(data)} contoh")
df = pd.DataFrame(data)

# Konversi ke parquet
dataset = Dataset.from_pandas(df)
dataset.to_parquet('training_data.parquet')
print("✅ Data berhasil dikonversi ke training_data.parquet")