#!/usr/bin/env python
# coding=utf-8

import csv
import os
import re
import requests
from bs4 import BeautifulSoup, Tag
from markdownify import markdownify
from datetime import datetime
from urllib.parse import urlparse
from typing import List, Tuple, Optional, Dict, Any

def read_server_list(csv_path: str) -> List[Tuple[str, str, str]]:
    """Read server URLs and names from CSV file."""
    servers = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if row and len(row) >= 3:  # Ensure we have URL, name, and category
                    servers.append((row[0].strip(), row[1].strip(), row[2].strip()))
    except Exception as e:
        print(f"Error reading CSV file: {e}")
    return servers

def create_filename(url: str, name: str, category: str) -> str:
    """Create a filename based on URL, name and category."""
    # Extract domain from URL
    domain = urlparse(url).netloc
    # Create a timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    # Create a valid filename
    filename = f"{timestamp}_{name}_{category}.md"
    # Replace invalid filename characters
    filename = re.sub(r'[\\/*?:"<>|]', "_", filename)
    return filename

def get_site_specific_content(url: str, soup: BeautifulSoup) -> Optional[Tag]:
    """Use site-specific extractors for known websites."""
    domain = urlparse(url).netloc.lower()
    path = urlparse(url).path.lower()
    
    # For Korean government sites
    if domain == 'www.samcheok.go.kr':
        # Samcheok city website
        
        # For the specific Samcheok site that we're working with, extract all potential announcements
        if 'cpage=' in url.lower() or path.endswith('web'):
            # Extract all links that might be announcements
            a_tags = soup.find_all('a')
            announcement_links = []
            
            for a in a_tags:
                text = a.get_text().strip()
                href = a.get('href', '')
                
                # Filter out navigation links - only keep substantial content links
                if (text and href and len(text) > 10 and 
                    not any(nav in text.lower() for nav in ['메뉴', '로그인', '사이트맵', '네비게이션', '바로가기']) and
                    not any(nav in href.lower() for nav in ['login', 'menu', 'navigation'])):
                    
                    # Skip links that might be navigation or utility links
                    skip_words = ['기상청', '여권', '지방세', '차량', '쓰레기', '처리안내', '이사 후', '110', '정부민원']
                    if not any(skip_word in text for skip_word in skip_words):
                        announcement_links.append((text, href))
            
            if announcement_links:
                # Create a clean div with just the announcement list
                container = Tag(name='div')
                container.append(soup.new_tag('h2'))
                container.h2.string = "공지 목록"
                
                for i, (text, href) in enumerate(announcement_links[:20]):  # Limit to 20 items
                    p = soup.new_tag('p')
                    p.string = f"- {text}"
                    container.append(p)
                
                return container
            
            # If we can't find good announcement links, try finding the board list table
            board_list = soup.select('.bbsList, .bbs-list, table.table')
            if board_list:
                # Create a cleaner version with just the table
                container = Tag(name='div')
                container.append(board_list[0])
                return container
            
        # For specific announcement pages, try these selectors
        content_divs = soup.select('.bbs_view, .bbs_content, .board_view, .board-view')
        if content_divs:
            return content_divs[0]
        
        # Try to find table inside content area
        tables = soup.select('table.table')
        if tables:
            for table in tables:
                # If table has some rows with good content, use it
                if len(table.find_all('tr')) > 3:
                    container = Tag(name='div')
                    container.append(table)
                    return container
                    
        # Try to find article content directly
        view_area = soup.select('.view, .view_cont, #sub_content')
        if view_area:
            return view_area[0]
            
        # Try to find content area
        content_area = soup.find('div', id='content')
        if content_area:
            title_div = content_area.find('div', class_='title')
            if title_div:
                title_div.decompose()  # Remove the title div as it's often redundant
            return content_area
            
        # Last resort: look for substantial paragraphs
        paragraphs = soup.find_all('p')
        if paragraphs:
            significant_paras = [p for p in paragraphs if len(p.get_text().strip()) > 100]
            if significant_paras:
                container = Tag(name='div')
                for p in significant_paras[:5]:  # Limit to first 5 substantial paragraphs
                    container.append(p)
                return container
    
    elif domain == 'www.anseong.go.kr':
        # Anseong city website
        # For list pages, extract the table of announcements
        if 'gosilist' in url.lower():
            # This is a listing page
            board_list = soup.select('.con_txt, table, .bbsList')
            if board_list:
                # Try to find a list of announcements
                announcements = []
                for item in board_list:
                    for a in item.find_all('a'):
                        text = a.get_text().strip()
                        if text and len(text) > 5:
                            announcements.append(f"- {text}")
                
                if announcements:
                    # Create a cleaner div with just the announcement list
                    container = Tag(name='div')
                    container.append(soup.new_tag('h2'))
                    container.h2.string = "공지 목록"
                    
                    for announcement in announcements[:15]:  # Limit to 15 items
                        p = soup.new_tag('p')
                        p.string = announcement
                        container.append(p)
                    
                    return container
                
                # If no announcements found, return the first board list
                return board_list[0]
        
        # For view pages, look for specific content containers
        if 'gosiview' in url.lower():
            # Look for specific view content
            view_content = soup.select('.view_cont, .view-content, .viewContent')
            if view_content:
                return view_content[0]
                
            # Try other content containers
            content_area = soup.select('.bbs_content, .board_view, .board_read, .con_txt')
            if content_area:
                return content_area[0]
    
    # No site-specific extractor found
    return None

