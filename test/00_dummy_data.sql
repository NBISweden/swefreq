DELETE FROM user_log WHERE user_pk < 0 OR dataset_pk < 0;
DELETE FROM dataset_access WHERE user_pk < 0 OR dataset_pk < 0;
DELETE FROM user WHERE user_pk < 0;
DELETE FROM dataset_file WHERE dataset_file_pk < 0;
DELETE FROM dataset_version WHERE dataset_pk < 0;
DELETE FROM dataset WHERE dataset_pk < 0;
DELETE FROM sample_set WHERE sample_set_pk < 0;
DELETE FROM study WHERE study_pk < 0;

INSERT INTO study (study_pk, pi_name, pi_email, contact_name, contact_email, title, description, publication_date, ref_doi)
    VALUES (-1, 'PI_STUDY1', 'pi1@example.com', 'Contact Study 1', 'contact1@example.com', 'Study 1', 'Study 1 description', '2017-01-01', 'study1DOI'),
           (-2, 'PI_STUDY2', 'pi2@example.com', 'Contact Study 2', 'contact2@example.com', 'Study 2', 'Study 2 description', '2017-02-01', 'study2DOI');

INSERT INTO sample_set (sample_set_pk, study_pk, ethnicity, collection, sample_size)
    VALUES (-1, -1, 'Ethnicity1', 'Collection1', 1001),
           (-2, -2, 'Ethnicity2', 'Collection2', 1002);

INSERT INTO dataset (dataset_pk, sample_set_pk, short_name, full_name, browser_uri, beacon_uri, avg_seq_depth, seq_type, seq_tech, seq_center, dataset_size)
    VALUES (-1, -1, 'Dataset 1', 'Dataset 1 Long name', 'http://example.com/browser1', 'http://example.com/beacon1', 1.0, 'SeqType1', 'SeqTech1', 'SeqCenter1', 1001),
           (-2, -2, 'Dataset 2', 'Dataset 2 Long name', 'http://example.com/browser2', 'http://example.com/beacon2', 2.0, 'SeqType2', 'SeqTech2', 'SeqCenter2', 1002);

INSERT INTO dataset_version (dataset_version_pk, dataset_pk, version, is_current, description, terms, var_call_ref, available_from, ref_doi)
    VALUES (-1, -1, 'Version 1-1', 1, 'Dataset 1-1, description', 'Dataset 1-1, terms', 'CallRef11', '2017-01-01', 'datset11DOI'),
           (-2, -2, 'Version 2-1', 0, 'Dataset 2-1, description', 'Dataset 2-1, terms', 'CallRef21', '2017-02-01', 'datset21DOI'),
           (-3, -2, 'Version 2-2', 1, 'Dataset 2-2, description', 'Dataset 2-2, terms', 'CallRef22', '2017-02-02', 'datset22DOI'),
           (-4, -2, 'InvVer  2-3', 1, 'Dataset 2-3, description', 'Dataset 2-3, terms', 'CallRef23', '2030-02-03', 'datset23DOI');

INSERT INTO dataset_file(dataset_file_pk, dataset_version_pk, name, uri)
    VALUES (-1, -1, 'File11-1', '/release/file111.txt'),
           (-2, -1, 'File11-2', '/release/file112.txt'),
           (-3, -2, 'File21-1', '/release/file211.txt'),
           (-4, -3, 'File22-1', '/release/file221.txt'),
           (-5, -4, 'File23-1', '/release/file231.txt');

INSERT INTO user(user_pk, name, email, affiliation, country) VALUES
    (-100, 'Not req yet',          'email0',  'i',     ''),
    (-101, 'Requested access',     'email1',  'w1',    ''),
    (-102, 'Approved access',      'email2',  'c1',    ''),
    (-103, 'Denied access',        'email3',  'i',     ''),
    (-104, 'Approved then denied', 'email4',  'i',     ''),
    (-105, 'R->A->D->R',           'email5',  'w1',    ''),
    (-106, 'R->A->D->R->A',        'email6',  'c1',    ''),
    (-107, 'R->A->D->R->D',        'email7',  'i',     ''),
    (-108, 'Combo1 w1 w2',         'email8',  'w1 w2', ''),
    (-109, 'Combo2 w1 c2',         'email9',  'w1 c2', ''),
    (-110, 'Combo3 c1 w2',         'email10', 'c1 w2', ''),
    (-111, 'Combo4 c1 c2',         'email11', 'c1 c2', ''),
    (-112, 'Combo4 w1 i2',         'email12', 'w1 i2', '');

