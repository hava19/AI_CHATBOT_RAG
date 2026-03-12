"""
Merge LoRA adapter dengan base model Qwen 2.5 7B
"""

from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import os

print("=" * 60)
print("🔄 MERGE LORA DENGAN BASE MODEL")
print("=" * 60)

# Konfigurasi
BASE_MODEL = "Qwen/Qwen2.5-7B-Instruct"
LORA_PATH = "./finetuned-qwen"
OUTPUT_PATH = "./merged-qwen"

# 1. Load base model
print(f"\n📥 Loading base model: {BASE_MODEL}")
print("⚠️  Ini akan download model ~15GB (butuh waktu 10-30 menit)")

base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    torch_dtype=torch.float16,
    device_map="auto",
    trust_remote_code=True
)

tokenizer = AutoTokenizer.from_pretrained(
    BASE_MODEL,
    trust_remote_code=True
)

print("✅ Base model loaded")

# 2. Load LoRA adapter
print(f"\n🔧 Loading LoRA adapter from: {LORA_PATH}")
model = PeftModel.from_pretrained(base_model, LORA_PATH)
print("✅ Adapter loaded")

# 3. Merge
print("\n🔄 Merging adapter with base model...")
merged_model = model.merge_and_unload()
print("✅ Merge completed")

# 4. Save merged model
print(f"\n💾 Saving merged model to: {OUTPUT_PATH}")
merged_model.save_pretrained(OUTPUT_PATH)
tokenizer.save_pretrained(OUTPUT_PATH)
print(f"✅ Model saved")

# 5. Info ukuran
import os
import shutil

size = sum(os.path.getsize(os.path.join(OUTPUT_PATH, f)) for f in os.listdir(OUTPUT_PATH) if os.path.isfile(os.path.join(OUTPUT_PATH, f)))
print(f"\n📊 Ukuran model: {size / 1024**3:.2f} GB")

print("\n✅ SELESAI! Model siap dikonversi ke GGUF")
