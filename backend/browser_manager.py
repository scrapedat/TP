#!/usr/bin/env python3
"""
Embedded Browser Manager for Ollama Control
===========================================

Advanced browser automation system with:
- Embedded browser sessions controllable by Ollama
- Real-time visual feedback in dashboard
- Takeover mechanism for AI control
- Session persistence and management
- Screenshot streaming for dashboard display
"""

import asyncio
import json
import logging
import os
import base64
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from urllib.parse import urlparse
import uuid

# Browser automation imports
try:
    from playwright.async_api import async_playwright, Browser, Page, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️  Playwright not available. Install with: pip install playwright && playwright install")

logger = logging.getLogger(__name__)

class EmbeddedBrowserSession:
    """Manages a single embedded browser session"""

    def __init__(self, session_id: str, user_id: str = "default"):
        self.session_id = session_id
        self.user_id = user_id
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.is_ai_controlled = False
        self.screenshot_callback: Optional[Callable] = None
        self.created_at = datetime.now(timezone.utc)
        self.last_activity = datetime.now(timezone.utc)
        self.status = "initializing"

    async def initialize(self):
        """Initialize the browser session"""
        if not PLAYWRIGHT_AVAILABLE:
            raise Exception("Playwright not available")

        try:
            self.status = "starting"
            playwright = await async_playwright().start()

            # Launch browser with specific configuration for embedding
            self.browser = await playwright.chromium.launch(
                headless=False,  # We want to see the browser for embedding
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu'
                ]
            )

            # Create context with viewport for dashboard embedding
            self.context = await self.browser.new_context(
                viewport={'width': 1200, 'height': 800},
                user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )

            # Create page
            self.page = await self.context.new_page()

            # Set up event listeners
            await self._setup_event_listeners()

            self.status = "ready"
            logger.info(f"Browser session {self.session_id} initialized")

        except Exception as e:
            self.status = "error"
            logger.error(f"Failed to initialize browser session: {e}")
            raise

    async def _setup_event_listeners(self):
        """Set up browser event listeners"""
        if not self.page:
            return

        # Listen for page loads
        self.page.on("load", self._on_page_load)

        # Listen for console messages (useful for debugging)
        self.page.on("console", self._on_console_message)

        # Listen for errors
        self.page.on("pageerror", self._on_page_error)

    async def _on_page_load(self):
        """Handle page load events"""
        self.last_activity = datetime.now(timezone.utc)
        await self.take_screenshot()

    async def _on_console_message(self, msg):
        """Handle console messages"""
        logger.debug(f"Browser console [{self.session_id}]: {msg.text}")

    async def _on_page_error(self, error):
        """Handle page errors"""
        logger.error(f"Browser page error [{self.session_id}]: {error}")

    async def navigate(self, url: str) -> Dict[str, Any]:
        """Navigate to a URL"""
        if not self.page:
            return {"success": False, "error": "Browser not initialized"}

        try:
            self.last_activity = datetime.now(timezone.utc)
            await self.page.goto(url, wait_until="networkidle")

            # Wait a moment for page to settle
            await asyncio.sleep(1)

            # Take screenshot
            screenshot_data = await self.take_screenshot()

            return {
                "success": True,
                "url": url,
                "title": await self.page.title(),
                "screenshot": screenshot_data
            }

        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return {"success": False, "error": str(e)}

    async def take_screenshot(self) -> Optional[str]:
        """Take a screenshot and return base64 data"""
        if not self.page:
            return None

        try:
            screenshot_bytes = await self.page.screenshot(
                type='png',
                full_page=False  # Just viewport for dashboard
            )

            # Convert to base64
            screenshot_b64 = base64.b64encode(screenshot_bytes).decode('utf-8')

            # Call callback if set (for real-time updates)
            if self.screenshot_callback:
                await self.screenshot_callback(screenshot_b64)

            return screenshot_b64

        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return None

    async def execute_action(self, action: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a browser action"""
        if not self.page:
            return {"success": False, "error": "Browser not initialized"}

        if not self.is_ai_controlled:
            return {"success": False, "error": "AI control not enabled"}

        try:
            self.last_activity = datetime.now(timezone.utc)

            if action == "click":
                selector = parameters.get("selector", "")
                await self.page.click(selector)
                result = {"success": True, "action": "click", "selector": selector}

            elif action == "type":
                selector = parameters.get("selector", "")
                text = parameters.get("text", "")
                await self.page.fill(selector, text)
                result = {"success": True, "action": "type", "selector": selector}

            elif action == "scroll":
                direction = parameters.get("direction", "down")
                if direction == "down":
                    await self.page.evaluate("window.scrollBy(0, 500)")
                elif direction == "up":
                    await self.page.evaluate("window.scrollBy(0, -500)")
                result = {"success": True, "action": "scroll", "direction": direction}

            elif action == "wait":
                seconds = parameters.get("seconds", 1)
                await asyncio.sleep(seconds)
                result = {"success": True, "action": "wait", "seconds": seconds}

            elif action == "extract_text":
                selector = parameters.get("selector", "body")
                text = await self.page.inner_text(selector)
                result = {"success": True, "action": "extract_text", "text": text}

            elif action == "get_url":
                current_url = self.page.url
                result = {"success": True, "action": "get_url", "url": current_url}

            else:
                result = {"success": False, "error": f"Unknown action: {action}"}

            # Take screenshot after action
            if result["success"]:
                screenshot = await self.take_screenshot()
                result["screenshot"] = screenshot

            return result

        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_page_info(self) -> Dict[str, Any]:
        """Get current page information"""
        if not self.page:
            return {"error": "Browser not initialized"}

        try:
            return {
                "url": self.page.url,
                "title": await self.page.title(),
                "is_loaded": True,
                "ai_controlled": self.is_ai_controlled,
                "last_activity": self.last_activity.isoformat()
            }
        except Exception as e:
            return {"error": str(e)}

    def enable_ai_control(self):
        """Enable AI control of the browser"""
        self.is_ai_controlled = True
        logger.info(f"AI control enabled for session {self.session_id}")

    def disable_ai_control(self):
        """Disable AI control of the browser"""
        self.is_ai_controlled = False
        logger.info(f"AI control disabled for session {self.session_id}")

    def set_screenshot_callback(self, callback: Callable):
        """Set callback for screenshot updates"""
        self.screenshot_callback = callback

    async def close(self):
        """Close the browser session"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()

            self.status = "closed"
            logger.info(f"Browser session {self.session_id} closed")

        except Exception as e:
            logger.error(f"Error closing browser session: {e}")

class OllamaBrowserManager:
    """Manages multiple embedded browser sessions for Ollama control"""

    def __init__(self):
        self.sessions: Dict[str, EmbeddedBrowserSession] = {}
        self.screenshot_callbacks: Dict[str, Callable] = {}
        self.max_sessions_per_user = 3

    async def create_session(self, user_id: str = "default") -> str:
        """Create a new browser session"""
        # Check session limit
        user_sessions = [s for s in self.sessions.values() if s.user_id == user_id]
        if len(user_sessions) >= self.max_sessions_per_user:
            raise Exception(f"Maximum {self.max_sessions_per_user} sessions per user")

        session_id = f"browser_{uuid.uuid4().hex[:8]}"

        session = EmbeddedBrowserSession(session_id, user_id)
        self.sessions[session_id] = session

        try:
            await session.initialize()
            logger.info(f"Created browser session {session_id} for user {user_id}")
            return session_id
        except Exception as e:
            # Clean up on failure
            if session_id in self.sessions:
                del self.sessions[session_id]
            raise

    async def get_session(self, session_id: str) -> Optional[EmbeddedBrowserSession]:
        """Get a browser session"""
        return self.sessions.get(session_id)

    async def list_sessions(self, user_id: str = "default") -> List[Dict[str, Any]]:
        """List all sessions for a user"""
        user_sessions = [s for s in self.sessions.values() if s.user_id == user_id]

        return [{
            "session_id": s.session_id,
            "status": s.status,
            "ai_controlled": s.is_ai_controlled,
            "created_at": s.created_at.isoformat(),
            "last_activity": s.last_activity.isoformat(),
            "current_url": s.page.url if s.page else None
        } for s in user_sessions]

    async def navigate_session(self, session_id: str, url: str) -> Dict[str, Any]:
        """Navigate a session to a URL"""
        session = await self.get_session(session_id)
        if not session:
            return {"success": False, "error": "Session not found"}

        return await session.navigate(url)

    async def execute_action(self, session_id: str, action: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute an action in a browser session"""
        session = await self.get_session(session_id)
        if not session:
            return {"success": False, "error": "Session not found"}

        return await session.execute_action(action, parameters or {})

    async def take_screenshot(self, session_id: str) -> Optional[str]:
        """Take a screenshot of a session"""
        session = await self.get_session(session_id)
        if not session:
            return None

        return await session.take_screenshot()

    def enable_ai_control(self, session_id: str) -> bool:
        """Enable AI control for a session"""
        session = self.sessions.get(session_id)
        if session:
            session.enable_ai_control()
            return True
        return False

    def disable_ai_control(self, session_id: str) -> bool:
        """Disable AI control for a session"""
        session = self.sessions.get(session_id)
        if session:
            session.disable_ai_control()
            return True
        return False

    def set_screenshot_callback(self, session_id: str, callback: Callable):
        """Set screenshot callback for a session"""
        session = self.sessions.get(session_id)
        if session:
            session.set_screenshot_callback(callback)
            self.screenshot_callbacks[session_id] = callback
            return True
        return False

    async def close_session(self, session_id: str) -> bool:
        """Close a browser session"""
        session = self.sessions.get(session_id)
        if session:
            await session.close()
            del self.sessions[session_id]
            if session_id in self.screenshot_callbacks:
                del self.screenshot_callbacks[session_id]
            logger.info(f"Closed browser session {session_id}")
            return True
        return False

    async def cleanup_inactive_sessions(self, max_age_minutes: int = 30):
        """Clean up inactive browser sessions"""
        now = datetime.now(timezone.utc)
        to_close = []

        for session_id, session in self.sessions.items():
            age_minutes = (now - session.last_activity).total_seconds() / 60
            if age_minutes > max_age_minutes:
                to_close.append(session_id)

        for session_id in to_close:
            await self.close_session(session_id)

        return len(to_close)

    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a session"""
        session = self.sessions.get(session_id)
        if not session:
            return None

        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "status": session.status,
            "ai_controlled": session.is_ai_controlled,
            "created_at": session.created_at.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "current_url": session.page.url if session.page else None,
            "playwright_available": PLAYWRIGHT_AVAILABLE
        }

# Global browser manager instance
browser_manager = OllamaBrowserManager()