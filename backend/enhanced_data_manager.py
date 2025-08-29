#!/usr/bin/env python3
"""
Enhanced Data Management System
===============================

Advanced data list management with search, filtering, analytics, and export capabilities.
"""

import json
import csv
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import pandas as pd
from collections import defaultdict, Counter

class EnhancedDataManager:
    """Enhanced data management with advanced features"""

    def __init__(self, storage_path: str = "/home/scrapedat/toollama/data"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.lists_file = self.storage_path / "lists.json"
        self.analytics_file = self.storage_path / "analytics.json"
        self.lists = self._load_lists()
        self.analytics = self._load_analytics()

    def _load_lists(self) -> Dict[str, Any]:
        """Load data lists from storage"""
        if self.lists_file.exists():
            try:
                with open(self.lists_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading lists: {e}")
        return {}

    def _save_lists(self):
        """Save data lists to storage"""
        try:
            with open(self.lists_file, 'w') as f:
                json.dump(self.lists, f, indent=2)
        except Exception as e:
            print(f"Error saving lists: {e}")

    def _load_analytics(self) -> Dict[str, Any]:
        """Load analytics data"""
        if self.analytics_file.exists():
            try:
                with open(self.analytics_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading analytics: {e}")
        return {"lists_created": 0, "items_added": 0, "searches_performed": 0}

    def _save_analytics(self):
        """Save analytics data"""
        try:
            with open(self.analytics_file, 'w') as f:
                json.dump(self.analytics, f, indent=2)
        except Exception as e:
            print(f"Error saving analytics: {e}")

    def create_list(self, name: str, description: str = "", list_type: str = "general",
                   tags: List[str] = None) -> str:
        """Create a new enhanced data list"""
        list_id = f"list_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"

        self.lists[list_id] = {
            "id": list_id,
            "name": name,
            "description": description,
            "type": list_type,
            "tags": tags or [],
            "items": [],
            "metadata": {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
                "item_count": 0,
                "total_size_bytes": 0,
                "data_types": set(),
                "sources": set()
            },
            "settings": {
                "auto_deduplicate": True,
                "max_items": None,
                "retention_days": None
            }
        }

        self.analytics["lists_created"] += 1
        self._save_lists()
        self._save_analytics()

        return list_id

    def add_item(self, list_id: str, data: Dict[str, Any], source: str = "",
                deduplicate_key: str = None) -> Dict[str, Any]:
        """Add item to list with enhanced features"""
        if list_id not in self.lists:
            return {"success": False, "error": f"List {list_id} not found"}

        list_data = self.lists[list_id]

        # Auto-deduplication if enabled
        if list_data["settings"]["auto_deduplicate"] and deduplicate_key:
            existing_items = [item for item in list_data["items"]
                            if item["data"].get(deduplicate_key) == data.get(deduplicate_key)]
            if existing_items:
                return {"success": False, "error": "Duplicate item found", "duplicate_of": existing_items[0]["id"]}

        # Check max items limit
        if list_data["settings"]["max_items"] and len(list_data["items"]) >= list_data["settings"]["max_items"]:
            # Remove oldest item if at limit
            list_data["items"].pop(0)

        item_id = f"item_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')}"

        item = {
            "id": item_id,
            "data": data,
            "source": source,
            "added_at": datetime.now(timezone.utc).isoformat(),
            "size_bytes": len(json.dumps(data).encode('utf-8'))
        }

        list_data["items"].append(item)
        list_data["metadata"]["updated_at"] = datetime.now(timezone.utc).isoformat()
        list_data["metadata"]["item_count"] = len(list_data["items"])
        list_data["metadata"]["total_size_bytes"] += item["size_bytes"]

        # Update data types and sources
        for key in data.keys():
            list_data["metadata"]["data_types"].add(key)
        if source:
            list_data["metadata"]["sources"].add(source)

        # Convert sets to lists for JSON serialization
        list_data["metadata"]["data_types"] = list(list_data["metadata"]["data_types"])
        list_data["metadata"]["sources"] = list(list_data["metadata"]["sources"])

        self.analytics["items_added"] += 1
        self._save_lists()
        self._save_analytics()

        return {"success": True, "item_id": item_id}

    def search_lists(self, query: str, list_type: str = None, tags: List[str] = None) -> List[Dict[str, Any]]:
        """Search across all lists"""
        self.analytics["searches_performed"] += 1
        self._save_analytics()

        results = []

        for list_id, list_data in self.lists.items():
            # Filter by type and tags
            if list_type and list_data["type"] != list_type:
                continue
            if tags and not any(tag in list_data["tags"] for tag in tags):
                continue

            # Search in name, description, and item data
            search_text = f"{list_data['name']} {list_data['description']}".lower()

            if query.lower() in search_text:
                results.append({
                    "list": list_data,
                    "match_type": "metadata",
                    "relevance_score": 1.0
                })
                continue

            # Search in items
            matching_items = []
            for item in list_data["items"]:
                item_text = json.dumps(item["data"]).lower()
                if query.lower() in item_text:
                    matching_items.append(item)

            if matching_items:
                results.append({
                    "list": list_data,
                    "match_type": "items",
                    "matching_items": matching_items,
                    "relevance_score": len(matching_items) / len(list_data["items"])
                })

        # Sort by relevance
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results

    def get_list_stats(self, list_id: str) -> Dict[str, Any]:
        """Get detailed statistics for a list"""
        if list_id not in self.lists:
            return {"error": f"List {list_id} not found"}

        list_data = self.lists[list_id]
        items = list_data["items"]

        # Basic stats
        stats = {
            "total_items": len(items),
            "total_size_bytes": list_data["metadata"]["total_size_bytes"],
            "data_types": list_data["metadata"]["data_types"],
            "sources": list_data["metadata"]["sources"],
            "created_at": list_data["metadata"]["created_at"],
            "updated_at": list_data["metadata"]["updated_at"]
        }

        if items:
            # Time-based stats
            timestamps = [datetime.fromisoformat(item["added_at"].replace('Z', '+00:00')) for item in items]
            stats["date_range"] = {
                "earliest": min(timestamps).isoformat(),
                "latest": max(timestamps).isoformat()
            }

            # Source distribution
            source_counts = Counter(item["source"] for item in items if item["source"])
            stats["source_distribution"] = dict(source_counts)

            # Size distribution
            sizes = [item["size_bytes"] for item in items]
            stats["size_stats"] = {
                "min": min(sizes),
                "max": max(sizes),
                "avg": sum(sizes) / len(sizes)
            }

        return stats

    def export_list_advanced(self, list_id: str, format: str = "json",
                           filters: Dict[str, Any] = None) -> Optional[str]:
        """Advanced export with filtering options"""
        if list_id not in self.lists:
            return None

        list_data = self.lists[list_id]
        items = list_data["items"]

        # Apply filters
        if filters:
            filtered_items = []
            for item in items:
                include_item = True

                # Date range filter
                if "date_from" in filters:
                    item_date = datetime.fromisoformat(item["added_at"].replace('Z', '+00:00'))
                    if item_date < datetime.fromisoformat(filters["date_from"]):
                        include_item = False

                if "date_to" in filters:
                    item_date = datetime.fromisoformat(item["added_at"].replace('Z', '+00:00'))
                    if item_date > datetime.fromisoformat(filters["date_to"]):
                        include_item = False

                # Source filter
                if "sources" in filters and item["source"] not in filters["sources"]:
                    include_item = False

                # Data field filters
                for field, value in filters.get("data_filters", {}).items():
                    if field in item["data"] and value not in str(item["data"][field]):
                        include_item = False

                if include_item:
                    filtered_items.append(item)
            items = filtered_items

        # Export based on format
        if format == "json":
            export_data = {
                "list_info": {
                    "name": list_data["name"],
                    "description": list_data["description"],
                    "type": list_data["type"],
                    "exported_at": datetime.now(timezone.utc).isoformat()
                },
                "items": items
            }
            return json.dumps(export_data, indent=2)

        elif format == "csv":
            if not items:
                return ""

            # Flatten data for CSV
            csv_rows = []
            for item in items:
                row = {
                    "item_id": item["id"],
                    "added_at": item["added_at"],
                    "source": item["source"],
                    "size_bytes": item["size_bytes"]
                }
                # Add data fields
                for key, value in item["data"].items():
                    if isinstance(value, (list, dict)):
                        row[key] = json.dumps(value)
                    else:
                        row[key] = str(value)
                csv_rows.append(row)

            # Create CSV
            if csv_rows:
                import io
                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=csv_rows[0].keys())
                writer.writeheader()
                writer.writerows(csv_rows)
                return output.getvalue()

        elif format == "excel":
            try:
                # Create DataFrame
                df_data = []
                for item in items:
                    row = {
                        "item_id": item["id"],
                        "added_at": item["added_at"],
                        "source": item["source"],
                        "size_bytes": item["size_bytes"]
                    }
                    row.update(item["data"])
                    df_data.append(row)

                df = pd.DataFrame(df_data)

                # Save to Excel
                excel_path = self.storage_path / f"export_{list_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                df.to_excel(excel_path, index=False)
                return str(excel_path)

            except Exception as e:
                print(f"Excel export error: {e}")
                return None

        return None

    def get_analytics(self) -> Dict[str, Any]:
        """Get system-wide analytics"""
        total_lists = len(self.lists)
        total_items = sum(len(list_data["items"]) for list_data in self.lists.values())
        total_size = sum(list_data["metadata"]["total_size_bytes"] for list_data in self.lists.values())

        # List type distribution
        type_counts = Counter(list_data["type"] for list_data in self.lists.values())

        # Recent activity (last 7 days)
        week_ago = datetime.now(timezone.utc).timestamp() - (7 * 24 * 60 * 60)
        recent_items = 0
        for list_data in self.lists.values():
            for item in list_data["items"]:
                item_timestamp = datetime.fromisoformat(item["added_at"].replace('Z', '+00:00')).timestamp()
                if item_timestamp > week_ago:
                    recent_items += 1

        return {
            "total_lists": total_lists,
            "total_items": total_items,
            "total_size_bytes": total_size,
            "list_types": dict(type_counts),
            "recent_activity": {
                "items_last_7_days": recent_items
            },
            "system_stats": self.analytics
        }

    def cleanup_old_data(self, retention_days: int = 30):
        """Clean up old data based on retention policy"""
        cutoff_date = datetime.now(timezone.utc).timestamp() - (retention_days * 24 * 60 * 60)

        total_removed = 0
        for list_id, list_data in self.lists.items():
            original_count = len(list_data["items"])
            list_data["items"] = [
                item for item in list_data["items"]
                if datetime.fromisoformat(item["added_at"].replace('Z', '+00:00')).timestamp() > cutoff_date
            ]
            removed = original_count - len(list_data["items"])
            total_removed += removed

            if removed > 0:
                list_data["metadata"]["item_count"] = len(list_data["items"])
                list_data["metadata"]["updated_at"] = datetime.now(timezone.utc).isoformat()

        if total_removed > 0:
            self._save_lists()

        return {"items_removed": total_removed}

# Global enhanced data manager instance
enhanced_data_manager = EnhancedDataManager()