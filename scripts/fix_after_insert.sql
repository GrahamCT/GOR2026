-- ============================================================
-- Run after bulk insert to fix slow performance
-- ============================================================

-- 1. Update statistics on both tables (stale stats = bad query plans)
UPDATE STATISTICS book_partner;
UPDATE STATISTICS book_branch;

-- 2. Check if index exists on book_branch.partner_id
--    (FK columns without an index cause table scans on every join)
SELECT
    i.name AS index_name,
    COL_NAME(ic.object_id, ic.column_id) AS column_name
FROM sys.indexes i
JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
WHERE i.object_id = OBJECT_ID('book_branch')
ORDER BY i.index_id;

-- 3. If no index on partner_id appears above, create one:
-- (comment out if it already exists)
IF NOT EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE object_id = OBJECT_ID('book_branch')
    AND name = 'IX_book_branch_partner_id'
)
BEGIN
    CREATE INDEX IX_book_branch_partner_id ON book_branch (partner_id);
    PRINT 'Index created on book_branch.partner_id';
END
ELSE
    PRINT 'Index already exists';

-- 4. Check for any open transactions (shouldn't be any but good to verify)
SELECT session_id, open_transaction_count, status, command, blocking_session_id
FROM sys.dm_exec_requests
WHERE open_transaction_count > 0;
