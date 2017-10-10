-- Patches a database that is using the master checkout of the
-- swefreq.sql schema definition to the develop version.

-- TODO: Rename user_log to user_access_log
-- TODO: Create user_consent_log
-- TODO: Create user_download_log
-- TODO: Add unique constraint on linkhash.hash
-- TODO: Remove "consent" and "download" enums from dataset_access_log
-- TODO: Remove has_concented from views
