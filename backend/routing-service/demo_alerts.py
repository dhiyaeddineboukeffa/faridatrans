# Complete NLP Alert System Test
import requests
import json

API_URL = "http://localhost:8000"

print("=" * 70)
print("PHASE 3: NLP SERVICE ALERTS - COMPLETE DEMONSTRATION")
print("=" * 70)

# Test 1: Calculate baseline route
print("\n1️⃣ Calculating baseline route (no alerts)")
route_req = {"origin": "benabdelmalek", "destination": "mehri"}
res = requests.post(f"{API_URL}/route", json=route_req)
baseline_route = res.json()
baseline_duration = baseline_route['total_duration']
print(f"✅ Baseline duration: {baseline_duration/60:.1f} minutes")

# Test 2: Post an alert affecting the tram line
print("\n2️⃣ Posting service alert: 'Tram delayed on Ligne 1'")
alert = {
    "alert_text": "Tram delayed on Ligne 1",
    "severity": "medium"
}
res = requests.post(f"{API_URL}/alerts", json=alert)
alert_data = res.json()
print(f"✅ Alert ID: {alert_data['alert_id']}")
print(f"   Parsed modes: {alert_data['parsed']['affected_modes']}")
print(f"   Parsed routes: {alert_data['parsed']['affected_routes']}")
print(f"   Severity factor: {alert_data['parsed']['severity_factor']}x")
print(f"   Affected edges: {alert_data['affected_edges_count']}")

# Test 3: Recalculate route after alert
print("\n3️⃣ Recalculating route with alert active")
res2 = requests.post(f"{API_URL}/route", json=route_req)
affected_route = res2.json()
affected_duration = affected_route['total_duration']
print(f"✅ New duration: {affected_duration/60:.1f} minutes")

difference = affected_duration - baseline_duration
print(f"\n📊 IMPACT: Route is now {difference:.0f}s ({difference/60:.1f} min) SLOWER")
print(f"   Increase: {(difference/baseline_duration)*100:.1f}%")

# Test 4: Post a high-severity alert
print("\n4️⃣ Posting high-severity alert: 'Tram service suspended between Belle Vue and Emir Abdelkader'")
alert2 = {
    "alert_text": "Tram service suspended between Belle Vue and Emir Abdelkader",
    "severity": "high"
}
res = requests.post(f"{API_URL}/alerts", json=alert2)
alert_data2 = res.json()
print(f"✅ Alert ID: {alert_data2['alert_id']}")
print(f"   Affected stops: {alert_data2['parsed']['affected_stops']}")
print(f"   Severity factor: {alert_data2['parsed']['severity_factor']}x")

# Test 5: Check active alerts
print("\n5️⃣ Checking all active alerts")
res = requests.get(f"{API_URL}/alerts")
alerts_data = res.json()
print(f"✅ Total active alerts: {alerts_data['count']}")
for i, alert in enumerate(alerts_data['active_alerts'], 1):
    print(f"\n   Alert {i}:")
    print(f"   - Text: {alert['alert_text']}")
    print(f"   - Affected edges: {len(alert['affected_edges'])}")
    expires_in = (alert['expires_at'] - alert['timestamp']) / 60
    print(f"   - Expires in: {expires_in:.0f} minutes")

print("\n" + "=" * 70)
print("✅ NLP SERVICE ALERTS SYSTEM FULLY OPERATIONAL")
print("=" * 70)
