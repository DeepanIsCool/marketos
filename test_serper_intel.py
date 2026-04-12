import os
import json
from agents.competitor.competitor_agent import competitor_agent_node
from schemas.campaign import CampaignPlan

def test_serper():
    print("\n🚀 TESTING COMPETITOR AGENT WITH SERPER.DEV\n")
    
    # Mock campaign plan with all required Pydantic fields
    plan = {
        "campaign_id": "TEST-123",
        "campaign_name": "VoltX Energy Drink",
        "target_audience": "fitness and gaming enthusiasts in India",
        "goal": "Gain market share from incumbents",
        "channels": ["Email", "SMS", "Social"],
        "budget": 50000.0,
        "timeline": "30 days",
        "tone": "Energetic and Bold",
        "key_messages": ["Level up your hustle", "Buy 2 Get 1 FREE", "India's choice"],
        "tasks": [
            {"agent": "competitor_agent", "task": "Market intelligence scan", "priority": "HIGH"}
        ]
    }
    
    state = {
        "campaign_plan": plan,
        "trace": [],
        "errors": []
    }
    
    # Run the node
    result = competitor_agent_node(state)
    
    # Verify results
    res = result.get("competitor_result", {})
    print(f"\n✅ INTEL ID: {res.get('intel_id')}")
    print(f"✅ ALERT LEVEL: {res.get('alert_level')}")
    
    intel = res.get("intel", {})
    print(f"\n📊 EXECUTIVE SUMMARY:\n{intel.get('executive_summary')}")
    
    print("\n🔍 DISCOVERED COMPETITORS:")
    for comp in intel.get("competitors", []):
        print(f"  - {comp.get('name')} ({comp.get('url')})")
        if comp.get("active_themes"):
            print(f"    Themes: {', '.join(comp['active_themes'])}")

if __name__ == "__main__":
    test_serper()
