import time
import json
import random
import os
import schedule
import logging

logging.basicConfig(level=logging.INFO)

# Configuration
KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
TOPIC = 'vehicle_positions'

# Constantine, Algeria - Approximate Center
DEFAULT_LAT = 36.365
DEFAULT_LON = 6.615

def create_producer():
    # Mock producer for testing without Kafka
    logging.info("Mock Kafka producer created")
    return {"mock": True}

producer = None

def send_vehicle_positions():
    global producer
    if not producer:
        producer = create_producer()
        if not producer:
            return

    # Mock Data - Constantine Tramway & Buses
    # Starting positions near key stations
    vehicles = [
        {"id": "tram_1", "route": "Ligne 1", "type": "tram", "lat": 36.36875, "lon": 6.60741, "status": "MOVING"}, # Benabdelmalek
        {"id": "tram_2", "route": "Ligne 1", "type": "tram", "lat": 36.31043, "lon": 6.61941, "status": "MOVING"}, # Zouaghi
        {"id": "bus_101", "route": "101", "type": "bus", "lat": 36.35085, "lon": 6.60099, "status": "MOVING"}, # Kadour
        {"id": "taxi_55", "route": "Taxi", "type": "taxi", "lat": 36.34072, "lon": 6.61768, "status": "STOPPED"}, # Mentouri
    ]
    
    # Update positions slightly to simulate movement
    for v in vehicles:
        # Random movement for demo purposes
        v["lat"] += random.uniform(-0.0005, 0.0005)
        v["lon"] += random.uniform(-0.0005, 0.0005)
        v["timestamp"] = time.time()
        
        logging.info(f"Position update for {v['id']} ({v['type']}) at {v['lat']:.5f}, {v['lon']:.5f}")
        # In production, this would send to Kafka:
        # producer.send(TOPIC, v)

def main():
    print(f"Starting Ingestion Service... Connecting to {KAFKA_BOOTSTRAP_SERVERS}")
    # Wait for Kafka to be ready
    time.sleep(10) 
    
    schedule.every(3).seconds.do(send_vehicle_positions)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
