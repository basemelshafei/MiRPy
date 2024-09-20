## Kafka Producer, Consumer, and Setup Automation Instructions

### Kafka Producer (`kafka_producer.py`)
- Script designed to generate multiple MiR data and send it to a Kafka topic at different partitions.
- Connects to a Kafka broker and sends messages to a specified topic (`my_mir_data`).
- Uses the Kafka Python client `KafkaProducer` to send serialized data.
- Supports real-time data generation using a time delay.
- Automatically retries on failures and logs delivery status of each message.


### Kafka Consumer (`kafka_consumer.py`)
- Script to consume messages from a specified Kafka topic (`my_mir_data`).
- Uses the `KafkaConsumer` from the `kafka-python` library to subscribe to the topic.
- Processes the incoming data in real-time and sends it to an AWS S3 bucket.


### Running Kafka Setup (`running_kafka.bat`)
- A batch script to automate the startup of Zookeeper and Kafka brokers on Windows.
- Starts Zookeeper in one command prompt window, waits for 10 seconds, then starts Kafka in another.
- Checks if the required Kafka topic (`my_mir_data`) exists, and creates it if not.
- Useful for setting up Kafka services and topics automatically before running producer/consumer scripts.


### Requirements
- Kafka installation is required, with Zookeeper and Kafka broker properly configured.
- Run `runningkafka.bat` to start the Kafka services, then run `kafka_producer.py` and `kafka_consumer.py` scripts to interact with the Kafka topic.
- Python packages: `kafka-python`, `boto3` (if using AWS S3).

