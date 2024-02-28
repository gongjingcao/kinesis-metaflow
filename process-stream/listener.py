import json
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import boto3
import subprocess
import time
from aws_config import config

# Read from kinesis continuously. After read a new record, save it to S3 "temp" bucket, invoke metaflow to
# process it

aws_config = {
    'endpoint_url': config['endpoint_url'],
    'aws_access_key_id': config['aws_access_key_id'],
    'aws_secret_access_key': config['aws_secret_access_key'],
    'region_name': config['region_name'],

}
stream_name = 'MyStream'
SLEEP_DURATION = 5


def fetch_new_data(stream_name):
    """
    Check if there is new data in the specified Kinesis stream.
    if yes, save data to "temp" bucket in S3
    """

    try:
        kinesis_client = boto3.client('kinesis', **aws_config)
        shard_response = kinesis_client.describe_stream(StreamName=stream_name)
        shard_id = shard_response['StreamDescription']['Shards'][0]['ShardId']
        print(f"shard id: {shard_id}")

        shard_iterator = kinesis_client.get_shard_iterator(StreamName=stream_name,
                                                           ShardId=shard_id,
                                                           ShardIteratorType='TRIM_HORIZON')['ShardIterator']

        # Use the shard iterator to read data records from the shard
        total_record_cnt, total_words = 0, 0
        s3_client = boto3.client('s3', **aws_config)

        while True:
            out = kinesis_client.get_records(ShardIterator=shard_iterator, Limit=100)
            records = out['Records']

            if not records:
                print("No more records to be processed. Wait for a few seconds to check again")
                time.sleep(SLEEP_DURATION)
                continue

            # Process records
            for record in records:
                data = json.loads(record['Data'].decode())
                # print(data)
                # assume to count the words in "content" field, not to include the metadata in the whole record
                data['word_count'] = len(data['content'].split())
                # print(f"record word count {data['word_count']}")
                upload_file(s3_client, bucket_temp, data)

                total_record_cnt += 1
                total_words += data['word_count']

                # print("New data detected, triggering Metaflow script...")
                trigger_metaflow_script()
            print(f"Processed {total_record_cnt} records with {total_words} words ...")

            # Move to the next iterator
            shard_iterator = out['NextShardIterator']

    except NoCredentialsError:
        print("Credentials not available")
    except PartialCredentialsError:
        print("Partial credentials provided, check your config")
    except Exception as e:

        print(f"An error occurred: {str(e)}")

    return len(records) > 0


def upload_file(s3_client, bucket_temp, data):
    try:
        json_data = json.dumps(data, indent=2)
        s3_client.put_object(Body=json_data, Bucket=bucket_temp, Key=f"{data['article_id']}.json")
    except Exception as err:
        print(f"Failed to upload record: {data['article_id']} with err: {err}")


def trigger_metaflow_script():
    """
    Trigger the Metaflow script.
    """
    # python or python{version}, depends on your environment
    subprocess.run(['python3', 'metaflow_word_count.py', 'run'])


def create_s3_bucket(bucket_name):
    s3_client = boto3.client('s3', **aws_config)
    bucket_list = s3_client.list_buckets()
    if bucket_name not in [bucket['Name'] for bucket in bucket_list.get('Buckets', [])]:
        s3_client.create_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' created.")
    else:
        print(f"Bucket '{bucket_name}' already exists.")


if __name__ == "__main__":
    stream_name = 'MyStream'
    bucket_temp = 'temp'

    create_s3_bucket(bucket_temp)

    INIT_WAIT = 30  # wait for the stream to be created

    time.sleep(INIT_WAIT)
    fetch_new_data(stream_name)

