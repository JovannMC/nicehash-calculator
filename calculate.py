import sys
import json
import requests
import os

# Check if the --debug flag is present in command line arguments
DEBUG_MODE = '--debug' in sys.argv

# Debug function to print messages
def debug_message(message):
    if DEBUG_MODE:
        print(f"DEBUG: {message}")

# Function to log the response to a file
def log_response(file_name, data):
    if DEBUG_MODE:
        # Ensure the logs directory exists
        os.makedirs('logs', exist_ok=True)
        with open(f'logs/{file_name}.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

# Function to get the list of devices from NiceHash
def get_devices():
    debug_message("Requesting list of devices from NiceHash...")
    response = requests.get('https://api2.nicehash.com/main/api/v2/public/profcalc/devices')
    devices = response.json()['devices']
    log_response('devices', devices)  # Log the response
    debug_message("Received list of devices. Printing names:")
    for device in devices:
        print(device['name'])  # Print the name of each device
    return devices

# Function to get the profitability data for a specific device
def get_device_profitability(device_id):
    debug_message(f"Requesting profitability data for device ID {device_id}...")
    response = requests.get(f'https://api2.nicehash.com/main/api/v2/public/profcalc/device?device={device_id}')
    data = response.json()
    log_response(f'device_{device_id}', data)  # Log the response
    debug_message("Received profitability data")
    return data

# Function to get the profitability for specific speeds and codes
def get_profitability(speeds):
    debug_message("Posting to profitability2 endpoint...")
    speedJson = json.loads(speeds)
    response = requests.post('https://api2.nicehash.com/main/api/v2/public/profcalc/profitability2', json={'speeds': speedJson})
    data = response.json()
    log_response('profitability2', data)  # Log the response
    debug_message("Received profitability2 data")
    return data

# Function to get the list of algorithms from NiceHash
def get_nicehash_algorithms():
    debug_message("Requesting list of algorithms from NiceHash...")
    response = requests.get('https://api2.nicehash.com/main/api/v2/mining/algorithms')
    algorithms = response.json()
    log_response('nicehash_algorithms', algorithms)  # Log the response
    debug_message("Received list of algorithms.")
    return algorithms

# Function to print the names of the available algorithms
def print_available_algorithms(speeds):
    if DEBUG_MODE:
        # Deserialize the speeds JSON string into a Python dictionary
        if isinstance(speeds, str):
            speeds_dict = json.loads(speeds)
        else:
            speeds_dict = speeds  # Assuming speeds is already a dictionary

        debug_message("Available algorithms with non-zero hashrate:")
        for algo, speed in speeds_dict.items():
            # Check if the speed is non-zero and print the algorithm
            if speed and float(speed) > 0:
                print(algo)


""" Commented out, this is for individual algorithm earnings (to which profitability2 for GPUs only returns the earnings for the most profitable algos)
Will work on later
# Function to calculate the average earnings for individual algorithms
def calculate_average_earnings(values, algorithm_code):
    debug_message(f"Calculating average earnings for algorithm code {algorithm_code}...")
    algorithm_entries = [v for v in values.values() if v.get('a') == algorithm_code] # slightly inaccurate as nicehash gives values for a lot of other algos too, but close enough
    if algorithm_entries:
        total = sum(entry['p'] for entry in algorithm_entries)
        average = total / len(algorithm_entries)
        debug_message(f"Calculated average earnings: {average}")
        return average
    else:
        debug_message("No data for the specified algorithm.")
        return "No data for the specified algorithm."
"""

# Function to calculate the average earnings
def calculate_average_earnings(values):
    debug_message("Calculating average earnings...")
    algorithm_entries = [v for v in values.values()]
    total = sum(entry['p'] for entry in algorithm_entries)
    average = total / len(algorithm_entries)
    debug_message(f"Calculated average earnings: {average}")
    return average

def get_order_by_algorithm(json_data, algorithm_name):
    for item in json_data:
        if item["algorithm"] == algorithm_name:
            return item["order"]
    return None  # Return None if algorithm name is not found

# Main script execution
if __name__ == '__main__':
    if DEBUG_MODE:
        debug_message("Debug mode is ON.")

    devices = get_devices()
    
    selected_device = input("Enter the name of your device: ")
    device_info = next((device for device in devices if device['name'].lower() == selected_device.lower()), None)
    
    if device_info:
        device_id = device_info['id']
        debug_message(f"Selected device ID: {device_id}")
        
        profitability_data = get_device_profitability(device_id)
        speeds = profitability_data['speeds']

        # Get NiceHash algorithms
        nicehash_algorithms = get_nicehash_algorithms()
        salad_codes = nicehash_algorithms.get('miningAlgorithms', [])
        
        # Get profitability data
        profitability = get_profitability(speeds)

        average_earnings = calculate_average_earnings(profitability['values'])
        print(f"Average daily earnings (in BTC) for {selected_device}:")
        print(f"Scientific notation: {average_earnings}")
        print(f"Real (rounded) number: {format(average_earnings, 'f')}")

        """ Commented out, this is for individual algorithm earnings (to which profitability2 for GPUs only returns the earnings for the most profitable algos)
        Will work on later
        # Ask user for algorithm
        selected_algorithm = input("Enter your algorithm: ")
        algorithm_code = next((algo['order'] for algo in salad_codes if algo['algorithm'].lower() == selected_algorithm.lower()), None)
        
        
        if algorithm_code is not None:
            debug_message(f"Selected algorithm code: {algorithm_code}")
            
            # Calculate average earnings
            average_earnings = calculate_average_earnings(profitability['values'])
            print(f"Average earnings (in BTC) for {selected_algorithm}: {format(average_earnings, 'f')}")
        else:
            debug_message("Algorithm not found.")
            print("Algorithm not found.")
        """
    else:
        print("Device not found.")
