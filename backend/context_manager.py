#!/usr/bin/env python3
"""
Ollama Context Persistence & Learning System
=============================================

Advanced context management for Ollama models including:
- Conversation history with semantic search
- User knowledge base and preferences
- Tool usage analytics and learning
- Context-aware prompt engineering
- Memory consolidation and optimization
"""

import json
import sqlite3
import os
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import hashlib
import re
from collections import defaultdict, Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class OllamaContextManager:
    """Advanced context management for Ollama models"""

    def __init__(self, db_path: str = "/home/scrapedat/toollama/data/ollama_context.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()

        # Initialize semantic search
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )

        # Context window settings
        self.max_context_length = 4000  # tokens
        self.conversation_memory = 50    # recent conversations
        self.knowledge_relevance_threshold = 0.3

    def init_database(self):
        """Initialize SQLite database for context storage"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Conversation history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    user_id TEXT DEFAULT 'default',
                    timestamp TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    tool_calls TEXT,
                    metadata TEXT,
                    embedding TEXT
                )
            """)

            # User knowledge base
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_base (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT DEFAULT 'default',
                    category TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    source TEXT,
                    confidence REAL DEFAULT 1.0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TEXT,
                    tags TEXT
                )
            """)

            # User preferences and patterns
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT DEFAULT 'default',
                    preference_type TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    confidence REAL DEFAULT 1.0,
                    last_updated TEXT NOT NULL,
                    UNIQUE(user_id, preference_type, key)
                )
            """)

            # Tool usage analytics
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tool_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT DEFAULT 'default',
                    tool_name TEXT NOT NULL,
                    success BOOLEAN NOT NULL,
                    execution_time REAL,
                    context TEXT,
                    timestamp TEXT NOT NULL,
                    error_message TEXT
                )
            """)

            # Learning patterns
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS learning_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT DEFAULT 'default',
                    pattern_type TEXT NOT NULL,
                    pattern_data TEXT NOT NULL,
                    confidence REAL DEFAULT 0.5,
                    occurrences INTEGER DEFAULT 1,
                    first_seen TEXT NOT NULL,
                    last_seen TEXT NOT NULL
                )
            """)

            conn.commit()

    def save_conversation(self, session_id: str, role: str, content: str,
                         tool_calls: Optional[List[Dict]] = None,
                         metadata: Optional[Dict] = None,
                         user_id: str = "default") -> int:
        """Save a conversation message to the database"""

        # Create embedding for semantic search
        embedding = self._create_text_embedding(content)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO conversations
                (session_id, user_id, timestamp, role, content, tool_calls, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id,
                user_id,
                datetime.now(timezone.utc).isoformat(),
                role,
                content,
                json.dumps(tool_calls) if tool_calls else None,
                json.dumps(metadata) if metadata else None,
                json.dumps(embedding.tolist()) if embedding is not None else None
            ))

            conversation_id = cursor.lastrowid
            conn.commit()

            return conversation_id

    def get_conversation_history(self, session_id: str, limit: int = 50,
                               user_id: str = "default") -> List[Dict[str, Any]]:
        """Retrieve conversation history for a session"""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, timestamp, role, content, tool_calls, metadata
                FROM conversations
                WHERE session_id = ? AND user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (session_id, user_id, limit))

            rows = cursor.fetchall()

            # Convert to list of dictionaries (reverse to chronological order)
            conversations = []
            for row in reversed(rows):
                conv = {
                    "id": row[0],
                    "timestamp": row[1],
                    "role": row[2],
                    "content": row[3],
                    "tool_calls": json.loads(row[4]) if row[4] else None,
                    "metadata": json.loads(row[5]) if row[5] else None
                }
                conversations.append(conv)

            return conversations

    def build_context_prompt(self, session_id: str, current_query: str,
                           max_tokens: int = 3000, user_id: str = "default") -> str:
        """Build an intelligent context prompt for Ollama"""

        context_parts = []

        # 1. Recent conversation history
        recent_conversations = self.get_conversation_history(session_id, 10, user_id)
        if recent_conversations:
            context_parts.append("## Recent Conversation:")
            for conv in recent_conversations[-5:]:  # Last 5 messages
                role = conv['role'].upper()
                content = conv['content'][:200] + "..." if len(conv['content']) > 200 else conv['content']
                context_parts.append(f"{role}: {content}")

        # 2. Relevant knowledge from knowledge base
        relevant_knowledge = self.search_knowledge_base(current_query, limit=3, user_id=user_id)
        if relevant_knowledge:
            context_parts.append("\n## Relevant Knowledge:")
            for knowledge in relevant_knowledge:
                context_parts.append(f"- {knowledge['title']}: {knowledge['content'][:150]}...")

        # 3. User preferences and patterns
        user_context = self.get_user_context(user_id)
        if user_context:
            context_parts.append(f"\n## User Context: {user_context}")

        # 4. Tool usage patterns
        tool_patterns = self.get_tool_usage_patterns(user_id)
        if tool_patterns:
            context_parts.append(f"\n## Preferred Tools: {', '.join(tool_patterns[:3])}")

        # Combine and truncate to fit token limit
        full_context = "\n".join(context_parts)

        # Simple token estimation (rough approximation)
        estimated_tokens = len(full_context.split()) * 1.3

        if estimated_tokens > max_tokens:
            # Truncate older parts first
            context_parts = context_parts[-2:]  # Keep only recent conversation and user context
            full_context = "\n".join(context_parts)

        return full_context

    def add_to_knowledge_base(self, category: str, title: str, content: str,
                            source: str = "", confidence: float = 1.0,
                            tags: List[str] = None, user_id: str = "default") -> int:
        """Add information to the user's knowledge base"""

        # Check if similar knowledge already exists
        existing = self.search_knowledge_base(title, limit=1, user_id=user_id)
        if existing and existing[0]['title'].lower() == title.lower():
            # Update existing knowledge
            return self.update_knowledge_base(existing[0]['id'], content, confidence, user_id)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            now = datetime.now(timezone.utc).isoformat()

            cursor.execute("""
                INSERT INTO knowledge_base
                (user_id, category, title, content, source, confidence, created_at, updated_at, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                category,
                title,
                content,
                source,
                confidence,
                now,
                now,
                json.dumps(tags) if tags else None
            ))

            knowledge_id = cursor.lastrowid
            conn.commit()

            return knowledge_id

    def search_knowledge_base(self, query: str, limit: int = 5,
                            user_id: str = "default") -> List[Dict[str, Any]]:
        """Search the knowledge base using semantic similarity"""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get all knowledge entries for the user
            cursor.execute("""
                SELECT id, category, title, content, source, confidence, tags, access_count
                FROM knowledge_base
                WHERE user_id = ?
                ORDER BY last_accessed DESC, confidence DESC
            """, (user_id,))

            rows = cursor.fetchall()

            if not rows:
                return []

            # Prepare text for similarity comparison
            texts = [f"{row[2]} {row[3]}" for row in rows]  # title + content

            try:
                # Create TF-IDF vectors
                tfidf_matrix = self.vectorizer.fit_transform([query] + texts)

                # Calculate similarities
                similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])[0]

                # Get top results
                top_indices = np.argsort(similarities)[::-1][:limit]
                top_similarities = similarities[top_indices]

                results = []
                for idx, similarity in zip(top_indices, top_similarities):
                    if similarity >= self.knowledge_relevance_threshold:
                        row = rows[idx]
                        result = {
                            "id": row[0],
                            "category": row[1],
                            "title": row[2],
                            "content": row[3],
                            "source": row[4],
                            "confidence": row[5],
                            "tags": json.loads(row[6]) if row[6] else [],
                            "access_count": row[7],
                            "relevance_score": float(similarity)
                        }
                        results.append(result)

                        # Update access count
                        self._update_knowledge_access(row[0])

                return results

            except Exception as e:
                # Fallback to simple text matching
                print(f"Semantic search failed, using text matching: {e}")
                return self._simple_text_search(query, rows, limit)

    def _simple_text_search(self, query: str, rows: List, limit: int) -> List[Dict[str, Any]]:
        """Fallback text search method"""
        query_lower = query.lower()
        results = []

        for row in rows:
            title = row[2].lower()
            content = row[3].lower()

            if query_lower in title or query_lower in content:
                score = 1.0 if query_lower in title else 0.7
                results.append({
                    "id": row[0],
                    "category": row[1],
                    "title": row[2],
                    "content": row[3],
                    "source": row[4],
                    "confidence": row[5],
                    "tags": json.loads(row[6]) if row[6] else [],
                    "access_count": row[7],
                    "relevance_score": score
                })

        return sorted(results, key=lambda x: x['relevance_score'], reverse=True)[:limit]

    def update_user_preference(self, preference_type: str, key: str, value: Any,
                             confidence: float = 1.0, user_id: str = "default"):
        """Update or create a user preference"""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO user_preferences
                (user_id, preference_type, key, value, confidence, last_updated)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                preference_type,
                key,
                json.dumps(value) if not isinstance(value, str) else value,
                confidence,
                datetime.now(timezone.utc).isoformat()
            ))

            conn.commit()

    def get_user_context(self, user_id: str = "default") -> str:
        """Get user context information for prompts"""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT preference_type, key, value, confidence
                FROM user_preferences
                WHERE user_id = ? AND confidence > 0.7
                ORDER BY confidence DESC
                LIMIT 10
            """, (user_id,))

            preferences = cursor.fetchall()

            if not preferences:
                return ""

            context_parts = []
            for pref_type, key, value, confidence in preferences:
                if pref_type == "communication_style":
                    context_parts.append(f"You prefer {key}: {value}")
                elif pref_type == "tool_preference":
                    context_parts.append(f"You often use {key} for {value}")
                elif pref_type == "knowledge_area":
                    context_parts.append(f"You're knowledgeable about {key}")

            return ". ".join(context_parts)

    def record_tool_usage(self, tool_name: str, success: bool, execution_time: float = None,
                         context: str = "", error_message: str = "", user_id: str = "default"):
        """Record tool usage for analytics and learning"""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO tool_analytics
                (user_id, tool_name, success, execution_time, context, timestamp, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                tool_name,
                success,
                execution_time,
                context,
                datetime.now(timezone.utc).isoformat(),
                error_message
            ))

            conn.commit()

    def get_tool_usage_patterns(self, user_id: str = "default", limit: int = 5) -> List[str]:
        """Get most successful tools for the user"""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT tool_name, COUNT(*) as usage_count,
                       AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) as success_rate
                FROM tool_analytics
                WHERE user_id = ?
                GROUP BY tool_name
                HAVING success_rate > 0.7
                ORDER BY usage_count DESC, success_rate DESC
                LIMIT ?
            """, (user_id, limit))

            rows = cursor.fetchall()
            return [row[0] for row in rows]

    def learn_from_interaction(self, user_query: str, ollama_response: str,
                             tool_used: str = None, success: bool = True,
                             user_id: str = "default"):
        """Learn patterns from user interactions"""

        # Extract patterns from successful interactions
        if success and tool_used:
            pattern_key = f"tool_success_{tool_used}"
            self._update_learning_pattern("tool_success", pattern_key, user_id)

        # Learn from query patterns
        query_patterns = self._extract_query_patterns(user_query)
        for pattern in query_patterns:
            self._update_learning_pattern("query_pattern", pattern, user_id)

        # Add successful interactions to knowledge base
        if success and len(ollama_response) > 50:
            category = "learned_interaction"
            title = f"Interaction: {user_query[:50]}..."
            content = f"Query: {user_query}\nResponse: {ollama_response}"
            if tool_used:
                content += f"\nTool Used: {tool_used}"

            self.add_to_knowledge_base(category, title, content,
                                     source="interaction_learning",
                                     confidence=0.8, user_id=user_id)

    def _extract_query_patterns(self, query: str) -> List[str]:
        """Extract patterns from user queries"""
        patterns = []

        # Simple pattern extraction
        if "scrape" in query.lower() or "extract" in query.lower():
            patterns.append("data_extraction_request")
        if "search" in query.lower() or "find" in query.lower():
            patterns.append("search_request")
        if "email" in query.lower() or "send" in query.lower():
            patterns.append("communication_request")
        if "analyze" in query.lower() or "summarize" in query.lower():
            patterns.append("analysis_request")

        return patterns

    def _update_learning_pattern(self, pattern_type: str, pattern_data: str, user_id: str):
        """Update or create a learning pattern"""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            now = datetime.now(timezone.utc).isoformat()

            # Check if pattern exists
            cursor.execute("""
                SELECT id, occurrences FROM learning_patterns
                WHERE user_id = ? AND pattern_type = ? AND pattern_data = ?
            """, (user_id, pattern_type, pattern_data))

            existing = cursor.fetchone()

            if existing:
                # Update existing pattern
                cursor.execute("""
                    UPDATE learning_patterns
                    SET occurrences = occurrences + 1,
                        confidence = MIN(confidence + 0.1, 1.0),
                        last_seen = ?
                    WHERE id = ?
                """, (now, existing[0]))
            else:
                # Create new pattern
                cursor.execute("""
                    INSERT INTO learning_patterns
                    (user_id, pattern_type, pattern_data, confidence, occurrences, first_seen, last_seen)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (user_id, pattern_type, pattern_data, 0.5, 1, now, now))

            conn.commit()

    def _create_text_embedding(self, text: str) -> Optional[np.ndarray]:
        """Create a simple text embedding for semantic search"""
        try:
            # Simple TF-IDF based embedding
            vector = self.vectorizer.fit_transform([text])
            return vector.toarray()[0]
        except Exception:
            return None

    def _update_knowledge_access(self, knowledge_id: int):
        """Update access count and timestamp for knowledge"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            now = datetime.now(timezone.utc).isoformat()

            cursor.execute("""
                UPDATE knowledge_base
                SET access_count = access_count + 1, last_accessed = ?
                WHERE id = ?
            """, (now, knowledge_id))

            conn.commit()

    def update_knowledge_base(self, knowledge_id: int, new_content: str,
                            confidence: float = None, user_id: str = "default") -> bool:
        """Update existing knowledge in the base"""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            updates = ["content = ?", "updated_at = ?"]
            values = [new_content, datetime.now(timezone.utc).isoformat()]

            if confidence is not None:
                updates.append("confidence = ?")
                values.append(confidence)

            query = f"""
                UPDATE knowledge_base
                SET {', '.join(updates)}
                WHERE id = ? AND user_id = ?
            """

            values.extend([knowledge_id, user_id])

            cursor.execute(query, values)
            success = cursor.rowcount > 0
            conn.commit()

            return success

    def get_system_stats(self, user_id: str = "default") -> Dict[str, Any]:
        """Get comprehensive system statistics"""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            stats = {
                "conversations": 0,
                "knowledge_entries": 0,
                "tool_uses": 0,
                "learning_patterns": 0,
                "total_tokens_estimated": 0
            }

            # Count conversations
            cursor.execute("SELECT COUNT(*) FROM conversations WHERE user_id = ?", (user_id,))
            stats["conversations"] = cursor.fetchone()[0]

            # Count knowledge entries
            cursor.execute("SELECT COUNT(*) FROM knowledge_base WHERE user_id = ?", (user_id,))
            stats["knowledge_entries"] = cursor.fetchone()[0]

            # Count tool uses
            cursor.execute("SELECT COUNT(*) FROM tool_analytics WHERE user_id = ?", (user_id,))
            stats["tool_uses"] = cursor.fetchone()[0]

            # Count learning patterns
            cursor.execute("SELECT COUNT(*) FROM learning_patterns WHERE user_id = ?", (user_id,))
            stats["learning_patterns"] = cursor.fetchone()[0]

            # Estimate total tokens (rough calculation)
            cursor.execute("SELECT SUM(LENGTH(content)) FROM conversations WHERE user_id = ?", (user_id,))
            conv_length = cursor.fetchone()[0] or 0
            stats["total_tokens_estimated"] = int(conv_length * 0.3)  # Rough token estimation

            return stats

    def cleanup_old_data(self, days_to_keep: int = 90, user_id: str = "default"):
        """Clean up old conversation data"""

        cutoff_date = (datetime.now(timezone.utc) - timedelta(days=days_to_keep)).isoformat()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Delete old conversations (keep recent ones)
            cursor.execute("""
                DELETE FROM conversations
                WHERE user_id = ? AND timestamp < ?
                AND id NOT IN (
                    SELECT id FROM conversations
                    WHERE user_id = ?
                    ORDER BY timestamp DESC
                    LIMIT 100
                )
            """, (user_id, cutoff_date, user_id))

            deleted_count = cursor.rowcount
            conn.commit()

            return {"conversations_deleted": deleted_count}

# Global context manager instance
context_manager = OllamaContextManager()