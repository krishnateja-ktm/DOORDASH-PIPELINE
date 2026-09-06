use role accountadmin;

create or replace storage integration DOORDASH_S3_INT
type = external_stage
storage_provider = 'S3'
enabled = true
storage_aws_role_arn = 'arn:aws:iam::564882306744:role/doordash-snowflake-role'
storage_allowed_locations = ('s3://yt-doordash-pipeline-dev/');

grant usage on integration DOORDASH_S3_INT to role DBT_ROLE;

desc integration DOORDASH_S3_INT