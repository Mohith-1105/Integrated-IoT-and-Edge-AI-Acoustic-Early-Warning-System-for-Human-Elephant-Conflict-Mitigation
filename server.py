"""
Integrated IoT and Edge-AI Acoustic Early Warning System
Major Project Phase II - Server & REST API Engine
Department of AI & ML, Sri Sairam College of Engineering
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
import random
import time
import math
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, 
            static_folder=os.path.join(base_dir, 'static'),
            template_folder=os.path.join(base_dir, 'templates'))

# Default Standby State for Bannerghatta National Park Fringe Village Nodes (All Clear / Safe)
NODES_DATA = [
    {
        "id": "ESP32-NODE-01",
        "name": "Node 1 - Buthanahalli (Bannerghatta NP)",
        "location": "Buthanahalli, Bannerghatta NP Fringe, KA",
        "lat": 12.8224,
        "lng": 77.5770,
        "pir": False,
        "vibration": 0.12, # m/s^2
        "acoustic_db": 34.5,
        "sound_class": "Ambient Forest Sound",
        "confidence": 99.2,
        "status": "SAFE",
        "battery": 95,
        "solar_v": 14.1,
        "lora_rssi": -72,
        "wifi_status": "Connected",
        "cache_count": 0,
        "last_seen": "Just now"
    },
    {
        "id": "ESP32-NODE-02",
        "name": "Node 2 - Begihalli (Anekal Taluk)",
        "location": "Begihalli, Anekal Taluk, KA",
        "lat": 12.79213,
        "lng": 77.61622,
        "pir": False,
        "vibration": 0.18,
        "acoustic_db": 36.1,
        "sound_class": "Ambient Forest Sound",
        "confidence": 98.5,
        "status": "SAFE",
        "battery": 94,
        "solar_v": 14.1,
        "lora_rssi": -65,
        "wifi_status": "Connected",
        "cache_count": 0,
        "last_seen": "2s ago"
    },
    {
        "id": "ESP32-NODE-03",
        "name": "Node 3 - Bettamugilalam (Hosur-Denkanikottai)",
        "location": "Bettamugilalam, Krishnagiri, TN",
        "lat": 12.5195,
        "lng": 77.8200,
        "pir": False,
        "vibration": 0.10,
        "acoustic_db": 32.8,
        "sound_class": "Ambient Forest Sound",
        "confidence": 99.1,
        "status": "SAFE",
        "battery": 92,
        "solar_v": 13.9,
        "lora_rssi": -81,
        "wifi_status": "LoRa Mesh",
        "cache_count": 0,
        "last_seen": "5s ago"
    },
    {
        "id": "ESP32-NODE-04",
        "name": "Node 4 - Ragihalli Village",
        "location": "Ragihalli, Bengaluru Urban, KA",
        "lat": 12.7180,
        "lng": 77.5840,
        "pir": False,
        "vibration": 0.15,
        "acoustic_db": 38.0,
        "sound_class": "Wind Noise",
        "confidence": 99.1,
        "status": "SAFE",
        "battery": 91,
        "solar_v": 14.0,
        "lora_rssi": -69,
        "wifi_status": "Connected",
        "cache_count": 0,
        "last_seen": "1s ago"
    },
    {
        "id": "ESP32-NODE-05",
        "name": "Node 5 - Thammanayakanahalli (Anekal Area)",
        "location": "Thammanayakanahalli, Bengaluru Urban, KA",
        "lat": 12.6100,
        "lng": 77.7100,
        "pir": False,
        "vibration": 0.09,
        "acoustic_db": 31.4,
        "sound_class": "Ambient Forest Sound",
        "confidence": 99.5,
        "status": "SAFE",
        "battery": 96,
        "solar_v": 14.2,
        "lora_rssi": -78,
        "wifi_status": "Connected",
        "cache_count": 0,
        "last_seen": "3s ago"
    },
    {
        "id": "ESP32-NODE-06",
        "name": "Node 6 - Kadusivanapalli (Jawalagiri Area)",
        "location": "Kadusivanapalli, Krishnagiri, TN",
        "lat": 12.5400,
        "lng": 77.7800,
        "pir": False,
        "vibration": 0.08,
        "acoustic_db": 35.2,
        "sound_class": "Rain/Foliage",
        "confidence": 97.4,
        "status": "SAFE",
        "battery": 96,
        "solar_v": 14.2,
        "lora_rssi": -58,
        "wifi_status": "Connected",
        "cache_count": 0,
        "last_seen": "Just now"
    }
]

DETERRENT_STATE = {
    "bio_acoustic_active": False,
    "strobe_light_active": False,
    "siren_active": False,
    "sms_alert_dispatched": False,
    "last_trigger_time": "None",
    "trigger_node": "None"
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status', methods=['GET'])
def get_status():
    active_alerts = [n for n in NODES_DATA if n['status'] == 'ALERT']
    warnings = [n for n in NODES_DATA if n['status'] == 'WARNING']
    overall_status = "CRITICAL_ALERT" if active_alerts else ("WARNING" if warnings else "NORMAL")
    
    return jsonify({
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "overall_status": overall_status,
        "total_nodes": len(NODES_DATA),
        "nodes_online": 6,
        "active_alerts_count": len(active_alerts),
        "warning_count": len(warnings),
        "lora_mesh_health": "100%",
        "cloud_sync": "Active (MakeAcademy Cloud)",
        "solar_power_avg": "14.05V",
        "battery_avg": "94.0%",
        "herd_info": None, # Default: No threat detected
        "deterrent_status": DETERRENT_STATE
    })

@app.route('/api/nodes', methods=['GET'])
def get_nodes():
    # Simulate slight live telemetry variance around ambient levels for safe nodes
    for node in NODES_DATA:
        if node['status'] == 'SAFE':
            node['acoustic_db'] = round(30.0 + random.uniform(0, 5), 1)
            node['vibration'] = round(0.05 + random.uniform(0, 0.15), 2)
            
    return jsonify(NODES_DATA)

@app.route('/api/simulate-node-alert', methods=['POST'])
def simulate_node_alert():
    data = request.json or {}
    node_id = data.get('node_id')
    reset = data.get('reset', False)
    
    if reset:
        for node in NODES_DATA:
            node['status'] = 'SAFE'
            node['pir'] = False
            node['vibration'] = 0.12
            node['acoustic_db'] = 34.0
            node['sound_class'] = 'Ambient Forest Sound'
            node['confidence'] = 99.1
        return jsonify({"status": "reset", "message": "All nodes restored to SAFE / Standby state."})
        
    target = None
    for node in NODES_DATA:
        if node['id'] == node_id:
            node['status'] = 'ALERT'
            node['pir'] = True
            node['vibration'] = 1.85
            node['acoustic_db'] = 88.5
            node['sound_class'] = 'Elephant Trumpet'
            node['confidence'] = 96.4
            target = node
        else:
            node['status'] = 'SAFE'
            node['pir'] = False
            node['vibration'] = 0.10
            node['acoustic_db'] = 32.0
            node['sound_class'] = 'Ambient Forest Sound'
            node['confidence'] = 99.0
            
    if target:
        return jsonify({"status": "alert_triggered", "node": target})
    return jsonify({"status": "error", "message": "Node ID not found"}), 404

@app.route('/api/node-event', methods=['POST'])
def handle_node_event():
    """Hardware ESP32 HTTP POST Telemetry Ingestion Endpoint"""
    data = request.json or {}
    node_id = data.get('node_id')
    
    for node in NODES_DATA:
        if node['id'] == node_id:
            node['pir'] = data.get('pir', node['pir'])
            node['vibration'] = data.get('vibration', node['vibration'])
            node['acoustic_db'] = data.get('acoustic_db', node['acoustic_db'])
            node['sound_class'] = data.get('sound_class', node['sound_class'])
            node['confidence'] = data.get('confidence', node['confidence'])
            if 'Elephant' in node['sound_class'] or node['pir']:
                node['status'] = 'ALERT'
            else:
                node['status'] = 'SAFE'
            return jsonify({"status": "accepted", "node": node})
            
    return jsonify({"status": "error", "message": "Node ID not found"}), 404

@app.route('/api/edge-ai/predict', methods=['POST'])
def predict_audio():
    data = request.json or {}
    sample_type = data.get('sample_type', 'wind')
    
    if sample_type == 'trumpet':
        res = {
            "class": "Elephant Trumpet",
            "confidence": round(96.4 + random.uniform(-1, 2), 1),
            "threat_score": 98,
            "mfcc": [14.2, -8.5, 6.2, 12.1, -4.3, 8.7, -2.1, 5.4, -1.8, 4.2, 2.1, -0.9],
            "frequency_peak_hz": 1450,
            "energy_db": 88.5,
            "pir_confirmation": True,
            "vibration_confirmed": True,
            "fused_decision": "CONFIRMED ELEPHANT DETECTED"
        }
    elif sample_type == 'rumble':
        res = {
            "class": "Elephant Infrasonic Rumble",
            "confidence": round(91.8 + random.uniform(-1, 2), 1),
            "threat_score": 85,
            "mfcc": [18.5, 12.1, -3.2, 4.5, -9.1, 2.2, -5.4, 1.2, 0.8, -2.1, 1.4, -0.5],
            "frequency_peak_hz": 24,
            "energy_db": 74.2,
            "pir_confirmation": True,
            "vibration_confirmed": True,
            "fused_decision": "CONFIRMED ELEPHANT DETECTED"
        }
    elif sample_type == 'wind':
        res = {
            "class": "Environmental Wind Noise",
            "confidence": 98.2,
            "threat_score": 5,
            "mfcc": [-5.2, 2.1, -1.5, 0.8, -0.4, 1.1, -0.2, 0.5, -0.1, 0.3, 0.1, -0.2],
            "frequency_peak_hz": 120,
            "energy_db": 34.0,
            "pir_confirmation": False,
            "vibration_confirmed": False,
            "fused_decision": "NON-ELEPHANT SOUND - CLEAR"
        }
    else: # Vehicle engine
        res = {
            "class": "Vehicle Motor Noise",
            "confidence": 94.6,
            "threat_score": 12,
            "mfcc": [8.1, -12.4, 2.3, -4.1, 1.8, -2.2, 0.9, -1.1, 0.4, -0.8, 0.2, -0.3],
            "frequency_peak_hz": 420,
            "energy_db": 58.0,
            "pir_confirmation": False,
            "vibration_confirmed": False,
            "fused_decision": "NON-ELEPHANT SOUND - CLEAR"
        }
        
    return jsonify(res)

@app.route('/api/deterrent/trigger', methods=['POST'])
def trigger_deterrent():
    data = request.json or {}
    device = data.get('device')
    action = data.get('action')
    
    if device == 'bio_acoustic':
        DETERRENT_STATE['bio_acoustic_active'] = not DETERRENT_STATE['bio_acoustic_active'] if action == 'toggle' else (action == 'on')
    elif device == 'strobe_light':
        DETERRENT_STATE['strobe_light_active'] = not DETERRENT_STATE['strobe_light_active'] if action == 'toggle' else (action == 'on')
    elif device == 'siren':
        DETERRENT_STATE['siren_active'] = not DETERRENT_STATE['siren_active'] if action == 'toggle' else (action == 'on')
    elif device == 'sms_broadcast':
        DETERRENT_STATE['sms_alert_dispatched'] = True
        
    DETERRENT_STATE['last_trigger_time'] = time.strftime("%H:%M:%S")
    return jsonify({
        "status": "success",
        "message": f"{device} set to {action}",
        "deterrent_state": DETERRENT_STATE
    })

@app.route('/api/dss/recommendations', methods=['GET'])
def get_dss():
    return jsonify({
        "predicted_conflict_time": "None (System Standby)",
        "target_vulnerable_village": "None - Boundary Secure",
        "recommended_actions": [
            {
                "priority": "LOW",
                "action": "All 6 ESP32 field nodes online and operating normally",
                "status": "ACTIVE"
            },
            {
                "priority": "LOW",
                "action": "Solar battery levels optimal (Avg 14.05V)",
                "status": "HEALTHY"
            },
            {
                "priority": "LOW",
                "action": "LoRa Mesh communication signal strength stable across Anekal sector",
                "status": "CONNECTED"
            }
        ]
    })

if __name__ == '__main__':
    print("Starting Integrated IoT and Edge-AI Acoustic Early Warning System Server...")
    print("Serving on http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
