import time
import requests

# MiR Configuration
MIR_IP = "http://10.148.127.210/api/v2.0.0/"
HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': 'Basic RGlzdHJpYnV0b3I6NjJmMmYwZjFlZmYxMGQzMTUyYzk1ZjZmMDU5NjU3NmU0ODJiYjhlNDQ4MDY0MzNmNGNmOTI5NzkyODM0YjAxNA=='
}

# Mission GUIDs
GO_TO_POSITION_GUID = "b0b69f85-9544-11ef-a1df-a41cb4015430"
GO_TO_CHARGING_GUID = "e5627397-d947-11ed-b436-a41cb4015430"

def send_mission(mission_guid):
    """
    Sends a mission with the specified GUID to the MiR mission queue.
    """
    url = f"{MIR_IP}/mission_queue"
    mission_data = {"mission_id": mission_guid}
    
    response = requests.post(url, headers=HEADERS, json=mission_data)
    if response.status_code == 201:
        print(f"Mission {mission_guid} started successfully.")
        return True
    else:
        print(f"Failed to start mission {mission_guid}: {response.status_code} - {response.text}")
        return False

def is_mission_complete():
    """
    Checks if the current mission is complete.
    """
    url = f"{MIR_IP}/status"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        return data["state_id"] == 3  # "3" typically means 'Idle' (check your MiR documentation)
    else:
        print(f"Failed to get status: {response.status_code} - {response.text}")
        return False

def get_battery_percentage():
    """
    Retrieves the current battery percentage from the MiR status.
    """
    url = f"{MIR_IP}/status"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        battery_percentage = data.get("battery_percentage", 100)  # Default to 100 if not available
        return battery_percentage
    else:
        print(f"Failed to retrieve battery status: {response.status_code} - {response.text}")
        return None

def mission_loop():
    """
    Main loop to alternate between 'go to position' and 'go to charging station' missions.
    """
    try:
        while True:
            # Check battery level before each mission
            battery_percentage = get_battery_percentage()
            if battery_percentage is not None:
                print(f"Current battery level: {battery_percentage}%")
                
                if battery_percentage < 15:
                    print("Battery is below 15%. Sending MiR to charging station and stopping loop.")
                    send_mission(GO_TO_CHARGING_GUID)  # Send to charging station
                    break  # Exit the loop to stop the cycle

            # Send the "go to position" mission
            if send_mission(GO_TO_POSITION_GUID):
                print("Going to specified position...")
                while not is_mission_complete():
                    time.sleep(5)  # Check mission status every 5 seconds

            # Send the "go to charging station" mission
            if send_mission(GO_TO_CHARGING_GUID):
                print("Returning to charging station...")
                while not is_mission_complete():
                    time.sleep(5)  # Check mission status every 5 seconds

            print("Cycle complete. Starting again...")
            time.sleep(2)  # Short delay before the next cycle

    except KeyboardInterrupt:
        print("Loop interrupted by user. Exiting...")

# Run the mission loop
mission_loop()
