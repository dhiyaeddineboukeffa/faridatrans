import requests
import time
import random

API_URL = "http://localhost:8000"

print("="*70)
print("🚀 LIVE RIDE TELEMETRY DEMONSTRATION")
print("="*70)
print()

# Calculate initial route
print("1️⃣  Calculating route: Benabdelmalek → Mehri (University)")
route_data = {
    "origin": "benabdelmalek",
    "destination": "mehri"
}

try:
    response = requests.post(f"{API_URL}/route", json=route_data)
    if response.status_code != 200:
        print(f"❌ Route calculation failed: {response.status_code}")
        print(f"Response: {response.text}")
        exit(1)
    
    route = response.json()
    initial_duration = route['total_duration']
    
    print(f"✅ Initial route calculated!")
    print(f"   Duration: {initial_duration/60:.1f} minutes ({len(route['steps'])} steps)")
    print()
    
    # Get transit steps (non-walking)
    transit_steps = [s for s in route['steps'] if s['mode'] in ['tram', 'bus']]
    print(f"2️⃣  Found {len(transit_steps)} transit segments to simulate")
    print()
    
    # Simulate live ride
    print("3️⃣  Starting Live Ride simulation...")
    print("-"*70)
    
    for i, step in enumerate(transit_steps[:5], 1):  # Limit to first 5 segments
        # Random speed between 12-25 m/s
        speed = 12 + random.random() * 13
        
        print(f"\n[Segment {i}]  {step['from_stop']} → {step['to_stop']}")
        print(f"   Mode: {step['mode'].upper()}")
        print(f"   Simulated speed: {speed:.1f} m/s ({speed*3.6:.1f} km/h)")
        
        # Send telemetry
        telemetry = {
            "u": step['from_stop'],
            "v": step['to_stop'],
            "speed_mps": speed
        }
        
        tel_res = requests.post(f"{API_URL}/telemetry", json=telemetry)
        if tel_res.status_code == 200:
            tel_data = tel_res.json()
            change = tel_data['new_duration'] - tel_data['old_duration']
            
            if abs(change) < 1:
                emoji = "➖"
                msg = "no change"
            elif change > 0:
                emoji = "🔴"
                msg = f"+{change:.0f}s slower"
            else:
                emoji = "🟢"
                msg = f"{change:.0f}s faster"
            
            print(f"   {emoji} Edge weight updated: {msg}")
        else:
            print(f"   ❌ Telemetry failed")
        
        time.sleep(0.5)  # Simulate travel time
    
    print()
    print("-"*70)
    
    # Recalculate route with updated weights
    print()
    print("4️⃣  Recalculating route with updated edge weights...")
    
    response2 = requests.post(f"{API_URL}/route", json=route_data)
    route2 = response2.json()
    new_duration = route2['total_duration']
    
    print(f"   Original ETA: {initial_duration/60:.1f} minutes")
    print(f"   Updated ETA:  {new_duration/60:.1f} minutes")
    
    difference = new_duration - initial_duration
    if abs(difference) < 5:
        print(f"   ➖  Minimal change ({difference:.0f}s)")
    elif difference > 0:
        print(f"   🔴  Route now {difference:.0f}s ({difference/60:.1f} min) SLOWER")
    else:
        print(f"   🟢  Route now {abs(difference):.0f}s ({abs(difference)/60:.1f} min) FASTER!")
    
    print()
    print("="*70)
    print("✅ Telemetry demonstration complete!")
    print("   Real-time data successfully updated edge weights in the graph.")
    print("="*70)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
