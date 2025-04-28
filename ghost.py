import os
import sys
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta

# Status codes to filter and their output files
STATUS_FILES = {
    200: '200-success.txt',
    301: '301-redirect.txt',
    404: '404-not-found.txt'
}

def load_domains(file_path):
    try:
        with open(file_path, 'r') as file:
            domains = [line.strip() for line in file if line.strip()]
        return domains
    except FileNotFoundError:
        print(f"❌ Error: File '{file_path}' not found.")
        sys.exit(1)

def scan_domain(domain):
    if not domain.startswith(('http://', 'https://')):
        domain = 'http://' + domain
    try:
        response = requests.get(domain, timeout=5)
        if response.status_code in STATUS_FILES:
            return response.status_code, domain
        return None, None  # Skip other status codes
    except requests.RequestException:
        return None, None  # Skip errors

def init_status_files():
    for code, filename in STATUS_FILES.items():
        with open(filename, 'w') as f:
            f.write(f"Domains with status {code}:\n\n")

def save_to_status_file(status_code, domain):
    with open(STATUS_FILES[status_code], 'a') as f:
        f.write(f"{domain}\n")

def show_progress(future_to_domain, total_domains):
    completed = 0
    saved_results = {code: 0 for code in STATUS_FILES}
    start_time = time.time()
    
    init_status_files()  # Create empty status files
    
    for future in as_completed(future_to_domain):
        completed += 1
        status_code, domain = future.result()
        
        if status_code:  # Only process valid status codes
            saved_results[status_code] += 1
            save_to_status_file(status_code, domain)
            
            # Calculate ETA
            elapsed = time.time() - start_time
            avg_time = elapsed / completed
            eta = int(avg_time * (total_domains - completed))
            eta_str = str(timedelta(seconds=eta)).split('.')[0]
            
            print(f"[{completed}/{total_domains}] {domain} --> {status_code} | ETA: {eta_str}")
        
        # Progress update every 10 domains
        if completed % 10 == 0:
            print(f"\n📊 Progress: {completed}/{total_domains}")
            for code, count in saved_results.items():
                print(f"  {code}: {count} domains")

def scan_domains(domains, max_threads=50):
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    print(f"⏳ Scanning {len(domains)} domains (saving to separate status files)...")
    
    try:
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            future_to_domain = {executor.submit(scan_domain, domain): domain for domain in domains}
            show_progress(future_to_domain, len(domains))
    except KeyboardInterrupt:
        print("\n⚠️ Scan interrupted! Partial results saved.")
    finally:
        print("\n✅ Scan completed! Results saved to:")
        for code, filename in STATUS_FILES.items():
            count = sum(1 for _ in open(filename)) - 2  # Subtract header lines
            print(f"  {filename} ({count} domains)")

if __name__ == "__main__":
    file_path = 'domains.txt'
    domains = load_domains(file_path)
    scan_domains(domains, max_threads=50)