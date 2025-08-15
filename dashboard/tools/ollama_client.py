#!/usr/bin/env python3
"""
Base Ollama client - shared dependency for all Ollama tools
"""
import requests
import json
from typing import Dict, Any, Optional

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
    
    def generate(self, model: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """Generate response from Ollama model"""
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                **kwargs
            }
            
            response = requests.post(f"{self.base_url}/api/generate", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "response": result.get("response", ""),
                    "model": model,
                    "done": result.get("done", True)
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Connection error: {str(e)}"
            }
    
    def list_models(self) -> Dict[str, Any]:
        """List available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                return {
                    "success": True,
                    "models": response.json().get("models", [])
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

def get_client() -> OllamaClient:
    """Factory function to get Ollama client"""
    return OllamaClient()