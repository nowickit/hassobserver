import subprocess
import json
import time
import os

# Load secrets from a separate file
def load_secrets():
    with open("secrets.json", "r") as json_file:
        return json.load(json_file)

# Constants
signalfx_url = "https://ingest.us1.signalfx.com/v2/datapoint"
secrets = load_secrets()  # Load the secrets
hass_base_url = secrets.get("hass_base_url")
hass_auth = secrets.get("hass_auth")
signalfx_token = secrets.get("signalfx_token")

# Set dimensions as variables
dimension_name = "tno_service_name"
dimension_value = "hass"

# Load JSON configuration for sensor paths and metrics
def load_config():
    with open("sensor_config.json", "r") as json_file:
        return json.load(json_file)

# Get sensor data from Home Assistant API
def get_sensor_data(sensor_path):
    hass_url = f"{hass_base_url}{sensor_path}"
    try:
        result = subprocess.run([
            "curl",
            "-H", f"Authorization: {hass_auth}",
            "-H", "Content-Type: application/json",
            hass_url
        ], capture_output=True, text=True)

        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            print(f"Error fetching sensor data: {result.stderr}")
            return None
    except Exception as e:
        print(f"Exception occurred while fetching sensor data: {e}")
        return None

# Post data to SignalFX
def post_data_to_signalfx(metric, state, timestamp):
    try:
        # Convert state from "on"/"off" to 1/0
        if state == "on":
            state = 1
        elif state == "off":
            state = 0
        else:
            state = float(state)  # Keep other states as float

        data = {
            "counter": [{
                "metric": metric,
                "value": state,
                "timestamp": timestamp,
                "dimensions": {
                    dimension_name: dimension_value
                }
            }]
        }

        json_data = json.dumps(data)
        curl_command = f'curl -i -X POST ' \
                       f'--header "Content-Type: application/json" ' \
                       f'--header "X-SF-TOKEN: {signalfx_token}" ' \
                       f'-d \'{json_data}\' ' \
                       f'{signalfx_url}'

        print(f"Executing curl command for SignalFX:\n{curl_command}\n")
        result = subprocess.run(curl_command, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"Data successfully posted to SignalFX. \n {result.stdout}")
        else:
            print(f"Error posting data to SignalFX: {result.stderr}")
    except Exception as e:
        print(f"Exception occurred while posting data: {e}")

# Main function to process sensor-metric pairs from JSON config
def main():
    config = load_config()

    while True:
        for sensor in config.get('sensors', []):
            sensor_path = sensor.get('api_path')
            metric = sensor.get('metric')

            sensor_data = get_sensor_data(sensor_path)
            if sensor_data:
                entity_id = sensor_data.get("entity_id")
                state = sensor_data.get("state")
                timestamp = time.time() * 1000

                print(f"Fetched data: entity_id={entity_id}, state={state}, timestamp={timestamp}")
                post_data_to_signalfx(metric, state, timestamp)

        time.sleep(10)  # Wait before repeating

if __name__ == "__main__":
    main()
