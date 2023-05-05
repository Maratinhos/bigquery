# GCP BigQuery Examples

### CloudSQL to BigQuery
Export from Google CloudSQL CSV-file to Cloud Storage
```
gcloud sql export csv cloud-sql-instance-name gs://folder/file.scv --database=cloud-sql-db-name --offload --query="select id::text, created_at from cloud-sql-table-name"
```

Import CSV-file from Cloud Storage to BigQuery
```
bq load --autodetect --source_format=CSV --max_bad_records=100 bq-dataset.bq-table-name gs://folder/file.scv id:STRING,created_at:TIMESTAMP
```
