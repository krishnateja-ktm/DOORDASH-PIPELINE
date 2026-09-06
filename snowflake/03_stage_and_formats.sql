use role accountadmin;
use database DOORDASH;
use schema RAW;

create or replace file format DOORDASH.RAW.CSV_FMT
    type = 'CSV'
    compression = 'AUTO'
    field_delimiter = ','
    field_optionally_enclosed_by = '"'
    skip_header = 1
    empty_field_as_null = TRUE
    null_if = (' ', '\\N', 'NULL')
    trim_space = FALSE
    error_on_column_count_mismatch = FALSE;

create or replace STAGE DOORDASH.RAW.DOORDASH_RAW_STAGE
    storage_integration = DOORDASH_S3_INT
    URL = 's3://yt-doordash-pipeline-dev/raw/'
    file_format = DOORDASH.RAW.CSV_FMT;

list @DOORDASH.RAW.DOORDASH_RAW_STAGE;