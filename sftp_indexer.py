import csv
import os
import re
import shutil
from datetime import datetime

import pyodbc
from dotenv import load_dotenv
from tqdm import tqdm

BACKUP_DIR = r"C:\CODE\GOR_BUBBLE_SFTP\data\backup"
PROCESSED_DIR = os.path.join(BACKUP_DIR, "processed")
BATCH_SIZE = 500

CREATE_TABLE_SQL = """
IF NOT EXISTS (
    SELECT * FROM sys.objects
    WHERE object_id = OBJECT_ID(N'sftp_file_index') AND type = 'U'
)
BEGIN
    CREATE TABLE sftp_file_index (
        id             INT IDENTITY(1,1) PRIMARY KEY,
        file_key       DATETIME      NOT NULL,
        file_name      VARCHAR(255)  NOT NULL,
        row_num        INT           NOT NULL,
        CustomerNumber VARCHAR(100),
        FirstName      VARCHAR(255),
        LastName       VARCHAR(255),
        MobileNumber   VARCHAR(100),
        Email          VARCHAR(255),
        Benefits       VARCHAR(MAX),
        Mandatenumber  VARCHAR(100),
        ActivationDate VARCHAR(100),
        Action         VARCHAR(100),
        indexed_at     DATETIME DEFAULT GETDATE()
    )
END
"""

ALTER_BENEFITS_SQL = """
IF EXISTS (
    SELECT * FROM sys.columns
    WHERE object_id = OBJECT_ID(N'sftp_file_index')
      AND name = 'Benefits'
      AND max_length != -1
)
    ALTER TABLE sftp_file_index ALTER COLUMN Benefits VARCHAR(MAX)
"""

CREATE_IDX_CUSTOMER = """
IF NOT EXISTS (
    SELECT * FROM sys.indexes
    WHERE name = 'ix_sftp_customer'
      AND object_id = OBJECT_ID('sftp_file_index')
)
    CREATE INDEX ix_sftp_customer ON sftp_file_index (CustomerNumber)
"""

CREATE_IDX_FILE_KEY = """
IF NOT EXISTS (
    SELECT * FROM sys.indexes
    WHERE name = 'ix_sftp_file_key'
      AND object_id = OBJECT_ID('sftp_file_index')
)
    CREATE INDEX ix_sftp_file_key ON sftp_file_index (file_key)
"""

INSERT_SQL = """
INSERT INTO sftp_file_index
    (file_key, file_name, row_num,
     CustomerNumber, FirstName, LastName, MobileNumber,
     Email, Benefits, Mandatenumber, ActivationDate, Action)
VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
"""

# Matches: TUGoRhinoData_2025-04-10 15_59_01.csv
FILE_PATTERN = re.compile(r"^TUGoRhinoData_(.+)\.csv$", re.IGNORECASE)


def parse_file_key(filename: str) -> datetime | None:
    m = FILE_PATTERN.match(filename)
    if not m:
        return None
    try:
        return datetime.strptime(m.group(1), "%Y-%m-%d %H_%M_%S")
    except ValueError:
        return None


def insert_file(cursor, file_path: str, file_name: str, file_key: datetime) -> int:
    with open(file_path, newline="", encoding="cp1252") as f:
        reader = csv.DictReader(f, delimiter="|")
        rows = []
        for i, row in enumerate(reader, start=1):
            rows.append((
                file_key,
                file_name,
                i,
                row.get("CustomerNumber"),
                row.get("FirstName"),
                row.get("LastName"),
                row.get("MobileNumber"),
                row.get("Email"),
                row.get("Benefits"),
                row.get("Mandatenumber"),
                row.get("ActivationDate"),
                row.get("Action"),
            ))

    cursor.fast_executemany = True
    for start in range(0, len(rows), BATCH_SIZE):
        cursor.executemany(INSERT_SQL, rows[start : start + BATCH_SIZE])

    return len(rows)


def main():
    load_dotenv()
    conn_str = os.environ["TUG_CONN_STRING"]

    os.makedirs(PROCESSED_DIR, exist_ok=True)

    csv_files = [
        f for f in os.listdir(BACKUP_DIR)
        if f.lower().endswith(".csv") and os.path.isfile(os.path.join(BACKUP_DIR, f))
    ]

    with pyodbc.connect(conn_str) as conn:
        cursor = conn.cursor()

        cursor.execute(CREATE_TABLE_SQL)
        cursor.execute(ALTER_BENEFITS_SQL)
        cursor.execute(CREATE_IDX_CUSTOMER)
        cursor.execute(CREATE_IDX_FILE_KEY)
        conn.commit()

        cursor.execute("SELECT DISTINCT file_name FROM sftp_file_index")
        already_indexed = {row[0] for row in cursor.fetchall()}

        total_files = 0
        total_rows = 0
        skipped = 0
        errors = 0

        for file_name in tqdm(csv_files, desc="Indexing files", unit="file"):
            if file_name in already_indexed:
                skipped += 1
                continue

            file_key = parse_file_key(file_name)
            if file_key is None:
                tqdm.write(f"  SKIP (unrecognised name): {file_name}")
                skipped += 1
                continue

            file_path = os.path.join(BACKUP_DIR, file_name)
            try:
                row_count = insert_file(cursor, file_path, file_name, file_key)
                conn.commit()
                shutil.move(file_path, os.path.join(PROCESSED_DIR, file_name))
                total_files += 1
                total_rows += row_count
            except Exception as exc:
                conn.rollback()
                tqdm.write(f"  ERROR ({file_name}): {exc}")
                errors += 1

    print(f"\nDone — {total_files} files indexed, {total_rows:,} rows inserted, "
          f"{skipped} skipped, {errors} errors.")


if __name__ == "__main__":
    main()
