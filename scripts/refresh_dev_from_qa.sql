-- ============================================================
-- Refresh GOR_DEV_26 from GOR_QA (production copy)
-- Safe to run entire script in one pass
-- ============================================================

DECLARE @BackupFile   NVARCHAR(500) = N'E:\Program Files\Microsoft SQL Server\MSSQL13.MSSQLSERVER\MSSQL\Backup\GOR_QA_for_dev.bak';
DECLARE @DataFile     NVARCHAR(500) = N'E:\Program Files\Microsoft SQL Server\MSSQL13.MSSQLSERVER\MSSQL\DATA\GOR_DEV_26.mdf';
DECLARE @LogFile      NVARCHAR(500) = N'E:\Program Files\Microsoft SQL Server\MSSQL13.MSSQLSERVER\MSSQL\DATA\GOR_DEV_26.ldf';

-- ============================================================
-- STEP 1: Back up GOR_QA
-- ============================================================

PRINT 'Backing up GOR_QA...';

BACKUP DATABASE GOR_QA
TO DISK = @BackupFile
WITH FORMAT,
     INIT,
     NAME = N'GOR_QA Full Backup for DEV refresh',
     STATS = 10;

PRINT 'Backup complete.';

-- ============================================================
-- STEP 2: Kill connections to GOR_DEV_26 & restore
-- ============================================================

PRINT 'Dropping connections to GOR_DEV_26...';

ALTER DATABASE GOR_DEV_26 SET SINGLE_USER WITH ROLLBACK IMMEDIATE;

PRINT 'Restoring GOR_QA over GOR_DEV_26...';

RESTORE DATABASE GOR_DEV_26
FROM DISK = @BackupFile
WITH REPLACE,
     RECOVERY,
     MOVE N'GOR'     TO @DataFile,
     MOVE N'GOR_log' TO @LogFile,
     STATS = 10;

ALTER DATABASE GOR_DEV_26 SET MULTI_USER;

PRINT 'Done. GOR_DEV_26 is now a fresh copy of GOR_QA.';
