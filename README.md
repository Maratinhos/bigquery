# GCP BigQuery Examples

### 1. CloudSQL to BigQuery.
Export from Google CloudSQL CSV-file to Cloud Storage
```
gcloud sql export csv cloud-sql-instance-name gs://folder/file.csv --database=cloud-sql-db-name --offload --query="select id::text, created_at from cloud-sql-table-name"
```

Import CSV-file from Cloud Storage to BigQuery
```
bq load --autodetect --source_format=CSV --max_bad_records=100 bq-dataset.bq-table-name gs://folder/file.csv id:STRING,created_at:TIMESTAMP
```

> It works slowly. I prefer the external connection.

### 2. Monthly expense statistics.
```sql
select date_trunc(date(creation_time), month)                               as month,
       count(job_id)                                                        as jobs,
       round(sum(total_bytes_billed) / (1024 * 1024 * 1024 * 1024), 0)      as billed_TB,
       round(sum(total_bytes_billed) / (1024 * 1024 * 1024 * 1024), 0) * 5  as sum_dollars
  from `region-europe-north1`.INFORMATION_SCHEMA.JOBS_BY_PROJECT 
 where project_id = 'long-perception-XXXXXX'
group by month
order by month;
```

### 3. Searching something in views and stored procedures.
```sql
select table_catalog || '.' || table_schema || '.' || table_name as object, 
       table_type                                                as type, 
       ddl                                                       as definition
  from `region-europe-north1`.INFORMATION_SCHEMA.TABLES
 where table_type = 'VIEW'
   and lower(ddl) like '%table.column%'

union all

select routine_catalog || '.' || routine_schema || '.' || routine_name as object, 
       routine_type                                                    as type, 
       ddl                                                             as definition, 
  from `region-europe-north1`.INFORMATION_SCHEMA.ROUTINES
 where lower(ddl) like '%table.column%'
```

### 4. Get the Monday date of the current week.
```sql
select date_trunc(current_date('Europe/Moscow'), week(monday)) as week_monday
```

### 5. Get the MIN value from the 3 previous rows.
```sql
with table_name as (
select '2023-05-01' as date, 10 as price, 'g001' as group_name union all
select '2023-05-02' as date, 12 as price, 'g001' as group_name union all
select '2023-05-03' as date,  9 as price, 'g001' as group_name union all
select '2023-05-04' as date, 11 as price, 'g001' as group_name union all
select '2023-05-05' as date, 12 as price, 'g001' as group_name
)
select t.date,
       t.price,
       t.group_name,
       min(t.price) over(partition by t.group_name order by t.date desc rows between 3 preceding and 1 preceding) as prev3_min_price,
  from table_name t
```

| Row | date | price | group_name | prev3_min_price |
| ---: | ---: | ---: | --- | ---: |
| 1 | 2023-05-05 | 12 | g001 | null |
| 2 | 2023-05-04 | 11 | g001 | 12 |
| 3 | 2023-05-03 | 9 | g001 | 11 |
| 4 | 2023-05-02 | 12 | g001 | 9 |
| 5 | 2023-05-01 | 10 | g001 | 9 |

### 6. Copy tables between datasets in different locations
```
bq mk --transfer_config --project_id=long-perception-XXXXXX --data_source=cross_region_copy --target_dataset=dataset-name-eu --display_name='dataset US to EU' --params='{"source_dataset_id":"dataset-name-us","source_project_id":"long-perception-XXXXXX","overwrite_destination_table":"true"}'
```
> Or you can use Data Transfer UI.

### 7. External connection (you can query data in Cloud SQL from BigQuery).
```
bq mk --connection --connection_type='CLOUD_SQL' --connection_credential='{"username":"bq_reader", "password":"bq_reader_password"}' --properties='{"instanceId":"long-perception-XXXXXX:europe-north1:postgres","database":"cloud-sql-db-name","type":"POSTGRES"}' --project_id=long-perception-XXXXXX --location=europe-north1 external-connection-name
```

```sql
select t.id, t.name
  from external_query(
    'external-connection-name',
    '''
    select id:text as id,
           name:text
      from public.table_name
    '''
  ) t
```

### 8. Get Scheduled queries.
```
bq ls --transfer_config --transfer_location=europe-north1 --format=csv
```
You can save csv to Cloud Storage and then load to BigQuery:
```sql
load data overwrite `long-perception-XXXXXX.dataset_name.scheduled_query_YYYYMMDD`
from files (
  format = 'CSV',
  uris = ['gs://bucket_name/scheduled_query/scheduled_query_YYYYMMDD.csv']);
```

### 9. Split text into words. And get the words offset.
```sql
select text, word, word_offset
  from `long-perception-XXXXXX.dataset_name.table_name` a
  cross join unnest(split(text, ' ')) as word with offset word_offset
```

| text | word | word_offset |
| --- | --- | ---: |
| qwe rty asd | qwe | 0 |
| qwe rty asd | rty | 1 |
| qwe rty asd | asd | 2 |
| zxc vbn | zxc | 0 |
| zxc vbn | vbn | 1 |

### 10. Get data from the past (Time travel).
```sql
select *
  from `long-perception-XXXXXX.dataset_name.table_name`
for system_time as timestamp_sub(current_timestamp(), interval 10 hour)
```
