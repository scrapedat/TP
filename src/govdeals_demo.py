#!/usr/bin/env python3
"""
GovDeals Scraping Demo - Complete workflow for finding specific government trucks
"""

import requests
import json
import time
from typing import Dict, List, Any
from datetime import datetime

class GovDealsAIScraper:
    def __init__(self, base_url: str = "http://localhost:8081"):
        self.base_url = base_url
        self.user_monitor_url = base_url
        self.status_api_url = "http://localhost:8080"

    def create_cpt_truck_target(self) -> Dict[str, Any]:
        """Create a scraping target for CPT (Cone Penetrometer) trucks"""
        print("🎯 Creating CPT Truck scraping target...")

        payload = {
            "name": "CPT Cone Penetrometer Trucks",
            "keywords": [
                "CPT", "cone penetrometer", "geotechnical",
                "soil testing", "penetrometer truck",
                "Vertek", "CPT truck", "cone penetration"
            ]
        }

        response = requests.post(f"{self.user_monitor_url}/scraping/targets", json=payload)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Created target: {result['target_id']}")
            return result
        else:
            print(f"❌ Failed to create target: {response.status_code}")
            return None

    def create_command_center_target(self) -> Dict[str, Any]:
        """Create a scraping target for command center trucks"""
        print("🎯 Creating Command Center scraping target...")

        payload = {
            "name": "Command Center Trucks",
            "keywords": [
                "command center", "mobile command",
                "emergency response", "incident command",
                "communications truck", "command vehicle"
            ]
        }

        response = requests.post(f"{self.user_monitor_url}/scraping/targets", json=payload)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Created target: {result['target_id']}")
            return result
        else:
            print(f"❌ Failed to create target: {response.status_code}")
            return None

    def create_freightliner_mack_target(self) -> Dict[str, Any]:
        """Create a scraping target for Freightliner and Mack chassis trucks"""
        print("🎯 Creating Freightliner/Mack Chassis scraping target...")

        payload = {
            "name": "Freightliner & Mack Heavy Trucks",
            "keywords": [
                "Freightliner", "Mack truck", "heavy duty",
                "commercial truck", "semi truck", "tractor trailer",
                "18 wheeler", "class 8 truck"
            ]
        }

        response = requests.post(f"{self.user_monitor_url}/scraping/targets", json=payload)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Created target: {result['target_id']}")
            return result
        else:
            print(f"❌ Failed to create target: {response.status_code}")
            return None

    def create_email_alert_rule(self, target_name: str, keywords: List[str]) -> Dict[str, Any]:
        """Create an email alert rule for specific equipment"""
        print(f"📧 Creating email alert for {target_name}...")

        payload = {
            "name": f"Email Alert - {target_name}",
            "conditions": [
                {"type": "keyword", "value": keywords[0]},
                {"type": "price_range", "min": 50000, "max": 500000},
                {"type": "confidence_above", "value": 0.7}
            ],
            "actions": [
                {
                    "type": "email",
                    "recipients": ["your-email@example.com"],
                    "template": f"New {target_name} found on GovDeals matching your criteria!"
                },
                {
                    "type": "notification",
                    "message": f"🚛 New {target_name} available!"
                }
            ]
        }

        response = requests.post(f"{self.user_monitor_url}/scraping/alerts", json=payload)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Created alert rule: {result['alert_id']}")
            return result
        else:
            print(f"❌ Failed to create alert: {response.status_code}")
            return None

    def run_scraping_session(self, target_id: str) -> Dict[str, Any]:
        """Run a complete scraping session with AI analysis"""
        print(f"🔍 Running scraping session for target {target_id}...")

        # Start browser session
        print("🌐 Starting browser session...")
        start_response = requests.post(f"{self.status_api_url}/control/start_all")
        if start_response.status_code == 200:
            print("✅ Browser session started")
        else:
            print(f"⚠️  Browser start failed: {start_response.status_code}")

        # Run scraping
        print("📊 Running scraper...")
        scrape_response = requests.post(f"{self.user_monitor_url}/scraping/targets/{target_id}/run")

        if scrape_response.status_code == 200:
            result = scrape_response.json()
            items_found = result.get('items_scraped', 0)
            print(f"✅ Scraped {items_found} items")

            # Show AI analysis results
            if items_found > 0:
                self.display_ai_analysis(result.get('items', []))

            return result
        else:
            print(f"❌ Scraping failed: {scrape_response.status_code}")
            return None

    def display_ai_analysis(self, items: List[Dict[str, Any]]):
        """Display AI analysis results for scraped items"""
        print("\n🧠 AI ANALYSIS RESULTS:")
        print("=" * 60)

        for i, item in enumerate(items, 1):
            print(f"\n📦 Item {i}: {item.get('title', 'Unknown')}")
            print(f"   💰 Price: ${item.get('price', 'N/A')}")
            print(f"   📍 Location: {item.get('location', 'Unknown')}")
            print(f"   🔗 URL: {item.get('url', 'N/A')}")

            if 'ai_analysis' in item and item['ai_analysis']:
                ai = item['ai_analysis']
                print(f"   🎯 Equipment Type: {ai.get('equipment_type', 'Unknown')}")
                print(".2f"                print(f"   ⭐ Key Features: {', '.join(ai.get('key_features', []))}")
                print(f"   🚨 Alerts: {', '.join(ai.get('alerts', []))}")
                print(f"   💡 Recommendations: {', '.join(ai.get('recommendations', []))}")
            else:
                print("   🤖 No AI analysis available")

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        print("\n📊 SYSTEM STATUS:")
        print("=" * 30)

        response = requests.get(f"{self.status_api_url}/status")
        if response.status_code == 200:
            status = response.json()
            print(f"System Status: {status.get('status', 'Unknown')}")
            print(f"Active Sessions: {status.get('active_sessions', 0)}")
            print(f"Total Requests: {status.get('total_requests', 0)}")

            components = status.get('components', {})
            for name, component in components.items():
                comp_status = component.get('status', 'Unknown')
                status_emoji = "✅" if comp_status == "Online" else "❌" if comp_status == "Offline" else "⚠️"
                print(f"{status_emoji} {name}: {comp_status}")

            return status
        else:
            print(f"❌ Failed to get status: {response.status_code}")
            return {}

    def run_complete_demo(self):
        """Run the complete GovDeals scraping demo"""
        print("🚛 GOVDEALS AI SCRAPING DEMO")
        print("=" * 50)
        print("🎯 Target: Government CPT Trucks, Command Centers, Freightliner/Mack Chassis")
        print("🤖 AI-Powered: Vision analysis, pattern recognition, intelligent filtering")
        print("📧 Alerts: Email notifications for matching equipment")
        print()

        # Check system status
        self.get_system_status()

        # Create scraping targets
        print("\n🎯 CREATING SCRAPING TARGETS:")
        print("-" * 30)

        cpt_target = self.create_cpt_truck_target()
        command_target = self.create_command_center_target()
        chassis_target = self.create_freightliner_mack_target()

        # Create alert rules
        print("\n📧 CREATING ALERT RULES:")
        print("-" * 30)

        if cpt_target:
            self.create_email_alert_rule(
                "CPT Trucks",
                ["CPT", "cone penetrometer", "Vertek"]
            )

        if command_target:
            self.create_email_alert_rule(
                "Command Centers",
                ["command center", "mobile command", "emergency response"]
            )

        if chassis_target:
            self.create_email_alert_rule(
                "Heavy Trucks",
                ["Freightliner", "Mack", "heavy duty"]
            )

        # Run scraping sessions
        print("\n🔍 RUNNING SCRAPING SESSIONS:")
        print("-" * 30)

        targets_to_run = [
            ("CPT Trucks", cpt_target),
            ("Command Centers", command_target),
            ("Heavy Trucks", chassis_target)
        ]

        for name, target in targets_to_run:
            if target:
                target_id = target.get('target_id')
                print(f"\n🔍 Scraping {name}...")
                result = self.run_scraping_session(str(target_id))
                if result:
                    print(f"✅ {name} scraping completed")
                else:
                    print(f"❌ {name} scraping failed")

        # Final status
        print("\n🎉 DEMO COMPLETED!")
        print("=" * 50)
        self.get_system_status()

        print("\n💡 NEXT STEPS:")
        print("1. Check email for equipment alerts")
        print("2. Review AI analysis in /scraping/items endpoint")
        print("3. Set up automated daily scraping schedules")
        print("4. Configure additional alert rules")
        print("5. Integrate with your procurement workflow")

def main():
    demo = GovDealsAIScraper()

    try:
        demo.run_complete_demo()
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")

if __name__ == "__main__":
    main()