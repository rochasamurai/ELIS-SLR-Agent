"""Minimal test - just load config and gold standard"""

import yaml
import json
from pathlib import Path

print("Test 1: Load benchmark config...")
try:
    with open("configs/benchmark_2_config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    print(f"✓ Config loaded: {config['benchmark']['id']}")
    print(
        f"  Phase 1 databases: {config['execution']['phases']['phase1']['databases']}"
    )
except Exception as e:
    print(f"✗ ERROR: {e}")
    exit(1)

print("\nTest 2: Load gold standard...")
try:
    with open(
        "data/tai_awasthi_2025_references_FINAL.json", "r", encoding="utf-8"
    ) as f:
        gold = json.load(f)
    print(f"✓ Gold standard loaded: {len(gold)} studies")
except Exception as e:
    print(f"✗ ERROR: {e}")
    exit(1)

print("\nTest 3: Check ELIS harvest scripts...")
repo_root = Path.cwd().parents[1]
scripts_dir = repo_root / "scripts"
print(f"  Scripts directory: {scripts_dir}")
print(f"  Exists: {scripts_dir.exists()}")

if scripts_dir.exists():
    harvest_scripts = list(scripts_dir.glob("*_harvest.py"))
    print(f"  Found {len(harvest_scripts)} harvest scripts:")
    for script in harvest_scripts[:5]:
        print(f"    - {script.name}")

print("\n✓ All basic tests passed!")
