# AutoDraw AI Agent - Flask API

A Flask-based REST API that wraps the AutoDraw AI Agent CLI functionality, providing web-based access to AutoCAD drawing automation.

## Features

- **REST API Interface**: HTTP endpoints for all AutoDraw functionality
- **Natural Language Processing**: Convert text descriptions to AutoCAD drawings
- **Batch Processing**: Handle multiple drawing requests
- **Health Monitoring**: Check system status and dependencies
- **CORS Support**: Web application integration
- **Comprehensive Documentation**: Full API documentation with examples

## Quick Start

### 1. Prerequisites

- Python 3.7 or higher
- AutoCAD (for drawing functionality)
- OpenAI API key

### 2. Installation

```bash
# Clone or navigate to the project directory
cd BasicAutoCAD

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-openai-api-key"
```

### 3. Start the API

#### Option A: Using the startup script (Recommended)
```bash
python start_api.py
```

#### Option B: Direct execution
```bash
python app.py
```

The API will be available at `http://localhost:5000`

### 4. Test the API

```bash
# Run the test suite
python test_api.py

# Or test manually with curl
curl http://localhost:5000/health
```

## API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check and system status |
| POST | `/api/v1/draw` | Create drawing from specifications |
| POST | `/api/v1/natural` | Process natural language request |
| POST | `/api/v1/natural-draw` | Natural language to drawing (one step) |
| POST | `/api/v1/batch` | Process multiple requests |
| GET | `/api/v1/commands` | Get available AutoCAD commands |
| GET | `/api/v1/lighting-systems` | Get lighting system types |
| GET | `/api/v1/config` | Get system configuration |
| POST | `/api/v1/validate` | Validate specifications |
| GET | `/api/v1/status` | Get current system status |

## Usage Examples

### Python Client

```python
import requests

# Base URL
base_url = "http://localhost:5000"

# Create a linear light
def create_linear_light():
    url = f"{base_url}/api/v1/draw"
    data = {
        "specifications": {
            "command": "linear_light",
            "dimensions": {"length": 10, "width": 4},
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

# Usage
result = create_linear_light()
print(f"Drawing result: {result}")

natural = process_natural_language("Draw a 10-foot linear light with 50W power")
print(f"Natural language result: {natural}")
```

### cURL Examples

```bash
# Health check
curl http://localhost:5000/health

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
curl http://localhost:5000/api/v1/commands
```

### JavaScript Client

```javascript
// Create drawing
async function createDrawing(specifications) {
    const response = await fetch('http://localhost:5000/api/v1/draw', {
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
    const response = await fetch('http://localhost:5000/api/v1/natural', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text })
    });
    return await response.json();
}

// Usage
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

const natural = await processNaturalLanguage('Draw a 10-foot linear light with 50W power');
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | None |
| `PORT` | API server port | 5000 |
| `FLASK_DEBUG` | Enable debug mode | False |

### Example Configuration

```bash
export OPENAI_API_KEY="sk-your-openai-api-key"
export PORT=5000
export FLASK_DEBUG=False
```

## File Structure

```
BasicAutoCAD/
├── app.py                 # Main Flask application
├── start_api.py          # Startup script with checks
├── test_api.py           # API test suite
├── requirements.txt      # Python dependencies
├── API_DOCUMENTATION.md  # Complete API documentation
├── README_API.md         # This file
├── autodraw_ai_agent.py  # Core AutoDraw agent
├── cli_autodraw.py       # Original CLI interface
└── config.py             # Configuration settings
```

## Testing

### Run the Test Suite

```bash
# Start the API first
python start_api.py

# In another terminal, run tests
python test_api.py
```

### Manual Testing

```bash
# Health check
curl http://localhost:5000/health

# Test natural language processing
curl -X POST http://localhost:5000/api/v1/natural \
  -H "Content-Type: application/json" \
  -d '{"text": "Draw a circle with radius 5"}'
```

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

### Logs

The API logs to the console. For production, consider redirecting logs to files:

```bash
python app.py > api.log 2>&1
```

## Development

### Adding New Endpoints

1. Add the endpoint to `app.py`
2. Update the test suite in `test_api.py`
3. Update documentation in `API_DOCUMENTATION.md`

### Code Structure

- `app.py`: Main Flask application with all endpoints
- `start_api.py`: Startup script with dependency checks
- `test_api.py`: Comprehensive test suite
- `API_DOCUMENTATION.md`: Complete API documentation

## Production Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "app.py"]
```

### Environment Variables for Production

```bash
export FLASK_ENV=production
export FLASK_DEBUG=False
export OPENAI_API_KEY="your-production-api-key"
```

## Security Considerations

- The API currently has no authentication
- Consider adding API keys or OAuth for production use
- Validate all input data on the client side
- Use HTTPS in production environments
- Implement rate limiting for production use

## Support

For issues and questions:

1. Check the troubleshooting section above
2. Review the complete API documentation in `API_DOCUMENTATION.md`
3. Run the test suite to verify functionality
4. Check the logs for detailed error messages

## License

This project is part of the AutoDraw AI Agent system. See the main project license for details. 