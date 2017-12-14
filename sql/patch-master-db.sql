-- Patches a database that is using the master checkout of the
-- swefreq.sql schema definition to the develop version.

-- Add some unique constraints
ALTER TABLE study ADD
    CONSTRAINT UNIQUE (pi_email, title);
ALTER TABLE dataset_version ADD
    CONSTRAINT UNIQUE (dataset_pk, version);
ALTER TABLE collection ADD
    CONSTRAINT UNIQUE (name);
ALTER TABLE sample_set ADD
    CONSTRAINT UNIQUE (dataset_pk, collection_pk);
ALTER TABLE dataset_file ADD
    CONSTRAINT UNIQUE (uri);

-- Add user.identity and user.identity_type

ALTER TABLE user
    ADD COLUMN (
    identity            VARCHAR(100),
    identity_type       ENUM ('google', 'elixir')),
    ADD CONSTRAINT
    UNIQUE (identity, identity_type);

-- Fill the above with existing data

UPDATE user
SET identity_type = 'google';

UPDATE user
SET identity = email;

-- Set those two columns as "NOT NULL"
ALTER TABLE user
MODIFY COLUMN
    identity            VARCHAR(100)    NOT NULL,
MODIFY COLUMN
    identity_type       ENUM ('google', 'elixir')
                                        NOT NULL;
