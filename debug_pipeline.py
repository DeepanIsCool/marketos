import os
from dotenv import load_dotenv
import traceback

# Load env before any agent imports
load_dotenv(override=True)

from graph.campaign_graph import campaign_graph

def run_debug():
    print("🚀 Starting Debug Pipeline...")
    
    initial_state = {
        "user_intent": "Launch a premium luxury watch collection for MarketOS. The tone should be highly sophisticated and exclusive. Offer early access and a signed certificate of authenticity.",
        "campaign_plan": None,
        "copy_output": None,
        "compliance_result": None,
        "send_result": None,
        "current_step": "supervisor",
        "errors": [],
        "trace": [],
        "recipient_email": "sadhukhandeepan@gmail.com",
        "sender_name": "MarketOS Timepieces",
        "company_name": "MarketOS",
        "unsubscribe_url": "https://example.com/unsubscribe",
    }

    try:
        print("⛓ Calling campaign_graph.invoke()...")
        result = campaign_graph.invoke(initial_state)
        print("✅ Pipeline Success!")
        print(f"Current Step: {result.get('current_step')}")
        if result.get('errors'):
            print(f"Errors noted in state: {result['errors']}")
            
    except Exception as e:
        print("\n❌ PIPELINE CRASH DETECTED!")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        print("\n--- FULL TRACEBACK ---")
        traceback.print_exc()
        print("----------------------\n")

if __name__ == "__main__":
    run_debug()
