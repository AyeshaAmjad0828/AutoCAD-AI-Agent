# AutoDraw AI Agent

An intelligent AI agent that creates AutoCAD drawings automatically from natural language specifications. This system leverages your existing AutoLISP infrastructure to generate lighting design drawings without human intervention.

## Features

- **Natural Language Processing**: Describe your drawing requirements in plain English
- **AutoCAD Integration**: Seamlessly connects to AutoCAD using COM API
- **Existing LISP Functions**: Utilizes your current AutoLISP commands without modification
- **Multiple Lighting Systems**: Supports LS, LSR, Rush, PG, and Magneto track systems
- **Batch Processing**: Process multiple drawing requests simultaneously
- **GUI Interface**: User-friendly graphical interface for easy operation
- **Real-time Logging**: Comprehensive logging and error handling

## Supported Lighting Systems

- **Linear Light (LS)**: Standard linear lighting system
- **Linear Light with Reflector (LSR)**: Enhanced output with reflector
- **Rush Light**: High-output rush lighting system
- **Rush Recessed**: Recessed rush lighting system
- **PG Light**: PG series lighting system
- **Magneto Track**: Track-mounted magneto lighting system

## Prerequisites

- **AutoCAD**: Any recent version with COM API support
- **Python 3.8+**: Required for the AI agent
- **OpenAI API Key**: For natural language processing
- **Windows OS**: Required for AutoCAD COM integration

## Installation

1. **Clone or download the project files**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up OpenAI API key**:
   - Get an API key from [OpenAI](https://platform.openai.com/)
   - Set environment variable:
     ```bash
     set OPENAI_API_KEY=your_api_key_here
     ```
   - Or create a `.env` file:
     ```
     OPENAI_API_KEY=your_api_key_here
     ```

4. **Ensure AutoCAD is installed and accessible**

## Usage

### GUI Interface (Recommended)

1. **Start the GUI**:
   ```bash
   python gui_interface.py
   ```

2. **Connect to AutoCAD**:
   - Click "Connect to AutoCAD"
   - Ensure AutoCAD is running

3. **Enter your drawing request**:
   - Type natural language description
   - Use examples or templates for guidance

4. **Create the drawing**:
   - Click "Create Drawing"
   - Monitor progress in the output log

### Command Line Interface

```python
from autodraw_ai_agent import AutoDrawAIAgent

# Initialize the agent
agent = AutoDrawAIAgent()

# Create a drawing
result = agent.create_complete_drawing(
    "Draw a 10-foot linear light from point 5,5 to 15,5 with 50W power and 4000K color temperature"
)

print(result)
```

### Batch Processing

1. **Create a batch file** (see `batch_example.txt`):
   ```
   Draw a 10-foot linear light from point 5,5 to 15,5 with 50W power and 4000K color temperature
   Create a rush light fixture 8 feet long, 4 inches wide, mounted on ceiling with frosted lens
   Design a magneto track system 12 feet long with 75W fixtures every 2 feet
   ```

2. **Load and execute**:
   - Use GUI: Load batch file and click "Execute Batch"
   - Use command line:
     ```python
     requests = [
         "Draw a 10-foot linear light...",
         "Create a rush light fixture...",
         "Design a magneto track system..."
     ]
     results = agent.batch_process_requests(requests)
     ```

## Natural Language Examples

### Basic Linear Light
```
"Draw a 10-foot linear light from point 5,5 to 15,5 with 50W power and 4000K color temperature"
```

### Rush Light with Specifications
```
"Create a rush light fixture 8 feet long, 4 inches wide, mounted on ceiling with frosted lens"
```

### Magneto Track System
```
"Design a magneto track system 12 feet long with 75W fixtures every 2 feet"
```

### Complex Specifications
```
"Generate a linear light with reflector 15 feet long, wall mounted, 60W power, 3500K color temperature, with emergency backup and dimming capability"
```

## Configuration

Edit `config.py` to customize:

- **OpenAI settings**: Model, temperature, max tokens
- **AutoCAD settings**: Timeout, command delay
- **Default specifications**: Wattage, color temperature, mounting type
- **Available options**: Lighting systems, lens types, mounting options

## File Structure

```
Coronet/
├── autodraw_ai_agent.py    # Main AI agent class
├── gui_interface.py        # Graphical user interface
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── batch_example.txt     # Example batch file
├── AD App&Assets/        # Your existing AutoCAD assets
├── AutoDraw.xtp          # Your existing tool palette
└── instructions.txt      # Original instructions
```

## Supported Commands

The AI agent maps to your existing AutoLISP commands:

- `_LSAUTO` - Linear Light AutoDraw
- `_LSRAUTO` - Linear Light with Reflector AutoDraw
- `_RushAuto` - Rush Light AutoDraw
- `_RushRecAuto` - Rush Recessed AutoDraw
- `_PGAuto` - PG Light AutoDraw
- `_MagTrkAuto` - Magneto Track AutoDraw
- `_LSREP` - Repeat Last Draw
- `_Details` - Details
- `_ADDEM` - Add EMPCK
- `_CustomLumenCalculator` - Output Modifier
- `_DriverCalculator` - Driver Calculator
- `_DriverUpdater` - Driver Update
- `_RunID` - RunID Update
- `_SuspCnt` - Susp Kit Count
- `_ArrowToggle` - WW Toggle
- `_ImportAssets` - Import Assets
- `_BlockRedefine` - Redefine Blocks
- `_PALL` - Purge ALL

## Error Handling

The system includes comprehensive error handling for:

- **AutoCAD connection issues**
- **Invalid commands or parameters**
- **Natural language parsing errors**
- **Command execution timeouts**
- **API rate limiting**

## Troubleshooting

### Common Issues

1. **"AutoCAD is not running"**
   - Ensure AutoCAD is open and running
   - Check that COM API is enabled

2. **"OpenAI API key required"**
   - Set the OPENAI_API_KEY environment variable
   - Or create a .env file with your API key

3. **"Command execution failed"**
   - Verify your AutoLISP functions are loaded
   - Check AutoCAD command line for specific errors

4. **"Parsing error"**
   - Try rephrasing your request more clearly
   - Use the provided examples as templates

### Debug Mode

Enable detailed logging by modifying the logging level in `config.py`:

```python
LOGGING_CONFIG = {
    "level": "DEBUG",  # Change from "INFO" to "DEBUG"
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "autodraw_ai.log"
}
```

## Performance Tips

1. **Batch Processing**: Use batch files for multiple drawings
2. **Clear Specifications**: Be specific about dimensions and requirements
3. **Template Usage**: Use provided templates for common scenarios
4. **Error Recovery**: Check logs for specific error messages

## Future Enhancements

- **Voice Input**: Speech-to-text for drawing requests
- **Image Recognition**: Generate drawings from sketches or photos
- **Advanced AI Models**: Integration with specialized CAD AI models
- **Cloud Integration**: Web-based interface for remote access
- **Custom Training**: Domain-specific model training for your industry

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review the error logs in the GUI
3. Verify your AutoCAD and AutoLISP setup
4. Ensure all dependencies are installed correctly

## License

This project is designed to work with your existing AutoLISP infrastructure. Ensure compliance with AutoCAD and OpenAI licensing terms.

---

**Note**: This AI agent is designed to work with your existing AutoLISP functions. Make sure all your LISP files are properly loaded in AutoCAD before using the system. 