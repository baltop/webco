# Web Crawler Project (webco)

A Python tool for crawling websites and saving their content as markdown files.

## Features

- Crawls websites from a CSV list
- Extracts main content from HTML
- Converts HTML to clean markdown
- Saves files with metadata frontmatter
- Handles errors gracefully

## Setup

1. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install required packages:
   ```bash
   pip install requests beautifulsoup4 markdownify
   ```

## Usage

1. Create a CSV file named `server.csv` with the following format:
   ```
   https://example.com/page,variable key,Site Name,Category,Start marker,End marker
   https://another-site.com,variable key,Another Site,Another Category,Start marker,End marker
   ```

2. Run the crawler:
   ```bash
   python webcrawler.py
   ```

3. The crawler will:
   - Read URLs from `server.csv`
   - Crawl each website
   - Save content as markdown files in the current directory
   - Files are named with the format: `YYYYMMDD_SiteName_varibaleValue.md`
   - VaribaleValue is number. the key is in csv file. 

## Output

Each markdown file contains:
- YAML frontmatter with metadata
- Title as H1 heading
- Main content of the webpage


## Customization

- Edit the `extract_main_content` function to customize content extraction
- Modify the `clean_content` function to remove unwanted elements
- Change the filename format in the `create_filename` function

## Requirements

- Python 3.6+
- BeautifulSoup4
- Markdownify
- Requests