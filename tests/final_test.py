#!/usr/bin/env python3
"""
ToolLlama Final System Test
===========================

Comprehensive test of all ToolLlama features before moving to next project.
"""

import requests
import json
import time
import sys

class ToolLlamaTester:
    """Comprehensive system tester"""

    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = {}

    def test_endpoint(self, name, method, url, data=None, expected_status=200):
        """Test a single endpoint"""
        try:
            if method == "GET":
                response = self.session.get(url)
            elif method == "POST":
                response = self.session.post(url, json=data)
            elif method == "DELETE":
                response = self.session.delete(url)

            success = response.status_code == expected_status
            result = {
                "success": success,
                "status_code": response.status_code,
                "expected": expected_status
            }

            if success and response.content:
                try:
                    result["data"] = response.json()
                except:
                    result["data"] = response.text

            self.test_results[name] = result
            return success

        except Exception as e:
            self.test_results[name] = {
                "success": False,
                "error": str(e)
            }
            return False

    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🧪 ToolLlama Final System Test")
        print("=" * 50)

        tests_passed = 0
        total_tests = 0

        # Health Check
        print("🔍 Testing Health Check...")
        total_tests += 1
        if self.test_endpoint("health_check", "GET", f"{self.base_url}/health"):
            tests_passed += 1
            print("   ✅ Health check passed")

        # Browser Management
        print("\n🌐 Testing Browser Management...")

        # Create session
        total_tests += 1
        if self.test_endpoint("create_session", "POST", f"{self.base_url}/api/browser/create_session"):
            session_id = self.test_results["create_session"]["data"]["session_id"]
            tests_passed += 1
            print(f"   ✅ Session created: {session_id}")

            # Test navigation
            total_tests += 1
            if self.test_endpoint("navigate", "POST", f"{self.base_url}/api/browser/{session_id}/navigate",
                                {"url": "https://example.com"}):
                tests_passed += 1
                print("   ✅ Navigation successful")

            # Test actions
            total_tests += 1
            if self.test_endpoint("action", "POST", f"{self.base_url}/api/browser/{session_id}/action",
                                {"action": "click", "parameters": {"selector": "button"}}):
                tests_passed += 1
                print("   ✅ Action execution successful")

            # Test screenshot
            total_tests += 1
            if self.test_endpoint("screenshot", "GET", f"{self.base_url}/api/browser/{session_id}/screenshot"):
                tests_passed += 1
                print("   ✅ Screenshot retrieval successful")

            # Test AI control
            total_tests += 1
            if self.test_endpoint("enable_ai", "POST", f"{self.base_url}/api/browser/{session_id}/enable_ai"):
                tests_passed += 1
                print("   ✅ AI control enabled")

            # Test session info
            total_tests += 1
            if self.test_endpoint("session_info", "GET", f"{self.base_url}/api/browser/{session_id}/info"):
                tests_passed += 1
                print("   ✅ Session info retrieved")

            # Close session
            total_tests += 1
            if self.test_endpoint("close_session", "DELETE", f"{self.base_url}/api/browser/{session_id}"):
                tests_passed += 1
                print("   ✅ Session closed")

        # Model Management
        print("\n🤖 Testing Model Management...")

        # Model status
        total_tests += 1
        if self.test_endpoint("model_status", "GET", f"{self.base_url}/api/models/status"):
            tests_passed += 1
            print("   ✅ Model status retrieved")

        # Model generation
        total_tests += 1
        if self.test_endpoint("model_generate", "POST", f"{self.base_url}/api/models/generate",
                            {"prompt": "Test message", "model": "llama3"}):
            tests_passed += 1
            print("   ✅ Model generation successful")

        # Data Management
        print("\n📊 Testing Data Management...")

        # Create list
        total_tests += 1
        if self.test_endpoint("create_list", "POST", f"{self.base_url}/api/data/lists",
                            {"name": "Test List", "description": "Final test", "list_type": "general"}):
            list_id = self.test_results["create_list"]["data"]["result"]["list_id"]
            tests_passed += 1
            print(f"   ✅ List created: {list_id}")

            # Add item
            total_tests += 1
            if self.test_endpoint("add_item", "POST", f"{self.base_url}/api/data/lists/items",
                                {"list_id": list_id, "data": {"test": "data"}, "source": "test"}):
                tests_passed += 1
                print("   ✅ Item added to list")

        # Get lists
        total_tests += 1
        if self.test_endpoint("get_lists", "GET", f"{self.base_url}/api/data/lists"):
            tests_passed += 1
            print("   ✅ Lists retrieved")

        # Web Scraping
        print("\n🌐 Testing Web Scraping...")
        total_tests += 1
        if self.test_endpoint("web_scrape", "POST", f"{self.base_url}/api/tools/scrape_webpage",
                            {"url": "https://httpbin.org/html"}):
            tests_passed += 1
            print("   ✅ Web scraping successful")

        # Summary
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {tests_passed}")
        print(f"Failed: {total_tests - tests_passed}")
        print(f"Success Rate: {(tests_passed/total_tests*100):.1f}%")
        if tests_passed == total_tests:
            print("🎉 ALL TESTS PASSED! System is fully functional.")
        elif tests_passed >= total_tests * 0.9:
            print("✅ System is highly functional with minor issues.")
        elif tests_passed >= total_tests * 0.7:
            print("⚠️  System is functional but has some issues.")
        else:
            print("❌ System has significant issues.")

        return tests_passed == total_tests

def main():
    """Main test execution"""
    print("🚀 ToolLlama Final System Validation")
    print("=" * 50)

    # Check if system is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("❌ Backend not responding. Please start the system first:")
            print("   cd /home/scrapedat/toollama")
            print("   ./venv/bin/python quick_start.py")
            return False
    except:
        print("❌ Cannot connect to backend. Please start the system first:")
        print("   cd /home/scrapedat/toollama")
        print("   ./venv/bin/python quick_start.py")
        return False

    # Run tests
    tester = ToolLlamaTester()
    success = tester.run_all_tests()

    # Save detailed results
    with open("/home/scrapedat/toollama/final_test_results.json", "w") as f:
        json.dump(tester.test_results, f, indent=2)

    print(f"\n💾 Detailed results saved to: final_test_results.json")

    if success:
        print("\n🎊 ToolLlama is READY for production use!")
        print("All features are properly wired and functional.")
    else:
        print("\n⚠️  Some features may need attention before production use.")

    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)