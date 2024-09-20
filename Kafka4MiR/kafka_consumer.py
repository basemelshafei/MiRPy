from kafka import KafkaConsumer
import json
import boto3
import signal
import sys

consumer = KafkaConsumer(
    'my_mir_data',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    enable_auto_commit=True, 
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
    max_poll_records=1,  
    fetch_max_wait_ms=100  
)


s3_client = boto3.client('s3')


bucket_name = 'mirdata'
s3_folder = 'mir_data_from_kafka/'


def upload_to_s3(data, file_name):
    try:
        json_data = json.dumps(data)
        s3_client.put_object(
            Body=json_data,
            Bucket=bucket_name,
            Key=f"{s3_folder}{file_name}"
        )
        print(f"Uploaded data to S3: {file_name}")
    except Exception as e:
        print(f"Error uploading to S3: {e}")


def signal_handler(sig, frame):
    print('Shutting down consumer...')
    consumer.close()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def consume_data():
    for message in consumer:
        mir_data = message.value
        print(f"Received: {mir_data}")

        robot_name = mir_data.get('robot_name', 'UnknownRobot')
        s3_file_name = f"mir_data_{message.partition}_{message.offset}_{robot_name}.json"

        upload_to_s3(mir_data, s3_file_name)

if __name__ == "__main__":
    print("Starting Kafka consumer...")
    consume_data()