def extract_main_content(soup: BeautifulSoup, url: str = "") -> Optional[Tag]:
    """Extract the main content area from the HTML."""
    # First try site-specific extractors if URL is provided
    if url:
        site_content = get_site_specific_content(url, soup)
        if site_content:
            return site_content
    
    # Common content container IDs and classes, ordered by specificity
    # First try very specific content containers that typically hold just the main content
    specific_content_selectors = [
        '.board_view', '.board-view', '.view_cont', '.view-content', '.board-content', '.boardContent',
        '.viewContent', '#viewContent', '.article-content', '.article_content', '.bbs_view',
        '.post-content', '.entry-content', '.content-detail', '.content-body', '.bbs_content',
        '#articleBody', '.article-body', '.news-content', '.news-body',
        '.board_cont', '.bd_content', '.bbs_content', '.content_area'
    ]
    
    # Try specific selectors first
    for selector in specific_content_selectors:
        content = soup.select(selector)
        if content:
            return content[0]
    
    # If nothing found with specific selectors, try to find the main content using heuristics
    # Look for elements with the most text content, as they're likely the main content
    paragraphs = soup.find_all('p')
    if paragraphs:
        # Find the paragraph with the most text
        max_text_len = 0
        max_p = None
        for p in paragraphs:
            text_len = len(p.get_text(strip=True))
            if text_len > max_text_len:
                max_text_len = text_len
                max_p = p
        
        # If found, get the closest div or article parent
        if max_p and max_text_len > 100:  # Only if paragraph has substantial text
            parent = max_p.find_parent(['div', 'article', 'section', 'main'])
            if parent:
                return parent
    
    # If still not found, look for the div with the most text
    divs = soup.find_all('div')
    if divs:
        max_text_len = 0
        max_div = None
        for div in divs:
            # Skip divs that are likely to be navigation
            if div.get('id') in ['header', 'footer', 'nav', 'menu', 'sidebar'] or \
               any(cls in div.get('class', []) for cls in ['header', 'footer', 'nav', 'menu', 'sidebar']):
                continue
                
            text_len = len(div.get_text(strip=True))
            if text_len > max_text_len:
                max_text_len = text_len
                max_div = div
        
        if max_div and max_text_len > 200:  # Only if div has substantial text
            return max_div
    
    # If all else fails, return the body (or None if no body)
    return soup.body

