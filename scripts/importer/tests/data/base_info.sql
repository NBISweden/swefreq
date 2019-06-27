SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

COPY data.collections (id, study_name, ethnicity) FROM stdin;
1	reg	undefined
2	reg	undefined
\.

COPY data.studies (id, pi_name, pi_email, contact_name, contact_email, title, study_description, publication_date, ref_doi) FROM stdin;
1	name	email	name	email	SweGen	\N	2001-01-01 00:00:00	doi
2	name2	email2	name2	email2	SweGen2	\N	2001-01-02 00:00:00	doi
\.

COPY data.datasets (id, study, short_name, full_name, browser_uri, beacon_uri, beacon_description, avg_seq_depth, seq_type, seq_tech, seq_center, dataset_size) FROM stdin;
1	1	Dataset 1	Dataset 1	url	\N	\N	0	type	method	place	0
2	2	Dataset 2	Dataset 2	url	\N	\N	0	type	method	place	0
\.

COPY data.dataset_versions (id, dataset, reference_set, dataset_version, dataset_description, terms, available_from, ref_doi, data_contact_name, data_contact_link, num_variants, coverage_levels, portal_avail, file_access, beacon_access) FROM stdin;
1	1	1	Version 1	desc	terms	2001-01-01 00:00:00	doi	place	email	\N	{1,5,10,15,20,25,30,50,100}	TRUE	REGISTERED	PUBLIC
2	1	1	Version 2	desc	terms	2001-01-02 00:00:00	doi	place	email	\N	{1,5,10,15,20,25,30,50,100}	TRUE	REGISTERED	PUBLIC
3	2	1	Version 1	desc	terms	2001-01-02 00:00:00	doi	place	email	\N	{1,5,10,15,20,25,30,50,100}	TRUE	REGISTERED	PUBLIC
\.

COPY data.sample_sets (id, dataset, collection, sample_size, phenotype) FROM stdin;
1	1	1	0	Undefined
2	2	1	0	Undefined
\.
