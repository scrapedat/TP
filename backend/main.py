#!/usr/bin/env python3
"""
ToolLlama Backend API
=====================

FastAPI backend for Ollama tool integration with advanced scraping capabilities.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional
import uvicorn

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import aiofiles

# Add project paths for imports
sys.path.append('/home/scrapedat/projects/auction_intelligence')
sys.path.append('/home/scrapedat/toollama')

# Import existing scraping tools
try:
    from scraping.ai_powered_scrapers import AIScrapingManager, AuctionListing
    AI_SCRAPERS_AVAILABLE = True
except ImportError:
    print("⚠️  AI scrapers not available")
    AI_SCRAPERS_AVAILABLE = False

try:
    from scraping.working_auction_scraper import WorkingAuctionScraper
    WORKING_SCRAPER_AVAILABLE = True
except ImportError:
    print("⚠️  Working scraper not available")
    WORKING_SCRAPER_AVAILABLE = False

# Import our custom tools
try:
    from document_extractor import DocumentExtractor, WebSearchTool
    from enhanced_data_manager import EnhancedDataManager
    from context_manager import OllamaContextManager
    from browser_manager import OllamaBrowserManager
    from model_manager import OllamaModelManager
    from website_preset_manager import WebsitePresetManager
    CUSTOM_TOOLS_AVAILABLE = True
except ImportError:
    print("⚠️  Custom tools not available")
    CUSTOM_TOOLS_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ToolLlama Backend API",
    description="Advanced Ollama tool integration with web scraping and data management",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
scraper_manager = None
auction_scraper = None
data_manager = None
document_extractor = None
web_search_tool = None
context_manager = None
browser_manager = None
model_manager = None
preset_manager = None

# Pydantic models for API
class ScrapeWebpageRequest(BaseModel):
    url: str = Field(..., description="URL to scrape")
    extraction_prompt: Optional[str] = Field(None, description="What data to extract")
    method: str = Field("auto", description="Scraping method to use")

class ScrapeAuctionRequest(BaseModel):
    site: str = Field(..., description="Auction site (govdeals, publicsurplus, etc.)")
    category: Optional[str] = Field(None, description="Equipment category filter")
    max_items: int = Field(50, description="Maximum items to retrieve")

class DataListCreateRequest(BaseModel):
    name: str = Field(..., description="List name")
    description: Optional[str] = Field(None, description="List description")
    list_type: str = Field(..., description="Type of data (urls, emails, phones, research)")

class DataListItemRequest(BaseModel):
    list_id: str = Field(..., description="List ID")
    data: Dict[str, Any] = Field(..., description="Data to add")
    source: Optional[str] = Field(None, description="Source of the data")

class EmailSendRequest(BaseModel):
    to: str = Field(..., description="Recipient email")
    subject: str = Field(..., description="Email subject")
    body: str = Field(..., description="Email body")
    account_id: Optional[str] = Field(None, description="Email account to use")

# Use enhanced data manager if available
if CUSTOM_TOOLS_AVAILABLE:
    DataManager = EnhancedDataManager
else:
    # Fallback to basic implementation
    class DataManager:
        """Basic data manager fallback"""

        def __init__(self, storage_path: str = "/home/scrapedat/toollama/data"):
            self.storage_path = Path(storage_path)
            self.storage_path.mkdir(parents=True, exist_ok=True)
            self.lists_file = self.storage_path / "lists.json"
            self.lists = self._load_lists()

        def _load_lists(self) -> Dict[str, Any]:
            if self.lists_file.exists():
                try:
                    with open(self.lists_file, 'r') as f:
                        return json.load(f)
                except Exception as e:
                    logger.error(f"Error loading lists: {e}")
            return {}

        def _save_lists(self):
            try:
                with open(self.lists_file, 'w') as f:
                    json.dump(self.lists, f, indent=2)
            except Exception as e:
                logger.error(f"Error saving lists: {e}")

        def create_list(self, name: str, description: str = "", list_type: str = "general", **kwargs) -> str:
            list_id = f"list_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
            self.lists[list_id] = {
                "id": list_id,
                "name": name,
                "description": description,
                "type": list_type,
                "items": [],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            self._save_lists()
            return list_id

        def add_item(self, list_id: str, data: Dict[str, Any], source: str = "", **kwargs) -> Dict[str, Any]:
            if list_id not in self.lists:
                return {"success": False, "error": f"List {list_id} not found"}

            item = {
                "id": f"item_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')}",
                "data": data,
                "source": source,
                "added_at": datetime.now(timezone.utc).isoformat(),
                "size_bytes": len(json.dumps(data).encode('utf-8'))
            }

            self.lists[list_id]["items"].append(item)
            self.lists[list_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
            self._save_lists()
            return {"success": True, "item_id": item["id"]}

        def get_list(self, list_id: str) -> Optional[Dict[str, Any]]:
            return self.lists.get(list_id)

        def get_all_lists(self) -> List[Dict[str, Any]]:
            return list(self.lists.values())

        def export_list(self, list_id: str, format: str = "json", **kwargs) -> Optional[str]:
            if list_id not in self.lists:
                return None

            list_data = self.lists[list_id]

            if format == "json":
                return json.dumps(list_data, indent=2)
            elif format == "csv" and list_data["items"]:
                import csv
                import io
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=list_data["items"][0]["data"].keys())
                writer.writeheader()
                for item in list_data["items"]:
                    writer.writerow(item["data"])
                return output.getvalue()

            return None

        list_data = self.lists[list_id]

        if format == "json":
            return json.dumps(list_data, indent=2)
        elif format == "csv":
            # Simple CSV export for basic data
            if list_data["items"]:
                import csv
                import io
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=list_data["items"][0]["data"].keys())
                writer.writeheader()
                for item in list_data["items"]:
                    writer.writerow(item["data"])
                return output.getvalue()

        return None

# Tool wrapper class
class OllamaToolWrapper:
    """Main tool execution wrapper for Ollama integration"""

    def __init__(self):
        global scraper_manager, auction_scraper, data_manager

        # Initialize data manager
        data_manager = DataManager()

        # Initialize scrapers if available
        if AI_SCRAPERS_AVAILABLE:
            scraper_manager = AIScrapingManager()
            logger.info("✅ AI scrapers initialized")

        if WORKING_SCRAPER_AVAILABLE:
            auction_scraper = WorkingAuctionScraper()
            logger.info("✅ Auction scraper initialized")

    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with given parameters"""

        tool_handlers = {
            'scrape_webpage': self._handle_scrape_webpage,
            'scrape_auction_data': self._handle_scrape_auction_data,
            'extract_document_data': self._handle_extract_document,
            'create_data_list': self._handle_create_data_list,
            'add_to_list': self._handle_add_to_list,
            'get_list': self._handle_get_list,
            'export_list': self._handle_export_list,
            'send_email': self._handle_send_email,
            'web_search': self._handle_web_search,
            'extract_text_from_url': self._handle_extract_text_from_url,
            'extract_tables_from_url': self._handle_extract_tables_from_url,
            'extract_links_from_url': self._handle_extract_links_from_url,
            'extract_images_from_url': self._handle_extract_images_from_url,
            'search_lists': self._handle_search_lists,
            'get_list_stats': self._handle_get_list_stats,
            'get_analytics': self._handle_get_analytics
        }

        handler = tool_handlers.get(tool_name)
        if not handler:
            return {"error": f"Unknown tool: {tool_name}", "success": False}

        try:
            result = await handler(parameters)
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"Tool execution error ({tool_name}): {e}")
            return {"error": str(e), "success": False}

    async def _handle_scrape_webpage(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle webpage scraping"""
        if not scraper_manager:
            raise HTTPException(status_code=503, detail="Scraping tools not available")

        url = params.get("url")
        extraction_prompt = params.get("extraction_prompt")
        method = params.get("method", "auto")

        logger.info(f"Scraping webpage: {url} with method: {method}")

        try:
            # Use existing scraper infrastructure
            listings = await scraper_manager.scrape_auction_site(
                url=url,
                site_name="generic_site",
                preferred_method=method
            )

            return {
                "url": url,
                "method_used": method,
                "listings_found": len(listings) if listings else 0,
                "data": [listing.__dict__ if hasattr(listing, '__dict__') else listing for listing in listings] if listings else []
            }
        except Exception as e:
            logger.error(f"Scraping error: {e}")
            raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")

    async def _handle_scrape_auction_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle auction data scraping"""
        if not auction_scraper:
            raise HTTPException(status_code=503, detail="Auction scraper not available")

        site = params.get("site", "govdeals")
        category = params.get("category")
        max_items = params.get("max_items", 50)

        logger.info(f"Scraping auction data from {site}")

        try:
            # Map site names to URLs
            site_urls = {
                "govdeals": "https://www.govdeals.com",
                "publicsurplus": "https://www.publicsurplus.com",
                "gsa": "https://www.gsaauctions.gov"
            }

            url = site_urls.get(site, f"https://www.{site}.com")
            result = await auction_scraper.scrape_specific_site(site, url)

            return {
                "site": site,
                "url": url,
                "success": result.success,
                "listings_count": result.listings_count,
                "method_used": result.method_used,
                "error_message": result.error_message
            }
        except Exception as e:
            logger.error(f"Auction scraping error: {e}")
            raise HTTPException(status_code=500, detail=f"Auction scraping failed: {str(e)}")

    async def _handle_extract_document(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle document data extraction"""
        if not CUSTOM_TOOLS_AVAILABLE:
            raise HTTPException(status_code=503, detail="Document extraction tools not available")

        url = params.get("url")
        extraction_type = params.get("extraction_type", "auto")

        if not url:
            raise HTTPException(status_code=400, detail="URL is required")

        global document_extractor
        if not document_extractor:
            document_extractor = DocumentExtractor()

        result = await document_extractor.extract_from_url(url, extraction_type)
        return result

    async def _handle_create_data_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle data list creation"""
        name = params.get("name")
        description = params.get("description", "")
        list_type = params.get("list_type", "general")

        if not data_manager:
            raise HTTPException(status_code=503, detail="Data manager not available")

        list_id = data_manager.create_list(name, description, list_type)

        return {
            "list_id": list_id,
            "name": name,
            "description": description,
            "type": list_type,
            "created": True
        }

    async def _handle_add_to_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle adding data to a list"""
        list_id = params.get("list_id")
        data = params.get("data", {})
        source = params.get("source", "")

        if not data_manager:
            raise HTTPException(status_code=503, detail="Data manager not available")

        success = data_manager.add_item(list_id, data, source)

        if not success:
            raise HTTPException(status_code=404, detail=f"List {list_id} not found")

        return {
            "list_id": list_id,
            "added": True,
            "item_count": len(data_manager.get_list(list_id)["items"])
        }

    async def _handle_get_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle retrieving a data list"""
        list_id = params.get("list_id")

        if not data_manager:
            raise HTTPException(status_code=503, detail="Data manager not available")

        list_data = data_manager.get_list(list_id)

        if not list_data:
            raise HTTPException(status_code=404, detail=f"List {list_id} not found")

        return list_data

    async def _handle_export_list(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle exporting a data list"""
        list_id = params.get("list_id")
        format = params.get("format", "json")
        filters = params.get("filters")

        if not data_manager:
            raise HTTPException(status_code=503, detail="Data manager not available")

        # Use enhanced export if available
        if hasattr(data_manager, 'export_list_advanced'):
            exported_data = data_manager.export_list_advanced(list_id, format, filters)
        else:
            exported_data = data_manager.export_list(list_id, format)

        if not exported_data:
            raise HTTPException(status_code=404, detail=f"List {list_id} not found or export failed")

        return {
            "list_id": list_id,
            "format": format,
            "data": exported_data,
            "filters_applied": filters is not None
        }

    async def _handle_search_lists(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle searching across data lists"""
        query = params.get("query", "")
        list_type = params.get("list_type")
        tags = params.get("tags")

        if not data_manager or not hasattr(data_manager, 'search_lists'):
            raise HTTPException(status_code=503, detail="Enhanced search not available")

        results = data_manager.search_lists(query, list_type, tags)

        return {
            "query": query,
            "results_count": len(results),
            "results": results
        }

    async def _handle_get_list_stats(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle getting list statistics"""
        list_id = params.get("list_id")

        if not data_manager or not hasattr(data_manager, 'get_list_stats'):
            raise HTTPException(status_code=503, detail="Enhanced stats not available")

        stats = data_manager.get_list_stats(list_id)
        return stats

    async def _handle_get_analytics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle getting system analytics"""
        if not data_manager or not hasattr(data_manager, 'get_analytics'):
            raise HTTPException(status_code=503, detail="Enhanced analytics not available")

        analytics = data_manager.get_analytics()
        return analytics

    async def _handle_send_email(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle email sending"""
        # Placeholder for email functionality
        return {"message": "Email sending not yet implemented", "to": params.get("to")}

    async def _handle_web_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle web search"""
        if not CUSTOM_TOOLS_AVAILABLE:
            raise HTTPException(status_code=503, detail="Web search tools not available")

        query = params.get("query")
        max_results = params.get("max_results", 10)

        if not query:
            raise HTTPException(status_code=400, detail="Query is required")

        global web_search_tool
        if not web_search_tool:
            web_search_tool = WebSearchTool()

        result = await web_search_tool.search(query, max_results)
        return result

    async def _handle_extract_text_from_url(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract text content from URL"""
        if not CUSTOM_TOOLS_AVAILABLE:
            raise HTTPException(status_code=503, detail="Document extraction tools not available")

        url = params.get("url")
        if not url:
            raise HTTPException(status_code=400, detail="URL is required")

        global document_extractor
        if not document_extractor:
            document_extractor = DocumentExtractor()

        result = await document_extractor.extract_from_url(url, "text")
        return result

    async def _handle_extract_tables_from_url(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract tables from URL"""
        if not CUSTOM_TOOLS_AVAILABLE:
            raise HTTPException(status_code=503, detail="Document extraction tools not available")

        url = params.get("url")
        if not url:
            raise HTTPException(status_code=400, detail="URL is required")

        global document_extractor
        if not document_extractor:
            document_extractor = DocumentExtractor()

        result = await document_extractor.extract_from_url(url, "tables")
        return result

    async def _handle_extract_links_from_url(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract links from URL"""
        if not CUSTOM_TOOLS_AVAILABLE:
            raise HTTPException(status_code=503, detail="Document extraction tools not available")

        url = params.get("url")
        if not url:
            raise HTTPException(status_code=400, detail="URL is required")

        global document_extractor
        if not document_extractor:
            document_extractor = DocumentExtractor()

        result = await document_extractor.extract_from_url(url, "links")
        return result

    async def _handle_extract_images_from_url(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Extract images from URL"""
        if not CUSTOM_TOOLS_AVAILABLE:
            raise HTTPException(status_code=503, detail="Document extraction tools not available")

        url = params.get("url")
        if not url:
            raise HTTPException(status_code=400, detail="URL is required")

        global document_extractor
        if not document_extractor:
            document_extractor = DocumentExtractor()

        result = await document_extractor.extract_from_url(url, "images")
        return result

# Global tool wrapper instance
tool_wrapper = OllamaToolWrapper()

# API Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "ToolLlama Backend API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": {
            "ai_scrapers": AI_SCRAPERS_AVAILABLE,
            "auction_scraper": WORKING_SCRAPER_AVAILABLE,
            "data_manager": data_manager is not None,
            "document_extractor": CUSTOM_TOOLS_AVAILABLE,
            "web_search": CUSTOM_TOOLS_AVAILABLE,
            "context_manager": context_manager is not None,
            "browser_manager": browser_manager is not None,
            "model_manager": model_manager is not None
        }
    }

@app.post("/api/tools/execute")
async def execute_tool(request: Dict[str, Any]):
    """Execute a tool with given parameters"""
    tool_name = request.get("tool_name")
    parameters = request.get("parameters", {})

    if not tool_name:
        raise HTTPException(status_code=400, detail="tool_name is required")

    result = await tool_wrapper.execute_tool(tool_name, parameters)
    return result

@app.post("/api/tools/scrape_webpage")
async def scrape_webpage(request: ScrapeWebpageRequest):
    """Scrape a webpage"""
    result = await tool_wrapper.execute_tool("scrape_webpage", request.dict())
    return result

@app.post("/api/tools/scrape_auction_data")
async def scrape_auction_data(request: ScrapeAuctionRequest):
    """Scrape auction data"""
    result = await tool_wrapper.execute_tool("scrape_auction_data", request.dict())
    return result

@app.post("/api/data/lists")
async def create_data_list(request: DataListCreateRequest):
    """Create a new data list"""
    result = await tool_wrapper.execute_tool("create_data_list", request.dict())
    return result

@app.post("/api/data/lists/items")
async def add_to_list(request: DataListItemRequest):
    """Add item to a data list"""
    result = await tool_wrapper.execute_tool("add_to_list", request.dict())
    return result

@app.get("/api/data/lists")
async def get_all_lists():
    """Get all data lists"""
    if not data_manager:
        raise HTTPException(status_code=503, detail="Data manager not available")

    lists = data_manager.get_all_lists()
    return {"lists": lists}

@app.get("/api/data/lists/{list_id}")
async def get_list(list_id: str):
    """Get a specific data list"""
    result = await tool_wrapper.execute_tool("get_list", {"list_id": list_id})
    return result

@app.post("/api/data/lists/{list_id}/export")
async def export_list(list_id: str, format: str = "json", filters: Dict[str, Any] = None):
    """Export a data list with optional filters"""
    params = {"list_id": list_id, "format": format}
    if filters:
        params["filters"] = filters
    result = await tool_wrapper.execute_tool("export_list", params)
    return result

# Enhanced data management endpoints
@app.get("/api/data/search")
async def search_lists(query: str, list_type: str = None, tags: str = None):
    """Search across all data lists"""
    tag_list = tags.split(",") if tags else None
    if hasattr(data_manager, 'search_lists'):
        results = data_manager.search_lists(query, list_type, tag_list)
        return {"results": results}
    else:
        return {"error": "Enhanced search not available"}

@app.get("/api/data/lists/{list_id}/stats")
async def get_list_stats(list_id: str):
    """Get detailed statistics for a list"""
    if hasattr(data_manager, 'get_list_stats'):
        stats = data_manager.get_list_stats(list_id)
        return stats
    else:
        return {"error": "Enhanced stats not available"}

@app.get("/api/data/analytics")
async def get_analytics():
    """Get system-wide analytics"""
    if hasattr(data_manager, 'get_analytics'):
        analytics = data_manager.get_analytics()
        return analytics
    else:
        return {"error": "Enhanced analytics not available"}

@app.post("/api/data/cleanup")
async def cleanup_old_data(retention_days: int = 30):
    """Clean up old data based on retention policy"""
    if hasattr(data_manager, 'cleanup_old_data'):
        result = data_manager.cleanup_old_data(retention_days)
        return result
    else:
        return {"error": "Cleanup not available"}

@app.post("/api/communication/send_email")
async def send_email(request: EmailSendRequest):
    """Send an email"""
    result = await tool_wrapper.execute_tool("send_email", request.dict())
    return result

# Document extraction endpoints
@app.post("/api/tools/extract_text")
async def extract_text_from_url(url: str):
    """Extract text content from a URL"""
    result = await tool_wrapper.execute_tool("extract_text_from_url", {"url": url})
    return result

@app.post("/api/tools/extract_tables")
async def extract_tables_from_url(url: str):
    """Extract tables from a URL"""
    result = await tool_wrapper.execute_tool("extract_tables_from_url", {"url": url})
    return result

@app.post("/api/tools/extract_links")
async def extract_links_from_url(url: str):
    """Extract links from a URL"""
    result = await tool_wrapper.execute_tool("extract_links_from_url", {"url": url})
    return result

@app.post("/api/tools/extract_images")
async def extract_images_from_url(url: str):
    """Extract images from a URL"""
    result = await tool_wrapper.execute_tool("extract_images_from_url", {"url": url})
    return result

# Web search endpoint
@app.post("/api/tools/web_search")
async def web_search(query: str, max_results: int = 10):
    """Perform web search"""
    result = await tool_wrapper.execute_tool("web_search", {"query": query, "max_results": max_results})
    return result

# Context Management Endpoints
@app.post("/api/context/save_conversation")
async def save_conversation(session_id: str, role: str, content: str,
                           tool_calls: Optional[List[Dict]] = None,
                           metadata: Optional[Dict] = None,
                           user_id: str = "default"):
    """Save a conversation message"""
    if not context_manager:
        raise HTTPException(status_code=503, detail="Context manager not available")

    try:
        conversation_id = context_manager.save_conversation(
            session_id, role, content, tool_calls, metadata, user_id
        )
        return {"success": True, "conversation_id": conversation_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save conversation: {str(e)}")

@app.get("/api/context/history/{session_id}")
async def get_conversation_history(session_id: str, limit: int = 50, user_id: str = "default"):
    """Get conversation history for a session"""
    if not context_manager:
        raise HTTPException(status_code=503, detail="Context manager not available")

    try:
        history = context_manager.get_conversation_history(session_id, limit, user_id)
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")

@app.post("/api/context/build_prompt")
async def build_context_prompt(session_id: str, current_query: str,
                              max_tokens: int = 3000, user_id: str = "default"):
    """Build intelligent context prompt for Ollama"""
    if not context_manager:
        raise HTTPException(status_code=503, detail="Context manager not available")

    try:
        context_prompt = context_manager.build_context_prompt(
            session_id, current_query, max_tokens, user_id
        )
        return {"context_prompt": context_prompt}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to build context: {str(e)}")

@app.post("/api/context/add_knowledge")
async def add_to_knowledge_base(category: str, title: str, content: str,
                               source: str = "", confidence: float = 1.0,
                               tags: List[str] = None, user_id: str = "default"):
    """Add information to knowledge base"""
    if not context_manager:
        raise HTTPException(status_code=503, detail="Context manager not available")

    try:
        knowledge_id = context_manager.add_to_knowledge_base(
            category, title, content, source, confidence, tags, user_id
        )
        return {"success": True, "knowledge_id": knowledge_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add knowledge: {str(e)}")

@app.get("/api/context/search_knowledge")
async def search_knowledge_base(query: str, limit: int = 5, user_id: str = "default"):
    """Search the knowledge base"""
    if not context_manager:
        raise HTTPException(status_code=503, detail="Context manager not available")

    try:
        results = context_manager.search_knowledge_base(query, limit, user_id)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search knowledge: {str(e)}")

@app.post("/api/context/learn")
async def learn_from_interaction(user_query: str, ollama_response: str,
                                tool_used: str = None, success: bool = True,
                                user_id: str = "default"):
    """Learn from user interaction"""
    if not context_manager:
        raise HTTPException(status_code=503, detail="Context manager not available")

    try:
        context_manager.learn_from_interaction(
            user_query, ollama_response, tool_used, success, user_id
        )
        return {"success": True, "learned": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to learn: {str(e)}")

@app.get("/api/context/stats")
async def get_context_stats(user_id: str = "default"):
    """Get context system statistics"""
    if not context_manager:
        raise HTTPException(status_code=503, detail="Context manager not available")

    try:
        stats = context_manager.get_system_stats(user_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.post("/api/context/cleanup")
async def cleanup_context_data(days_to_keep: int = 90, user_id: str = "default"):
    """Clean up old context data"""
    if not context_manager:
        raise HTTPException(status_code=503, detail="Context manager not available")

    try:
        result = context_manager.cleanup_old_data(days_to_keep, user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cleanup: {str(e)}")

# Browser Management Endpoints
@app.post("/api/browser/create_session")
async def create_browser_session(user_id: str = "default"):
    """Create a new browser session"""
    if not browser_manager:
        raise HTTPException(status_code=503, detail="Browser manager not available")

    try:
        session_id = await browser_manager.create_session(user_id)
        return {"success": True, "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@app.get("/api/browser/sessions")
async def list_browser_sessions(user_id: str = "default"):
    """List browser sessions for a user"""
    if not browser_manager:
        raise HTTPException(status_code=503, detail="Browser manager not available")

    try:
        sessions = await browser_manager.list_sessions(user_id)
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")

@app.post("/api/browser/{session_id}/navigate")
async def navigate_browser_session(session_id: str, url: str):
    """Navigate a browser session to a URL"""
    if not browser_manager:
        raise HTTPException(status_code=503, detail="Browser manager not available")

    try:
        result = await browser_manager.navigate_session(session_id, url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to navigate: {str(e)}")

@app.post("/api/browser/{session_id}/action")
async def execute_browser_action(session_id: str, action: str, parameters: Dict[str, Any] = None):
    """Execute an action in a browser session"""
    if not browser_manager:
        raise HTTPException(status_code=503, detail="Browser manager not available")

    try:
        result = await browser_manager.execute_action(session_id, action, parameters or {})
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute action: {str(e)}")

@app.get("/api/browser/{session_id}/screenshot")
async def get_browser_screenshot(session_id: str):
    """Get a screenshot of a browser session"""
    if not browser_manager:
        raise HTTPException(status_code=503, detail="Browser manager not available")

    try:
        screenshot = await browser_manager.take_screenshot(session_id)
        if screenshot:
            return {"success": True, "screenshot": screenshot}
        else:
            return {"success": False, "error": "Screenshot failed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get screenshot: {str(e)}")

@app.post("/api/browser/{session_id}/enable_ai")
async def enable_ai_control(session_id: str):
    """Enable AI control for a browser session"""
    if not browser_manager:
        raise HTTPException(status_code=503, detail="Browser manager not available")

    try:
        success = browser_manager.enable_ai_control(session_id)
        return {"success": success, "ai_controlled": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to enable AI control: {str(e)}")

@app.post("/api/browser/{session_id}/disable_ai")
async def disable_ai_control(session_id: str):
    """Disable AI control for a browser session"""
    if not browser_manager:
        raise HTTPException(status_code=503, detail="Browser manager not available")

    try:
        success = browser_manager.disable_ai_control(session_id)
        return {"success": success, "ai_controlled": False}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to disable AI control: {str(e)}")

@app.get("/api/browser/{session_id}/info")
async def get_browser_session_info(session_id: str):
    """Get information about a browser session"""
    if not browser_manager:
        raise HTTPException(status_code=503, detail="Browser manager not available")

    try:
        info = browser_manager.get_session_info(session_id)
        if info:
            return info
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session info: {str(e)}")

@app.delete("/api/browser/{session_id}")
async def close_browser_session(session_id: str):
    """Close a browser session"""
    if not browser_manager:
        raise HTTPException(status_code=503, detail="Browser manager not available")

    try:
        success = await browser_manager.close_session(session_id)
        return {"success": success, "closed": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to close session: {str(e)}")

@app.post("/api/browser/cleanup")
async def cleanup_browser_sessions(max_age_minutes: int = 30):
    """Clean up inactive browser sessions"""
    if not browser_manager:
        raise HTTPException(status_code=503, detail="Browser manager not available")

    try:
        closed_count = await browser_manager.cleanup_inactive_sessions(max_age_minutes)
        return {"success": True, "sessions_closed": closed_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cleanup: {str(e)}")

# Website Preset Management Endpoints
@app.get("/api/presets")
async def get_user_presets(user_id: str = "default"):
    """Get all website presets for a user"""
    if not preset_manager:
        raise HTTPException(status_code=503, detail="Preset manager not available")

    try:
        presets = preset_manager.get_user_presets(user_id)
        return {"presets": presets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get presets: {str(e)}")

@app.post("/api/presets")
async def create_preset(request: Dict[str, Any], user_id: str = "default"):
    """Create a new website preset"""
    if not preset_manager:
        raise HTTPException(status_code=503, detail="Preset manager not available")

    try:
        name = request.get("name")
        url = request.get("url")
        category = request.get("category", "custom")
        icon = request.get("icon", "🌐")
        description = request.get("description", "")

        if not name or not url:
            raise HTTPException(status_code=400, detail="Name and URL are required")

        preset = preset_manager.create_preset(name, url, category, icon, description, user_id)
        return {"success": True, "preset": preset.to_dict()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create preset: {str(e)}")

@app.put("/api/presets/{preset_id}")
async def update_preset(preset_id: str, request: Dict[str, Any], user_id: str = "default"):
    """Update an existing website preset"""
    if not preset_manager:
        raise HTTPException(status_code=503, detail="Preset manager not available")

    try:
        updates = {}
        for field in ["name", "url", "category", "icon", "description"]:
            if field in request:
                updates[field] = request[field]

        preset = preset_manager.update_preset(preset_id, updates, user_id)
        if not preset:
            raise HTTPException(status_code=404, detail="Preset not found or access denied")

        return {"success": True, "preset": preset.to_dict()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update preset: {str(e)}")

@app.delete("/api/presets/{preset_id}")
async def delete_preset(preset_id: str, user_id: str = "default"):
    """Delete a website preset"""
    if not preset_manager:
        raise HTTPException(status_code=503, detail="Preset manager not available")

    try:
        success = preset_manager.delete_preset(preset_id, user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Preset not found or access denied")

        return {"success": True, "deleted": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete preset: {str(e)}")

@app.get("/api/presets/categories")
async def get_preset_categories(user_id: str = "default"):
    """Get all categories for a user's presets"""
    if not preset_manager:
        raise HTTPException(status_code=503, detail="Preset manager not available")

    try:
        categories = preset_manager.get_categories(user_id)
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get categories: {str(e)}")

@app.get("/api/presets/search")
async def search_presets(query: str, user_id: str = "default"):
    """Search presets by name or URL"""
    if not preset_manager:
        raise HTTPException(status_code=503, detail="Preset manager not available")

    try:
        results = preset_manager.search_presets(query, user_id)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search presets: {str(e)}")

@app.post("/api/presets/{preset_id}/use")
async def mark_preset_used(preset_id: str, user_id: str = "default"):
    """Mark a preset as recently used"""
    if not preset_manager:
        raise HTTPException(status_code=503, detail="Preset manager not available")

    try:
        preset_manager.mark_used(preset_id, user_id)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to mark preset as used: {str(e)}")

# Model Management Endpoints
@app.get("/api/models/status")
async def get_model_status():
    """Get comprehensive model status"""
    if not model_manager:
        raise HTTPException(status_code=503, detail="Model manager not available")

    try:
        status = await model_manager.get_model_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get model status: {str(e)}")

@app.post("/api/models/refresh")
async def refresh_models():
    """Refresh the list of available models"""
    if not model_manager:
        raise HTTPException(status_code=503, detail="Model manager not available")

    try:
        models = await model_manager.refresh_models()
        return {"success": True, "models_count": len(models), "models": list(models.keys())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refresh models: {str(e)}")

@app.post("/api/models/load/{model_name}")
async def load_model(model_name: str):
    """Load a model into memory"""
    if not model_manager:
        raise HTTPException(status_code=503, detail="Model manager not available")

    try:
        success = await model_manager.load_model(model_name)
        return {"success": success, "model": model_name, "loaded": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load model: {str(e)}")

@app.post("/api/models/select")
async def select_model_for_task(task_type: str, context: str = ""):
    """Select the best model for a task"""
    if not model_manager:
        raise HTTPException(status_code=503, detail="Model manager not available")

    try:
        model_name = model_manager.select_model_for_task(task_type, context)
        return {"selected_model": model_name, "task_type": task_type}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to select model: {str(e)}")

@app.post("/api/models/generate")
async def generate_with_model(request: Dict[str, Any]):
    """Generate response using specified or auto-selected model"""
    if not model_manager:
        raise HTTPException(status_code=503, detail="Model manager not available")

    try:
        prompt = request.get("prompt", "")
        model_name = request.get("model")
        task_type = request.get("task_type", "general_chat")
        context = request.get("context", "")

        # Auto-select model if not specified
        if not model_name:
            model_name = model_manager.select_model_for_task(task_type, context)

        # Generate response
        result = await model_manager.generate_response(
            model_name=model_name,
            prompt=prompt,
            context=context,
            **{k: v for k, v in request.items() if k not in ["prompt", "model", "task_type", "context"]}
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate response: {str(e)}")

@app.get("/api/models/tasks")
async def get_available_tasks():
    """Get available task types for model routing"""
    if not model_manager:
        raise HTTPException(status_code=503, detail="Model manager not available")

    try:
        tasks = {}
        for name, task in model_manager.task_definitions.items():
            tasks[name] = {
                "description": task.description,
                "required_capabilities": task.required_capabilities,
                "preferred_models": task.preferred_models,
                "fallback_models": task.fallback_models
            }
        return {"tasks": tasks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get tasks: {str(e)}")

@app.get("/api/models/capabilities")
async def get_model_capabilities():
    """Get capabilities of all available models"""
    if not model_manager:
        raise HTTPException(status_code=503, detail="Model manager not available")

    try:
        capabilities = {}
        for model_name, caps in model_manager.model_capabilities.items():
            capabilities[model_name] = caps
        return {"capabilities": capabilities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get capabilities: {str(e)}")

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("🚀 ToolLlama Backend starting up...")
    logger.info(f"AI Scrapers Available: {AI_SCRAPERS_AVAILABLE}")
    logger.info(f"Auction Scraper Available: {WORKING_SCRAPER_AVAILABLE}")
    logger.info(f"Custom Tools Available: {CUSTOM_TOOLS_AVAILABLE}")

    # Initialize custom tools
    if CUSTOM_TOOLS_AVAILABLE:
        global document_extractor, web_search_tool, context_manager, browser_manager, model_manager, preset_manager
        document_extractor = DocumentExtractor()
        web_search_tool = WebSearchTool()
        context_manager = OllamaContextManager()
        browser_manager = OllamaBrowserManager()
        model_manager = OllamaModelManager()
        preset_manager = WebsitePresetManager()

        # Refresh available models
        await model_manager.refresh_models()
        logger.info("✅ Custom tools, context manager, browser manager, model manager, and preset manager initialized")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up services on shutdown"""
    logger.info("🛑 ToolLlama Backend shutting down...")

    # Close scrapers if they exist
    if scraper_manager and hasattr(scraper_manager, 'close_all'):
        try:
            await scraper_manager.close_all()
        except Exception as e:
            logger.error(f"Error closing scraper manager: {e}")

    if auction_scraper and hasattr(auction_scraper, 'close'):
        try:
            await auction_scraper.close()
        except Exception as e:
            logger.error(f"Error closing auction scraper: {e}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )