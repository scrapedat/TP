#!/usr/bin/env python3
"""
Test script for Ollama integration with browser automation system
"""

import requests
import json
import time
from typing import Dict, Any

class OllamaTester:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.models_to_test = [
            "llama3.2:1b",
            "qwen2.5:1.5b",
            "moondream:latest"
        ]

    def test_model_availability(self) -> Dict[str, bool]:
        """Test which models are available"""
        print("🔍 Checking model availability...")

        available_models = {}
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                installed_models = [model['name'] for model in data.get('models', [])]

                for model in self.models_to_test:
                    available_models[model] = model in installed_models
                    status = "✅" if available_models[model] else "❌"
                    print(f"  {status} {model}")
            else:
                print(f"❌ Failed to get model list: {response.status_code}")
                for model in self.models_to_test:
                    available_models[model] = False

        except Exception as e:
            print(f"❌ Connection failed: {e}")
            for model in self.models_to_test:
                available_models[model] = False

        return available_models

    def test_browser_analysis(self, model: str) -> Dict[str, Any]:
        """Test browser action analysis with a specific model"""
        print(f"\n🧠 Testing browser analysis with {model}...")

        prompt = """
Analyze this browser user action:
Action Type: click
Element: button (id: "submit-btn", classes: ["btn", "btn-primary"])
Text Content: "Submit Form"
Page Context: https://example.com/contact - Contact Us

Provide analysis including:
1. What the user is trying to do
2. Confidence level (0-1)
3. Suggested next actions
4. Any patterns detected
"""

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": 200
            }
        }

        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30
            )
            end_time = time.time()

            if response.status_code == 200:
                data = response.json()
                analysis = data.get('response', '')

                print("✅ Analysis successful!")
                print(f"⏱️  Response time: {end_time - start_time:.2f}s")
                print(f"📝 Analysis: {analysis[:200]}...")

                return {
                    "success": True,
                    "response_time": end_time - start_time,
                    "analysis": analysis,
                    "model": model
                }
            else:
                print(f"❌ Analysis failed: {response.status_code}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "model": model
                }

        except Exception as e:
            print(f"❌ Analysis error: {e}")
            return {
                "success": False,
                "error": str(e),
                "model": model
            }

    def run_comprehensive_test(self):
        """Run comprehensive test suite"""
        print("🚀 Starting Ollama Integration Test Suite")
        print("=" * 50)

        # Test 1: Model availability
        available_models = self.test_model_availability()

        # Test 2: Browser analysis for available models
        results = []
        for model, available in available_models.items():
            if available:
                result = self.test_browser_analysis(model)
                results.append(result)
            else:
                print(f"\n⏭️  Skipping {model} (not available)")

        # Test 3: Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")

        successful_tests = sum(1 for r in results if r.get("success", False))
        total_tests = len(results)

        print(f"Models tested: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Success rate: {(successful_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%")

        if results:
            avg_response_time = sum(r.get("response_time", 0) for r in results if r.get("success")) / successful_tests
            print(f"Avg response time: {avg_response_time:.2f}s")
        # Recommendations
        print("\n💡 RECOMMENDATIONS:")
        if successful_tests == 0:
            print("❌ No models working. Check Ollama installation and model downloads.")
        elif successful_tests < total_tests:
            print("⚠️  Some models failed. Consider using only successful models in production.")
        else:
            print("✅ All tested models working well!")

        print("\n🎯 Ready for browser automation integration!")

        return {
            "available_models": available_models,
            "test_results": results,
            "summary": {
                "total_tests": total_tests,
                "successful": successful_tests,
                "avg_response_time": avg_response_time if successful_tests > 0 else 0
            }
        }

if __name__ == "__main__":
    tester = OllamaTester()
    results = tester.run_comprehensive_test()

    # Save results
    with open("/home/scrapedat/ollama_integration_test_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n📄 Results saved to: /home/scrapedat/ollama_integration_test_results.json")