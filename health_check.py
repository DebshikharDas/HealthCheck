import yaml
import requests
from requests.exceptions import RequestException
import time
from urllib.parse import urlparse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s', handlers=[logging.StreamHandler()])

def read_yaml(file_path):
    with open(file_path, 'r') as file:
        endpoints = yaml.safe_load(file)
    return [endpoint['url'] for endpoint in endpoints]

# Set this flag to True for simulated responses, False for actual HTTP requests
SIMULATED_MODE = False

simulated_responses = {
    "https://fetch.com/": [(200, 100), (200, 100)],  # UP, UP
    "https://fetch.com/careers": [(200, 600), (200, 300)],  # DOWN, UP
    "https://fetch.com/some/post/endpoint": [(500, 50), (201, 50)],  # DOWN, UP
    "https://www.fetchrewards.com/": [(200, 100), (200, 900)]  # UP, DOWN 
} 

check_counts = {url: 0 for url in simulated_responses}

def check_endpoint(url):
    if SIMULATED_MODE:
        # Logic for simulated responses
        if url in simulated_responses:
            response_index = min(check_counts[url], len(simulated_responses[url]) - 1)
            status_code, latency = simulated_responses[url][response_index]
            check_counts[url] += 1
            return status_code >= 200 and status_code < 300 and latency < 500
        else:
            return False
    else:
        # Logic for actual HTTP requests
        try:
            start_time = time.time()
            response = requests.get(url, timeout=0.5)
            latency = (time.time() - start_time) * 1000  # Convert to milliseconds
            status = response.status_code
            # Below statement to Log actual response data for testing purposes, remove '#' below to activate logging
            #logging.info(f"URL: {url}, Status Code: {status}, Latency: {latency}ms")
            return status >= 200 and status < 300 and latency < 500
        except RequestException as e:
            logging.info(f"URL: {url}, Error: {e}")
            return False


def get_domain(url):
    return urlparse(url).netloc

def main():
    yaml_file_path = 'endpoints.yaml'
    endpoints = read_yaml(yaml_file_path)
    domain_status = {get_domain(url): {'up': 0, 'total': 0} for url in endpoints}

    while True:
        domain_check_count = {domain: 0 for domain in domain_status}

        for url in endpoints:
            domain = get_domain(url)
            is_up = check_endpoint(url)
            domain_check_count[domain] += 1
            if is_up:
                domain_status[domain]['up'] += 1
            domain_status[domain]['total'] += 1

        # Log after completing a cycle for all endpoints
        for domain in domain_status:
            if domain_check_count[domain] > 0:
                availability = (domain_status[domain]['up'] / domain_status[domain]['total']) * 100
                logging.info(f"{domain} has {round(availability)}% availability percentage")
        
        # Adding a blank line for readability after each cycle
        logging.info("")

        time.sleep(15)

if __name__ == "__main__":
    main()
