# Define AWS common configuration

# endpoint_url = 'http://localhost:4566'  # when run ir locally
endpoint_url = 'http://localstack:4566'  # when run it in Docker container

config = {
    'endpoint_url': endpoint_url,
    'aws_access_key_id': 'test',
    'aws_secret_access_key': 'test',
    'region_name': 'us-east-1',
    'bucket_name': 'my-bucket',
    'stream_name': 'MyStream'
}
