import boto3
import json
from faker import Faker
import os
import time

fake = Faker()

aws_config = {
    'endpoint_url': 'http://localstack:4566',
    'aws_access_key_id': 'test',
    'aws_secret_access_key': 'test',
    'region_name': 'us-east-1'
}


def create_s3_bucket(bucket_name):
    s3_client = boto3.client('s3', **aws_config)
    bucket_list = s3_client.list_buckets()
    if bucket_name not in [bucket['Name'] for bucket in bucket_list.get('Buckets', [])]:
        s3_client.create_bucket(Bucket=bucket_name)
        print(f"Bucket '{bucket_name}' created.")
    else:
        print(f"Bucket '{bucket_name}' already exists.")


def create_kinesis_stream(stream_name, shard_count=1):
    kinesis_client = boto3.client('kinesis', **aws_config)
    try:
        kinesis_client.create_stream(StreamName=stream_name, ShardCount=shard_count)
        print(f"Stream '{stream_name}' created.")
        time.sleep(5)  # Wait for stream to be created  
    except kinesis_client.exceptions.ResourceInUseException:
        print(f"Stream '{stream_name}' already exists.")


def generate_mock_article():
    return {
        'article_id': fake.uuid4(),
        'title': fake.sentence(nb_words=6),
        'author': fake.name(),
        'publish_date': fake.date_time_this_year().isoformat(),
        'content': ' '.join(fake.paragraphs(nb=100))
    }


def publish_articles_to_kinesis(stream_name, target_size_mb):
    # Directly specifying 'kinesis' as the service name
    kinesis_client = boto3.client('kinesis', **aws_config)
    total_size = 0
    # target_bytes = target_size_mb * 1024 * 1024  # Convert MB to Bytes
    target_bytes = target_size_mb * 1024 * 50  # adjust the size for testing
    articles_count = 0

    while total_size < target_bytes:
        article = generate_mock_article()
        article_json = json.dumps(article)
        article_bytes = article_json.encode('utf-8')
        kinesis_client.put_record(StreamName=stream_name, Data=article_bytes, PartitionKey=article['article_id'])
        total_size += len(article_bytes)
        articles_count += 1

        if articles_count % 100 == 0:
            print(f"Published {articles_count} articles, {total_size / (1024 * 1024)} MB so far...")

    print(f"Finished: Published {articles_count} articles, approx {total_size / (1024 * 1024)} MB of data to Kinesis.")


if __name__ == '__main__':
    bucket_name = 'my-bucket'
    stream_name = 'MyStream'

    dataset_size_mb = int(os.getenv('DATASET_SIZE_MB', '1'))
    num_iterations = int(os.getenv('NUM_ITERATIONS', '1'))

    create_s3_bucket(bucket_name)
    create_s3_bucket('temp')
    create_kinesis_stream(stream_name)

    for iteration in range(num_iterations):
        print(f"Iteration {iteration + 1}...")
        publish_articles_to_kinesis(stream_name, dataset_size_mb)
        if iteration < 99:
            time.sleep(60)
