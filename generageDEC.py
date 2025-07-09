#!/usr/bin/env python3
"""
NEAT Pulse Device Enrollment Code Generator (Simplified)

This script fetches all rooms from a NEAT Pulse organization and generates
device enrollment codes (DEC) for each room using the Pulse API.

Requirements:
- python-dotenv
- requests

Usage:
1. Create a .env file with ORG_ID and API_KEY
2. Run: python neat_pulse_enrollment_simple.py
"""

import os
import time
import csv
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv


class NeatPulseClient:
    """Simplified client for NEAT Pulse API"""
    
    def __init__(self, api_key: str, org_id: str):
        self.api_key = api_key
        self.org_id = org_id
        self.base_url = "https://api.pulse.neat.no/v1"
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    
    def _make_request(self, method: str, endpoint: str) -> requests.Response:
        """Make API request with basic error handling"""
        time.sleep(1)  # Simple rate limiting
        
        url = f"{self.base_url}/{endpoint}"
        response = requests.request(method, url, headers=self.headers)
        response.raise_for_status()
        return response
    
    def get_rooms(self) -> List[Dict]:
        """Fetch all rooms for the organization"""
        endpoint = f"orgs/{self.org_id}/rooms"
        response = self._make_request('GET', endpoint)
        data = response.json()
        
        # Handle different response structures
        if isinstance(data, dict):
            rooms = data.get('rooms', data.get('data', data.get('items', [])))
        else:
            rooms = data if isinstance(data, list) else []
        
        return rooms
    
    def regenerate_device_enrollment_code(self, room_id: str) -> Optional[str]:
        """Generate device enrollment code for a room"""
        endpoint = f"orgs/{self.org_id}/rooms/{room_id}/regenerate_dec"
        
        try:
            response = self._make_request('POST', endpoint)
            result = response.json()
            return result.get('dec') or result.get('deviceEnrollmentCode') or result.get('code')
        except requests.exceptions.RequestException:
            return None


def export_to_csv(results: List[Dict], filename: str) -> None:
    """Export results to CSV file"""
    if not results:
        print("No data to export")
        return
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['room_name', 'room_id', 'device_enrollment_code']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Exported {len(results)} rooms to {filename}")


def get_room_info(room) -> tuple:
    """Extract room ID and name from room data"""
    if isinstance(room, str):
        return room, f"Room {room}"
    elif isinstance(room, dict):
        room_id = room.get('id') or room.get('roomId')
        room_name = room.get('name') or room.get('roomName', 'Unknown')
        return room_id, room_name
    return None, None


def main():
    """Main function to process all rooms and generate DECs"""
    load_dotenv()
    
    api_key = os.getenv('API_KEY')
    org_id = os.getenv('ORG_ID')
    
    if not api_key or not org_id:
        print("Error: API_KEY and ORG_ID must be set in .env file")
        return 1
    
    try:
        client = NeatPulseClient(api_key, org_id)
        
        # Get all rooms
        print("Fetching rooms...")
        rooms = client.get_rooms()
        
        if not rooms:
            print("No rooms found")
            return 0
        
        print(f"Found {len(rooms)} rooms")
        
        # Generate DEC for each room
        results = []
        for i, room in enumerate(rooms, 1):
            room_id, room_name = get_room_info(room)
            
            if not room_id:
                continue
            
            print(f"Processing {i}/{len(rooms)}: {room_name}")
            dec = client.regenerate_device_enrollment_code(room_id)
            
            if dec:
                results.append({
                    'room_name': room_name,
                    'room_id': room_id,
                    'device_enrollment_code': dec
                })
        
        # Export results
        csv_filename = "neat_device_enrollment_codes_simple.csv"
        export_to_csv(results, csv_filename)
        
        print(f"Successfully generated {len(results)} device enrollment codes")
        return 0
        
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())