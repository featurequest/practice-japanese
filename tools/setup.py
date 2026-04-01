"""tools/setup.py — Check prerequisites and auto-download missing data."""
import os
import subprocess
import sys
from pathlib import Path


def run_setup():
    """Check all prerequisites; auto-build vocabulary data if absent."""
    project_root = Path(__file__).parent.parent
    all_ok = True

    # 1. Font
    font_path = project_root / "fonts" / "KleeOne-SemiBold.ttf"
    if font_path.exists():
        print("Font (KleeOne)       \u2713 bundled")
    else:
        print(f"Font (KleeOne)       \u2717 missing at {font_path}")
        all_ok = False

    # 2. Vocabulary data
    vocab_path = project_root / "data" / "vocabulary.json"
    if vocab_path.exists():
        import json
        with open(vocab_path, encoding="utf-8") as f:
            data = json.load(f)
        print(f"Vocabulary data      \u2713 {vocab_path.name} ({len(data)} words)")
    else:
        print("Vocabulary data      \u2717 missing \u2014 building now...")
        result = subprocess.run(
            [sys.executable, str(project_root / "tools" / "build_jlpt_vocabulary.py")],
            cwd=str(project_root),
        )
        if result.returncode != 0:
            print("  Error: failed to build vocabulary data.")
            all_ok = False
        else:
            print("  Done.")

    # 3. Python packages
    missing = []
    for pkg in ["reportlab", "pykakasi"]:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        print(f"Python packages      \u2717 missing: {', '.join(missing)}")
        print("  Run: pip install -r requirements.txt")
        all_ok = False
    else:
        print("Python packages      \u2713 reportlab, pykakasi")

    print()
    if all_ok:
        print("All prerequisites satisfied.")
    else:
        print("Setup incomplete. Fix the issues above.")
        sys.exit(1)
