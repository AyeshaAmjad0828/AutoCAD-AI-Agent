# AutoDraw AI Agent

An intelligent AutoCAD automation system that uses natural language processing to create complex lighting design drawings using your existing AutoDraw palette commands.

## 🚀 Enhanced Features

### Complex Drawing Capabilities
- **Full AutoDraw Palette Integration**: Uses all your existing AutoLISP commands (`LSAUTO`, `LSRAUTO`, `RushAuto`, etc.)
- **Advanced Lighting Systems**: Support for Linear Light, Rush Light, PG Light, Magneto Track, and more
- **Emergency Backup Systems**: Add emergency packs and backup lighting
- **Driver Management**: Calculate and update driver specifications
- **Asset Management**: Import and redefine blocks and assets
- **Drawing Utilities**: Purge, details, suspension kit counting, and more

### Natural Language Processing
- **Complex Requests**: Handle detailed specifications in plain English
- **Multi-Parameter Support**: Dimensions, positions, specifications, and additional parameters
- **Context Awareness**: Understands lighting design terminology and requirements

### Command Line Interface
- **Parameter-based Specification**: Precise control via command-line arguments
- **Batch Processing**: Process multiple drawing requests from files
- **Validation**: Built-in specification validation and error handling
- **Dry Run Mode**: Test specifications without executing AutoCAD commands

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

## 🚀 Usage

### Command Line Interface

#### Natural Language Processing
```bash
python cli_autodraw.py --natural "Draw a 10-foot linear light from point 5,5 to 15,5 with 50W power and 4000K color temperature"
```

#### Parameter-based Specification
```bash
python cli_autodraw.py --system linear_light --length 10 --width 4 --wattage 50 --color-temp 4000k --start 5,5 --end 15,5
```

#### Complex Specifications
```bash
python cli_autodraw.py --system rush_light --length 8 --width 6 --wattage 75 --mounting ceiling_mount --lens frosted --emergency-backup --dimmable
```

#### Batch Processing
```bash
python cli_autodraw.py --batch-file example_requests.txt --output results.json
```

#### Utility Commands
```bash
python cli_autodraw.py --command add_empck --quantity 1
python cli_autodraw.py --command details
python cli_autodraw.py --command purge_all
```

### GUI Interface

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

### Python API

```python
from autodraw_ai_agent import AutoDrawAIAgent

# Initialize the agent
agent = AutoDrawAIAgent()

# Create complex drawings
result = agent.create_complete_drawing(
    "Create a rush light fixture 8 feet long, 4 inches wide, mounted on ceiling with frosted lens"
)

# Batch processing
requests = [
    "Draw a 10-foot linear light with 50W power",
    "Add emergency pack",
    "Calculate driver specifications"
]
results = agent.batch_process_requests(requests)
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

## 🎯 Supported AutoDraw Commands

The AI agent now supports **ALL** your AutoDraw palette commands:

### Lighting Systems
- `_LSAUTO` - Linear Light AutoDraw
- `_LSRAUTO` - Linear Light with Reflector AutoDraw  
- `_RushAuto` - Rush Light AutoDraw
- `_RushRecAuto` - Rush Recessed AutoDraw
- `_PGAuto` - PG Light AutoDraw
- `_MagTrkAuto` - Magneto Track AutoDraw

### Utility Commands
- `_LSREP` - Repeat Last Draw
- `_Details` - Add Details
- `_ADDEM` - Add Emergency Pack
- `_CustomLumenCalculator` - Output Modifier
- `_DriverCalculator` - Driver Calculator
- `_DriverUpdater` - Driver Update
- `_RunID` - RunID Update
- `_SuspCnt` - Suspension Kit Count
- `_ArrowToggle` - Wire Way Toggle
- `_ImportAssets` - Import Assets
- `_BlockRedefine` - Redefine Blocks
- `_PALL` - Purge All

## 📋 Example Complex Requests

The system can now handle sophisticated drawing requests:

### Basic Lighting
```
"Draw a 10-foot linear light from point 5,5 to 15,5 with 50W power and 4000K color temperature"
```

### Advanced Systems
```
"Create a rush light fixture 8 feet long, 4 inches wide, mounted on ceiling with frosted lens"
"Design a magneto track system 12 feet long with 75W fixtures every 2 feet"
"Generate a PG light 6 feet long with 40W power and 3000K color temperature"
```

### Emergency and Utility
```
"Create a linear light with reflector 15 feet long, 6 inches wide, with emergency backup"
"Add emergency pack to the current drawing"
"Calculate driver specifications for 60W linear light"
"Update driver brand for existing fixtures"
"Add suspension kit count for ceiling mounted fixtures"
```

### Asset Management
```
"Import all lighting assets and blocks"
"Redefine all blocks in the drawing"
"Purge all unused elements from the drawing"
```

## 🧪 Testing

### Run Comprehensive Tests
```bash
# Test without AutoCAD (dry run)
python test_autodraw_commands.py

# Test with AutoCAD (requires AutoCAD to be running)
python test_autodraw_commands.py --test-autocad

# Verbose output
python test_autodraw_commands.py --verbose
```

### Test Individual Components
```bash
# Test CLI functionality
python test_cli.py

# Test AutoCAD connection
python test_autocad_connection.py
```

## 🔧 Configuration

Edit `config.py` to customize:

- **AutoDraw Commands**: All AutoLISP command mappings
- **Lighting Systems**: System specifications and defaults
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