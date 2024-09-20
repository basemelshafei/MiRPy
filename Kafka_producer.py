import json
import random
import time
from kafka import KafkaProducer

# Initialize the Kafka producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),  # Serialize data as JSON
    linger_ms=100,  # Batches messages for 100ms before sending
    batch_size=16384  # Batch size to improve throughput
)

# Callback for success
def on_success(metadata):
    print(f"Message delivered to {metadata.topic} partition {metadata.partition} offset {metadata.offset}")

# Callback for error
def on_error(exception):
    print(f"Failed to deliver message: {exception}")

# Send the data to the Kafka topic with partitioning by robot_name
def handle_data_fetched(data):
    try:
        partition_map = {'Robot-1': 0, 'Robot-2': 1, 'Robot-3': 2}
        partition = partition_map.get(data['robot_name'], 0)  # Default to partition 0 if robot_name not found
        future = producer.send('my_mir_data', value=data, partition=partition)
        future.add_callback(on_success).add_errback(on_error)
        producer.flush()  # Ensures the message is sent immediately
    except Exception as e:
        print(f"Error sending message: {e}")

# Validate the data before sending
def validate_data(data):
    required_fields = ["robot_name", "battery_percentage", "timestamp"]
    for field in required_fields:
        if field not in data:
            print(f"Data validation failed: {field} is missing.")
            return False
    return True

# Simulated MiR data fetching logic for multiple robots
def generate_mir_data():
    robots = ['Robot-1', 'Robot-2', 'Robot-3']  # Define 3 specific MiRs
    while True:
        for robot in robots:
            data = {
                "joystick_low_speed_mode_enabled": random.choice([True, False]),
                "mission_queue_url": "http://example.com/mission_queue",
                "mode_id": random.randint(1, 10),
                "moved": random.randint(0, 1000),
                "mission_queue_id": random.randint(1, 100),
                "robot_name": robot,  # Use one of the 3 defined robots
                "joystick_web_session_id": f"Session-{random.randint(1, 100)}",
                "uptime": random.randint(0, 10000),
                "errors": random.choice([[], ["Error 1", "Error 2"]]),
                "unloaded_map_changes": random.randint(0, 5),
                "distance_to_next_target": round(random.uniform(0, 10), 2),
                "serial_number": f"SN-{random.randint(1000, 9999)}",
                "mode_key_state": random.choice(["STATE1", "STATE2"]),
                "battery_percentage": round(random.uniform(0, 100), 2),
                "map_id": random.randint(1, 10),
                "safety_system_muted": random.choice([True, False]),
                "mission_text": "Mission in progress",
                "state_text": "Active",
                "velocity": round(random.uniform(0, 2), 2),
                "footprint": "Normal",
                "user_prompt": "No prompt",
                "allowed_methods": ["GET", "POST"],
                "robot_model": "MiR100",
                "mode_text": "Operational",
                "session_id": f"Session-{random.randint(100, 999)}",
                "state_id": random.randint(1, 5),
                "battery_time_remaining": random.randint(0, 120),
                "position": {"x": round(random.uniform(0, 100), 2), "y": round(random.uniform(0, 100), 2)},
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            }
            
            if validate_data(data):
                handle_data_fetched(data)  # Send valid data to Kafka
            
        time.sleep(2)  # Adjust the interval as needed

# Run the data generator
if __name__ == "__main__":
    generate_mir_data()
