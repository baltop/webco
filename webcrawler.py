#!/usr/bin/env python
# coding=utf-8

import csv
import requests
from bs4 import BeautifulSoup
from typing import List, Tuple
import time
import random
import os
from datetime import datetime
from markdownify import markdownify

def read_urls_from_csv(csv_file: str) -> List[Tuple[str, str, str, str, str, str]]:
    """Read URLs and parameters from CSV file."""
    urls = []
    with open(csv_file, 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            if len(row) >= 6:
                url, param_name, site_name, category, start_marker, end_marker = row
                urls.append((url, param_name, site_name, category, start_marker, end_marker))
    return urls

def extract_param_value(url: str, param_name: str) -> int:
    """Extract the parameter value from the URL."""
    try:
        parts = url.split(f"{param_name}=")
        if len(parts) < 2:
            return 0
        
        value_part = parts[1]
        value = ""
        for char in value_part:
            if char.isdigit():
                value += char
            else:
                break
                
        return int(value) if value else 0
    except (ValueError, IndexError):
        return 0

def construct_url(base_url: str, param_name: str, value: int) -> str:
    """Construct a URL with the given parameter value."""
    if f"{param_name}=" in base_url:
        parts = base_url.split(f"{param_name}=")
        value_part = parts[1]
        
        # Find where the numeric part ends
        end_pos = 0
        for char in value_part:
            if char.isdigit():
                end_pos += 1
            else:
                break
                
        new_url = f"{parts[0]}{param_name}={value}{value_part[end_pos:]}"
        return new_url
    return base_url

def crawl_page(url: str) -> str:
    """Crawl a webpage and return its content."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error crawling {url}: {e}")
        return ""

def process_content(content: str, start_marker: str, end_marker: str) -> str:
    """Process the webpage content to markdown format and reduce file size using markers."""
    try:
        soup = BeautifulSoup(content, 'html.parser')
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        # Convert to markdown with links preserved
        markdown_text = markdownify(str(soup), heading_style="ATX")
        
        # Apply start and end markers to reduce file size
        reduced_text = ""
        start_found = False
        for line in markdown_text.splitlines():
            if not start_found and start_marker in line:
                start_found = True
                continue
            
            if start_found and end_marker in line:
                break
                
            if start_found:
                reduced_text += line + "\n"
        
        return reduced_text
    except Exception as e:
        print(f"Error processing content: {e}")
        return ""

def main():
    csv_file = "server.csv"
    urls = read_urls_from_csv(csv_file)
    
    for url, param_name, site_name, category, start_marker, end_marker in urls:
        print(f"Processing {site_name} ({category})")
        print(f"Using start marker: '{start_marker}' and end marker: '{end_marker}'")
        
        # Extract initial parameter value
        initial_value = extract_param_value(url, param_name)
        if not initial_value:
            print(f"Could not extract {param_name} value from {url}")
            continue
            
        # Crawl decreasing parameter values (10 pages)
        for i in range(10):
            current_value = initial_value - i
            current_url = construct_url(url, param_name, current_value)
            
            print(f"Crawling: {current_url}")
            content = crawl_page(current_url)
            if content:
                processed_text = process_content(content, start_marker, end_marker)
                
                # Create directory structure for saving files
                # Main directory with site name (지자체명)
                site_dir = os.path.join(os.getcwd(), site_name)
                os.makedirs(site_dir, exist_ok=True)
                
                # Current date directory (YYYY-MM-DD)
                current_date = datetime.now().strftime("%Y-%m-%d")
                date_dir = os.path.join(site_dir, current_date)
                os.makedirs(date_dir, exist_ok=True)
                
                # Save the processed text to a file with only the index number as name
                output_file = os.path.join(date_dir, f"{current_value}.md")
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(processed_text)
                
                print(f"Saved content to {output_file}")
            else:
                print(f"No content retrieved for {current_url}")
            
            # Add a small delay to avoid overloading the server
            time.sleep(random.uniform(1, 3))

if __name__ == "__main__":
    main()