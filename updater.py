import requests
import concurrent.futures
import os
from datetime import datetime
import time 

def download_file(url, file_path):
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(file_path, 'w') as file:
            file.write(response.text)
        return True
    except requests.RequestException as e:
        print(f"Error downloading {url}: {str(e)}")
        return False

def check_proxy(proxy):
    try:
        response = requests.get("http://httpbin.org/ip", proxies={"http": proxy, "https": proxy}, timeout=5)
        return proxy if response.status_code == 200 else None
    except:
        return None

def process_proxies(file_path, output_file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return 0

    with open(file_path, 'r') as file:
        proxies = [line.strip() for line in file]

    working_proxies = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_proxy = {executor.submit(check_proxy, proxy): proxy for proxy in proxies}
        for future in concurrent.futures.as_completed(future_to_proxy):
            result = future.result()
            if result:
                working_proxies.append(result)

    with open(output_file_path, 'w') as file:
        for proxy in working_proxies:
            file.write(proxy + '\n')
            
    print(f"{os.path.splitext(os.path.basename(file_path))[0]} - Found {len(working_proxies)} working proxies.")
    return len(working_proxies)

def download_files(urls, file_paths):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_file = {executor.submit(download_file, url, path): path for url, path in zip(urls, file_paths)}
        for future in concurrent.futures.as_completed(future_to_file):
            if not future.result():
                print(f"Failed to download file: {future_to_file[future]}")
                
def update_readme(content, readme_path='README.md'):
    try:
        with open(readme_path, 'w') as readme_file:
            readme_file.write(content)
        return True
    except Exception as e:
        print(f"Error updating README: {e}")
        return False

def main(urls, proxy_file_paths, output_file_paths):
    current_time = datetime.utcnow().strftime('%A %d-%m-%Y %H:%M:%S UTC')

    # Step 1: Download files
    download_files(urls, proxy_file_paths)
    print("Files downloaded. Sleeping for 20 seconds.")

    # Step 2: Process proxies and construct README content
    readme_content = f"# PROXY-Alive\n\nAccess a publicly-sourced, regularly validated list of proxies, pre-checked for availability to save you the hassle of verification.\n\nLast Checked: `{current_time}`\n\nAlive:\n"
    for proxy_file_path, output_file_path in zip(proxy_file_paths, output_file_paths):
        count = process_proxies(proxy_file_path, output_file_path)
        proxy_type = os.path.splitext(os.path.basename(proxy_file_path))[0]
        readme_content += f"- {proxy_type}: `{count if count is not None else 'N/A'}`\n"

    # Append additional content here if needed
    readme_content += '''
## GET PROXY

### HTTP(S)

```https://raw.githubusercontent.com/junioralive/PROXY-Alive/main/http.txt```

### SOCKS4

```https://raw.githubusercontent.com/junioralive/PROXY-Alive/main/socks4.txt```

### SOCKS5

```https://raw.githubusercontent.com/junioralive/PROXY-Alive/main/socks5.txt```

## DISCLAIMER

This resource is provided solely for educational purposes. I neither endorse nor encourage engaging in any illegal activities.

If you appreciate my work, kindly consider giving credit, starring, and following. Your support is greatly appreciated! 

## [CONTACT](https://t.me/TheJuniorAlive)
'''

    # Step 3: Update README.md
    update_readme(readme_content)
    print("README updated successfully.")

# DATA
urls = [
    'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
    'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt',
    'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt'
]
proxy_file_paths = [
    'http.txt',
    'socks4.txt',
    'socks5.txt'
]
output_file_paths = [
    'http.txt',
    'socks4.txt',
    'socks5.txt'
]

# Run the script
main(urls, proxy_file_paths, output_file_paths)
