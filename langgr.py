from typing import Annotated, List, Dict, TypedDict, Tuple, Any
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from smolagents import CodeAgent, LiteLLMModel, Tool
from pydantic import BaseModel, Field

import csv
import requests
from bs4 import BeautifulSoup
import time
import random
import os
from datetime import datetime


# Web crawling functions ported from webcrawler.py
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
    """Process the webpage content and reduce file size using markers."""
    try:
        soup = BeautifulSoup(content, 'html.parser')
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        # Get text
        text = soup.get_text()
        # Break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Apply start and end markers to reduce file size
        reduced_text = ""
        start_found = False
        for line in text.splitlines():
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


def save_content(content: str, site_name: str, current_value: int) -> str:
    """Save the processed content to a file."""
    try:
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
            f.write(content)
        
        return f"Content saved to {output_file}"
    except Exception as e:
        return f"Error saving content: {e}"


# Input/Output models for tools
class CrawlUrlInput(BaseModel):
    url: str = Field(description="URL to crawl")

class ProcessContentInput(BaseModel):
    content: str = Field(description="HTML content to process")
    start_marker: str = Field(description="Start marker for content extraction")
    end_marker: str = Field(description="End marker for content extraction")
    
class SaveContentInput(BaseModel):
    content: str = Field(description="Processed content to save")
    site_name: str = Field(description="Site name for directory structure")
    current_value: int = Field(description="Current parameter value for filename")


# Tools for the agent
class CrawlWebpageTool(Tool):
    name = "crawl_webpage"
    description = "Crawls a webpage and returns its content."
    inputs = CrawlUrlInput
    
    def __call__(self, url: str) -> str:
        return crawl_page(url)


class ProcessContentTool(Tool):
    name = "process_content"
    description = "Processes webpage content with markers."
    inputs = ProcessContentInput
    
    def __call__(self, content: str, start_marker: str, end_marker: str) -> str:
        return process_content(content, start_marker, end_marker)


class SaveContentTool(Tool):
    name = "save_content"
    description = "Saves processed content to a file."
    inputs = SaveContentInput
    
    def __call__(self, content: str, site_name: str, current_value: int) -> str:
        return save_content(content, site_name, current_value)


# LangGraph state definition
class WebCrawlerState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    csv_file: str
    current_url_index: int
    current_page_index: int
    crawl_results: List[Dict]
    completed: bool


# Initialize LLM model
model = LiteLLMModel(model_id="anthropic/claude-3-5-sonnet-latest")


# Function to get content directly without using agent
def get_page_content(url: str, start_marker: str, end_marker: str, site_name: str, current_value: int) -> str:
    """Process a page and save content directly without using the agent."""
    print(f"Processing URL: {url}")
    # 1. Crawl the page
    content = crawl_page(url)
    if not content:
        return f"Failed to crawl {url}"
    
    # 2. Process the content
    processed_content = process_content(content, start_marker, end_marker)
    if not processed_content:
        return f"Failed to process content from {url}"
    
    # 3. Save the content
    result = save_content(processed_content, site_name, current_value)
    return result


# LangGraph node functions
def initialize_crawler(state: WebCrawlerState) -> Dict:
    """Initialize the crawler with data from CSV file."""
    csv_file = state.get('csv_file', 'server.csv')
    
    return {
        "csv_file": csv_file,
        "current_url_index": 0,
        "current_page_index": 0,
        "crawl_results": [],
        "completed": False
    }


def process_next_url(state: WebCrawlerState) -> Dict:
    """Process the next URL from the CSV file."""
    csv_file = state['csv_file']
    current_url_index = state['current_url_index']
    current_page_index = state['current_page_index']
    
    # Read all URLs from CSV
    urls = read_urls_from_csv(csv_file)
    
    # Check if we've processed all URLs
    if current_url_index >= len(urls):
        return {"completed": True}
    
    # Get current URL info
    url, param_name, site_name, category, start_marker, end_marker = urls[current_url_index]
    
    # Extract initial parameter value
    initial_value = extract_param_value(url, param_name)
    if not initial_value:
        print(f"Could not extract {param_name} value from {url}")
        return {
            "current_url_index": current_url_index + 1,
            "current_page_index": 0
        }
    
    # Calculate current parameter value (decreasing order)
    current_value = initial_value - current_page_index
    current_url = construct_url(url, param_name, current_value)
    
    print(f"Processing {site_name} ({category})")
    print(f"Using start marker: '{start_marker}' and end marker: '{end_marker}'")
    print(f"Crawling: {current_url}")
    
    # Process the page directly instead of using agent
    result = get_page_content(current_url, start_marker, end_marker, site_name, current_value)
    print(f"Result: {result}")
    
    # Add a small delay to avoid overloading the server
    time.sleep(random.uniform(2, 4))
    
    # Update state based on current progress
    if current_page_index < 39:  # We want to crawl 10 pages (0-9)
        # Move to next page of the same URL
        next_state = {
            "current_page_index": current_page_index + 1,
            "crawl_results": state['crawl_results'] + [{"url": current_url, "result": result}]
        }
    else:
        # Move to next URL, reset page index
        next_state = {
            "current_url_index": current_url_index + 1,
            "current_page_index": 0,
            "crawl_results": state['crawl_results'] + [{"url": current_url, "result": result}]
        }
    
    return next_state


def check_completion(state: WebCrawlerState) -> str:
    """Check if crawling is completed and decide next step."""
    if state.get('completed', False):
        return "completed"
    else:
        return "continue_crawling"


# Define the workflow
workflow = StateGraph(WebCrawlerState)

# Add nodes
workflow.add_node("initialize", initialize_crawler)
workflow.add_node("process_url", process_next_url)

# Set entry point
workflow.set_entry_point("initialize")

# Define edges
workflow.add_conditional_edges(
    "process_url",
    check_completion,
    {
        "continue_crawling": "process_url",
        "completed": END
    }
)
workflow.add_edge("initialize", "process_url")

# Compile the graph
graph = workflow.compile()

# Run the workflow
if __name__ == "__main__":
    initial_state = {
        "messages": [HumanMessage(content="Start web crawling")],
        "csv_file": "server.csv",
        "current_url_index": 0,
        "current_page_index": 0,
        "crawl_results": [],
        "completed": False
    }
    
    # for output in graph.stream(initial_state, {"recursion_limit": 100}):
    for output in graph.invoke(initial_state, {"recursion_limit": 300}):
        print("#################### WORKFLOW OUTPUT ####################")
        if "current_url_index" in output:
            print(f"URL Index: {output['current_url_index']}, Page Index: {output['current_page_index']}")
        if output.get('completed', False):
            print("Web crawling completed!")
            # Optional: Summarize results
            for i, result in enumerate(output.get('crawl_results', [])):
                print(f"Result {i+1}: {result['url']}")
        print("########################################################")