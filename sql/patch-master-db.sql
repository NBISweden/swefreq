-- Patches a database that is using the master checkout of the
-- swefreq.sql schema definition to the develop version.

-- user_log.dataset_pk changes to user_log.dataset_version_pk
-- 1. Insert new column user_log.dataset_version_pk
-- 2. Add foreign constraints
-- 3. Populate column user_log.dataset_version_pk
-- 4. Update dependent views and tables
-- 5. Drop old dataset_pk foreign constraint in user_log
-- 6. Drop column user_log.dataset_pk

-- TODO: Rename user_log to user_access_log
-- TODO: Create user_consent_log
-- TODO: Create user_download_log
-- TODO: Add unique constraint on linkhash.hash
-- TODO: Remove "consent" and "download" enums from dataset_access_log
-- TODO: Remove has_concented from views
