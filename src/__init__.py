from pathlib import Path
import numpy as np

BASE_DIR = Path(__file__).resolve().parents[1]
OUT_DIR = BASE_DIR / "outputs"

def ensure_dirs():
    (OUT_DIR / "cache").mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "models").mkdir(parents=True, exist_ok=True)

def save_cache(name, **arrays):
    ensure_dirs()
    filepath = OUT_DIR / "cache" / f"{name}.npz"
    np.savez(filepath, **arrays)
    print(f"[saved] {filepath}")

def load_cache(name):
    filepath = OUT_DIR / "cache" / f"{name}.npz"
    return np.load(filepath)

def save_model(name, model):
    ensure_dirs()
    filepath = OUT_DIR / "models" / f"{name}.npy"
    np.save(filepath, model)
    print(f"[saved] {filepath}")

def load_model(name):
    filepath = OUT_DIR / "models" / f"{name}.npy"
    return np.load(filepath)