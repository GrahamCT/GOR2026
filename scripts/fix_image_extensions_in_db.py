"""
Fix partner image paths in DB where the file was converted from .png/.jpeg to .jpg.
Only updates a record when:
  - DB path ends in .png or .jpeg
  - The corresponding .jpg file exists on disk
  - The original .png/.jpeg no longer exists (i.e. was replaced by the batch script)
"""
import os
from pathlib import Path
from dotenv import load_dotenv
import pyodbc

load_dotenv(dotenv_path=".env")

CONN_STRING = os.getenv("GOR_CONNECTION")
STATIC_DIR = Path("app/static")


def needs_update(db_path: str) -> str | None:
    """Return the corrected path if the file was renamed to .jpg, else None."""
    if not db_path:
        return None
    suffix = Path(db_path).suffix.lower()
    if suffix not in (".png", ".jpeg"):
        return None
    jpg_path = STATIC_DIR / Path(db_path).with_suffix(".jpg")
    orig_path = STATIC_DIR / db_path
    if jpg_path.exists() and not orig_path.exists():
        return str(Path(db_path).with_suffix(".jpg"))
    return None


with pyodbc.connect(CONN_STRING) as conn:
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, partner_name, logo_image, landing_image FROM book_partner "
        "WHERE logo_image IS NOT NULL OR landing_image IS NOT NULL"
    )
    rows = cursor.fetchall()

    updates = []
    for row in rows:
        pid, name, logo, landing = row
        new_logo = needs_update(logo)
        new_landing = needs_update(landing)
        if new_logo or new_landing:
            updates.append((pid, name, logo, landing, new_logo, new_landing))

    if not updates:
        print("No DB records need updating.")
    else:
        print(f"{'ID':>4}  {'Partner':<40}  {'Field':<10}  {'Old':<55}  ->  New")
        print("-" * 160)
        for pid, name, logo, landing, new_logo, new_landing in updates:
            if new_logo:
                print(f"{pid:>4}  {name:<40}  {'logo':<10}  {logo:<55}  ->  {new_logo}")
                cursor.execute(
                    "UPDATE book_partner SET logo_image = ? WHERE id = ?",
                    (new_logo, pid)
                )
            if new_landing:
                print(f"{pid:>4}  {name:<40}  {'landing':<10}  {landing:<55}  ->  {new_landing}")
                cursor.execute(
                    "UPDATE book_partner SET landing_image = ? WHERE id = ?",
                    (new_landing, pid)
                )
        conn.commit()
        print(f"\n{len(updates)} record(s) updated.")
