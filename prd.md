Okay, let's break down the provided Python script (`webcrawler.py`) and create a detailed Product Requirements Definition (PRD) document suitable for another developer.

---

## Product Requirements Definition: Configurable Web Content Extractor

**Version:** 1.0
**Date:** 2023-10-27
**Author:** (Based on analysis of `webcrawler.py`)
**Status:** Definition

**1. Introduction**

This document defines the requirements for a Python-based web crawler designed to extract specific content sections from multiple target websites, convert them to Markdown format, and save them locally. The crawler's behavior is configured through an external CSV file, allowing users to specify target URLs, relevant parameters for iteration, and markers to isolate desired content blocks. The primary use case is collecting updates or articles (like notices or posts) from specific web pages, particularly focusing on content identified by start and end markers within the HTML structure after initial cleaning and Markdown conversion.

**2. Goals and Objectives**

*   **Automate Content Collection:** To automatically fetch and save specific content sections from predefined web pages.
*   **Configurability:** Allow users to easily define and manage target websites and extraction parameters via a CSV file without modifying the core script.
*   **Content Isolation:** Extract only the relevant portion of a webpage's content using user-defined start and end text markers.
*   **Format Conversion:** Convert the extracted HTML content into a clean Markdown format.
*   **Structured Storage:** Save the extracted content into a hierarchical directory structure based on the site name and the date of crawling.
*   **Basic Politeness:** Implement simple delays between requests to avoid overwhelming target servers.

**3. Scope**

**3.1. In Scope:**

*   Reading crawler configuration from a specified CSV file (`server.csv`).
*   Parsing base URLs to extract an initial numeric parameter value.
*   Generating a sequence of target URLs by decrementing the extracted numeric parameter value (for a fixed number of iterations, currently 10).
*   Fetching HTML content from generated URLs using HTTP GET requests.
*   Spoofing a standard browser `User-Agent` header.
*   Setting a timeout for HTTP requests.
*   Basic error handling for HTTP request failures (e.g., connection errors, timeouts, non-2xx status codes).
*   Parsing fetched HTML content using BeautifulSoup.
*   Removing `<script>` and `<style>` elements from the parsed HTML.
*   Converting the cleaned HTML snippet to Markdown format (using `markdownify` library with ATX heading style).
*   Extracting lines of text from the generated Markdown content that fall between specified start and end marker strings (inclusive of start, exclusive of end).
*   Creating a directory structure: `./<Site Name>/<YYYY-MM-DD>/`.
*   Saving the extracted Markdown content into files named `<numeric_parameter_value>.md` within the date-specific directory.
*   Implementing a randomized delay (1-3 seconds) between processing each URL.
*   Printing status messages (processing site, crawling URL, saving file, errors) to the standard output.

**3.2. Out of Scope:**

*   Crawling websites requiring JavaScript execution for content rendering.
*   Handling complex login mechanisms or session management.
*   Advanced anti-bot measure bypass techniques (e.g., CAPTCHA solving, complex header manipulation, IP rotation).
*   Storing extracted data in databases or other formats besides individual Markdown files.
*   Providing a graphical user interface (GUI).
*   Incremental crawling or detecting changes (it re-fetches content on each run).
*   Advanced error handling and retry logic beyond basic request exceptions.
*   Sophisticated rate limiting or respecting `robots.txt` (beyond the simple delay).
*   Input validation for the CSV file contents beyond basic row length checking.
*   Handling non-numeric parameter values for iteration.

**4. Functional Requirements**

| ID    | Requirement Description                                                                                                                                                                                               | Details & Constraints                                                                                                                                                                                                 | Priority |
| :---- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------- |
| FR1   | **Configuration Loading:** The system shall read crawler configurations from a CSV file named `server.csv` located in the same directory as the script.                                                              | - CSV format: `url, param_name, site_name, category, start_marker, end_marker` per row.<br>- Encoding: UTF-8.<br>- Rows with fewer than 6 columns should be skipped or handled gracefully (currently skipped implicitly). | Must     |
| FR2   | **Initial Parameter Extraction:** For each configuration row, the system shall extract an initial *integer* value associated with the `param_name` from the provided `url`.                                          | - Assumes `param_name=` exists in the URL.<br>- Extracts the consecutive digits immediately following `param_name=`.<br>- If extraction fails or is non-numeric, processing for this URL should be skipped.          | Must     |
| FR3   | **URL Generation:** The system shall generate 10 target URLs for each configuration by decrementing the initial parameter value by 0, 1, 2, ..., 9 and reconstructing the URL.                                    | - Reconstructs the URL by replacing the original numeric value associated with `param_name` with the new decremented value.<br>- Handles potential non-parameter parts of the URL following the numeric value.         | Must     |
| FR4   | **Web Page Fetching:** The system shall fetch the HTML content of each generated URL using an HTTP GET request.                                                                                                       | - Include `User-Agent` header: 'Mozilla/5.0...'.<br>- Set request timeout to 10 seconds.<br>- Raise an error for non-successful HTTP status codes (e.g., 4xx, 5xx).                                                  | Must     |
| FR5   | **HTML Parsing and Cleaning:** The system shall parse the fetched HTML content and remove `<script>` and `<style>` tags and their contents.                                                                         | - Use `BeautifulSoup` with a standard parser (e.g., `html.parser`).                                                                                                                                                 | Must     |
| FR6   | **Markdown Conversion:** The system shall convert the cleaned HTML structure into Markdown format.                                                                                                                    | - Use the `markdownify` library.<br>- Preserve links.<br>- Use ATX style for headings (`# Heading`).                                                                                                                  | Must     |
| FR7   | **Content Section Extraction:** The system shall process the generated Markdown text line by line and extract only the lines between the `start_marker` and `end_marker` specified in the configuration.           | - Search starts after the line containing `start_marker`.<br>- Extraction stops *before* the line containing `end_marker`.<br>- Markers are simple string containment checks.<br>- If start marker isn't found, no content is extracted.<br>- If end marker isn't found after start, content until the end is extracted. | Must     |
| FR8   | **Output File Storage:** The system shall save the extracted Markdown content to a local file.                                                                                                                        | - Directory structure: `./<site_name>/<YYYY-MM-DD>/`. Directories must be created if they don't exist.<br>- Filename: `<current_parameter_value>.md`.<br>- File encoding: UTF-8.                                       | Must     |
| FR9   | **Request Throttling:** The system shall pause execution for a random duration between 1 and 3 seconds after processing each URL.                                                                                   | - Use `time.sleep()` and `random.uniform(1, 3)`.                                                                                                                                                                   | Must     |
| FR10  | **Basic Logging:** The system shall print status information to the console during execution.                                                                                                                         | - Indicate which site/category is being processed.<br>- Print the URL being crawled.<br>- Confirm successful saving and the output file path.<br>- Print error messages encountered during crawling or processing.     | Must     |
| FR11  | **Error Handling (Network):** The system shall catch exceptions during web page fetching and print an error message.                                                                                                  | - Catch `requests.RequestException`.<br>- Print the failing URL and the error message.<br>- Continue processing the next URL or configuration.                                                                          | Must     |
| FR12  | **Error Handling (Content Processing):** The system shall catch general exceptions during content processing (parsing, markdown conversion, marker logic) and print an error message.                                  | - Catch generic `Exception`.<br>- Print an error message indicating a processing failure.<br>- Return/save empty content for that URL.                                                                                | Should   |

