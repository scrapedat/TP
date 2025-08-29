#!/usr/bin/env python3
"""
Website Preset Manager for ToolLlama
====================================

Manages user-defined website presets for quick browser launching.
Supports categories, custom icons, and user authentication.
"""

import json
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import uuid

logger = logging.getLogger(__name__)

class WebsitePreset:
    """Represents a website preset"""

    def __init__(self, name: str, url: str, category: str = "custom",
                 icon: str = "🌐", description: str = "", user_id: str = "default",
                 preset_id: Optional[str] = None, created_at: Optional[str] = None):
        self.preset_id = preset_id or f"preset_{uuid.uuid4().hex[:8]}"
        self.name = name
        self.url = url
        self.category = category
        self.icon = icon
        self.description = description
        self.user_id = user_id
        self.created_at = created_at or datetime.now().isoformat()
        self.last_used: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "preset_id": self.preset_id,
            "name": self.name,
            "url": self.url,
            "category": self.category,
            "icon": self.icon,
            "description": self.description,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "last_used": self.last_used
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WebsitePreset':
        """Create from dictionary"""
        preset = cls(
            name=data["name"],
            url=data["url"],
            category=data.get("category", "custom"),
            icon=data.get("icon", "🌐"),
            description=data.get("description", ""),
            user_id=data.get("user_id", "default"),
            preset_id=data.get("preset_id"),
            created_at=data.get("created_at")
        )
        preset.last_used = data.get("last_used")
        return preset

class WebsitePresetManager:
    """Manages website presets for users"""

    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.presets_file = self.data_dir / "website_presets.json"
        self.presets: Dict[str, WebsitePreset] = {}
        self.load_presets()

        # Default presets for new users
        self.default_presets = [
            {
                "name": "Google",
                "url": "https://google.com",
                "category": "search",
                "icon": "🔍",
                "description": "Search engine"
            },
            {
                "name": "Gmail",
                "url": "https://gmail.com",
                "category": "email",
                "icon": "📧",
                "description": "Email service"
            },
            {
                "name": "GitHub",
                "url": "https://github.com",
                "category": "development",
                "icon": "💻",
                "description": "Code repository"
            },
            {
                "name": "YouTube",
                "url": "https://youtube.com",
                "category": "media",
                "icon": "📺",
                "description": "Video platform"
            }
        ]

    def load_presets(self):
        """Load presets from file"""
        try:
            if self.presets_file.exists():
                with open(self.presets_file, 'r') as f:
                    data = json.load(f)
                    for preset_data in data.get("presets", []):
                        preset = WebsitePreset.from_dict(preset_data)
                        self.presets[preset.preset_id] = preset
                logger.info(f"Loaded {len(self.presets)} website presets")
        except Exception as e:
            logger.error(f"Error loading presets: {e}")
            self.presets = {}

    def save_presets(self):
        """Save presets to file"""
        try:
            data = {
                "presets": [preset.to_dict() for preset in self.presets.values()],
                "last_updated": datetime.now().isoformat()
            }
            with open(self.presets_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved {len(self.presets)} website presets")
        except Exception as e:
            logger.error(f"Error saving presets: {e}")

    def get_user_presets(self, user_id: str = "default") -> List[Dict[str, Any]]:
        """Get all presets for a user"""
        user_presets = [p for p in self.presets.values() if p.user_id == user_id]

        # If user has no presets, initialize with defaults
        if not user_presets:
            user_presets = self.initialize_user_defaults(user_id)

        # Sort by category, then by last used
        return sorted(
            [p.to_dict() for p in user_presets],
            key=lambda x: (x["category"], x.get("last_used") or "", x["name"])
        )

    def initialize_user_defaults(self, user_id: str) -> List[WebsitePreset]:
        """Initialize default presets for a new user"""
        user_presets = []
        for default in self.default_presets:
            preset = WebsitePreset(
                name=default["name"],
                url=default["url"],
                category=default["category"],
                icon=default["icon"],
                description=default["description"],
                user_id=user_id
            )
            self.presets[preset.preset_id] = preset
            user_presets.append(preset)

        self.save_presets()
        return user_presets

    def create_preset(self, name: str, url: str, category: str = "custom",
                     icon: str = "🌐", description: str = "",
                     user_id: str = "default") -> WebsitePreset:
        """Create a new preset"""
        preset = WebsitePreset(name, url, category, icon, description, user_id)
        self.presets[preset.preset_id] = preset
        self.save_presets()
        logger.info(f"Created preset: {name} for user {user_id}")
        return preset

    def update_preset(self, preset_id: str, updates: Dict[str, Any],
                     user_id: str = "default") -> Optional[WebsitePreset]:
        """Update an existing preset"""
        preset = self.presets.get(preset_id)
        if not preset or preset.user_id != user_id:
            return None

        for key, value in updates.items():
            if hasattr(preset, key):
                setattr(preset, key, value)

        self.save_presets()
        logger.info(f"Updated preset: {preset.name}")
        return preset

    def delete_preset(self, preset_id: str, user_id: str = "default") -> bool:
        """Delete a preset"""
        preset = self.presets.get(preset_id)
        if not preset or preset.user_id != user_id:
            return False

        # Don't allow deleting default presets
        if preset.preset_id.startswith("preset_default_"):
            return False

        del self.presets[preset_id]
        self.save_presets()
        logger.info(f"Deleted preset: {preset.name}")
        return True

    def mark_used(self, preset_id: str, user_id: str = "default"):
        """Mark a preset as recently used"""
        preset = self.presets.get(preset_id)
        if preset and preset.user_id == user_id:
            preset.last_used = datetime.now().isoformat()
            self.save_presets()

    def get_categories(self, user_id: str = "default") -> List[str]:
        """Get all categories for a user"""
        user_presets = [p for p in self.presets.values() if p.user_id == user_id]
        categories = set(p.category for p in user_presets)
        return sorted(list(categories))

    def search_presets(self, query: str, user_id: str = "default") -> List[Dict[str, Any]]:
        """Search presets by name or URL"""
        user_presets = [p for p in self.presets.values() if p.user_id == user_id]
        query_lower = query.lower()

        matches = []
        for preset in user_presets:
            if (query_lower in preset.name.lower() or
                query_lower in preset.url.lower() or
                query_lower in preset.category.lower()):
                matches.append(preset.to_dict())

        return matches

    def get_preset_by_id(self, preset_id: str, user_id: str = "default") -> Optional[Dict[str, Any]]:
        """Get a specific preset by ID"""
        preset = self.presets.get(preset_id)
        if preset and preset.user_id == user_id:
            return preset.to_dict()
        return None

# Global preset manager instance
preset_manager = WebsitePresetManager()