def clean_content(element: Tag) -> Tag:
    """Clean up the content by removing navigation, headers, footers, etc."""
    # Clone the element to avoid modifying the original
    content = element
    
    # Common elements to remove
    selectors_to_remove = [
        # Navigation elements
        'header', 'footer', 'nav', '.navigation', '.nav', '.menu', '#menu',
        'ul.menu', 'div.menu', '.navbar', '.gnb', '.lnb', '#gnb', '#lnb',
        '.main-nav', '.main-menu', '.sub-menu', '.top-menu', '.bottom-menu',
        
        # Sidebars and auxiliary content
        '.sidebar', '#sidebar', '.site-header', '.site-footer', '.widget',
        '.header', '.footer', '.breadcrumb', '.pagination', '.paging',
        
        # Utility elements
        '.search-form', '.search', '.searchbox', '#search', '.search-container',
        '.login', '.auth', '.user-info', '.user-menu', '.account-menu',
        
        # Advertisement and promotional content
        '.banner', '.ad', '.advertisement', '.promotion', '.sponsor',
        
        # Technical elements
        'script', 'style', 'iframe', 'noscript', 'meta', 'link',
        
        # Social media
        '.social', '.social-links', '.share', '.share-buttons',
        
        # Site utilities
        '.site-info', '.copyright', '.site-tools', '.tools', '.utility'
    ]
    
    # Remove unwanted elements
    for selector in selectors_to_remove:
        for element in content.select(selector):
            element.decompose()
    
    # Remove all navigation links that might be in lists
    for a_tag in content.find_all('a'):
        # If the link is part of a list or menu structure, remove it
        if a_tag.parent and (a_tag.parent.name == 'li' or 'menu' in a_tag.parent.get('class', [])):
            a_tag.decompose()
        # Or replace link with just its text content 
        else:
            a_tag.replace_with(a_tag.get_text())
    
    # Remove empty list elements that might have been left after removing links
    for ul_tag in content.find_all(['ul', 'ol']):
        if not ul_tag.find_all(string=True, recursive=True):
            ul_tag.decompose()
    
    # Remove table rows that are likely navigation items
    for tr in content.find_all('tr'):
        if len(tr.find_all('a')) > 3:  # If a row has too many links, it's likely navigation
            tr.decompose()
            
    # Remove very short paragraphs (often navigation fragments)
    for p in content.find_all('p'):
        if len(p.get_text(strip=True)) < 5:
            p.decompose()
    
    return content

def post_process_markdown(text: str) -> str:
    """Clean up the markdown content to make it more readable."""
    # Remove multiple line breaks
    text = re.sub(r"\n{3,}", "\n\n", text)
    
    # Remove markdown links but keep text, e.g. [text](url) -> text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    
    # Remove very short lines (likely navigation fragments)
    lines = text.split('\n')
    filtered_lines = []
    
    skip_next_lines = 0
    for i, line in enumerate(lines):
        if skip_next_lines > 0:
            skip_next_lines -= 1
            continue
            
        # Skip lines with just symbols or very short text
        stripped = line.strip()
        
        # Skip navigation-like elements (expanded for Korean government sites)
        skip_patterns = [
            r'^(홈|home)$', 
            r'^메뉴$', 
            r'^네비게이션$',
            r'^목록$',
            r'^(로그인|login)$',
            r'^사이트맵$',
            r'^[0-9]+$',  # Just a number
            r'^포털\s*(홈|사이트)$',  # Portal home
            r'^(global\s*navigation|전체메뉴|상단\s*메뉴|주\s*메뉴)$',  # Navigation menus
            r'^language$',
            r'^배너(모음)?$',  # Banner collection
            r'^전화번호$',
            r'^날씨$',
            r'^통합검색$',
            r'^이동$',
            r'^바로가기$'
        ]
        
        if stripped and len(stripped) > 2 and not all(c in '|*-_>#' for c in stripped):
            # Skip if it matches a navigation pattern
            if not any(re.match(pattern, stripped, re.IGNORECASE) for pattern in skip_patterns):
                # Check if it's a heading followed by navigation items
                if stripped.startswith('#') and i < len(lines) - 1:
                    next_line = lines[i+1].strip() if i+1 < len(lines) else ""
                    if next_line.startswith('*') or next_line.startswith('-'):
                        # Check if this is a navigation menu
                        nav_words = ['메뉴', '네비게이션', 'navigation', '안내', '바로가기', '링크']
                        if any(nav_word in stripped.lower() for nav_word in nav_words):
                            # Skip heading and the bullet points that follow
                            j = i + 1
                            while j < len(lines) and (lines[j].strip().startswith('*') or lines[j].strip().startswith('-')):
                                j += 1
                            skip_next_lines = j - i - 1
                        else:
                            filtered_lines.append(line)
                    else:
                        filtered_lines.append(line)
                else:
                    filtered_lines.append(line)
    
    text = '\n'.join(filtered_lines)
    
    # Remove extra blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    
    # Attempt to remove table-like structures that are likely navigation
    lines = text.split('\n')
    filtered_lines = []
    
    in_table = False
    table_lines = []
    
    for line in lines:
        if line.strip().startswith('|') and line.strip().endswith('|'):
            if not in_table:
                in_table = True
                table_lines = [line]
            else:
                table_lines.append(line)
        else:
            if in_table:
                # Check if this was a navigation table
                table_text = ' '.join([re.sub(r'\|', '', line).strip() for line in table_lines])
                words = [w for w in re.split(r'\s+', table_text) if w]
                
                # If average word length is short, it's likely navigation
                if words and sum(len(w) for w in words)/len(words) < 4 and len(words) < 10:
                    # Skip the table, it's likely navigation
                    pass
                else:
                    # Keep the table, it's likely content
                    filtered_lines.extend(table_lines)
                
                in_table = False
                table_lines = []
            
            if line.strip():
                filtered_lines.append(line)
    
    # Add any remaining table lines
    if in_table and table_lines:
        filtered_lines.extend(table_lines)
    
    text = '\n'.join(filtered_lines)
    
    # Remove multiple blank spaces and tabs
    text = re.sub(r' {2,}', ' ', text)
    text = re.sub(r'\t+', ' ', text)
    
    # For Korean content, remove some common navigation/utility phrases that might remain
    korean_nav_phrases = [
        r'누리집 이동 메뉴 여닫기',
        r'이 누리집은 대한민국 공식 전자정부 누리집입니다',
        r'새 창',
        r'본문 바로가기',
        r'만나이 보기 새창열림',
        r'SNS 공유하기 버튼',
        r'JavaScript has been disabled',
        r'본문인쇄'
    ]
    
    for phrase in korean_nav_phrases:
        text = re.sub(phrase, '', text, flags=re.IGNORECASE)
    
    # Final cleanup of empty lines and extra spaces
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join([line for line in lines if line])
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text

