# AutoDraw AI Agent - Flask API Documentation

## Overview

The AutoDraw AI Agent Flask API provides REST endpoints for AutoCAD drawing automation. It wraps the existing CLI functionality and provides a web-based interface for creating drawings, processing natural language requests, and managing batch operations.

## Base URL

```
http://localhost:5000
```

## Authentication

Currently, the API does not require authentication. However, you need to set the `OPENAI_API_KEY` environment variable for natural language processing functionality.

## Endpoints

### 1. Health Check

**GET** `/health`

Check the health status of the API and its dependencies.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "autocad_connection": true,
  "openai_api_key": true,
  "version": "1.0.0"
}
```

### 2. Create Drawing

**POST** `/api/v1/draw`

Create a drawing from specifications.

**Request Body:**
```json
{
  "specifications": {
    "command": "linear_light",
    "dimensions": {
      "length": 10,
      "width": 4
    },
    "position": {
      "start_point": [5, 5, 0],
      "end_point": [15, 5, 0]
    },
    "specifications": {
      "wattage": 50,
      "color_temperature": "4000k",
      "lens_type": "frosted"
    }
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Drawing created successfully",
  "result": {
    "success": true,
    "summary": "Linear light created with 50W power"
  },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### 3. Process Natural Language

**POST** `/api/v1/natural`

Process natural language request and return specifications.

**Request Body:**
```json
{
  "text": "Draw a 10-foot linear light from point 5,5 to 15,5 with 50W power and 4000K color temperature"
}
```

**Response:**
```json
{
  "success": true,
  "specifications": {
    "command": "linear_light",
    "dimensions": {
      "length": 10
    },
    "position": {
      "start_point": [5, 5, 0],
      "end_point": [15, 5, 0]
    },
    "specifications": {
      "wattage": 50,
      "color_temperature": "4000k"
    }
  },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### 4. Natural Language to Drawing

**POST** `/api/v1/natural-draw`

Process natural language and create drawing in one step.

**Request Body:**
```json
{
  "text": "Create a rush light with 75W power, 8 feet long, mounted on ceiling"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Drawing created successfully from natural language",
  "result": {
    "success": true,
    "summary": "Rush light created with 75W power"
  },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### 5. Batch Processing

**POST** `/api/v1/batch`

Process multiple drawing requests.

**Request Body:**
```json
{
  "requests": [
    "Draw a 4-foot linear light at position 0,0",
    "Create a circle with radius 3 at center 10,10",
    "Add text 'Sample' at position 5,5"
  ]
}
```

**Response:**
```json
{
  "success": true,
  "total_requests": 3,
  "successful": 2,
  "failed": 1,
  "results": [
    {
      "success": true,
      "specifications": {...}
    },
    {
      "success": true,
      "specifications": {...}
    },
    {
      "success": false,
      "error": "Invalid command"
    }
  ],
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### 6. Get Available Commands

**GET** `/api/v1/commands`

Get list of available AutoCAD commands.

**Response:**
```json
{
  "success": true,
  "commands": {
    "linear_light": "_LSAUTO",
    "circle": "circle",
    "rectangle": "rectangle",
    "polyline": "polyline",
    "text": "text"
  },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### 7. Get Lighting Systems

**GET** `/api/v1/lighting-systems`

Get available lighting system types.

**Response:**
```json
{
  "success": true,
  "lighting_systems": {
    "ls": {
      "name": "Linear Light",
      "command": "linear_light"
    },
    "rush": {
      "name": "Rush Light",
      "command": "rush_light"
    }
  },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### 8. Get Configuration

**GET** `/api/v1/config`

Get current system configuration.

**Response:**
```json
{
  "success": true,
  "configuration": {
    "openai_model": "gpt-4.1-mini",
    "openai_temperature": 0.1,
    "autocad_timeout": 30,
    "command_map": {...},
    "lighting_systems": {...},
    "color_temperatures": ["3000k", "4000k", "5000k"],
    "lens_options": ["clear", "frosted", "prismatic"],
    "mounting_options": ["wall_mount", "ceiling_mount", "suspension"]
  },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### 9. Validate Specifications

**POST** `/api/v1/validate`

Validate drawing specifications without executing.

**Request Body:**
```json
{
  "specifications": {
    "command": "linear_light",
    "dimensions": {
      "length": 10
    }
  }
}
```

**Response:**
```json
{
  "success": true,
  "valid": true,
  "message": "Specifications are valid",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### 10. Export Drawing

**POST** `/api/v1/export`

Create drawing and prepare for export.

**Request Body:**
```json
{
  "specifications": {
    "command": "linear_light",
    "dimensions": {
      "length": 10
    }
  },
  "format": "dwg"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Drawing created and ready for DWG export",
  "format": "dwg",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### 11. Get Status

**GET** `/api/v1/status`

Get current system status.

**Response:**
```json
{
  "success": true,
  "status": {
    "autocad_connection": true,
    "openai_api_key": true,
    "agent_status": "initialized",
    "server_time": "2024-01-15T10:30:00.000Z"
  },
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

## Error Responses

All endpoints return consistent error responses:

```json
{
  "success": false,
  "error": "Error description",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

Common HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid input)
- `404`: Not Found
- `500`: Internal Server Error
- `503`: Service Unavailable (AutoCAD not running)

## Usage Examples

### Python Example

```python
import requests
import json

# Base URL
base_url = "http://localhost:5000"

# Create a linear light
def create_linear_light():
    url = f"{base_url}/api/v1/draw"
    data = {
        "specifications": {
            "command": "linear_light",
            "dimensions": {
                "length": 10,
                "width": 4
            },
            "position": {
                "start_point": [5, 5, 0],
                "end_point": [15, 5, 0]
            },
            "specifications": {
                "wattage": 50,
                "color_temperature": "4000k"
            }
        }
    }
    
    response = requests.post(url, json=data)
    return response.json()

# Process natural language
def process_natural_language(text):
    url = f"{base_url}/api/v1/natural"
    data = {"text": text}
    
    response = requests.post(url, json=data)
    return response.json()

# Check health
def check_health():
    url = f"{base_url}/health"
    response = requests.get(url)
    return response.json()

# Usage
if __name__ == "__main__":
    # Check if service is healthy
    health = check_health()
    print(f"Service status: {health['status']}")
    
    # Create drawing from natural language
    result = process_natural_language(
        "Draw a 10-foot linear light with 50W power"
    )
    print(f"Natural language result: {result}")
    
    # Create specific drawing
    drawing = create_linear_light()
    print(f"Drawing result: {drawing}")
```

### cURL Examples

```bash
# Health check
curl -X GET http://localhost:5000/health

# Create drawing
curl -X POST http://localhost:5000/api/v1/draw \
  -H "Content-Type: application/json" \
  -d '{
    "specifications": {
      "command": "linear_light",
      "dimensions": {"length": 10},
      "position": {"start_point": [5,5,0], "end_point": [15,5,0]},
      "specifications": {"wattage": 50}
    }
  }'

# Natural language processing
curl -X POST http://localhost:5000/api/v1/natural \
  -H "Content-Type: application/json" \
  -d '{"text": "Draw a 10-foot linear light with 50W power"}'

# Get available commands
curl -X GET http://localhost:5000/api/v1/commands
```

### JavaScript Example

```javascript
// Base URL
const baseUrl = 'http://localhost:5000';

// Create drawing
async function createDrawing(specifications) {
    const response = await fetch(`${baseUrl}/api/v1/draw`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ specifications })
    });
    return await response.json();
}

// Process natural language
async function processNaturalLanguage(text) {
    const response = await fetch(`${baseUrl}/api/v1/natural`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text })
    });
    return await response.json();
}

// Usage
async function main() {
    try {
        // Create a linear light
        const drawing = await createDrawing({
            command: 'linear_light',
            dimensions: { length: 10, width: 4 },
            position: {
                start_point: [5, 5, 0],
                end_point: [15, 5, 0]
            },
            specifications: {
                wattage: 50,
                color_temperature: '4000k'
            }
        });
        console.log('Drawing result:', drawing);
        
        // Process natural language
        const natural = await processNaturalLanguage(
            'Draw a 10-foot linear light with 50W power'
        );
        console.log('Natural language result:', natural);
        
    } catch (error) {
        console.error('Error:', error);
    }
}

main();
```

## Environment Variables

Set these environment variables before running the API:

```bash
# Required
export OPENAI_API_KEY="your-openai-api-key"

# Optional
export PORT=5000
export FLASK_DEBUG=False
```

## Running the API

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

3. Start AutoCAD (required for drawing functionality)

4. Run the API:
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## Troubleshooting

### Common Issues

1. **AutoCAD Connection Failed**
   - Ensure AutoCAD is running
   - Check if pywin32 is installed: `pip install pywin32`

2. **OpenAI API Key Missing**
   - Set the `OPENAI_API_KEY` environment variable
   - Natural language processing will not work without this

3. **Port Already in Use**
   - Change the port: `export PORT=5001`
   - Or kill the process using the port

4. **CORS Issues**
   - The API includes CORS headers for web applications
   - If issues persist, check your client configuration

### Debug Mode

Enable debug mode for detailed logging:

```bash
export FLASK_DEBUG=True
python app.py
```

## API Versioning

The API uses version 1 (`/api/v1/`). Future versions will be available at `/api/v2/`, etc.

## Rate Limiting

Currently, no rate limiting is implemented. Consider implementing rate limiting for production use.

## Security Considerations

- The API currently has no authentication
- Consider adding API keys or OAuth for production use
- Validate all input data on the client side
- Use HTTPS in production environments 