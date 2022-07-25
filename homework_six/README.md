start localstack docker container in homework_six folder
```bash
$ docker-compose up -d
```

set up aws on windows:
1) start Windows PowerShell with admin rights
2) install aws on Windows PowerShell: https://docs.aws.amazon.
   com/powershell/latest/userguide/pstools-getting-set-up-windows.html
3) restart PyCharm IDE to use it

create s3 bucket on localstack docker container
```bash
`$ aws --endpoint-url=http://localhost:4566 s3 mb s3://nyc-duration
```

copy files to s3 on localstack
```bash
$ aws --endpoint-url=http://localhost:4566 s3 cp .\fhv_tripdata_2021-01.parquet s3://nyc-duration/in/
```