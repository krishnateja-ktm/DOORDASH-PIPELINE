use role accountadmin;

-- Compute: extra-small, auto-suspend fast so the trial credits last.
create warehouse if not exists DOORDASH_WH
warehouse_size = 'xsmall'
auto_suspend = 60
auto_resume = true
initially_suspended = true;

-- Database + medallion schemas
create database if not exists DOORDASH; -- Iceberg tables spark-wrote (dbt sources)
create schema if not exists DOORDASH.RAW; -- only used by the copy fallback path
create schema if not exists DOORDASH.STAGING; -- cleaned / conformed (dbt)
create schema if not exists DOORDASH.MARTS; --gold, iceberg (dbt)
create schema if not exists DOORDASH.SNAPSHOTS; --scd2 history (dbt)
create schema if not exists DOORDASH.AI; --LLM-enriched tables (openAI jobs)

-- A role dbt/airflow will use
create role if not exists DBT_ROLE;
grant usage on warehouse DOORDASH_WH to role DBT_ROLE;
grant operate on warehouse DOORDASH_WH to role DBT_ROLE;
grant all on database DOORDASH to role DBT_ROLE;
grant all on all schemas in database DOORDASH to role DBT_ROLE;
grant all on future schemas in database DOORDASH to role DBT_ROLE;
grant all on future tables in database DOORDASH to role DBT_ROLE;
grant all on future views in database DOORDASH to role DBT_ROLE;


-- Let your login use the role
set my_user = current_user();
grant role DBT_ROLE to user identifier($my_user);

select 'setup complete' as status;