# NEAT Pulse Device Enrollment Code Generator

This script connects to the NEAT Pulse API to fetch rooms and generate device enrollment codes (DEC) for each room, then exports the results to a CSV file.

## Prerequisites

- Python 3.7 or higher
- NEAT Pulse API key and Organization ID

## Setup Instructions

### 1. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 2. Install Requirements

```bash
pip install python-dotenv requests
```
or 

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project directory:

```bash
# Create .env file
touch .env
```

Add your API credentials to the `.env` file:

```
API_KEY=your_neat_pulse_api_key_here
ORG_ID=your_organization_id_here
```

**Note:** Replace `your_neat_pulse_api_key_here` and `your_organization_id_here` with your actual NEAT Pulse API credentials.

### 4. Run the Script
```bash
python3 generateDEC.py
```

## Output

The script will:
1. Connect to the NEAT Pulse API
2. Fetch all rooms in your organization
3. Generate device enrollment codes for each room
4. Export results to a CSV file:
   - `neat_device_enrolllment_codes.csv` (original script)
   - `neat_device_enrollment_codes_simple.csv` (simplified script)

## CSV Output Format

The generated CSV file contains:
- `room_name`: Name of the room
- `room_id`: Unique room identifier
- `device_enrollment_code`: Generated DEC for the room
- `status`: Success/failure status (original script only)

## Troubleshooting

**Missing API credentials:**
- Ensure your `.env` file exists and contains valid `API_KEY` and `ORG_ID`
- Check that there are no extra spaces or quotes around the values

**API errors:**
- Verify your API key has the necessary permissions
- Check that your organization ID is correct
- The script includes rate limiting (1 request per second) to avoid API limits

**No rooms found:**
- Verify your organization ID is correct
- Check that your API key has access to view rooms

## API Rate Limiting

The script includes built-in rate limiting to comply with API restrictions:
- 1 second delay between API requests
- Automatic retry handling for failed requests

## Deactivating Virtual Environment

When finished, deactivate the virtual environment:

```bash
deactivate
```
