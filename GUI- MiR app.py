import tkinter as tk
from tkinter import messagebox
import requests
import json
from requests.auth import HTTPBasicAuth
import time
import threading

def set_ip():
    global mir_ip, host, headers
    mir_ip = ip_entry.get()
    if mir_ip:
        host = f'http://{mir_ip}/api/v2.0.0/'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Basic RGlzdHJpYnV0b3I6NjJmMmYwZjFlZmYxMGQzMTUyYzk1ZjZmMDU5NjU3NmU0ODJiYjhlNDQ4MDY0MzNmNGNmOTI5NzkyODM0YjAxNA=='
        }
        request_button.config(state=tk.NORMAL)
        stop_button.config(state=tk.NORMAL)
        messagebox.showinfo("Success", f"IP address {mir_ip} set successfully!")
    else:
        messagebox.showerror("Error", "Please enter a valid IP address.")

def fetch_data(endpoint):
    try:
        response = requests.get(f'{host}{endpoint}', headers=headers)
        
        if response.status_code == 200:
            # Parse JSON response
            data = response.json()
            return data  
        else:
            print(f'Error fetching {endpoint}: {response.status_code} - {response.text}')
            return None  

    except requests.exceptions.RequestException as e:
        print(f'An error occurred fetching {endpoint}: {e}')
        return None 

def request_data():
    global running
    running = True
    try:
        while running:

            missions_data = fetch_data('missions')

            status_data = fetch_data('status')

            if missions_data:
                print("Missions:")
                for mission in missions_data:
                    print(mission['name'])

            if status_data:
                # Extract and print each data tag from status_data
                joystick_low_speed_mode_enabled = status_data['joystick_low_speed_mode_enabled']
                print("Joystick Low Speed Mode Enabled:", joystick_low_speed_mode_enabled)

                mission_queue_url = status_data['mission_queue_url']
                print("Mission Queue URL:", mission_queue_url)

                mode_id = status_data['mode_id']
                print("Mode ID:", mode_id)

                moved = status_data['moved']
                print("Moved:", moved)

                mission_queue_id = status_data['mission_queue_id']
                print("Mission Queue ID:", mission_queue_id)

                robot_name = status_data['robot_name']
                print("Robot Name:", robot_name)

                joystick_web_session_id = status_data['joystick_web_session_id']
                print("Joystick Web Session ID:", joystick_web_session_id)

                uptime = status_data['uptime']
                print("Uptime:", uptime)

                errors = status_data['errors']
                print("Errors:", errors)

                unloaded_map_changes = status_data['unloaded_map_changes']
                print("Unloaded Map Changes:", unloaded_map_changes)

                distance_to_next_target = status_data['distance_to_next_target']
                print("Distance to Next Target:", distance_to_next_target)

                serial_number = status_data['serial_number']
                print("Serial Number:", serial_number)

                mode_key_state = status_data['mode_key_state']
                print("Mode Key State:", mode_key_state)

                battery_percentage = status_data['battery_percentage']
                print("Battery Percentage:", battery_percentage)

                map_id = status_data['map_id']
                print("Map ID:", map_id)

                safety_system_muted = status_data['safety_system_muted']
                print("Safety System Muted:", safety_system_muted)

                mission_text = status_data['mission_text']
                print("Mission Text:", mission_text)

                state_text = status_data['state_text']
                print("State Text:", state_text)

                velocity = status_data['velocity']
                print("Velocity:", velocity)

                footprint = status_data['footprint']
                print("Footprint:", footprint)

                user_prompt = status_data['user_prompt']
                print("User Prompt:", user_prompt)

                allowed_methods = status_data['allowed_methods']
                print("Allowed Methods:", allowed_methods)

                robot_model = status_data['robot_model']
                print("Robot Model:", robot_model)

                mode_text = status_data['mode_text']
                print("Mode Text:", mode_text)

                session_id = status_data['session_id']
                print("Session ID:", session_id)

                state_id = status_data['state_id']
                print("State ID:", state_id)

                battery_time_remaining = status_data['battery_time_remaining']
                print("Battery Time Remaining:", battery_time_remaining)

                position = status_data['position']
                print("Position:", position)

            time.sleep(2)

    except Exception as e:
        print(f'An error occurred in the loop: {e}')


def stop_request():
    global running
    running = False
    print("Data request loop stopped.")


root = tk.Tk()
root.title("MiR Connection Interface")


tk.Label(root, text="Enter MiR IP:").grid(row=0, column=0, padx=10, pady=10)
ip_entry = tk.Entry(root)
ip_entry.grid(row=0, column=1, padx=10, pady=10)


set_ip_button = tk.Button(root, text="Set IP", command=set_ip)
set_ip_button.grid(row=0, column=2, padx=10, pady=10)


request_button = tk.Button(root, text="Request Data", command=lambda: threading.Thread(target=request_data).start(), state=tk.DISABLED)
request_button.grid(row=1, column=0, columnspan=3, pady=20)


stop_button = tk.Button(root, text="Stop Request", command=stop_request, state=tk.DISABLED)
stop_button.grid(row=2, column=0, columnspan=3, pady=20)


root.mainloop()
