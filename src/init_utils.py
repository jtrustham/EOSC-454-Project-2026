from pathlib import Path
import numpy as np
import pandas as pd

#Fix path to data directory
NOTEBOOK_DIR = Path().resolve()
DATA_DIR = NOTEBOOK_DIR.parent / "data" / "raw"

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

def read_obs_mag(filename):
    data = np.loadtxt(DATA_DIR / filename, skiprows=3)

    df = pd.DataFrame(data, columns=["X", "Y", "Z", "MAG", "ERR"])
    return df

def read_topo(filename):
    data = np.loadtxt(DATA_DIR / filename, skiprows=1)

    df = pd.DataFrame(data, columns=["X", "Y", "Z"])
    return df

def read_model(filename):
    data = np.loadtxt(DATA_DIR / filename)

    df = pd.DataFrame(data, columns=['sus'])
    return df

def read_tensor_mesh(file):
    with open(file, "r") as f:
        lines = [l.strip() for l in f if l.strip()]

    nx, ny, nz = map(int, lines[0].split())
    x0, y0, z0 = map(float, lines[1].split())

    def parse(line):
        n, v = line.split("*")
        return int(n), float(v)

    nx2, dx = parse(lines[2])
    ny2, dy = parse(lines[3])
    nz2, dz = parse(lines[4])

    assert (nx, ny, nz) == (nx2, ny2, nz2)

    return {
        "nx": nx, "ny": ny, "nz": nz,
        "x0": x0, "y0": y0, "z0": z0,
        "dx": dx, "dy": dy, "dz": dz
    }