def crawl_website(url: str) -> str:
    """Crawl a website and return its content as markdown."""
    try:
        # Send a GET request to the URL with a timeout
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, timeout=30, verify=False, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get page title
        title = soup.title.text.strip() if soup.title else "Untitled Page"
        # Clean up title - remove site name if present after a separator
        title = re.sub(r'\s*[|:]\s*.+$', '', title)
        
        # Extract main content, passing the URL for site-specific extraction
        main_content = extract_main_content(soup, url)
        
        if main_content:
            # Clean the content
            clean_main_content = clean_content(main_content)
            
            # Convert the HTML content to Markdown with options to remove links
            markdown_options = {
                'strip': ['a'], # Strip links from text
                'heading_style': 'ATX', # Use # style headings
                'bullets': '*', # Use * for bullets
                'strip_empty': True # Remove empty tags
            }
            
            try:
                markdown_content = markdownify(str(clean_main_content), **markdown_options).strip()
            except TypeError:
                # If markdownify doesn't accept the options, try without options
                markdown_content = markdownify(str(clean_main_content)).strip()
            
            # Post-process the markdown to clean it up further
            markdown_content = post_process_markdown(markdown_content)
            
            # Extract a content summary if the content is too short
            if len(markdown_content) < 100:
                # Try to find the most significant text on the page as a fallback
                paragraphs = soup.find_all('p')
                significant_paragraphs = [p.get_text().strip() for p in paragraphs 
                                         if len(p.get_text().strip()) > 100]
                if significant_paragraphs:
                    markdown_content += "\n\n" + "\n\n".join(significant_paragraphs[:3])
            
            # Add title as heading
            return f"# {title}\n\n{markdown_content}"
        else:
            return f"# {title}\n\nNo content could be extracted from the page."
    except requests.exceptions.Timeout:
        return "# Error\nThe request timed out. Please try again later or check the URL."
    except requests.exceptions.RequestException as e:
        return f"# Error\nError fetching the webpage: {str(e)}"
    except Exception as e:
        return f"# Error\nAn unexpected error occurred: {str(e)}"

