#!/usr/bin/env python
# coding=utf-8

from dataclasses import dataclass
from typing import Any, Dict, Optional

from smolagents.local_python_executor import (
    BASE_BUILTIN_MODULES,
    BASE_PYTHON_TOOLS,
    evaluate_python_code,
)
from smolagents.tools import PipelineTool, Tool


class VisitWebpageTool2(Tool):
    name = "visit_webpage"
    description = (
        "Visits a webpage at the given url and reads its content as a markdown string. Use this to browse webpages."
    )
    inputs = {
        "url": {
            "type": "string",
            "description": "The url of the webpage to visit.",
        }
    }
    output_type = "string"

    def forward(self, url: str) -> str:
        try:
            import re

            import requests
            from markdownify import markdownify
            from requests.exceptions import RequestException

            from smolagents.utils import truncate_content
        except ImportError as e:
            raise ImportError(
                "You must install packages `markdownify` and `requests` to run this tool: for instance run `pip install markdownify requests`."
            ) from e
        try:
            # Send a GET request to the URL with a 20-second timeout
            response = requests.get(url, timeout=20, verify=False)
            response.raise_for_status()  # Raise an exception for bad status codes

            # Convert the HTML content to Markdown
            markdown_content = markdownify(response.text).strip()

            # Remove multiple line breaks
            markdown_content = re.sub(r"\n{3,}", "\n\n", markdown_content)

            # @baltop return truncate_content(markdown_content, 10000)
            return markdown_content

        except requests.exceptions.Timeout:
            return "The request timed out. Please try again later or check the URL."
        except RequestException as e:
            return f"Error fetching the webpage: {str(e)}"
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"

class FileDownloadTool(Tool):
    name = "file_download"
    description = (
        "Download a file from the given url and save it current directory. Use this tool to download files from webpages."
    )
    inputs = {
        "url": {
            "type": "string",
            "description": "The url of file to download.",
        },
        "file_name": {
            "type": "string",
            "description": "The name of file to download.",
        }        
    }
    output_type = "string"

    def forward(self, url: str, file_name: str) -> str:
        try:
            from requests import get
            from requests.exceptions import RequestException
        except ImportError as e:
            raise ImportError(
                "You must install packages  `requests` to run this tool: for instance run `pip install requests`."
            ) from e
        try:
            with open(file_name, "wb") as file:   # open in binary mode
                response = get(url)               # get request
                file.write(response.content)      # write to file
            return "down"
        except requests.exceptions.Timeout:
            return "The request timed out. Please try again later or check the URL."
        except RequestException as e:
            return f"Error fetching the webpage: {str(e)}"
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"