INSERT INTO dataset_access(user_pk, dataset_pk) VALUES
    (-100, -1), (-101, -1), (-102, -1), (-103, -1), (-104, -1), (-105, -1),
    (-106, -1), (-107, -1), (-108, -1), (-108, -2), (-109, -1), (-109, -2),
    (-110, -1), (-110, -2), (-111, -1), (-111, -2), (-112, -1), (-112, -2);

INSERT INTO user_log(user_pk, dataset_pk, action, ts) VALUES
    (-101, -1, 'access_requested', '2017-01-01'),
    (-102, -1, 'access_requested', '2017-01-02'),
    (-103, -1, 'access_requested', '2017-01-03'),
    (-104, -1, 'access_requested', '2017-01-04'),
    (-105, -1, 'access_requested', '2017-01-05'),
    (-106, -1, 'access_requested', '2017-01-06'),
    (-107, -1, 'access_requested', '2017-01-07'),
    (-102, -1, 'access_granted',   '2017-01-08'),
    (-103, -1, 'access_revoked',   '2017-01-09'),
    (-104, -1, 'access_granted',   '2017-01-10'),
    (-104, -1, 'access_revoked',   '2017-01-11'),
    (-105, -1, 'access_granted',   '2017-01-12'),
    (-105, -1, 'access_revoked',   '2017-01-13'),
    (-105, -1, 'access_requested', '2017-01-14'),
    (-106, -1, 'access_granted',   '2017-01-15'),
    (-106, -1, 'access_revoked',   '2017-01-16'),
    (-106, -1, 'access_requested', '2017-01-17'),
    (-106, -1, 'access_granted',   '2017-01-18'),
    (-107, -1, 'access_granted',   '2017-01-19'),
    (-107, -1, 'access_revoked',   '2017-01-20'),
    (-107, -1, 'access_requested', '2017-01-21'),
    (-107, -1, 'access_revoked',   '2017-01-22'),
    (-108, -1, 'access_requested', '2017-01-23'),
    (-108, -2, 'access_requested', '2017-01-24'),
    (-109, -1, 'access_requested', '2017-01-25'),
    (-109, -2, 'access_requested', '2017-01-26'),
    (-109, -2, 'access_granted',   '2017-01-27'),
    (-110, -1, 'access_requested', '2017-01-28'),
    (-110, -2, 'access_requested', '2017-01-29'),
    (-110, -1, 'access_granted',   '2017-01-30'),
    (-111, -1, 'access_requested', '2017-01-31'),
    (-111, -2, 'access_requested', '2017-02-01'),
    (-111, -1, 'access_granted',   '2017-02-02'),
    (-111, -2, 'access_granted',   '2017-02-03'),
    (-112, -1, 'access_requested', '2017-02-04'),
    (-112, -2, 'access_requested', '2017-02-05'),
    (-112, -1, 'access_granted',   '2017-02-06'),
    (-112, -2, 'access_granted',   '2017-02-07'),
    (-112, -2, 'access_revoked',   '2017-02-08');

SELECT "Waiting", user.name, user.affiliation as visibility, user.user_pk,
       dataset_access_waiting.dataset_pk,
       dataset_access_waiting.dataset_access_pk
FROM dataset_access_waiting JOIN user ON (dataset_access_waiting.user_pk = user.user_pk)
WHERE dataset_pk < 0;

SELECT "Current", user.name, user.affiliation as visibility, user.user_pk, dataset_access_current.dataset_pk,
       dataset_access_current.dataset_access_pk
FROM dataset_access_current JOIN user ON (dataset_access_current.user_pk = user.user_pk)
WHERE dataset_pk < 0;
