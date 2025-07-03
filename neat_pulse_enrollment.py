#!/usr/bin/env python3
"""
NEAT Pulse Device Enrollment Code Generator

This script fetches all rooms from a NEAT Pulse organization and generates
device enrollment codes (DEC) for each room using the Pulse API.

Requirements:
- python-dotenv
- requests

Usage:
1. Create a .env file with ORG_ID and API_KEY
2. Run: python neat_pulse_enrollment.py
"""

import os
import time
import csv
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv


class NeatPulseClient:
    """Client for interacting with NEAT Pulse API"""
    
    def __init__(self, api_key: str, org_id: str, base_url: str = "https://api.pulse.neat.no/v1"):
        self.api_key = api_key
        self.org_id = org_id
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        # Rate limiting: 1 request per second to be conservative
        self.rate_limit_delay = 1.0
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Implement rate limiting between API calls"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - time_since_last
            print(f"Rate limiting: sleeping for {sleep_time:.2f} seconds...")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make a rate-limited API request"""
        self._rate_limit()
        
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        print(f"Making {method.upper()} request to: {url}")
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response body: {e.response.text}")
            raise
    
    def get_rooms(self) -> List[Dict]:
        """Fetch all rooms for the organization using roomsGet endpoint"""
        endpoint = f"orgs/{self.org_id}/rooms"
        response = self._make_request('GET', endpoint)
        
        rooms_data = response.json()
        print(f"API Response type: {type(rooms_data)}")
        print(f"API Response: {rooms_data}")
        
        # Handle different response structures
        if isinstance(rooms_data, dict):
            # Check if rooms are nested in a property
            rooms = rooms_data.get('rooms') or rooms_data.get('data') or rooms_data.get('items') or []
            if not rooms:
                print("Warning: No rooms found in API response structure")
                print(f"Available keys: {list(rooms_data.keys())}")
        elif isinstance(rooms_data, list):
            rooms = rooms_data
        else:
            print(f"Unexpected API response type: {type(rooms_data)}")
            return []
        
        print(f"Found {len(rooms)} rooms in organization {self.org_id}")
        return rooms
    
    def regenerate_device_enrollment_code(self, room_id: str) -> Optional[str]:
        """Generate device enrollment code for a room using roomRegenerateDec endpoint"""
        endpoint = f"orgs/{self.org_id}/rooms/{room_id}/regenerate_dec"
        
        try:
            response = self._make_request('POST', endpoint)
            result = response.json()
            
            # The DEC might be in different fields depending on API response structure
            dec = result.get('dec') or result.get('deviceEnrollmentCode') or result.get('code')
            
            if dec:
                print(f"Generated DEC for room {room_id}: {dec}")
                return dec
            else:
                print(f"Warning: No DEC found in response for room {room_id}")
                print(f"Response: {result}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Failed to generate DEC for room {room_id}: {e}")
            return None


def export_to_csv(results: List[Dict], filename: str) -> None:
    """Export room list and device enrollment codes to CSV file"""
    
    if not results:
        print("No data to export to CSV")
        return
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['room_name', 'room_id', 'device_enrollment_code', 'status']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header
            writer.writeheader()
            
            # Write data rows
            for result in results:
                writer.writerow({
                    'room_name': result['room_name'],
                    'room_id': result['room_id'],
                    'device_enrollment_code': result['dec'] if result['dec'] else 'FAILED',
                    'status': 'SUCCESS' if result['success'] else 'FAILED'
                })
        
        print(f"CSV export completed: {len(results)} rows written to {filename}")
        
    except Exception as e:
        print(f"Error exporting to CSV: {e}")


def main():
    """Main function to process all rooms and generate DECs"""
    
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv('API_KEY')
    org_id = os.getenv('ORG_ID')
    
    if not api_key or not org_id:
        print("Error: API_KEY and ORG_ID must be set in .env file")
        print("Please create a .env file with:")
        print("API_KEY=your_api_key_here")
        print("ORG_ID=your_organization_id_here")
        return 1
    
    print(f"Starting device enrollment code generation for organization: {org_id}")
    
    try:
        # Initialize API client
        client = NeatPulseClient(api_key, org_id)
        
        # Get all rooms
        print("\n=== Fetching Rooms ===")
        rooms = client.get_rooms()
        
        if not rooms:
            print("No rooms found in the organization")
            return 0
        
        # Generate DEC for each room
        print("\n=== Generating Device Enrollment Codes ===")
        results = []
        
        for i, room in enumerate(rooms, 1):
            print(f"Processing room {i}: type={type(room)}, value={room}")
            
            # Handle case where room might be a string ID instead of dict
            if isinstance(room, str):
                room_id = room
                room_name = f"Room {room_id}"
            elif isinstance(room, dict):
                room_id = room.get('id') or room.get('roomId')
                room_name = room.get('name') or room.get('roomName', 'Unknown')
            else:
                print(f"Warning: Unexpected room type {type(room)}, skipping")
                continue
            
            if not room_id:
                print(f"Warning: Room {i} has no ID, skipping")
                continue
            
            print(f"\nProcessing room {i}/{len(rooms)}: {room_name} (ID: {room_id})")
            
            dec = client.regenerate_device_enrollment_code(room_id)
            
            results.append({
                'room_id': room_id,
                'room_name': room_name,
                'dec': dec,
                'success': dec is not None
            })
        
        # Print summary
        print("\n" + "="*60)
        print("DEVICE ENROLLMENT CODES SUMMARY")
        print("="*60)
        
        successful = 0
        for result in results:
            status = "✓" if result['success'] else "✗"
            dec_display = result['dec'] if result['dec'] else "FAILED"
            print(f"{status} {result['room_name']} (ID: {result['room_id']})")
            print(f"  DEC: {dec_display}")
            print()
            
            if result['success']:
                successful += 1
        
        print(f"Successfully generated {successful}/{len(results)} device enrollment codes")
        
        # Export to CSV
        csv_filename = "neat_device_enrolllment_codes.csv"
        export_to_csv(results, csv_filename)
        print(f"\nResults exported to {csv_filename}")
        
        return 0 if successful == len(results) else 1
        
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())