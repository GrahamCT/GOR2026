import os
import shutil
import glob
from datetime import date
import pyodbc
import openpyxl
from dotenv import load_dotenv

DOWNLOADS = os.path.join(os.path.expanduser("~"), "Downloads")
DEST = r"\\CTI-AZURE-SQL1\Backup"

PATTERNS = [
    ("export_export-bookreport_*.csv", "export_export-bookreport.csv"),
    ("export_Export-establishmentReport_*.csv", "export_Export-establishmentReport.csv"),
]

def newest_match(folder: str, pattern: str) -> str | None:
    matches = glob.glob(os.path.join(folder, pattern))
    if not matches:
        return None
    # Pick most recently modified (in case there are multiple)
    return max(matches, key=os.path.getmtime)

def main():
    os.makedirs(DEST, exist_ok=True)

    renamed_files = []

    # 1 + 2: find in Downloads and rename to fixed names
    for pattern, fixed_name in PATTERNS:
        src = newest_match(DOWNLOADS, pattern)
        if not src:
            print(f"❌ Not found in Downloads: {pattern}")
            return

        fixed_path = os.path.join(DOWNLOADS, fixed_name)

        # If fixed name already exists in Downloads, remove it to allow rename
        if os.path.exists(fixed_path):
            os.remove(fixed_path)

        os.rename(src, fixed_path)
        print(f"✅ Renamed: {os.path.basename(src)} -> {fixed_name}")
        renamed_files.append(fixed_path)

    # 3 + 4: delete old copies in DEST, then copy new ones across
    for src_path in renamed_files:
        dest_path = os.path.join(DEST, os.path.basename(src_path))

        if os.path.exists(dest_path):
            os.remove(dest_path)
            print(f"🗑️ Removed existing in DEST: {os.path.basename(dest_path)}")

        shutil.copy2(src_path, dest_path)
        print(f"📄 Copied to DEST: {dest_path}")

    # Run spFullWeeklyReport and copy results to clipboard
    load_dotenv()
    conn_str = os.environ["TUG_CONN_STRING"]
    print("⏳ Running spFullWeeklyReport...")
    with pyodbc.connect(conn_str) as conn:
        cursor = conn.execute("EXEC spFullWeeklyReport")
        while cursor.description is None:
            if not cursor.nextset():
                raise RuntimeError("spFullWeeklyReport returned no result set")
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()

    today = date.today()
    filename = f"Booking_report_{today.year}_{today.strftime('%B')}_{today.strftime('%d')}.xlsx"
    filepath = os.path.join(DOWNLOADS, filename)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(columns)
    for row in rows:
        ws.append([v if v is not None else "" for v in row])
    wb.save(filepath)
    print(f"📊 {len(rows)} rows written to {filepath}")

    print("🎉 Done.")

if __name__ == "__main__":
    print("Processing Started...")
    main()
