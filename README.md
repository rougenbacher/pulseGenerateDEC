# NEAT Pulse Device Enrollment Code Generator

This Python script automatically fetches all rooms from a NEAT Pulse organization and generates device enrollment codes (DEC) for each room using the Pulse API.

## Features

- Fetches all rooms using the `roomsGet` endpoint
- Generates device enrollment codes using the `roomRegenerateDec` endpoint
- Exports room list and device enrollment codes to CSV file
- Built-in rate limiting to prevent API throttling
- Comprehensive error handling and progress reporting
- Environment variable configuration for security

## Prerequisites

- Python 3.6 or higher
- NEAT Pulse API access with valid API key
- Organization ID for your NEAT Pulse account

## Setup Instructions

### 1. Create and Activate Virtual Environment

#### On macOS/Linux:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

#### On Windows:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

1. Create a `.env` file in the project root directory:
   ```bash
   touch .env
   ```

2. Add your credentials to the `.env` file:
   ```
   API_KEY=your_actual_api_key_here
   ORG_ID=your_actual_organization_id_here
   ```

   **Required Variables:**
   - `API_KEY`: Your NEAT Pulse API key with appropriate permissions
   - `ORG_ID`: Your NEAT Pulse organization ID

   **Note:** If a `.env.example` file exists, you can copy it instead:
   ```bash
   cp .env.example .env
   ```

### 4. Run the Script

Make sure your virtual environment is activated, then:

```bash
python neat_pulse_enrollment.py
```

## Script Output

The script will:

1. Display progress as it fetches rooms and generates codes
2. Show rate limiting delays between API calls
3. Provide a summary table with all generated device enrollment codes
4. Report success/failure status for each room
5. Export all results to a CSV file named `neat_device_enrolllment_codes.csv`

## Example Output

```
Starting device enrollment code generation for organization: your-org-id

=== Fetching Rooms ===
Making GET request to: https://api.pulse.neat.no/v1/orgs/your-org-id/rooms
Found 5 rooms in organization your-org-id

=== Generating Device Enrollment Codes ===

Processing room 1/5: Conference Room A (ID: room-123)
Rate limiting: sleeping for 1.00 seconds...
Making POST request to: https://api.pulse.neat.no/v1/orgs/your-org-id/rooms/room-123/regenerate_dec
Generated DEC for room room-123: ABC123DEF456

============================================================
DEVICE ENROLLMENT CODES SUMMARY
============================================================
✓ Conference Room A (ID: room-123)
  DEC: ABC123DEF456

✓ Conference Room B (ID: room-124)
  DEC: GHI789JKL012

Successfully generated 5/5 device enrollment codes

Results exported to neat_device_enrolllment_codes.csv
```

## CSV Output

The script generates a CSV file named `neat_device_enrolllment_codes.csv` with the following columns:

- `room_name`: Name of the room
- `room_id`: Unique identifier for the room
- `device_enrollment_code`: Generated device enrollment code (or "FAILED" if generation failed)
- `status`: SUCCESS or FAILED for each room

### Example CSV Content:
```csv
room_name,room_id,device_enrollment_code,status
Conference Room A,room-123,ABC123DEF456,SUCCESS
Conference Room B,room-124,GHI789JKL012,SUCCESS
Meeting Room 1,room-125,FAILED,FAILED
```

## Rate Limiting

The script includes built-in rate limiting with a 1-second delay between API requests to prevent hitting API rate limits. This can be adjusted in the `NeatPulseClient` class if needed.

## Error Handling

- Missing environment variables will be detected and reported
- API errors are caught and displayed with detailed information
- Failed room processing is logged but doesn't stop the entire process
- Final summary shows success/failure count

## Security Notes

- Never commit your `.env` file to version control
- Keep your API key secure and rotate it regularly
- The `.env.example` file is safe to commit as it contains no real credentials

## Deactivating Virtual Environment

When you're done working with the script, you can deactivate the virtual environment:

```bash
deactivate
```

## Troubleshooting

- **Virtual Environment Issues**: Make sure the virtual environment is activated before running the script
- **API Key Issues**: Verify your API key is correct and has necessary permissions
- **Organization ID**: Ensure the organization ID matches your NEAT Pulse account
- **Network Issues**: Check internet connectivity and firewall settings
- **Rate Limiting**: If you see 429 errors, the script will automatically handle rate limiting