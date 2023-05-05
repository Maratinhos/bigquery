# GCP BigQuery Examples

### 1. CloudSQL to BigQuery
Export from Google CloudSQL CSV-file to Cloud Storage
```
gcloud sql export csv cloud-sql-instance-name gs://folder/file.csv --database=cloud-sql-db-name --offload --query="select id::text, created_at from cloud-sql-table-name"
```

Import CSV-file from Cloud Storage to BigQuery
```
bq load --autodetect --source_format=CSV --max_bad_records=100 bq-dataset.bq-table-name gs://folder/file.csv id:STRING,created_at:TIMESTAMP
```


> It works slowly. I prefer the external connection.


### 2. Monthly expense statistics
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
