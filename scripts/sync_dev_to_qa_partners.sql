-- ============================================================
-- Sync book_partner + book_branch: gor_dev_26 --> gor_QA
-- Updates existing rows, inserts rows that are missing in QA.
-- Run connected to the same SQL Server instance that hosts both DBs.
-- ============================================================

USE gor_QA;
GO

BEGIN TRANSACTION;

-- ============================================================
-- 1. book_partner
-- ============================================================

SET IDENTITY_INSERT book_partner ON;

MERGE INTO book_partner AS tgt
USING gor_dev_26.dbo.book_partner AS src
ON tgt.id = src.id

WHEN MATCHED THEN UPDATE SET
    tgt.partner_name     = src.partner_name,
    tgt.logo_image       = src.logo_image,
    tgt.landing_image    = src.landing_image,
    tgt.partner_write_up = src.partner_write_up,
    tgt.partner_offer    = src.partner_offer,
    tgt.book_category_id = src.book_category_id,
    tgt.isActive         = src.isActive,
    tgt.create_date      = src.create_date

WHEN NOT MATCHED BY TARGET THEN INSERT
    (id, partner_name, logo_image, landing_image, partner_write_up,
     partner_offer, book_category_id, isActive, create_date)
VALUES
    (src.id, src.partner_name, src.logo_image, src.landing_image,
     src.partner_write_up, src.partner_offer, src.book_category_id,
     src.isActive, src.create_date);

SET IDENTITY_INSERT book_partner OFF;

PRINT CONCAT('book_partner synced. Rows affected: ', @@ROWCOUNT);

-- ============================================================
-- 2. book_branch
-- ============================================================

SET IDENTITY_INSERT book_branch ON;

MERGE INTO book_branch AS tgt
USING gor_dev_26.dbo.book_branch AS src
ON tgt.id = src.id

WHEN MATCHED THEN UPDATE SET
    tgt.partner_id   = src.partner_id,
    tgt.branch_name  = src.branch_name,
    tgt.address      = src.address,
    tgt.province     = src.province

WHEN NOT MATCHED BY TARGET THEN INSERT
    (id, partner_id, branch_name, address, province)
VALUES
    (src.id, src.partner_id, src.branch_name, src.address, src.province);

SET IDENTITY_INSERT book_branch OFF;

PRINT CONCAT('book_branch synced. Rows affected: ', @@ROWCOUNT);

COMMIT TRANSACTION;
PRINT 'Done.';
