#!/usr/bin/env python3
"""
Multi-Model Management System for Ollama
=========================================

Advanced model management with:
- Multiple concurrent models
- Task-based model routing
- Model performance tracking
- Automatic model switching
- Vision model support
"""

import asyncio
import json
import logging
import os
import time
import requests
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
import statistics

logger = logging.getLogger(__name__)

@dataclass
class ModelInfo:
    """Information about an Ollama model"""
    name: str
    size: str
    modified_at: str
    digest: str
    loaded: bool = False
    memory_usage: int = 0
    last_used: Optional[datetime] = None
    performance_score: float = 1.0

@dataclass
class ModelTask:
    """Task definition for model routing"""
    name: str
    description: str
    required_capabilities: List[str]
    preferred_models: List[str]
    fallback_models: List[str]

@dataclass
class ModelPerformance:
    """Performance metrics for a model"""
    model_name: str
    task_type: str
    response_time: float
    token_count: int
    success: bool
    timestamp: datetime

class OllamaModelManager:
    """Manages multiple Ollama models with intelligent routing"""

    def __init__(self, base_url: str = None):
        # Allow overriding via env var; default to local Ollama
        self.base_url = base_url or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.models: Dict[str, ModelInfo] = {}
        self.active_models: Dict[str, ModelInfo] = {}
        self.performance_history: List[ModelPerformance] = []
        self.task_definitions = self._load_task_definitions()

        # Model capabilities mapping
        self.model_capabilities = {
            # Text generation models
            "llama3": ["text_generation", "conversation", "analysis"],
            "llama3:8b": ["text_generation", "conversation", "analysis"],
            "llama3:70b": ["text_generation", "conversation", "analysis", "complex_reasoning"],
            "llama2": ["text_generation", "conversation"],
            "llama2:13b": ["text_generation", "conversation", "analysis"],
            "llama2:70b": ["text_generation", "conversation", "analysis", "complex_reasoning"],

            # Instruction-tuned models
            "phi3": ["text_generation", "conversation", "web_search", "analysis"],
            "phi3:3.8b": ["text_generation", "conversation", "web_search", "analysis"],
            "mistral": ["text_generation", "conversation", "analysis", "coding"],
            "mixtral": ["text_generation", "conversation", "analysis", "coding", "multilingual"],

            # Coding models
            "codellama": ["coding", "text_generation", "analysis"],
            "codellama:13b": ["coding", "text_generation", "analysis"],
            "codellama:34b": ["coding", "text_generation", "analysis", "complex_reasoning"],

            # Vision models
            "llava": ["vision", "text_generation", "image_analysis"],
            "llava:7b": ["vision", "text_generation", "image_analysis"],
            "llava:13b": ["vision", "text_generation", "image_analysis", "detailed_analysis"],
            "bakllava": ["vision", "text_generation", "image_analysis"],
            "moondream": ["vision", "text_generation", "image_analysis", "fast_inference"],

            # Specialized models
            "orca-mini": ["text_generation", "conversation", "fast_inference"],
            "vicuna": ["text_generation", "conversation", "open_ended"],
            "wizard-vicuna": ["text_generation", "conversation", "creative_writing"],
            "nous-hermes": ["text_generation", "conversation", "analysis", "logical_reasoning"],
            "openchat": ["text_generation", "conversation", "uncensored"],
            "dolphin-mistral": ["text_generation", "conversation", "uncensored", "roleplay"],
        }

    def _load_task_definitions(self) -> Dict[str, ModelTask]:
        """Load predefined task definitions"""
        return {
            "general_chat": ModelTask(
                name="general_chat",
                description="General conversation and Q&A",
                required_capabilities=["text_generation", "conversation"],
                preferred_models=["llama3", "mistral", "phi3"],
                fallback_models=["llama2", "orca-mini"]
            ),
            "web_search": ModelTask(
                name="web_search",
                description="Web search and information retrieval",
                required_capabilities=["web_search", "analysis"],
                preferred_models=["phi3", "mistral", "llama3"],
                fallback_models=["llama2", "nous-hermes"]
            ),
            "code_generation": ModelTask(
                name="code_generation",
                description="Code writing and programming tasks",
                required_capabilities=["coding", "text_generation"],
                preferred_models=["codellama", "mistral", "llama3"],
                fallback_models=["llama2", "phi3"]
            ),
            "image_analysis": ModelTask(
                name="image_analysis",
                description="Image understanding and analysis",
                required_capabilities=["vision", "image_analysis"],
                preferred_models=["llava", "bakllava", "moondream"],
                fallback_models=["llava:7b"]
            ),
            "complex_analysis": ModelTask(
                name="complex_analysis",
                description="Complex reasoning and analysis tasks",
                required_capabilities=["complex_reasoning", "analysis"],
                preferred_models=["llama3:70b", "codellama:34b", "mixtral"],
                fallback_models=["llama3", "mistral", "phi3"]
            ),
            "creative_writing": ModelTask(
                name="creative_writing",
                description="Creative writing and content generation",
                required_capabilities=["text_generation", "creative_writing"],
                preferred_models=["wizard-vicuna", "llama2", "mistral"],
                fallback_models=["llama3", "phi3"]
            ),
            "fast_response": ModelTask(
                name="fast_response",
                description="Quick responses and simple tasks",
                required_capabilities=["fast_inference", "text_generation"],
                preferred_models=["moondream", "orca-mini", "phi3"],
                fallback_models=["llama3", "mistral"]
            )
        }

    async def refresh_models(self) -> Dict[str, ModelInfo]:
        """Refresh the list of available models from Ollama"""
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None, requests.get, f"{self.base_url}/api/tags", {"timeout": 10}
            )

            if response.status_code == 200:
                data = response.json()
                current_models = {}

                for model_data in data.get("models", []):
                    name = model_data["name"]
                    model_info = ModelInfo(
                        name=name,
                        size=model_data.get("size", "unknown"),
                        modified_at=model_data.get("modified_at", ""),
                        digest=model_data.get("digest", ""),
                        loaded=name in self.active_models
                    )

                    current_models[name] = model_info

                self.models = current_models
                logger.info(f"Refreshed {len(self.models)} models from Ollama")
                return self.models
            else:
                logger.error(f"Failed to get models: {response.status_code}")
                return {}

        except Exception as e:
            logger.error(f"Error refreshing models: {e}")
            return {}

    async def load_model(self, model_name: str) -> bool:
        """Load a model into memory"""
        if model_name not in self.models:
            logger.warning(f"Model {model_name} not available")
            return False

        try:
            # Generate a small prompt to load the model
            payload = {
                "model": model_name,
                "prompt": "Hello",
                "stream": False
            }

            response = await asyncio.get_event_loop().run_in_executor(
                None, requests.post,
                f"{self.base_url}/api/generate",
                {"json": payload, "timeout": 30}
            )

            if response.status_code == 200:
                self.active_models[model_name] = self.models[model_name]
                self.models[model_name].loaded = True
                self.models[model_name].last_used = datetime.now(timezone.utc)
                logger.info(f"Successfully loaded model: {model_name}")
                return True
            else:
                logger.error(f"Failed to load model {model_name}: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Error loading model {model_name}: {e}")
            return False

    def select_model_for_task(self, task_type: str, context: str = "") -> Optional[str]:
        """Select the best model for a given task"""
        if task_type not in self.task_definitions:
            logger.warning(f"Unknown task type: {task_type}")
            return self._get_default_model()

        task_def = self.task_definitions[task_type]

        # Try preferred models first
        for model_name in task_def.preferred_models:
            if self._is_model_available(model_name):
                return model_name

        # Try fallback models
        for model_name in task_def.fallback_models:
            if self._is_model_available(model_name):
                return model_name

        # Try any model with required capabilities
        for model_name, capabilities in self.model_capabilities.items():
            if self._is_model_available(model_name):
                if all(cap in capabilities for cap in task_def.required_capabilities):
                    return model_name

        # Return default model as last resort
        return self._get_default_model()

    def _is_model_available(self, model_name: str) -> bool:
        """Check if a model is available and loaded"""
        return model_name in self.models and self.models[model_name].loaded

    def _get_default_model(self) -> str:
        """Get the default fallback model"""
        default_order = ["llama3", "mistral", "phi3", "llama2", "orca-mini"]

        for model in default_order:
            if self._is_model_available(model):
                return model

        # Return first available model
        if self.active_models:
            return list(self.active_models.keys())[0]

        return "llama3"  # Ultimate fallback

    async def generate_response(self, model_name: str, prompt: str,
                              context: str = "", **kwargs) -> Dict[str, Any]:
        """Generate a response using the specified model"""
        start_time = time.time()

        try:
            # Build full prompt with context
            full_prompt = prompt
            if context:
                full_prompt = f"Context: {context}\n\nQuestion: {prompt}"

            payload = {
                "model": model_name,
                "prompt": full_prompt,
                "stream": False,
                **kwargs
            }

            response = await asyncio.get_event_loop().run_in_executor(
                None, requests.post,
                f"{self.base_url}/api/generate",
                {"json": payload, "timeout": 120}
            )

            end_time = time.time()
            response_time = end_time - start_time

            if response.status_code == 200:
                data = response.json()
                response_text = data.get("response", "")
                token_count = len(response_text.split())

                # Record performance
                self._record_performance(model_name, "text_generation",
                                       response_time, token_count, True)

                # Update model usage
                if model_name in self.models:
                    self.models[model_name].last_used = datetime.now(timezone.utc)

                return {
                    "success": True,
                    "response": response_text,
                    "model": model_name,
                    "response_time": response_time,
                    "token_count": token_count
                }
            else:
                # Record failed performance
                self._record_performance(model_name, "text_generation",
                                       response_time, 0, False)

                return {
                    "success": False,
                    "error": f"API error: {response.status_code}",
                    "model": model_name
                }

        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time

            # Record failed performance
            self._record_performance(model_name, "text_generation",
                                   response_time, 0, False)

            return {
                "success": False,
                "error": str(e),
                "model": model_name
            }

    def _record_performance(self, model_name: str, task_type: str,
                           response_time: float, token_count: int, success: bool):
        """Record model performance metrics"""
        performance = ModelPerformance(
            model_name=model_name,
            task_type=task_type,
            response_time=response_time,
            token_count=token_count,
            success=success,
            timestamp=datetime.now(timezone.utc)
        )

        self.performance_history.append(performance)

        # Update model performance score
        if model_name in self.models:
            recent_perf = [p for p in self.performance_history[-20:]
                          if p.model_name == model_name and p.success]

            if recent_perf:
                avg_response_time = statistics.mean(p.response_time for p in recent_perf)
                success_rate = len(recent_perf) / 20.0

                # Performance score combines speed and reliability
                self.models[model_name].performance_score = (success_rate * 10) / (avg_response_time + 1)

    async def get_model_status(self) -> Dict[str, Any]:
        """Get comprehensive model status"""
        await self.refresh_models()

        return {
            "total_models": len(self.models),
            "active_models": len(self.active_models),
            "models": {name: asdict(info) for name, info in self.models.items()},
            "active_model_names": list(self.active_models.keys()),
            "task_definitions": {name: asdict(task) for name, task in self.task_definitions.items()},
            "performance_stats": self._get_performance_stats()
        }

    def _get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        if not self.performance_history:
            return {"message": "No performance data available"}

        # Calculate stats for each model
        model_stats = {}
        for model_name in set(p.model_name for p in self.performance_history):
            model_perfs = [p for p in self.performance_history if p.model_name == model_name]

            successful_perfs = [p for p in model_perfs if p.success]

            if successful_perfs:
                avg_response_time = statistics.mean(p.response_time for p in successful_perfs)
                avg_tokens = statistics.mean(p.token_count for p in successful_perfs)
                success_rate = len(successful_perfs) / len(model_perfs)
                tokens_per_second = avg_tokens / avg_response_time if avg_response_time > 0 else 0

                model_stats[model_name] = {
                    "total_requests": len(model_perfs),
                    "success_rate": success_rate,
                    "avg_response_time": avg_response_time,
                    "avg_tokens": avg_tokens,
                    "tokens_per_second": tokens_per_second,
                    "performance_score": self.models.get(model_name, ModelInfo("", "", "", "")).performance_score
                }

        return model_stats

    async def optimize_model_selection(self, task_type: str, context_length: int = 0) -> str:
        """Advanced model selection with optimization"""
        if task_type not in self.task_definitions:
            return self._get_default_model()

        task_def = self.task_definitions[task_type]

        # Get performance data for candidate models
        candidates = task_def.preferred_models + task_def.fallback_models
        candidate_scores = {}

        for model_name in candidates:
            if model_name in self.models:
                model = self.models[model_name]

                # Base score from performance history
                base_score = model.performance_score

                # Adjust for context length (larger models handle longer contexts better)
                if "70b" in model_name or "34b" in model_name:
                    context_score = 1.2 if context_length > 2000 else 1.0
                elif "13b" in model_name:
                    context_score = 1.1 if context_length > 1000 else 1.0
                else:
                    context_score = 1.0

                # Adjust for recency (prefer recently used models)
                recency_score = 1.0
                if model.last_used:
                    hours_since_used = (datetime.now(timezone.utc) - model.last_used).total_seconds() / 3600
                    recency_score = max(0.5, 1.0 - (hours_since_used / 24))  # Decay over 24 hours

                candidate_scores[model_name] = base_score * context_score * recency_score

        # Return highest scoring available model
        if candidate_scores:
            best_model = max(candidate_scores.items(), key=lambda x: x[1])[0]
            if self._is_model_available(best_model):
                return best_model

        # Fallback to basic selection
        return self.select_model_for_task(task_type)

# Global model manager instance
model_manager = OllamaModelManager()