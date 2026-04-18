"""
One-time batch resize of partner images.
- landing_*  -> max 1280px wide, JPEG q=82
- logo_*     -> max 220x220px,   JPEG q=85
Originals are moved to static/partners/originals/ before overwriting.
"""
import shutil
from pathlib import Path
from PIL import Image

PARTNERS_DIR = Path(__file__).parent.parent / "app" / "static" / "partners"
ORIGINALS_DIR = PARTNERS_DIR / "originals"
ORIGINALS_DIR.mkdir(exist_ok=True)

LANDING_MAX_W = 1280
LOGO_MAX = 220
JPEG_QUALITY_LANDING = 82
JPEG_QUALITY_LOGO = 85
EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def convert(src: Path, max_size: tuple[int, int], quality: int) -> None:
    backup = ORIGINALS_DIR / src.name
    if not backup.exists():
        shutil.copy2(src, backup)

    with Image.open(src) as img:
        orig_w, orig_h = img.size
        img.thumbnail(max_size, Image.LANCZOS)
        new_w, new_h = img.size

        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        dest = src.with_suffix(".jpg")
        img.save(dest, "JPEG", quality=quality, optimize=True)

    # Remove original if it was a different format (e.g. .png -> .jpg)
    if src.suffix.lower() != ".jpg" and src != dest:
        src.unlink()

    orig_kb = backup.stat().st_size / 1024
    new_kb = dest.stat().st_size / 1024
    print(f"  {src.name:55s}  {orig_w}x{orig_h} {orig_kb:>7.0f}KB  ->  {new_w}x{new_h} {new_kb:>6.0f}KB")


def main() -> None:
    landings = [
        f for f in PARTNERS_DIR.iterdir()
        if f.stem.startswith("landing_") and f.suffix.lower() in EXTENSIONS
    ]
    logos = [
        f for f in PARTNERS_DIR.iterdir()
        if f.stem.startswith("logo_") and f.suffix.lower() in EXTENSIONS
    ]

    print(f"\n=== Landing images ({len(landings)} files, max {LANDING_MAX_W}px wide) ===")
    for f in sorted(landings):
        convert(f, (LANDING_MAX_W, LANDING_MAX_W * 2), JPEG_QUALITY_LANDING)

    print(f"\n=== Logo images ({len(logos)} files, max {LOGO_MAX}x{LOGO_MAX}px) ===")
    for f in sorted(logos):
        convert(f, (LOGO_MAX, LOGO_MAX), JPEG_QUALITY_LOGO)

    print("\nDone. Originals saved to:", ORIGINALS_DIR)


if __name__ == "__main__":
    main()
