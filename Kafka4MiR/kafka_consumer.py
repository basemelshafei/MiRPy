# Kafka consumer to read the messages from the topic
from kafka import KafkaConsumer
import json
import boto3

consumer = KafkaConsumer(
    'my_mir_data',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    enable_auto_commit=True,  # Commits the read offset automatically
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    max_poll_records=1,  # Poll only one record at a time
    fetch_max_wait_ms=100  # Set a short wait time for new records
)

# Initialize the S3 client
s3_client = boto3.client('s3')

# Define the S3 bucket name and the folder where the data will be stored
bucket_name = 'mirdata'
s3_folder = 'mir_data_from_kafka/'

# Function to upload data to S3
def upload_to_s3(data, file_name):
    try:
        # Convert the data to a JSON string
        json_data = json.dumps(data)

        # Upload the data to S3
        s3_client.put_object(
            Body=json_data,
            Bucket=bucket_name,
            Key=f"{s3_folder}{file_name}"
        )
        print(f"Uploaded data to S3: {file_name}")
    except Exception as e:
        print(f"Error uploading to S3: {e}")

# Consume messages
# Main consumer loop
def consume_data():
    for message in consumer:
        mir_data = message.value
        print(f"Received: {mir_data}")

        # Define the S3 file name for each message (you can customize the naming)
        s3_file_name = f"mir_data_{message.offset}.json"

        # Upload the data to S3
        upload_to_s3(mir_data, s3_file_name)

# Run the consumer
if __name__ == "__main__":
    consume_data()