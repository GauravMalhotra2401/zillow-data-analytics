from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator
import json
import requests
from airflow.operators.bash import BashOperator
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from airflow.providers.amazon.aws.transfers.s3_to_redshift import S3ToRedshiftOperator

with open('/opt/airflow/config/config_file.json', 'r') as config_file:
    api_host_key = json.load(config_file)

now = datetime.now()
dt_string = now.strftime("%d%m%Y%H%M%S")

def extract_zillow_data(**kwargs):
    url = kwargs['url']
    querystring = kwargs['querystring']
    headers = kwargs['headers']
    date_string = kwargs['date_string']

    response = requests.get(url=url, headers=headers, params=querystring)
    response_data = response.json()

    output_file_path = f"/opt/airflow/zillow_data/response_data_{date_string}.json"
    file_str = f"response_data_{date_string}.csv"

    with open(output_file_path, 'w') as output_file:
        json.dump(response_data, output_file, indent=4)
    output_list = [output_file_path, file_str]
    return output_list

default_args = {
    "owner" : "airflow",
    "depends_on_past":False,
    "start_date": datetime(2024,7,1),
    "email": ["airflow@example.com"],
    "email_on_retry":False,
    "email_on_failure":False, 
    "retries":2,
    "retry_delay":timedelta(seconds=15)
}

with DAG("zillow_analytics_dag",
    default_args = default_args,
    schedule_interval = '@daily',
    catchup = False) as dag:

    extract_zillow_data_variable = PythonOperator(
        task_id = 'tsk_zillow_extract_data',
        python_callable = extract_zillow_data,
        op_kwargs = {
                    'url' : 'https://zillow56.p.rapidapi.com/search',
                    'querystring' : {
                        "location":"houston, tx",
                         "output":"json",
                         "status":"forSale",
                         "sortSelection":"priorityscore",
                         "listing_type":"by_agent",
                         "doz":"any"
                    },
                    'headers' : api_host_key,
                    'date_string' : dt_string
                    }
    )

    copytoS3bucket = BashOperator(
        task_id = 'tsk_copy_to_S3_bucket',
        bash_command = 'aws s3 mv {{ti.xcom_pull("tsk_zillow_extract_data")[0]}} s3://zillow-data-landing-zone/',
    )

    is_file_in_s3_available = S3KeySensor(
        task_id='tsk_is_file_available_in_s3',
        bucket_key='{{ti.xcom_pull("tsk_zillow_extract_data")[1]}}',
        bucket_name='cleaned-data-zone-csvbucket',
        aws_conn_id='aws_s3_conn',
        wildcard_match=False,  # Set this to True if you want to use wildcards in the prefix
        timeout=60,  # Optional: Timeout for the sensor (in seconds)
        poke_interval=5  # Optional: Time interval between S3 checks (in seconds)
    )

    transfer_s3_to_redshift = S3ToRedshiftOperator(
        task_id="tsk_transfer_s3_to_redshift",
        aws_conn_id='aws_s3_conn',
        redshift_conn_id='conn_id_redshift',
        s3_bucket='cleaned-data-zone-csvbucket',
        s3_key='{{ti.xcom_pull("tsk_zillow_extract_data")[1]}}',
        schema="PUBLIC",
        table="zillowdata",
        copy_options=["csv IGNOREHEADER 1"],
    )

    

    extract_zillow_data_variable >> copytoS3bucket >> is_file_in_s3_available >> transfer_s3_to_redshift
    
