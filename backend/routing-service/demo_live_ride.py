import requests
import time
import json

API_URL = "http://localhost:8000"

def demo_live_ride():
    print("=" * 60)
    print("🚀 LIVE RIDE SIMULATION - Global Transit Neural Network")
    print("=" * 60)
    print()
    
    # Step 1: Get all stops
    print("📍 Fetching transit network...")
    stops_res = requests.get(f"{API_URL}/stops")
    stops = stops_res.json()
    print(f"✅ Loaded {len(stops)} stops")
    print()
    
    # Step 2: Calculate route
    print("🗺️  Calculating route: Benabdelmalek Ramdane → Université Abdelhamid Mehri")
    route_req = {
        "origin": "benabdelmalek",
        "destination": "mehri"
    }
    route_res = requests.post(f"{API_URL}/route", json=route_req)
    route = route_res.json()
    
    print(f"✅ Route found!")
    print(f"   Duration: {route['total_duration'] / 60:.1f} minutes")
    print(f"   Transfers: {route['transfers']}")
    print(f"   Steps: {len(route['steps'])}")
    print()
    
    # Step 3: Display route
    print("📋 Route Details:")
    print("-" * 60)
    for i, step in enumerate(route['steps'], 1):
        mode_emoji = {
            'tram': '🚊',
            'bus': '🚌',
            'walk': '🚶'
        }.get(step['mode'], '❓')
        
        from_stop = next(s for s in stops if s['id'] == step['from_stop'])
        to_stop = next(s for s in stops if s['id'] == step['to_stop'])
        
        print(f"{i:2}. {mode_emoji} {step['mode'].upper():5} | "
              f"{from_stop['name']:30} → {to_stop['name']:30} | "
              f"{step['duration']/60:.1f} min")
    print("-" * 60)
    print()
    
    # Step 4: Start Live Ride Simulation
    print()
    print("🚀 STARTING LIVE RIDE SIMULATION")
    print("=" * 60)
    
    transit_steps = [s for s in route['steps'] if s['mode'] != 'walk']
    
    for i, step in enumerate(transit_steps, 1):
        from_stop = next(s for s in stops if s['id'] == step['from_stop'])
        to_stop = next(s for s in stops if s['id'] == step['to_stop'])
        
        # Simulate random speed between 10-30 m/s
        import random
        speed = 10 + random.random() * 20
        
        print(f"\n[Segment {i}/{len(transit_steps)}]")
        print(f"🚊 {from_stop['name']} → {to_stop['name']}")
        print(f"⚡ Simulated speed: {speed:.2f} m/s ({speed * 3.6:.1f} km/h)")
        
        # Send telemetry
        telemetry_data = {
            "u": step['from_stop'],
            "v": step['to_stop'],
            "speed_mps": speed
        }
        
        try:
            res = requests.post(f"{API_URL}/telemetry", json=telemetry_data)
            data = res.json()
            
            if res.status_code == 200:
                print(f"✅ Telemetry sent!")
                print(f"   Old duration: {data['old_duration']:.2f}s")
                print(f"   New duration: {data['new_duration']:.2f}s")
                
                change_pct = ((data['new_duration'] - data['old_duration']) / data['old_duration']) * 100
                if change_pct > 0:
                    print(f"   ⬆️  +{change_pct:.1f}% slower")
                else:
                    print(f"   ⬇️  {change_pct:.1f}% faster")
            else:
                print(f"❌ Error: {data}")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        # Simulate travel time
        time.sleep(1.5)
    
    print()
    print("=" * 60)
    print("✅ LIVE RIDE SIMULATION COMPLETE!")
    print("=" * 60)
    print()
    
    # Step 5: Recalculate route to see updated times
    print("🔄 Recalculating route with updated edge weights...")
    route_res_2 = requests.post(f"{API_URL}/route", json=route_req)
    route_2 = route_res_2.json()
    
    old_duration = route['total_duration']
    new_duration = route_2['total_duration']
    
    print(f"   Original ETA: {old_duration / 60:.1f} minutes")
    print(f"   Updated ETA:  {new_duration / 60:.1f} minutes")
    
    if new_duration < old_duration:
        savings = old_duration - new_duration
        print(f"   ✨ Route is now {savings:.0f}s ({savings/60:.1f} min) faster based on real-time data!")
    elif new_duration > old_duration:
        delay = new_duration - old_duration
        print(f"   ⚠️  Route is now {delay:.0f}s ({delay/60:.1f} min) slower based on real-time data")
    else:
        print(f"   ➖ Route duration unchanged")
    
    print()
    print("🎯 Telemetry system demo complete!")

if __name__ == "__main__":
    try:
        demo_live_ride()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure the backend is running on http://localhost:8000")
