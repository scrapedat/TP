#!/usr/bin/env python3
"""
ToolLlama Backend Test Script
=============================

Test the ToolLlama backend API endpoints to ensure everything is working.
"""

import asyncio
import json
import requests
import time
from typing import Dict, Any

class BackendTester:
    """Test the ToolLlama backend API"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()

    def test_health_check(self) -> Dict[str, Any]:
        """Test health check endpoint"""
        print("🔍 Testing health check...")
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print("✅ Health check passed")
                print(f"   Status: {data.get('status')}")
                print(f"   Services: {', '.join([k for k, v in data.get('services', {}).items() if v])}")
                return {"success": True, "data": data}
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return {"success": False, "error": str(e)}

    def test_data_list_operations(self) -> Dict[str, Any]:
        """Test data list creation and management"""
        print("\n📝 Testing data list operations...")

        # Create a test list
        create_payload = {
            "name": "Test Research List",
            "description": "A test list for research data",
            "list_type": "research"
        }

        try:
            response = self.session.post(
                f"{self.base_url}/api/data/lists",
                json=create_payload,
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    list_id = result["result"]["list_id"]
                    print(f"✅ List created: {list_id}")

                    # Add an item to the list
                    item_payload = {
                        "list_id": list_id,
                        "data": {
                            "url": "https://example.com",
                            "title": "Example Website",
                            "description": "A test website"
                        },
                        "source": "test_script"
                    }

                    response2 = self.session.post(
                        f"{self.base_url}/api/data/lists/items",
                        json=item_payload,
                        timeout=10
                    )

                    if response2.status_code == 200:
                        result2 = response2.json()
                        if result2.get("success"):
                            print("✅ Item added to list")
                            return {"success": True, "list_id": list_id}
                        else:
                            print(f"❌ Failed to add item: {result2}")
                            return {"success": False, "error": "Failed to add item"}
                    else:
                        print(f"❌ Add item failed: {response2.status_code}")
                        return {"success": False, "error": f"HTTP {response2.status_code}"}
                else:
                    print(f"❌ List creation failed: {result}")
                    return {"success": False, "error": "List creation failed"}
            else:
                print(f"❌ List creation HTTP error: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}

        except Exception as e:
            print(f"❌ Data list test error: {e}")
            return {"success": False, "error": str(e)}

    def test_web_scraping(self) -> Dict[str, Any]:
        """Test web scraping capabilities"""
        print("\n🌐 Testing web scraping...")

        scrape_payload = {
            "url": "https://httpbin.org/html",
            "extraction_prompt": "Extract the main heading and any list items",
            "method": "auto"
        }

        try:
            response = self.session.post(
                f"{self.base_url}/api/tools/scrape_webpage",
                json=scrape_payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    print("✅ Web scraping successful")
                    data = result.get("result", {})
                    print(f"   URL: {data.get('url')}")
                    print(f"   Listings found: {data.get('listings_found', 0)}")
                    return {"success": True, "data": data}
                else:
                    print(f"❌ Scraping failed: {result}")
                    return {"success": False, "error": result.get("error", "Unknown error")}
            else:
                print(f"❌ Scraping HTTP error: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}

        except Exception as e:
            print(f"❌ Web scraping test error: {e}")
            return {"success": False, "error": str(e)}

    def test_document_extraction(self) -> Dict[str, Any]:
        """Test document extraction capabilities"""
        print("\n📄 Testing document extraction...")

        # Test text extraction from a simple webpage
        try:
            response = self.session.post(
                f"{self.base_url}/api/tools/extract_text",
                json={"url": "https://httpbin.org/html"},
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    data = result.get("result", {})
                    if data.get("success"):
                        print("✅ Document extraction successful")
                        print(f"   Content type: {data.get('content_type')}")
                        text_length = len(data.get("text_content", ""))
                        print(f"   Text extracted: {text_length} characters")
                        return {"success": True, "data": data}
                    else:
                        print(f"❌ Extraction failed: {data.get('error')}")
                        return {"success": False, "error": data.get("error")}
                else:
                    print(f"❌ API call failed: {result}")
                    return {"success": False, "error": result.get("error", "API error")}
            else:
                print(f"❌ HTTP error: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}

        except Exception as e:
            print(f"❌ Document extraction test error: {e}")
            return {"success": False, "error": str(e)}

    def test_web_search(self) -> Dict[str, Any]:
        """Test web search capabilities"""
        print("\n🔍 Testing web search...")

        try:
            response = self.session.post(
                f"{self.base_url}/api/tools/web_search",
                json={"query": "test search", "max_results": 3},
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    data = result.get("result", {})
                    if data.get("success"):
                        print("✅ Web search successful")
                        print(f"   Query: {data.get('query')}")
                        print(f"   Results found: {data.get('results_count', 0)}")
                        return {"success": True, "data": data}
                    else:
                        print(f"❌ Search failed: {data.get('error')}")
                        return {"success": False, "error": data.get("error")}
                else:
                    print(f"❌ API call failed: {result}")
                    return {"success": False, "error": result.get("error", "API error")}
            else:
                print(f"❌ HTTP error: {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}

        except Exception as e:
            print(f"❌ Web search test error: {e}")
            return {"success": False, "error": str(e)}

    async def run_all_tests(self):
        """Run all backend tests"""
        print("🧪 ToolLlama Backend Test Suite")
        print("=" * 40)

        # Wait a moment for server to start
        print("⏳ Waiting for server to be ready...")
        time.sleep(2)

        results = []

        # Test 1: Health check
        health_result = self.test_health_check()
        results.append(("Health Check", health_result))

        # Test 2: Data list operations
        data_result = self.test_data_list_operations()
        results.append(("Data Lists", data_result))

        # Test 3: Web scraping
        scrape_result = self.test_web_scraping()
        results.append(("Web Scraping", scrape_result))

        # Test 4: Document extraction
        doc_result = self.test_document_extraction()
        results.append(("Document Extraction", doc_result))

        # Test 5: Web search
        search_result = self.test_web_search()
        results.append(("Web Search", search_result))

        # Summary
        print("\n" + "=" * 40)
        print("📊 TEST SUMMARY")

        passed = 0
        total = len(results)

        for test_name, result in results:
            status = "✅ PASS" if result.get("success") else "❌ FAIL"
            print(f"{status} {test_name}")
            if not result.get("success"):
                print(f"   Error: {result.get('error', 'Unknown')}")

        passed = sum(1 for _, result in results if result.get("success"))
        print(f"\nOverall: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 All tests passed! Backend is ready.")
        elif passed >= total * 0.7:
            print("⚠️  Most tests passed. Backend is partially functional.")
        else:
            print("❌ Many tests failed. Check backend configuration.")

        return results

async def main():
    """Main test function"""
    tester = BackendTester()

    # Check if server is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ Backend server is not running on http://localhost:8000")
            print("   Please start the backend first:")
            print("   cd /home/scrapedat/toollama/backend")
            print("   python run_backend.py")
            return
    except:
        print("❌ Cannot connect to backend server")
        print("   Please start the backend first:")
        print("   cd /home/scrapedat/toollama/backend")
        print("   python run_backend.py")
        return

    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())