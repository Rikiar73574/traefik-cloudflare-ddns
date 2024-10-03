import os
import requests
import logging
import socket
import time

traefik_host = os.getenv('TRAEFIK_HOST', 'traefik')
traefik_port = os.getenv('TRAEFIK_PORT', '8080')
#check that CF_ZONE_ID and CF_API_KEY have been set in the environment
if 'CF_ZONE_ID' and 'CF_API_KEY' == '':
    logging.error('CF_ZONE_ID and CF_API_KEY variables not set environment variable not set')
    exit(1)
else:
    cf_zone_id = os.getenv('CF_ZONE_ID')
    cf_api_key = os.getenv('CF_API_KEY')
extra_domains = os.getenv('EXTRA_DOMAINS', '').split(',')


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_subdomains_from_traefik(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        routers = response.json()

        subdomains = []
        for router in routers:
            # Check if 'rule' exists and does not contain '@'
            if 'rule' in router:
                rule = router['rule']
                # Extract the subdomain from the rule
                if rule.startswith("Host(`") and rule.endswith("`)"):
                    subdomain = rule[6:-2]  # Remove "Host(`" and "`)"
                    subdomains.append(subdomain)

        return subdomains

    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching subdomains from Traefik: {e}")
        return []

def get_public_ip():
    try:
        # Use an external service to get the public IP address
        response = requests.get('https://api.ipify.org?format=json')
        response.raise_for_status()
        ip_info = response.json()
        return ip_info['ip']
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching public IP: {e}")
        return None
    

def get_a_record(domain):
    try:
        url = f"https://api.cloudflare.com/client/v4/zones/{cf_zone_id}/dns_records"
        headers = {
            "Authorization": f"Bearer {cf_api_key}",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        records = response.json().get('result', [])
        for record in records:
            if record['type'] == 'A' and record['name'] == domain:
                return record  # Return the entire record
                
        logging.error(f"No A record found for domain: {domain}")
        return None
        
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching A record for {domain}: {e}")
        return None

def update_a_record(domain, ip):
    try:
        record = get_a_record(domain)
        if not record:
            logging.error(f"Cannot update A record for {domain} because it was not found.")
            return

        record_id = record['id']
        current_ip = record['content']
        ttl = record['ttl']
        proxied = record['proxied']
        if current_ip == ip:
            logging.info(f"IP for {domain} has not changed. Skipping update.")
            return
            
        logging.info(f"Current Record Info - Domain: {domain}, IP: {current_ip}, TTL: {ttl}, Proxied: {proxied}")

        url = f"https://api.cloudflare.com/client/v4/zones/{cf_zone_id}/dns_records/{record_id}"
        headers = {
            "Authorization": f"Bearer {cf_api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "type": "A",
            "name": domain,
            "content": ip,
            "ttl": ttl,  # Retain existing TTL
            "comment": "Updated by Cloudflare-traefik DDNS",
            "proxied": proxied  # Retain existing proxy status
        }
        response = requests.put(url, headers=headers, json=data)
        response.raise_for_status()
        logging.info(f"Updated A record for {domain} with IP {ip}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error updating A record for {domain}: {e}")

def main():
    traefik_api_url = f'http://{traefik_host}:{traefik_port}/api/http/routers'
    subdomains = get_subdomains_from_traefik(traefik_api_url)
    if extra_domains != ['']:
        subdomains.extend(extra_domains)  # Ensure extra_domains is defined
    old_ip = None  # Initialize old_ip to None to force initial run

    while True:
        # Get current public IP
        new_ip = get_public_ip()

        # Run the logic if there's an IP change or it's the first run (old_ip is None)
        if new_ip != old_ip or old_ip is None:
            logging.info(f"IP change detected or first run: {old_ip} -> {new_ip}")
            for domain in subdomains:
                print(f"Domain: {domain}, Public IP: {new_ip}")
                logging.info(f"Domain: {domain}, Public IP: {new_ip}")
                update_a_record(domain, new_ip)
            old_ip = new_ip
        
        # Sleep for a longer duration since we're monitoring network interface changes
        time.sleep(30)  # Check every 5 minutes



if __name__ == "__main__":
    main()
