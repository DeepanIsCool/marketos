import os
from dotenv import load_dotenv
import traceback

load_dotenv(override=True)

from graph.campaign_graph import campaign_graph

def run_test():
    print("🚀 Starting Energy Drink Campaign Test...")
    
    initial_state = {
        "user_intent": "Launch a new energy drink called 'VibeRush'. The packaging is vibrant neon green and electric purple. High caffeine, zero sugar. Target: Gen Z gamers and night owls.",
        "campaign_plan": None,
        "copy_output": None,
        "compliance_result": None,
        "send_result": None,
        "current_step": "supervisor",
        "errors": [],
        "trace": [],
        "recipient_email": "sadhukhandeepan@gmail.com",
        "sender_name": "VibeRush Team",
        "company_name": "VibeRush Energy",
        "company_address": "404 Neon City, Metaverse",
        "unsubscribe_url": "https://viberush.com/unsubscribe",
    }

    try:
        print("⛓ Calling campaign_graph.invoke()...")
        result = campaign_graph.invoke(initial_state)
        print("\n✅ Pipeline Finished!")
        print(f"Status: {result.get('current_step')}")
        if result.get('errors'):
            print(f"Errors: {result['errors']}")
        
        copy = result.get('copy_output', {})
        winner_id = copy.get('selected_variant_id')
        variants = copy.get('variants', [])
        winner = next((v for v in variants if v.get('variant_id') == winner_id), None)
        
        if winner:
            print(f"Winning Subject: {winner.get('subject_line')}")
            print(f"Image URL: {copy.get('hero_image_url')}")
            
    except Exception as e:
        print("\n❌ CRASH!")
        traceback.print_exc()

if __name__ == '__main__':
    run_test()