**5. Non-Functional Requirements**

| ID   | Requirement Description      | Details & Constraints                                                                                                                               | Priority |
| :--- | :--------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------- | :------- |
| NFR1 | **Reliability:**             | The script should handle common network errors gracefully and continue processing other URLs/configurations. It should not crash on single failures. | Must     |
| NFR2 | **Maintainability:**         | The code should be reasonably well-structured with functions for distinct tasks. Type hints should be used for clarity.                              | Should   |
| NFR3 | **Usability (Developer):**   | Configuration via the external `server.csv` file should be straightforward. Console output should provide adequate feedback on the process.         | Must     |
| NFR4 | **Performance:**             | While not highly optimized for speed (sequential requests per site), the script should complete within a reasonable timeframe for 10 pages per site. | Should   |
| NFR5 | **Resource Usage:**          | Memory and CPU usage should be reasonable for processing typical web pages.                                                                         | Should   |

**6. Input/Output Specifications**

**6.1. Input:**

*   **`server.csv` file:**
    *   Location: Same directory as the script.
    *   Encoding: UTF-8.
    *   Columns:
        1.  `url`: The base URL containing the parameter to be decremented (e.g., `http://example.com/notice?boardId=123&page=1`).
        2.  `param_name`: The name of the query parameter whose value will be decremented (e.g., `boardId`).
        3.  `site_name`: A human-readable name for the website, used for creating the output directory (e.g., `Example Notices`).
        4.  `category`: A category name, currently used for logging context (e.g., `Government`).
        5.  `start_marker`: A string that identifies the beginning of the content block to extract (searched in the Markdown output).
        6.  `end_marker`: A string that identifies the end of the content block to extract (searched in the Markdown output).

**6.2. Output:**

*   **Markdown Files:**
    *   Location: `./<site_name>/<YYYY-MM-DD>/<numeric_parameter_value>.md`
    *   Content: Extracted and cleaned content in Markdown format.
    *   Encoding: UTF-8.
*   **Console Output:**
    *   Status messages indicating progress and errors (as defined in FR10).

**7. Error Handling Strategy**

*   **Network Errors (`requests.RequestException`):** Log the error with the URL and continue to the next URL. Do not attempt retries.
*   **Parameter Extraction Errors:** Log the error with the URL and skip processing for this entire configuration entry (site).
*   **Content Processing Errors (`Exception` during `process_content`):** Log the error, return an empty string for the content, resulting in an empty `.md` file being saved (or no file, depending on implementation details if empty content should prevent saving).
*   **File System Errors (Directory/File Creation):** Standard Python `IOError`/`OSError` exceptions will likely halt the script if permissions are incorrect. Basic handling involves `os.makedirs(exist_ok=True)`. More robust handling is out of scope.

**8. Dependencies**

The system requires the following Python libraries to be installed:

*   `requests`
*   `beautifulsoup4`
*   `markdownify`
*   `typing` (Standard library, but usage implies Python 3.5+)

**9. Future Considerations / Potential Enhancements (Out of Scope for v1.0)**

*   Support for non-numeric or more complex pagination/iteration parameters.
*   Ability to configure the number of pages/iterations per site.
*   More robust error handling, including retries with exponential backoff.
*   Asynchronous fetching (e.g., using `asyncio` with `aiohttp`, or migrating to Scrapy) for significantly improved performance.
*   Support for JavaScript rendering (e.g., using `requests-html`, `Selenium`, or `Playwright`).
*   Database integration for storing results.
*   Delta checking to only download new or changed content.
*   More sophisticated content extraction methods (e.g., CSS selectors, XPath directly on HTML before Markdown conversion).
*   Respecting `robots.txt`.
*   Better configuration management (e.g., YAML or JSON files).
*   Monitoring and alerting capabilities.

---

This PRD provides a detailed breakdown of what the `webcrawler.py` script does, its inputs, outputs, limitations, and requirements, making it easier for another developer to understand, maintain, or potentially build upon it.
