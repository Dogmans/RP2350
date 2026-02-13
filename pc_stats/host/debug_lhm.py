import json
import urllib.request
from pathlib import Path
from dotenv import load_dotenv
import os

# Load .env
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

LHM_URL = os.environ.get("LHM_URL", "")

if not LHM_URL:
    print("LHM_URL not set in .env")
    exit(1)

print(f"Fetching from: {LHM_URL}\n")

try:
    with urllib.request.urlopen(LHM_URL, timeout=2) as response:
        data = json.loads(response.read().decode("utf-8"))
    
    def print_temps(node, indent=0, parent=""):
        if isinstance(node, dict):
            name = node.get("Text") or node.get("Name") or ""
            value = node.get("Value") or node.get("value")
            sensor_type = node.get("SensorType") or node.get("Type") or ""
            
            full_path = f"{parent}/{name}" if parent else name
            
            if value and ("°C" in str(value) or "temp" in name.lower()):
                print("  " * indent + f"{full_path}: {value} [{sensor_type}]")
            
            for child in node.get("Children", []) + node.get("children", []):
                print_temps(child, indent + 1, full_path)
        elif isinstance(node, list):
            for item in node:
                print_temps(item, indent, parent)
    
    print("Temperature sensors found:")
    print_temps(data)
    
except Exception as e:
    print(f"Error: {e}")
