from metaflow import FlowSpec, step
import boto3
import json
from aws_config import config

aws_config = {
    'endpoint_url': config['endpoint_url'],
    'aws_access_key_id': config['aws_access_key_id'],
    'aws_secret_access_key': config['aws_secret_access_key'],
    'region_name': config['region_name']
}
# temp bucket in S3 where the original records are read from
bucket_temp = 'temp'
# destination bucket in S3 where the computed data is writen into
bucket_name = 'my-bucket'
stream_name = 'MyStream'


class WordCountPipeline(FlowSpec):
    """
    A Metaflow Flow to read any new files from S3 bucket "temp", process them, then save the final results to S3 "my-bucket"
    """

    def __init__(self, use_cli=True):
        super().__init__(use_cli)
        self.word_counts = None
        self.records = None

    @step
    def start(self):
        """
        Start step: Reads JSON files from the specified S3 bucket "temp", then deletes them.
        """
        s3_client = boto3.client('s3', **aws_config)

        try:
            # List all objects within the specified bucket "temp"
            bucket_objects = s3_client.list_objects(Bucket=bucket_temp)
            self.records = []
            first_file_key = None

            if 'Contents' in bucket_objects:
                for obj in bucket_objects['Contents']:
                    # Get the object key (file name)
                    file_key = obj['Key']
                    print(f"Key of the file: {file_key}")
                    # Get the object's content
                    file_content = s3_client.get_object(Bucket=bucket_temp, Key=file_key)
                    # Read the content and decode it
                    file_text = file_content['Body'].read().decode('utf-8')
                    # Convert the JSON string to a Python dictionary
                    file_data = json.loads(file_text)
                    # print(f"File: {file_key}, Content: {file_data}")
                    content = file_data
                    self.records.append(content)

                    # Delete the retrieved file from the bucket
                    s3_client.delete_object(Bucket=bucket_temp, Key=file_key)
                    # print(f"File '{file_key}' deleted from bucket '{bucket_temp}'.")

            else:
                print(f"No files found in bucket '{bucket_temp}'.")

            print(f"read {len(self.records)} files from S3 bucket")
        except Exception as e:
            print(f"An error occurred: {e}")

        self.next(self.process_records)

    @step
    def process_records(self):
        """
        Process records: count words in 'content' and add 'word_count' field.
        """
        self.word_counts = []
        for record in self.records:
            content = record.get('content', '')
            word_count = len(content.split())
            self.word_counts.append(word_count)
            record['word_count'] = word_count
            # print(f"{record}")
            print(f"word count in the record: {word_count}")

        self.next(self.write_to_s3)

    @step
    def write_to_s3(self):
        """
        Write processed records to S3.
        """
        s3_client = boto3.client('s3', **aws_config)

        # Ensure bucket exists
        if bucket_name not in [bucket['Name'] for bucket in s3_client.list_buckets()['Buckets']]:
            s3_client.create_bucket(Bucket=bucket_name)

        # Write each record as a separate file in S3
        for record in self.records:
            file_name = f"{record['article_id']}.json"
            # print(record)
            s3_client.put_object(Bucket=bucket_name, Key=file_name, Body=json.dumps(record))

        self.next(self.end)

    @step
    def end(self):
        """
        End step of the flow.
        """
        print("Word Counting data processing completed.")


def read_records_from_file(file_name='records.json'):
    try:
        with open(file_name, 'r') as f:
            records = json.load(f)
        print(f"Successfully read {len(records)} records from {file_name}")
        return records
    except FileNotFoundError:
        print(f"Error: The file {file_name} does not exist.")
        return []
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from {file_name}.")
        return []


if __name__ == '__main__':
    WordCountPipeline()
