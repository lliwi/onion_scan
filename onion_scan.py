import requests
from bs4 import BeautifulSoup
import csv
import random
import string
import argparse
import signal
import sys
import os
import fcntl

import re

def is_onion_url(url):
    pattern16 = r"http[s]?://[a-z0-9]{16}\.onion"
    pattern56 = r"http[s]?://[a-z0-9]{56}\.onion"
    match16 = re.match(pattern56, url)
    match56 = re.match(pattern56, url)
    return bool(match16 or match56)


# Add URLs to file
def add_file(title, url):
    file_exists = os.path.isfile('onion_archive.csv')
    if not file_exists:
        with open('onion_archive.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Title', 'URL'])  # Write headers if the file is empty

    with open('onion_archive.csv', mode='r') as file:
        reader = csv.reader(file)
        urls = [row[1] for row in reader]

    if url in urls:
        pass
    else:
        with open('onion_archive.csv', mode='a+', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([title, url])
        print(f"Added '{title}' with URL '{url}' to the file.")

# Mantener un conjunto de URLs visitadas
visited_urls = set()

# Check onion URL
def check_url(url):
    try:
        domain = url.split("/")
        domain = domain[2]
        if domain in visited_urls:
            pass
        elif not is_onion_url(url):
            pass
        else:
            visited_urls.add(domain)

            response = requests.get(url, proxies=proxies)
            html_content = response.content

            soup = BeautifulSoup(html_content, 'html.parser')
            title = soup.title.string.strip()

            if response.status_code == 200:
                add_file(title, url)
                find_onion_links(url)
    except Exception as e:
        pass

# Find URLs
def find_onion_links(url):
    try:
        response = requests.get(url, proxies=proxies)
        html_content = response.content

        soup = BeautifulSoup(html_content, 'html.parser')
        links = soup.find_all('a')

        for link in links:
            check_url(link.get('href'))
    except Exception as e:
        pass


# Handle Ctrl+C event
def signal_handler(sig, frame):
    print('Program stopped by Ctrl+C')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# Set file descriptor to non-blocking mode
fcntl.fcntl(sys.stdout, fcntl.F_SETFL, os.O_NONBLOCK)

# Generate base URL
parser = argparse.ArgumentParser(description='Description of the script')
parser.add_argument('-u', '--start_url', type=str, help='start onion URL')
parser.add_argument('-f', '--start_url_file', type=str, help='start onion URLs by file')
parser.add_argument('-p', '--proxy', type=str, help='Tor proxy URL and port')

args = parser.parse_args()

proxy_url = args.proxy

if proxy_url is not None:
    proxies = {
        'http': proxy_url,
        'https': proxy_url
    }
else:
    print('Set the --proxy (proxy URL) and --port (proxy port)')
    sys.exit(0)

start_url = args.start_url
start_url_file = args.start_url_file

if start_url is not None:
    try:
        check_url(args.start_url)
    except KeyboardInterrupt:
        print('Program stopped by Ctrl+C')
        sys.exit(0)

if start_url_file is not None:
    try:
        with open(args.start_url_file, 'r') as file:
            for line in file:
                url = line.strip()
                check_url(url)
    except FileNotFoundError:
        print(f"File '{args.start_url_file}' not found.")
    except IOError:
        print(f"Error reading the file '{args.start_url_file}'.")

if (start_url & start_url_file) is None:
    print(f"Starting with random urls, be patient. :)")
    try:
        while True:
            alphabet = string.ascii_lowercase + string.digits
            onion_url = ''.join(random.choice(alphabet) for _ in range(56))
            check_url(f"http://{onion_url}.onion")
    except KeyboardInterrupt:
        print('Program stopped by Ctrl+C')
        sys.exit(0)
