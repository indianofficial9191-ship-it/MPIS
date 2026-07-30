import importlib
from pathlib import Path

out = []
try:
    m = importlib.import_module("mpis")
    out.append(f"IMPORT_OK {m.__version__}")
except Exception as e:
    out.append(f"IMPORT_FAIL {e}")

root = Path(__file__).resolve().parents[1]
checks = [
    'pyproject.toml',
    'README.md',
    'src/mpis/__init__.py',
    'src/mpis/config/settings.py',
    'tests/test_imports.py',
    '.github/workflows/python-package.yml',
]
for p in checks:
    out.append(f"{p} -> { (root / p).exists() }")

print('\n'.join(out))