def get_paginated_urls(base_url: str, max_pages: int = 6) -> List[str]:
    """Generate paginated URLs from the base URL."""
    urls = []
    parsed_url = urlparse(base_url)
    domain = parsed_url.netloc.lower()
    path = parsed_url.path.lower()
    query = parsed_url.query
    
    # Different pagination handling for different sites
    if domain == 'www.samcheok.go.kr':
        # Extract current page parameter if it exists
        query_params = {}
        for param in query.split('&'):
            if '=' in param:
                key, value = param.split('=', 1)
                query_params[key] = value
        
        # Check if cpage parameter exists or needs to be added
        if 'cpage' in query_params:
            base_query = '&'.join([f"{k}={v}" for k, v in query_params.items() if k != 'cpage'])
            for page in range(1, max_pages + 1):
                if base_query:
                    urls.append(f"{parsed_url.scheme}://{domain}{path}?{base_query}&cpage={page}")
                else:
                    urls.append(f"{parsed_url.scheme}://{domain}{path}?cpage={page}")
        else:
            # If no cpage parameter, try adding it
            if query:
                for page in range(1, max_pages + 1):
                    urls.append(f"{parsed_url.scheme}://{domain}{path}?{query}&cpage={page}")
            else:
                for page in range(1, max_pages + 1):
                    urls.append(f"{parsed_url.scheme}://{domain}{path}?cpage={page}")
    
    elif domain == 'www.anseong.go.kr':
        # For Anseong site, we need a special approach - the URL is case-sensitive
        # The original URL case must be preserved
        original_path = parsed_url.path
        
        # Extract current parameters
        query_params = {}
        for param in query.split('&'):
            if '=' in param:
                key, value = param.split('=', 1)
                query_params[key] = value
        
        # Fix: For Anseong site, preserve the URL case and use the correct pagination parameter
        if 'gosiList.do' in original_path:
            # This is the list page, retain case sensitivity
            for page in range(1, max_pages + 1):
                page_url = f"{parsed_url.scheme}://{domain}{original_path}?{query}&curPage={page}"
                urls.append(page_url)
        else:
            # If it's not a recognized format, just return the original URL
            urls.append(base_url)
    
    # If we couldn't determine the pagination format or it's another site,
    # just return the original URL
    if not urls:
        return [base_url]
    
    return urls

def combine_announcements(announcements_list: List[List[str]]) -> List[str]:
    """Combine and deduplicate announcements from multiple pages."""
    # Flatten list of lists and remove duplicates while preserving order
    seen = set()
    combined = []
    
    for announcements in announcements_list:
        for item in announcements:
            # Use the text without the "- " prefix as the key to detect duplicates
            key = item[2:] if item.startswith("- ") else item
            if key not in seen:
                seen.add(key)
                combined.append(item)
    
    return combined

def crawl_paginated_site(base_url: str, name: str, category: str, max_pages: int = 6) -> str:
    """Crawl a paginated site and combine content from multiple pages."""
    print(f"  Generating paginated URLs for {name}...")
    urls = get_paginated_urls(base_url, max_pages)
    
    all_announcements = []
    all_content = []
    
    for page_num, url in enumerate(urls, 1):
        try:
            print(f"    Crawling page {page_num} of {len(urls)}...")
            content = crawl_website(url)
            
            # Extract announcements (lines starting with "- ")
            lines = content.split('\n')
            announcements = [line for line in lines if line.strip().startswith("- ")]
            
            if announcements:
                all_announcements.append(announcements)
            else:
                # If no announcements found, keep the full content
                all_content.append(content)
                
        except Exception as e:
            print(f"    Error crawling page {page_num}: {e}")
            continue
    
    # If we found announcements across pages, combine them
    if all_announcements:
        combined_announcements = combine_announcements(all_announcements)
        
        # Use the title and structure from the first page's content
        if all_content:
            first_content = all_content[0]
            # Extract title and any content before the announcements
            title_and_header = first_content.split("## 공지 목록")[0].strip()
            
            # Combine with the deduplicated announcements
            return f"{title_and_header}\n\n## 공지 목록\n\n" + "\n".join(combined_announcements)
        else:
            # If we don't have the structure, create a basic one
            return f"# {name} {category}\n\n## 공지 목록\n\n" + "\n".join(combined_announcements)
    elif all_content:
        # If no announcements were found but we have content, use the first page
        return all_content[0]
    else:
        # If nothing was found
        return f"# {name} {category}\n\nNo content could be extracted from any page."

def main():
    """Main function to crawl websites from server.csv."""
    # Disable SSL warnings
    requests.packages.urllib3.disable_warnings()
    
    # Read server list
    servers = read_server_list('server.csv')
    
    if not servers:
        print("No servers found in server.csv")
        return
    
    print(f"Found {len(servers)} servers in server.csv")
    
    # Crawl each server with pagination
    for url, name, category in servers:
        print(f"Crawling {name} ({category})...")
        
        # Get paginated content (up to 6 pages)
        content = crawl_paginated_site(url, name, category, max_pages=6)
        
        # Create filename
        filename = create_filename(url, name, category)
        
        # Add metadata as frontmatter
        frontmatter = f"""---
url: {url}
source: {name}
category: {category}
crawled_at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
paginated: yes
max_pages: 6
---

"""
        
        # Save content to file
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(frontmatter + content)
            print(f"  Saved to {filename}")
        except Exception as e:
            print(f"  Error saving file: {e}")

if __name__ == "__main__":
    main()