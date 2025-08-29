#!/usr/bin/env python3
"""
Document Extraction Tools
=========================

Advanced document and image data extraction capabilities for Ollama tools.
"""

import asyncio
import logging
import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import fitz  # PyMuPDF for PDF processing
import pytesseract
from PIL import Image
import io

logger = logging.getLogger(__name__)

class DocumentExtractor:
    """Advanced document extraction tool"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })

    async def extract_from_url(self, url: str, extraction_type: str = "auto") -> Dict[str, Any]:
        """Extract data from a URL based on content type"""

        try:
            # Determine content type
            response = self.session.head(url, timeout=10)
            content_type = response.headers.get('content-type', '').lower()

            if 'pdf' in content_type:
                return await self._extract_pdf(url)
            elif any(img_type in content_type for img_type in ['image', 'jpeg', 'png', 'gif', 'webp']):
                return await self._extract_image(url)
            else:
                # Assume HTML/webpage
                return await self._extract_webpage(url, extraction_type)

        except Exception as e:
            logger.error(f"Extraction error for {url}: {e}")
            return {
                "url": url,
                "extraction_type": extraction_type,
                "success": False,
                "error": str(e),
                "data": {}
            }

    async def _extract_pdf(self, url: str) -> Dict[str, Any]:
        """Extract text and metadata from PDF"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            # Save PDF to memory
            pdf_data = io.BytesIO(response.content)

            # Open with PyMuPDF
            doc = fitz.open(stream=pdf_data, filetype="pdf")

            text_content = ""
            metadata = {
                "title": doc.metadata.get("title", ""),
                "author": doc.metadata.get("author", ""),
                "subject": doc.metadata.get("subject", ""),
                "creator": doc.metadata.get("creator", ""),
                "producer": doc.metadata.get("producer", ""),
                "pages": len(doc)
            }

            # Extract text from all pages
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text_content += page.get_text()

            doc.close()

            return {
                "url": url,
                "content_type": "pdf",
                "success": True,
                "metadata": metadata,
                "text_content": text_content,
                "word_count": len(text_content.split()),
                "character_count": len(text_content)
            }

        except Exception as e:
            return {
                "url": url,
                "content_type": "pdf",
                "success": False,
                "error": str(e)
            }

    async def _extract_image(self, url: str) -> Dict[str, Any]:
        """Extract text from image using OCR"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            # Open image
            image = Image.open(io.BytesIO(response.content))

            # Extract text using OCR
            text_content = pytesseract.image_to_string(image)

            return {
                "url": url,
                "content_type": "image",
                "success": True,
                "image_size": image.size,
                "image_format": image.format,
                "text_content": text_content,
                "word_count": len(text_content.split()),
                "character_count": len(text_content)
            }

        except Exception as e:
            return {
                "url": url,
                "content_type": "image",
                "success": False,
                "error": str(e)
            }

    async def _extract_webpage(self, url: str, extraction_type: str) -> Dict[str, Any]:
        """Extract structured data from webpage"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract basic metadata
            metadata = {
                "title": soup.title.string if soup.title else "",
                "description": "",
                "keywords": "",
                "author": ""
            }

            # Extract meta tags
            for meta in soup.find_all('meta'):
                if meta.get('name') == 'description':
                    metadata['description'] = meta.get('content', '')
                elif meta.get('name') == 'keywords':
                    metadata['keywords'] = meta.get('content', '')
                elif meta.get('name') == 'author':
                    metadata['author'] = meta.get('content', '')

            # Extract main content based on type
            if extraction_type == "text":
                content = self._extract_text_content(soup)
            elif extraction_type == "tables":
                content = self._extract_tables(soup)
            elif extraction_type == "links":
                content = self._extract_links(soup)
            elif extraction_type == "images":
                content = self._extract_images(soup, url)
            else:
                # Auto extraction
                content = {
                    "text": self._extract_text_content(soup),
                    "links": self._extract_links(soup),
                    "tables": self._extract_tables(soup),
                    "images": self._extract_images(soup, url)
                }

            return {
                "url": url,
                "content_type": "webpage",
                "extraction_type": extraction_type,
                "success": True,
                "metadata": metadata,
                "content": content
            }

        except Exception as e:
            return {
                "url": url,
                "content_type": "webpage",
                "success": False,
                "error": str(e)
            }

    def _extract_text_content(self, soup: BeautifulSoup) -> str:
        """Extract main text content from webpage"""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text
        text = soup.get_text()

        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)

        return text

    def _extract_links(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract all links from webpage"""
        links = []
        for a in soup.find_all('a', href=True):
            links.append({
                "text": a.get_text().strip(),
                "url": a['href'],
                "title": a.get('title', '')
            })
        return links

    def _extract_tables(self, soup: BeautifulSoup) -> List[List[List[str]]]:
        """Extract tables from webpage"""
        tables = []
        for table in soup.find_all('table'):
            table_data = []
            for row in table.find_all('tr'):
                row_data = []
                for cell in row.find_all(['td', 'th']):
                    row_data.append(cell.get_text().strip())
                if row_data:
                    table_data.append(row_data)
            if table_data:
                tables.append(table_data)
        return tables

    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract images from webpage"""
        images = []
        for img in soup.find_all('img', src=True):
            src = img['src']
            # Convert relative URLs to absolute
            if not src.startswith(('http://', 'https://')):
                src = f"{base_url.rstrip('/')}/{src.lstrip('/')}"

            images.append({
                "src": src,
                "alt": img.get('alt', ''),
                "title": img.get('title', '')
            })
        return images

# Web search capabilities
class WebSearchTool:
    """Simple web search tool using search engines"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })

    async def search(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Perform web search and return results"""
        try:
            # Use DuckDuckGo for search (no API key required)
            search_url = f"https://duckduckgo.com/html/?q={query}"

            response = self.session.get(search_url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            results = []
            for result in soup.find_all('div', class_='result')[:max_results]:
                title_elem = result.find('a', class_='result__a')
                snippet_elem = result.find('a', class_='result__snippet')

                if title_elem:
                    title = title_elem.get_text().strip()
                    url = title_elem.get('href', '')

                    # Extract actual URL from DuckDuckGo redirect
                    if url.startswith('/'):
                        url = f"https://duckduckgo.com{url}"

                    snippet = snippet_elem.get_text().strip() if snippet_elem else ""

                    results.append({
                        "title": title,
                        "url": url,
                        "snippet": snippet
                    })

            return {
                "query": query,
                "results_count": len(results),
                "results": results,
                "success": True
            }

        except Exception as e:
            logger.error(f"Search error for query '{query}': {e}")
            return {
                "query": query,
                "success": False,
                "error": str(e),
                "results": []
            }

# Global instances
document_extractor = DocumentExtractor()
web_search_tool = WebSearchTool()