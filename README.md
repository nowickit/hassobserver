# Home Assistant to Splunk Observability Cloud Integration Script

This script facilitates the collection of sensor data from a Home Assistant instance and sends it to Splunk Observability Cloud (formerly SignalFX). It runs in a continuous loop, fetching sensor data from Home Assistant at regular intervals, then posting the data to SignalFX with the appropriate metrics.

## Requirements

- Home Assistant instance with available sensors.
- A Splunk Observability Cloud (SignalFX) account with an ingestion API token.
- `curl` installed on the machine running the script.
- `secrets.json` and `sensor_config.json` files configured appropriately (see structure below).
- Python 3.x installed on the machine.

## How to Run the Script

1. **Prepare Configuration Files:**
   - **`secrets.json`**: This file should contain your sensitive information such as API URLs and tokens. Here's the structure (ensure this file is not included in version control for security reasons):
   
     ```json
     {
       "hass_base_url": "http://<home_assistant_instance_url>:<port>/api/states",
       "hass_auth": "Bearer <your_home_assistant_long_lived_token>",
       "signalfx_token": "<your_signalfx_api_token>"
     }
     ```

   - **`sensor_config.json`**: This file maps Home Assistant sensor API paths to metrics. Here's an example structure:

     ```json
     {
       "sensors": [
         {
           "api_path": "/sensor.your_sensor_id",
           "metric": "your_metric_name"
         }
       ]
     }
     ```

2. **Run the Script Using `screen` Command (to prevent termination on SSH disconnect):**

   To ensure the script continues running even if your SSH session is disconnected, use the `screen` command as follows:

   ```bash
   screen -S hass_to_signalfx
   python3 script.py
   ```

This will start the script inside a screen session named hass_to_signalfx.

- To detach from the screen session (while keeping it running), press Ctrl + A, then D.
- To reattach to the session later, use:

    ```bash
    screen -r hass_to_signalfx
    ```

3. **Stopping the Script: If you need to stop the script, you can reattach to the screen session and stop it by pressing Ctrl + C or by killing the session:**
```bash
screen -XS hass_to_signalfx quit
```

## Script Workflow

1. **Secrets Loading**:
   - The script loads sensitive information like the Home Assistant base URL, authentication token, and SignalFX token from a `secrets.json` file.
2. **Fetching Sensor Data**:
   - Sensor data is fetched from Home Assistant using the API path specified in `sensor_config.json`.
3. **Data Processing**:
   - The script processes the sensor data, converting it into a format that SignalFX can ingest (e.g., converting "on"/"off" states to `1`/`0`).
4. **Sending Data to SignalFX**:
   - The sensor data is posted to SignalFX using `curl`. Each sensor's data is mapped to a metric and sent at regular intervals.
5. **Looping**:
   - The script runs in an infinite loop, collecting and sending data every 10 seconds.

## Important Notes

- Ensure that the `secrets.json` and `sensor_config.json` files are correctly formatted and placed in the same directory as the script.
- Modify the `time.sleep(10)` interval in the script if you need to adjust the data collection frequency.
- You can customize the `dimension_name` and `dimension_value` variables to add metadata or context to your metrics in SignalFX.

## Troubleshooting

- If the script fails to run, check the following:
  - Ensure that `curl` is installed and available in your system's PATH.
  - Ensure that the Home Assistant and SignalFX tokens are valid.
  - Make sure that the sensor paths in `sensor_config.json` are correct and that the sensors are active in your Home Assistant instance.
- If you encounter errors with sensor data fetching or posting to SignalFX, check the error messages printed in the script logs for debugging.