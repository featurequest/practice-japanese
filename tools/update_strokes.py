"""tools/update_strokes.py — Download latest KanjiVG and regenerate stroke data."""
import json
import os
import shutil
import sys
import tempfile
import urllib.request
import zipfile


def run_update_strokes():
    """Download latest KanjiVG release and regenerate stroke data."""
    api_url = "https://api.github.com/repos/KanjiVG/kanjivg/releases/latest"
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cache_dir = os.path.join(project_root, ".kanjivg_cache")

    print("Finding latest KanjiVG release...")
    try:
        req = urllib.request.Request(api_url, headers={"Accept": "application/vnd.github+json"})
        with urllib.request.urlopen(req) as resp:
            release = json.loads(resp.read())
        url = None
        for asset in release.get("assets", []):
            if asset["name"].endswith("-all.zip"):
                url = asset["browser_download_url"]
                break
        if not url:
            print("Error: No '-all.zip' asset found in latest KanjiVG release")
            sys.exit(1)
    except Exception as e:
        print(f"Error finding KanjiVG release: {e}")
        sys.exit(1)

    print(f"Downloading {url}...")
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        urllib.request.urlretrieve(url, tmp_path)
    except Exception as e:
        print(f"Error downloading KanjiVG: {e}")
        os.unlink(tmp_path)
        sys.exit(1)

    print(f"Extracting to {cache_dir}...")
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
    os.makedirs(cache_dir)
    with zipfile.ZipFile(tmp_path) as zf:
        for member in zf.namelist():
            if member.endswith(".svg"):
                filename = os.path.basename(member)
                with zf.open(member) as src, open(os.path.join(cache_dir, filename), "wb") as dst:
                    dst.write(src.read())
    os.unlink(tmp_path)

    print("Regenerating stroke data...")
    from tools.generate_strokes_from_kanjivg import (
        HIRAGANA_CHARS, KATAKANA_CHARS, SMALL_HIRAGANA, SMALL_KATAKANA,
        generate_stroke_file,
    )

    out_h = os.path.join(project_root, "data", "strokes", "hiragana.py")
    hiragana_code = generate_stroke_file(HIRAGANA_CHARS, SMALL_HIRAGANA, "hiragana", cache_dir)
    with open(out_h, "w") as f:
        f.write(hiragana_code)
    print(f"  Written to {out_h}")

    out_k = os.path.join(project_root, "data", "strokes", "katakana.py")
    katakana_code = generate_stroke_file(KATAKANA_CHARS, SMALL_KATAKANA, "katakana", cache_dir)
    with open(out_k, "w") as f:
        f.write(katakana_code)
    print(f"  Written to {out_k}")

    print("Done! Run 'python -m pytest tests/test_strokes.py -v' to verify.")
