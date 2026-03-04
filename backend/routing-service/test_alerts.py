# Service Alert Testing Script
import requests

API_URL = "http://localhost:8000"

print("Testing NLP Service Alerts")
print("=" * 60)

# Test 1: Alert affecting a specific line
alert1 = {
    "alert_text": "Tram delayed on Ligne 1",
    "severity": "medium"
}

print("\n1. Testing: 'Tram delayed on Ligne 1'")
res = requests.post(f"{API_URL}/alerts", json=alert1)
if res.status_code == 200:
    data = res.json()
    print(f"✅ Alert posted: {data['alert_id']}")
    print(f"   Parsed: {data['parsed']}")
    print(f"   Affected edges: {data['affected_edges_count']}")
else:
    print(f"❌ Failed: {res.status_code}")

# Check active alerts
print("\n2. Checking active alerts...")
res = requests.get(f"{API_URL}/alerts")
if res.status_code == 200:
    data = res.json()
    print(f"✅ Active alerts: {data['count']}")
    for alert in data['active_alerts']:
        print(f"   - {alert['alert_text']}")
else:
    print(f"❌ Failed")

print("\n" + "=" * 60)
